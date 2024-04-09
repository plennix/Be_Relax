from odoo import models, api, fields, _


class PosPayment(models.Model):
    _inherit = "pos.payment"

    def _prepare_void_order_payment_data(self, void_order):
        current_date = fields.Datetime.now()
        return {
            'name': self.name + _(' VOID') if self.name else False,
            'pos_order_id': void_order.id,
            'amount': -self.amount,
            'account_currency': -self.amount,
            'payment_method_id': self.payment_method_id.id,
            # 'card_type': self.card_type,
            # 'cardholder_name': self.cardholder_name,
            # 'transaction_id': self.transaction_id,
            # 'payment_status': self.payment_status,
            # 'ticket': self.ticket,
            # 'is_change': self.is_change,
        }
