from odoo import api, fields, models, _
from datetime import  datetime,timedelta

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

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    default_code=fields.Char('Internal Ref', related='product_id.default_code')
    product_name=fields.Char('Product', related='product_id.name')

class Purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('date_order')
    def _check_change(self):
        if self.date_order:
            date_planned = self.date_order + timedelta(days=45)
            print(date_planned)
            self.date_planned = date_planned
        else:
             self.date_planned = False

