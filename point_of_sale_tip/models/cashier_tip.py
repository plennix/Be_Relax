from odoo import fields, models


class CashierTip(models.Model):
    _name = 'cashier.tip'
    _description = 'CasherTip'

    cashier_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Cashier',
    )

    tip = fields.Float(
        string='Tip',
        required=False
    )

    pos_id = fields.Many2one(
        comodel_name='pos.order',
        string='Pos',
        required=False
    )
