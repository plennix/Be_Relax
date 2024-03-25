from odoo import fields, models, api,_

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    create_receipt = fields.Boolean("Create Receipt", default=True)

    def _create_picking(self):
        if self.create_receipt:
            return super(PurchaseOrder, self)._create_picking()
        else:
            return True
