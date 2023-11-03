from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    boarding_pass_ids = fields.One2many(
        comodel_name='boarding.pass',
        inverse_name='pos_id',
        string='Boarding Pass',
        required=False
    )

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super(PosOrder, self).create_from_ui(orders, draft)
        for order in self.sudo().browse([o['id'] for o in order_ids]):
            for o in orders:
                boarding = o.get('data').get('boarding')
                for b_pass in boarding:
                    pos_boarding = self.env['boarding.pass'].sudo().create({
                        'pos_id': order.id,
                        'passenger_name': b_pass.get('passenger_name') or '',
                        'departure': b_pass.get('departure') or '',
                        'destination': b_pass.get('destination') or '',
                        'flight_company': b_pass.get('flight_company') or '',
                        'flight_number': b_pass.get('flight_number') or '',
                        'partner_id': order.partner_id.id or False,
                    })
                    order.partner_id.email = b_pass.get('flight_email') or ''
                    order.partner_id.phone = b_pass.get('flight_phone') or ''
        return order_ids
