import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.base.models.res_partner import _tz_get


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    attendance_record_ids = fields.One2many('attendance.record', 'attendance_id', string='POS Attendance Record(s)')
    config_id = fields.Many2one('pos.config',string="Shop")
    timezone = fields.Selection(_tz_get, string='Timezone', compute='_get_company_timezone', store=True)

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
                newrecord.employee_id.sudo().write({'pos_attendance_state': 'checked_in', 'last_pos_attendance_record': attendance.id})
        return newrecord

    def write(self, vals):
        newrecord = super(HrAttendance, self).write(vals)
        return newrecord