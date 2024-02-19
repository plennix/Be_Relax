from odoo import models,fields,api
import datetime


class HrEmployeeExt(models.Model):
    _inherit = "hr.employee"

    pos_attendance_state = fields.Selection(
        string="Attendance Status",
        selection=[('checked_out', "Checked out"), ('checked_in', "Checked in")])
    last_pos_attendance_record = fields.Many2one('attendance.record')
    # remove_pos_order_line = fields.Boolean(string='Allow Remove pos order line', help='Allow cashiers to Remove order line')
    # allow_pos_order_line_disc = fields.Boolean(string='Allow Pos order line Discount', help='Allow cashiers Add Discount to order line.')

    def check_pos_cashier_checkin(self, session):
        employee_id = self
        already_checkin_another_session = False
        session_obj = self.env['pos.session'].browse(session)
        if employee_id.pos_attendance_state == 'checked_in' and employee_id.last_pos_attendance_record and session_obj.config_id.enable_attendance:
            if employee_id.last_pos_attendance_record.session_id != session:
                already_checkin_another_session = True
        emp_attendance_status = False
        if employee_id and employee_id.attendance_state == 'checked_in' and employee_id.attendance_break_state != 'break':
            emp_attendance_status = True

        return {'already_checkin_another_session':already_checkin_another_session,'emp_attendance_status':emp_attendance_status}

    def pos_cashier_checkin(self, session):
        attendance = self.env['attendance.record'].create({
            'employee_id':self.id,
            'session_id':session,
            'check_in': datetime.datetime.now(),
        })
        self.sudo().write({'pos_attendance_state':'checked_in', 'last_pos_attendance_record':attendance.id})

    def pos_cashier_checkout(self, session):
        attendance = self.env['attendance.record'].sudo().search([('session_id','=',session),('employee_id','=',self.id)],limit=1)
        if attendance:
            attendance.write({'check_out':datetime.datetime.now()})
            self.sudo().write({'pos_attendance_state': 'checked_out','last_pos_attendance_record':attendance.id})

class HrJobExt(models.Model):
    _inherit = 'hr.job'

    is_supervisor = fields.Boolean(string='Is Supervisor')
    is_refund_allow = fields.Boolean(string='Is Refund Allow', default=False)
