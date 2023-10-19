from odoo import api, fields, models

class ResPartnerTus(models.Model):
    _inherit = 'res.partner'

    boarding_pass_ids = fields.One2many(
        comodel_name='boarding.pass',
        inverse_name='partner_id',
        string='Boarding Pass',
        required=False
    )