from odoo import models


class PosSessionExt(models.Model):
    _inherit = 'pos.session'

    def _get_pos_ui_hr_employee(self, params):
        res = super(PosSessionExt, self)._get_pos_ui_hr_employee(params)
        for emp in res:
            emp['line_emp_pin'] = self.env['hr.employee'].sudo().browse(emp['id']).pin or False
        return res