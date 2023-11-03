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
    pos_ref = fields.Char(
        related='pos_id.name',
        readonly=False,
        string='Pos Ref',
        store=True,
    )

    pos_date = fields.Datetime(
        related='pos_id.date_order',
        string='Date',
        required=False,
        store=True
    )


