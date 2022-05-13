from odoo import api, fields, models, _

class Customer(models.Model):
    _inherit = 'res.partner'

    vendor_code=fields.Char(string='Vendor Code')
    alias_name=fields.Char(string='Alias Name')
    customer_incoterm_id = fields.Many2one('account.incoterms', string='Incoterm')
    iban = fields.Char( string='IBAN')
    swift = fields.Char(string='SWIFT BIC')


class Product(models.Model):
    _inherit = 'product.product'

    status = fields.Selection([('active','ACTIVE'),('eol','EOL'),('dev','DEV')])
    hs_code =fields.Char(String='Hs Code')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    status = fields.Selection([('active','ACTIVE'),('eol','EOL'),('dev','DEV')])