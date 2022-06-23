from odoo import api, fields, models


class InheritResCompany(models.Model):
    _inherit = 'res.company'

    br_alias_company_name = fields.Char(string="Alias Name")