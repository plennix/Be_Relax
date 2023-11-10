from odoo import models,fields,api


class HrEmployeeExt(models.Model):
    _inherit = "hr.employee"

    @api.model
    def check_pos_cashier_checkin(self, employee):
        employee_id = self.browse(employee.get('emp_id')) if employee else False
        if employee_id and employee_id.attendance_state == 'checked_in':
            return True
        else:
            return False
            
