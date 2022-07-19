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
        # print(self.id)
        # print(self.quant_ids)
        for id in self.quant_ids.ids:
            self._cr.execute(f"""UPDATE stock_quant SET create_date='{self.forced_date}' WHERE id={id}""")