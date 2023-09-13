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
                        line_val = (0, 0, {
                            'cashier_id':int(emp_id),
                            'tip':float(tip or 0)
                        })
                        order_line_list.append(line_val)
                    order.cashier_tip_ids = order_line_list


        return order_ids

