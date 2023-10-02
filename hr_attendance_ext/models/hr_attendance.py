# -*- coding: utf-8 -*-

from odoo import models
from datetime import datetime,timedelta
from odoo.osv.expression import AND


class HrAttendanceExt(models.Model):
    _inherit = "hr.attendance"

    def send_checkout_email(self):
        print('sdcsdc')
        attendance_ids = self.sudo().search([('check_in', '>=', datetime.now().date()-timedelta(days=1)),('check_in', '<', datetime.now().date()), ('check_out', '=', False)])
        if attendance_ids:
            for attendance in attendance_ids:
                self.env['mail.template'].sudo().browse(
                    self.env.ref('hr_attendance_ext.checkout_mail_template').id).send_mail(
                    attendance.id, force_send=True)
