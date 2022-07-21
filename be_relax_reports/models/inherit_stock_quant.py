from odoo import api, fields, models, _
from datetime import  datetime,timedelta


# class InheritStockQuant(models.Model):
#     _inherit = 'stock.quant'
#
#     @api.model
#     def create(self, values):
#         res = super(InheritStockQuant, self).create(values)
#         if 'import_file' in self.env.context:
#             print(self.env.context)
#         return res


class InheritStockInventoryAdjust(models.TransientModel):
    _inherit = 'stock.inventory.adjustment.name'

    forced_date = fields.Datetime(string="Forced Date")

    def action_apply(self):
        res = super(InheritStockInventoryAdjust, self).action_apply()
        # context = self.env.context
        print("action_apply is working")
        print(self.id)
        print(self.quant_ids)
        for id in self.quant_ids.ids:
            self._cr.execute(f"""UPDATE stock_quant SET create_date='{self.forced_date}' WHERE id={id}""")
            # print("self.quant_ids.product_name", self.quant_ids.product_name)
            # print("self.quant_ids.default_code", self.quant_ids.default_code)
            # search_product = self.env['product.product'].search(['|', ('name', '=', self.quant_ids.product_name),
            #                                                      ('default_code', '=', self.quant_ids.product_name)])
            # search_prodcut_stock_valuation = self.env["stock.valuation.layer"].search([('product_id', '=', search_product.id)])
            # print(search_prodcut_stock_valuation)
            # stock_valuation = self.env["stock.valuation.layer"]
            # print(stock_valuation)
            # search_prodcut_stock_valuation._cr.execute(f"""UPDATE stock_valuation_layer SET create_date='{self.forced_date}' WHERE id={search_prodcut_stock_valuation.ids[-1]}""")
