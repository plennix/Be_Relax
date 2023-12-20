from odoo import models, fields, api


class IataCode(models.Model):
    _name = "iata.code"
    _rec_name = 'code'

    code = fields.Char(string='Code')
    airport = fields.Char(string='Airport')
    country = fields.Char(string='County')
