from odoo import models, api, fields


class ResCompanyExt(models.Model):
    _inherit = 'res.company'

    iata_code = fields.Char(string='Code')
