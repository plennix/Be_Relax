from odoo import models, api, fields, _
from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = "pos.order"

    is_void_order = fields.Boolean("Is Void Order", default=False)

    def void_order(self):
        """Create a copy of order  for void order (complete refund order to nullify whole order)"""
        voided_orders = self.env['pos.order']
        for order in self:
            # When a void order operation is performed, we are creating it in a session having the same config as the original
            # order. It can be the same session, or if it has been closed the new one that has been opened.
            current_session = order.session_id.config_id.current_session_id
            if not current_session:
                raise UserError(_('To void order, you need to open a session in the POS %s', order.session_id.config_id.display_name))
            prepared_void_order_values = order._prepare_refund_values(current_session)
            prepared_void_order_values.update({
                'name': self.name + _(' VOID'),
                'is_void_order': True,
            })
            voidOrder = order.copy(prepared_void_order_values)
            for line in order.lines:
                PosOrderLineLot = self.env['pos.pack.operation.lot']
                for pack_lot in line.pack_lot_ids:
                    PosOrderLineLot += pack_lot.copy()
                void_line_prepared_values = line._prepare_refund_data(voidOrder, PosOrderLineLot)
                void_line_prepared_values.update({
                    'name': self.name + _(' VOID'),
                })
                line.copy(void_line_prepared_values)

            for tip_line in order.cashier_tip_ids:
                tip_line.copy(tip_line._prepare_void_order_tip_data(voidOrder))

            for payment in order.payment_ids:
                pos_payment = payment.copy(payment._prepare_void_order_payment_data(voidOrder))
                pos_payment._create_payment_moves()

            voidOrder.amount_paid = sum(voidOrder.payment_ids.mapped('amount'))

            if voidOrder._is_pos_order_paid():
                voidOrder.action_pos_order_paid()
                voidOrder._create_order_picking()
                voidOrder._compute_total_cost_in_real_time()


            voided_orders |= voidOrder

        return voided_orders

    def btn_void_order(self):
        """Create a copy of order  for void order (complete refund order to nullify whole order)"""
        voided_orders = self.void_order()

        return {
            'name': _('Void Order'),
            'view_mode': 'form',
            'res_model': 'pos.order',
            'res_id': voided_orders.ids[0],
            'view_id': False,
            'context': self.env.context,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    def call_void_order(self):
        order_to_void = self.order_id
        order_to_void.void_order()