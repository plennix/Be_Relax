from odoo import fields, models, api


class PosLineAddEmp(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super(PosLineAddEmp, self).create_from_ui(orders, draft)
        for po_order in order_ids:
            po_line = self.env['pos.order.line'].sudo().search([('order_id', '=', po_order.get('id'))])
            for line in po_line:
                if not line.employee_id:
                    line.employee_id = self.env.user.employee_id.id
        return order_ids

class PosOrderLineEmp(models.Model):
    _inherit = 'pos.order.line'

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Therapist',
        required=False
    )
