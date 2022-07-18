from odoo import api, fields, models, _
from datetime import  datetime,timedelta


class InheritStockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def create(self, values):
        res = super(InheritStockQuant, self).create(values)
        if 'import_file' in self.env.context:
            print(self.env.context)
        return res