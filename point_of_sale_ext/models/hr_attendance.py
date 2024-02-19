import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    attendance_record_ids = fields.One2many('attendance.record', 'attendance_id', string='POS Attendance Record(s)')