from odoo import api, fields, models, _
from datetime import  datetime,timedelta

from odoo.exceptions import ValidationError
# from odoo.osv.orm import except_orm
import logging
from odoo.osv import osv


class Customer(models.Model):
    _inherit = 'res.partner'

    vendor_code=fields.Char(string='Code')
    alias_name=fields.Char(string='Alias Name')
    customer_incoterm_id = fields.Many2one('account.incoterms', string='Incoterm')
    iban = fields.Char( string='IBAN')
    swift = fields.Char(string='SWIFT BIC')
    br_vat_mentions = fields.Selection([
        ('option_1', '0% Dutch VAT intra-community supply, art 138 VAT Directive/Table II, post a.6, Ducth VAT act'),
        ('option_2', '0% Dutch VAT export supply, art 146 VAT Directive/Table II, post a.2, Ducth VAT act'),
        ('option_3', 'VAT to be declare by customer due to reverse charge mechanism, article 12-3, Dutch'),
                                        ], string="VAT mentions")
    br_lead_time = fields.Char(string='Lead time')

# class Product(models.Model):
#     _inherit = 'product.product'
#
#     status = fields.Selection([('active','ACTIVE'),('eol','EOL'),('dev','DEV')])
#     hs_code =fields.Char(String='Hs Code')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hs_code = fields.Char(String='Hs Code')
    status = fields.Selection([('active','ACTIVE'),('eol','EOL'),('dev','DEV')])
    country_of_origin = fields.Many2one("res.country", string="Country of Origin")
    dont_show_on_invoice_report = fields.Boolean(string="Dont show on invoice report", default=False)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    default_code=fields.Char('Internal Ref', related='product_id.default_code')
    product_name=fields.Char('Product', related='product_id.name')


class InheritProductSupplier(models.Model):
    _inherit = 'product.supplierinfo'

    br_moq = fields.Float(string="MOQ")


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    incoterm_id = fields.Many2one('account.incoterms', 'Incoterm', states={'done': [('readonly', True)]}, help="International Commercial Terms are a series of predefined commercial terms used in international transactions.", related="partner_id.customer_incoterm_id")

    @api.onchange('date_order')
    def _check_change(self):
        if self.date_order:
            date_planned = self.date_order + timedelta(days=45)
            self.date_planned = date_planned
        else:
             self.date_planned = False

    @api.depends('date_order', 'currency_id', 'company_id', 'company_id.currency_id', 'partner_id', 'incoterm_id')
    def _compute_currency_rate(self):
        for order in self:
            order.currency_rate = self.env['res.currency']._get_conversion_rate(order.company_id.currency_id,
                                                                                order.currency_id, order.company_id,
                                                                                order.date_order)

    # @api.depends('partner_id')
    # def set_incoterm(self):
    #     if self.partner_id.customer_incoterm_id:
    #         self.incoterm_id = self.partner_id.customer_incoterm_id.id

    @api.model
    def default_get(self, fields):
        # print("default get executed")
        res = super(PurchaseOrderInherit, self).default_get(fields)
        res['notes'] = '1 : Order should be acknowledged within 48 Hours  with Confirmed delivery date.<br/>' \
                       '2 : Delivery should be on pallets / same quantity per carton.'
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id', 'product_qty', 'product_uom')
    def _onchange_suggest_packaging(self):
        # remove packaging if not match the product
        if self.product_packaging_id.product_id != self.product_id:
            self.product_packaging_id = False
        # suggest biggest suitable packaging
        if self.product_id and self.product_qty and self.product_uom:
            self.product_packaging_id = self.product_id.packaging_ids.filtered(
                'purchase')._find_suitable_product_packaging(self.product_qty, self.product_uom)
        for line in self:
            search_vendor_pricelist = self.env["product.supplierinfo"].search(
                [('name', '=', self.partner_id.id), ('product_tmpl_id', '=', line.product_id.id)], limit=1)
            # print(search_vendor_pricelist)
            # print(line)
            if line.product_qty:
                if line.product_qty < search_vendor_pricelist.br_moq:
                    return {
                        'warning': {
                            'title': _('Warning!'),
                            'message': _(f"Minimum Quantity of '{line.product_id.name}' must "
                                         f"be {search_vendor_pricelist.br_moq}")
                        }
                    }