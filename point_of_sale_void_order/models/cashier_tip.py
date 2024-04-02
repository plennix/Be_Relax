from odoo import fields, models, _


class CashierTip(models.Model):
    _inherit = 'cashier.tip'
    
    def _prepare_void_order_tip_data(self, void_order):
        """
        This prepares CashierTip data for void order line.

        @param void_order: the pre-created void order
        @type void_order: pos.order

        @return: dictionary of data which is for creating a void order line from the original line
        @rtype: dict
        """
        self.ensure_one()
        return {
            'cashier_id': self.cashier_id.id,
            'pos_id': void_order.id,
            'tip': -self.tip,
            'void_tipline_id': self.id,
        }