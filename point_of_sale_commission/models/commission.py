from odoo import fields, models


class Commission(models.Model):
    _name = 'pos.commission'
    _description = 'Commission'

    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Employee',
        required=False
    )
    commission = fields.Float(
        string='Commission (%)',
        required=False
    )

    pos_commission_line_id = fields.Many2one(
        comodel_name='pos.commission.line',
        string='Pos Commission Line',
        required=False)


class PosCommissionLine(models.Model):
    _name = 'pos.commission.line'
    _description = 'Commission Line'


    name = fields.Char(string='Name')

    pos_commission_ids = fields.One2many(
        comodel_name='pos.commission',
        inverse_name='pos_commission_line_id',
        string='Commission',
        required=False
    )
