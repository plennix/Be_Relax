from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PosConfigExt(models.Model):
    _inherit = 'pos.config'

    pos_line_discount = fields.Boolean(string="POS Line Discount",compute='_compute_pos_line_discount')
    pos_order_line = fields.Boolean(string="POS Order Line", compute='_compute_pos_line_discount')
    is_us = fields.Boolean(string="Is US")

    @api.depends()
    def _compute_pos_line_discount(self):
        for rec in self:
            rec.pos_line_discount = self.env.user.has_group('point_of_sale_ext.group_cashiers_discount')
            rec.pos_order_line = self.env.user.has_group('point_of_sale_ext.group_remove_order_line')
