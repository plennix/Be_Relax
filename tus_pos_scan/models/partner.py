from odoo import api, fields, models


class ResPartnerTus(models.Model):
    _inherit = 'res.partner'

    boarding_pass_ids = fields.One2many(
        comodel_name='boarding.pass',
        inverse_name='partner_id',
        string='Boarding Pass',
        required=False
    )

    @api.model
    def create_from_ui(self, partner):
        res = super().create_from_ui(partner)
        partner_id = self.browse(res)
        partner_id.phone = partner.get('phone')
        partner_id.email = partner.get('email')
        return res
