import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.base.models.res_partner import _tz_get
import collections
import contextlib
from odoo.addons.resource.models.resource import float_to_time


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    attendance_record_ids = fields.One2many('attendance.record', 'attendance_id', string='POS Attendance Record(s)')
    config_id = fields.Many2one('pos.config', string="Shop")
    timezone = fields.Selection(_tz_get, string='Timezone', compute='_get_company_timezone', store=True)

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

    @api.depends('employee_id', 'employee_id.company_id', 'employee_id.company_id.timezone')
    def _get_company_timezone(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.company_id and rec.employee_id.company_id.timezone:
                rec.timezone = rec.employee_id.company_id.timezone
            else:
                rec.timezone = False

    @api.model
    def create(self, vals):
        newrecord = super(HrAttendance, self).create(vals)
        user_id = self.env['res.users'].sudo().browse(self._context.get('uid'))
        if user_id and user_id.allowed_pos_configs:
            newrecord.config_id = user_id.allowed_pos_configs[0].id
            attendance = self.env['attendance.record'].create({
                'employee_id': newrecord.employee_id.id,
                'check_in': newrecord.check_in,
                'config_id': user_id.allowed_pos_configs[0].id,
                'attendance_id': newrecord.id if newrecord else False,
            })
            if newrecord.employee_id:
                newrecord.employee_id.sudo().write(
                    {'pos_attendance_state': 'checked_in', 'last_pos_attendance_record': attendance.id})
        return newrecord

    def write(self, vals):
        newrecord = super(HrAttendance, self).write(vals)
        return newrecord
