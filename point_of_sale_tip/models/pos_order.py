from odoo import fields, models, api


class PosOrderTip(models.Model):
    _inherit = 'pos.order'

    cashier_tip_ids = fields.One2many(
        comodel_name='cashier.tip',
        inverse_name='pos_id',
        string='Cashier',
        required=False
    )

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super(PosOrderTip, self).create_from_ui(orders, draft)
        for order in self.sudo().browse([o['id'] for o in order_ids]):
            for o in orders:
                tip = o.get('data').get('cashier_tip')
                if o.get('data').get('name') == order.pos_reference and tip:
                    order_line_list = []
                    for emp_id, tip in tip.items():
                        if tip and float(tip) != 0.00:
                            line_val = (0, 0, {
                                'cashier_id': int(emp_id) if not o.get('data').get('is_user') else self.env[
                                    'res.users'].sudo().browse(int(emp_id)).employee_id.id,
                                'tip': float(tip or 0)
                            })
                            order_line_list.append(line_val)
                    order.cashier_tip_ids = order_line_list
        return order_ids

    @api.model
    def pos_order_paid_tips(self, orders):
        order_id = self.sudo().browse(orders.get('order_id'))
        if order_id:
            tip = orders.get('CashierTip')
            if orders.get('name') == order_id.pos_reference and tip:
                order_line_list = []
                for emp_id, tip in tip.items():
                    if tip and float(tip) != 0.00:
                        line_val = (0, 0, {
                            'cashier_id': int(emp_id),
                            'tip': float(tip or 0)
                        })
                        order_line_list.append(line_val)
                order_id.cashier_tip_ids = order_line_list
        return True


