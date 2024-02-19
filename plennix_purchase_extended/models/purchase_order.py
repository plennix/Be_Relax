from odoo import fields, models, api,_

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    total_order_qty = fields.Float('Total Quantity',compute='_compute_total_order_qty')

    @api.depends('order_line','order_line.product_qty')
    def _compute_total_order_qty(self):
        for rec in self:
            rec.total_order_qty = sum(rec.order_line.mapped('product_qty'))
