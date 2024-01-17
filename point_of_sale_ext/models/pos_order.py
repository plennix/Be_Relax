from odoo import models, api, fields


class PosOrder(models.Model):
    _inherit = "pos.order"

    payment_given = fields.Char('Payment Given')
    other_payment = fields.Float('Other Payment')

    @api.model
    def _payment_fields(self, order, ui_paymentline):
        res = super(PosOrder, self)._payment_fields(order, ui_paymentline)
        print("\n\n\n")
        print(">>>>>>>>",ui_paymentline)
        print("\n\n\n")
        if ui_paymentline.get('manual_currency_amount', False) and ui_paymentline.get('manual_currency_id', False):
            taken_currency = order.currency_id.browse(int(ui_paymentline.get('manual_currency_id')))
            order.payment_given = ''
            order.payment_given += order.payment_given and (", " + ui_paymentline.get('manual_currency_amount')) + ' ' + str(taken_currency.symbol) or str(
                ui_paymentline.get('manual_currency_amount')) + ' ' + str(taken_currency.symbol)
            order.other_payment += float(ui_paymentline.get('manual_currency_amount'))
        return res
