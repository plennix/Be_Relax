from odoo import models,fields,api
from odoo.addons.base.models.res_partner import _tz_get
from odoo.fields import Datetime
import pytz
import logging
from datetime import datetime
import collections
import contextlib
from odoo.addons.resource.models.resource import float_to_time

_logger = logging.getLogger(__name__)


class DatetimeExtend(Datetime):

    @staticmethod
    def context_timestamp_custom(record, timestamp):
        assert isinstance(timestamp, datetime), 'Datetime instance expected'
        if record._name == 'attendance.record' and record.timezone:
            tz_name = record.timezone
        else:
            tz_name = record._context.get('tz') or record.env.user.tz

        utc_timestamp = pytz.utc.localize(timestamp, is_dst=False)  # UTC = no DST
        if tz_name:
            try:
                context_tz = pytz.timezone(tz_name)
                return utc_timestamp.astimezone(context_tz)
            except Exception:
                _logger.debug("failed to compute context/client-specific timestamp, "
                              "using the UTC value",
                              exc_info=True)
        return utc_timestamp

    Datetime.context_timestamp = context_timestamp_custom

class AttendanceRecord(models.Model):
    _name = "attendance.record"
    _description = "POS Attendance"
    _order = "check_in desc"

    employee_id = fields.Many2one('hr.employee')
    session_id = fields.Many2one('pos.session')
    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=True)
    check_out = fields.Datetime(string="Check Out")
    break_time = fields.Datetime(string="Break Time")
    resume_time = fields.Datetime(string="Resume Time")
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)
    config_id = fields.Many2one('pos.config', string='Point of Sale', readonly=True, store=True)
    company_id = fields.Many2one('res.company',related='config_id.company_id', string='Company', readonly=True, store=True)
    timezone = fields.Selection(_tz_get, string='Timezone', compute='_get_company_timezone', store=True)
    attendance_id = fields.Many2one(
        "hr.attendance",
        ondelete="cascade",
        store=True,
        copy=False,
        string="Attendance Reference",
    )
    break_hours = fields.Char(
        string="Break Hours",
        compute="_compute_break_hours",
        store=True,
        readonly=True,
    )

    @api.depends("break_time", "resume_time")
    def _compute_break_hours(self):
        for rec in self:
            if rec.break_time and rec.resume_time:
                delta = rec.resume_time - rec.break_time
                rec.break_hours = delta.total_seconds() / 3600.0
            else:
                rec.break_hours = False

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                delta = attendance.check_out - attendance.check_in
                worked_hours = delta.total_seconds() / 3600.0
                if attendance.break_time and attendance.resume_time:
                    delta = attendance.resume_time - attendance.break_time
                    break_hours = delta.total_seconds() / 3600.0
                    worked_hours = worked_hours - break_hours
                attendance.worked_hours = worked_hours
            else:
                attendance.worked_hours = False

    @api.depends('employee_id', 'employee_id.company_id', 'employee_id.company_id.timezone')
    def _get_company_timezone(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.company_id and rec.employee_id.company_id.timezone:
                rec.timezone = rec.employee_id.company_id.timezone
            else:
                rec.timezone = False

    def _export_rows(self, fields, *, _is_toplevel_call=True):
        import_compatible = self.env.context.get('import_compat', True)
        lines = []

        def splittor(rs):
            """ Splits the self recordset in batches of 1000 (to avoid
            entire-recordset-prefetch-effects) & removes the previous batch
            from the cache after it's been iterated in full
            """
            for idx in range(0, len(rs), 1000):
                sub = rs[idx:idx + 1000]
                for rec in sub:
                    yield rec
                sub.invalidate_recordset()

        if not _is_toplevel_call:
            splittor = lambda rs: rs

        # memory stable but ends up prefetching 275 fields (???)
        for record in splittor(self):
            # main line of record, initially empty
            current = [''] * len(fields)
            lines.append(current)

            # list of primary fields followed by secondary field(s)
            primary_done = []

            # process column by column
            for i, path in enumerate(fields):
                if not path:
                    continue

                name = path[0]
                if name in primary_done:
                    continue

                if name == '.id':
                    current[i] = str(record.id)
                elif name == 'id':
                    current[i] = (record._name, record.id)
                else:

                    field = record._fields[name]
                    value = record[name]
                    if field.name == 'worked_hours':
                        value = record[name]
                        converted_time = float_to_time(value)
                        hours = str(converted_time.hour)
                        minute = str(converted_time.minute)
                        if converted_time.hour < 10:
                            hours = '0' + hours
                        if converted_time.minute < 10:
                            minute = '0' + minute
                        value = hours + ':' + minute

                    # this part could be simpler, but it has to be done this way
                    # in order to reproduce the former behavior
                    if not isinstance(value, models.BaseModel):
                        current[i] = field.convert_to_export(value, record)
                    else:
                        primary_done.append(name)
                        # recursively export the fields that follow name; use
                        # 'display_name' where no subfield is exported
                        fields2 = [(p[1:] or ['display_name'] if p and p[0] == name else [])
                                   for p in fields]

                        # in import_compat mode, m2m should always be exported as
                        # a comma-separated list of xids or names in a single cell
                        if import_compatible and field.type == 'many2many':
                            index = None
                            # find out which subfield the user wants & its
                            # location as we might not get it as the first
                            # column we encounter
                            for name in ['id', 'name', 'display_name']:
                                with contextlib.suppress(ValueError):
                                    index = fields2.index([name])
                                    break
                            if index is None:
                                # not found anything, assume we just want the
                                # name_get in the first column
                                name = None
                                index = i

                            if name == 'id':
                                xml_ids = [xid for _, xid in value.__ensure_xml_id()]
                                current[index] = ','.join(xml_ids)
                            else:
                                current[index] = field.convert_to_export(value, record)
                            continue

                        lines2 = value._export_rows(fields2, _is_toplevel_call=False)
                        if lines2:
                            # merge first line with record's main line
                            for j, val in enumerate(lines2[0]):
                                if val or isinstance(val, (int, float)):
                                    current[j] = val
                            # append the other lines at the end
                            lines += lines2[1:]
                        else:
                            current[i] = ''

        # if any xid should be exported, only do so at toplevel
        if _is_toplevel_call and any(f[-1] == 'id' for f in fields):
            bymodels = collections.defaultdict(set)
            xidmap = collections.defaultdict(list)
            # collect all the tuples in "lines" (along with their coordinates)
            for i, line in enumerate(lines):
                for j, cell in enumerate(line):
                    if isinstance(cell, tuple):
                        bymodels[cell[0]].add(cell[1])
                        xidmap[cell].append((i, j))
            # for each model, xid-export everything and inject in matrix
            for model, ids in bymodels.items():
                for record, xid in self.env[model].browse(ids).__ensure_xml_id():
                    for i, j in xidmap.pop((record._name, record.id)):
                        lines[i][j] = xid
            assert not xidmap, "failed to export xids for %s" % ', '.join('{}:{}' % it for it in xidmap.items())

        return lines
