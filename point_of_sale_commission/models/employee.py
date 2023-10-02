from odoo import api, fields, models

class HrEmpExt(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('is_employee') and self._context.get('detailed_type') and self.env['pos.commission'].sudo().search([]).employee_ids.ids:
            args = [('id', 'not in', self.env['pos.commission'].sudo().search([('pos_commission_line_id.detailed_type','=',self._context.get('detailed_type'))]).employee_ids.ids)]
        return super(HrEmpExt, self).name_search(name=name, args=args, operator=operator, limit=limit)
