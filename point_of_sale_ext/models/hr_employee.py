from odoo import models,fields,api


class HrEmployeeExt(models.Model):
    _inherit = "hr.employee"

    # remove_pos_order_line = fields.Boolean(string='Allow Remove pos order line', help='Allow cashiers to Remove order line')
    # allow_pos_order_line_disc = fields.Boolean(string='Allow Pos order line Discount', help='Allow cashiers Add Discount to order line.')

    @api.model
    def check_pos_cashier_checkin(self, employee):
        employee_id = self.browse(employee.get('emp_id')) if employee else False
        if employee_id and employee_id.attendance_state == 'checked_in' and employee_id.attendance_break_state != 'break':
            return True
        else:
            return False


class HrJobExt(models.Model):
    _inherit = 'hr.job'

    is_supervisor = fields.Boolean(string='Is Supervisor')

        
            
