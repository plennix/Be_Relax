import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
