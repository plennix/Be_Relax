from odoo import models,fields,api
from odoo.addons.base.models.res_partner import _tz_get
from odoo.fields import Datetime
import pytz
import logging
from datetime import datetime
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
