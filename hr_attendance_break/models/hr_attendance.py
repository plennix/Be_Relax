import pytz

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from odoo.tools import format_datetime


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    break_ids = fields.One2many(
        "hr.attendance.break",
        "attendance_id",
        help="list of attendances breaks for the employee",
        string="Break",
    )
    break_hours = fields.Char(
        string="Break Hours",
        compute="_compute_break_hours",
        store=True,
        readonly=True,
    )

    @api.depends("break_ids.break_time", "break_ids.resume_time")
    def _compute_break_hours(self):
        totalSecs = 0
        for br in self.break_ids:
            if br.break_hours:
                delta = br.resume_time - br.break_time
                totalSecs = delta.seconds
        totalSecs, sec = divmod(totalSecs, 60)
        hr, min = divmod(totalSecs, 60)
        self.break_hours = "%d:%02d:%02d" % (hr, min, sec)

    @api.depends("check_in", "check_out", "break_hours")
    def _compute_worked_hours(self):
        super()._compute_worked_hours()
        for attendance in self:
            if attendance.break_hours and attendance.worked_hours:
                h, m, s = attendance.break_hours.split(":")
                attendance.worked_hours = (
                    attendance.worked_hours
                    - (int(h) * 3600 + int(m) * 60 + int(s)) / 3600.0
                )

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            # if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
            #     raise exceptions.ValidationError(
            #         _("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
            #             'empl_name': attendance.employee_id.name,
            #             'datetime': format_datetime(self.env, attendance.check_in, dt_format=False),
            #         })

            if not attendance.check_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                # if no_check_out_attendances:
                # raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                #     'empl_name': attendance.employee_id.name,
                #     'datetime': format_datetime(self.env, no_check_out_attendances.check_in, dt_format=False),
                # })
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '<', attendance.check_out),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                # if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                #     raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                #         'empl_name': attendance.employee_id.name,
                #         'datetime': format_datetime(self.env, last_attendance_before_check_out.check_in, dt_format=False),
                #     })


class HrAttendanceBreak(models.Model):
    _name = "hr.attendance.break"
    _rec_name = "rec_name"

    webcam_check_in = fields.Binary(
        string="Webcam snapshot check in", readonly=True
    )
    webcam_check_out = fields.Binary(
        string="Webcam snapshot check out", readonly=True
    )
    attendance_id = fields.Many2one(
        "hr.attendance",
        ondelete="cascade",
        store=True,
        copy=False,
        string="Attendance Reference",
    )
    employee_id = fields.Many2one("hr.employee", string="Employee")
    break_time = fields.Datetime(string="Break Time")
    resume_time = fields.Datetime(string="Resume Time")
    attendance_break_state = fields.Selection(
        string="Status",
        selection=[("break", "Break"), ("resume", "Resume")],
        default="resume",
    )
    rec_name = fields.Char(
        string="Record Name", compute="_get_rec_name", store=True
    )
    break_hours = fields.Char(
        string="Break Hours",
        compute="_compute_break_hours",
        store=True,
        readonly=True,
    )
    pos_attendance_id = fields.Many2one(
        "attendance.record",
        ondelete="cascade",
        store=True,
        copy=False,
        string="POS Attendance Reference",
    )

    @api.constrains("attendance_id", "break_time", "resume_time")
    def _check_break_time(self):
        for record in self:
            if record.attendance_id:
                if record.break_time:
                    if record.attendance_id.check_out:
                        if record.attendance_id.check_out < record.break_time:
                            raise ValidationError(
                                _(
                                    "Break start time cant be more check out time"
                                )
                            )
                    if record.attendance_id.check_in > record.break_time:
                        raise ValidationError(
                            _("Break start time cant be less check in time")
                        )

                if record.break_time and record.resume_time:
                    if record.attendance_id.check_out:
                        if record.attendance_id.check_out < record.resume_time:
                            raise ValidationError(
                                _(
                                    "Break resume time cant be more check out time"
                                )
                            )
                    if record.attendance_id.check_in > record.resume_time:
                        raise ValidationError(
                            _("Break resume time cant be less check in time")
                        )
                    if record.break_time > record.resume_time:
                        raise ValidationError(
                            _("Break start time cant be more break resume time")
                        )

                if not record.break_time and record.resume_time:
                    raise ValidationError(
                        _("Break start time cant be empty if set resume time")
                    )

    @api.depends("break_time", "resume_time")
    def _get_rec_name(self):
        for rec in self:
            break_time = False
            resume_time = False
            local_tz = pytz.timezone(self._context.get("tz") or "UTC")
            if rec.break_time:
                break_time = rec.break_time.replace(tzinfo=pytz.utc).astimezone(local_tz).time()
                # break_time = rec.break_time.time()
            if rec.resume_time:
                resume_time = rec.resume_time.replace(tzinfo=pytz.utc).astimezone(local_tz).time()
                # resume_time = rec.resume_time.time()

            break_time = (
                break_time.strftime("%H:%M:%S")
                if break_time
                else "No Break Time"
            )
            resume_time = (
                resume_time.strftime("%H:%M:%S")
                if resume_time
                else "No Resume Time"
            )

            if break_time and resume_time:
                rec.rec_name = break_time + " - " + resume_time

    @api.depends("break_time", "resume_time")
    def _compute_break_hours(self):
        for rec in self:
            if rec.break_time and rec.resume_time:
                break_hours = str(rec.resume_time - rec.break_time)
                rec.break_hours = break_hours

class AttendanceRecord(models.Model):
    _inherit = "attendance.record"

    break_ids = fields.One2many(
        "hr.attendance.break",
        "pos_attendance_id",
        help="list of attendances breaks for the employee",
        string="Break",
    )
    break_hours = fields.Char(
        string="Break Hours",
        compute="_compute_break_hours",
        store=True,
        readonly=True,
    )

    @api.depends("break_ids.break_time", "break_ids.resume_time")
    def _compute_break_hours(self):
        totalSecs = 0
        for br in self.break_ids:
            if br.break_hours:
                delta = br.resume_time - br.break_time
                totalSecs = delta.seconds
        totalSecs, sec = divmod(totalSecs, 60)
        hr, min = divmod(totalSecs, 60)
        self.break_hours = "%d:%02d:%02d" % (hr, min, sec)

    @api.depends("check_in", "check_out", "break_hours")
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                delta = attendance.check_out - attendance.check_in
                worked_hours = delta.total_seconds() / 3600.0
                if attendance.break_hours and worked_hours:
                    h, m, s = attendance.break_hours.split(":")
                    worked_hours = (
                        worked_hours
                        - (int(h) * 3600 + int(m) * 60 + int(s)) / 3600.0
                    )
                attendance.worked_hours = worked_hours
            else:
                attendance.worked_hours = False