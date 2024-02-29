from odoo import models,fields,api


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
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = False