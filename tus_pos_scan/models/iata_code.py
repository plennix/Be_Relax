from odoo import models, fields, api


class IataCode(models.Model):
    _name = "iata.code"
    _rec_name = 'code'

    code = fields.Char(string='Code')
    airport = fields.Char(string='Airport')
    country = fields.Char(string='County')

    def default_company_code(self):
        if self.env.company.country_id and self.env.company.country_id.name:
            iata_code_id = self.search([('code', '=', self.env.company.iata_code)],limit=1)
            return iata_code_id.id

