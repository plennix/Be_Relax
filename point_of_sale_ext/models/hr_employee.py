from odoo import _, exceptions, fields, models
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
        # session_obj = self.env['pos.session'].browse(session)
        # if employee_id.pos_attendance_state == 'checked_in' and employee_id.last_pos_attendance_record and session_obj.config_id.enable_attendance:
        #     if employee_id.last_pos_attendance_record.session_id.id != session:
        #         already_checkin_another_session = True
        emp_attendance_status = False
        if employee_id and employee_id.attendance_state == 'checked_in' and employee_id.attendance_break_state != 'break':
            emp_attendance_status = True

        return {'already_checkin_another_session':already_checkin_another_session,'emp_attendance_status':emp_attendance_status}

    def pos_cashier_checkin(self, session):
        session_obj = self.env['pos.session'].sudo().browse(session)
        emp_session_attendance_rec = session_obj.attendance_record_ids.filtered(lambda x:x.employee_id.id == self.id and x.check_in and not x.check_out)
        if not emp_session_attendance_rec:
            attendance = self.env['attendance.record'].create({
                'employee_id':self.id,
                'session_id':session,
                'check_in': datetime.datetime.now(),
                'attendance_id': self.last_attendance_id.id if self.last_attendance_id else False,
            })
        else:
            attendance = emp_session_attendance_rec[0]
        self.sudo().write({'pos_attendance_state':'checked_in', 'last_pos_attendance_record':attendance.id})

    def pos_cashier_checkout(self, session):
        attendance = self.env['attendance.record'].sudo().search([('session_id','=',session),('employee_id','=',self.id)],limit=1)
        if attendance:
            attendance.write({'check_out':datetime.datetime.now(), 'attendance_id': self.last_attendance_id.id if self.last_attendance_id else False})
            self.sudo().write({'pos_attendance_state': 'checked_out','last_pos_attendance_record':attendance.id})

    def _attendance_action_change(self):
        """Check In/Check Out action
        Check In: create a new attendance record
        Check Out: modify check_out field of appropriate attendance record
        """
        self.ensure_one()
        action_date = fields.Datetime.now()
        user_id = self.env['res.users'].sudo().browse(self._context.get('uid'))

        # attendance = self.env["hr.attendance"].search(
        #     [("employee_id", "=", self.id), ("check_out", "!=", False), ("check_in", "!=", False),('create_uid','=',user_id.id)], limit=1
        # )
        attendance = self.env["hr.attendance"].search(
            [("employee_id", "=", self.id), ("check_out", "=", False), ("check_in", "!=", False),
             ('create_uid', '=', user_id.id)], limit=1
        )

        if not attendance:
            vals = {
                "employee_id": self.id,
                "check_in": action_date,
            }
            self.parse_param(vals)
            return self.env["hr.attendance"].create(vals)

        # # and self.env.user != user_id
        # if self.attendance_state != "checked_in":
        #     vals = {
        #         "employee_id": self.id,
        #         "check_in": action_date,
        #     }
        #     self.parse_param(vals)
        #     return self.env["hr.attendance"].create(vals)


        # attendance = self.env["hr.attendance"].search(
        #     [("employee_id", "=", self.id), ("check_out", "=", False),("check_in", "!=", False),('create_uid','=',user_id.id)], limit=1
        # )
        if attendance:
            vals = {
                "check_out": action_date,
            }
            self.parse_param(vals, "out")
            attendance.write(vals)

            pos_attendance = self.env['attendance.record'].sudo().search([('attendance_id','=',attendance.id)],limit=1)

            if pos_attendance:
                pos_attendance.write({'check_out': datetime.datetime.now()});
                self.sudo().write({'pos_attendance_state': 'checked_out'})
        else:
            raise exceptions.UserError(
                _(
                    "Cannot perform check out on %(empl_name)s, could not find corresponding check in. "
                    "Your attendances have probably been modified manually by human resources."
                )
                % {
                    "empl_name": self.sudo().name,
                }
            )
        return attendance


class HrJobExt(models.Model):
    _inherit = 'hr.job'

    is_supervisor = fields.Boolean(string='Is Supervisor')
    is_refund_allow = fields.Boolean(string='Is Refund Allow', default=False)
