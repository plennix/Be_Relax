from odoo import fields, models, api


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

    void_tipline_id = fields.Many2one(
        comodel_name='cashier.tip',
        string='Void Tip',
        required=False
    )
    pos_config_id = fields.Many2one('pos.config', string="Pos Name", compute="compute_pos_config_id", store=True)
    company_id = fields.Many2one('res.company', string="Airport name", compute="compute_pos_config_id", store=True)
    employee_id = fields.Char(string="Employee id", compute="compute_pos_config_id", store=True)

    @api.depends('pos_id')
    def compute_pos_config_id(self):
        for record in self:
            employee_id = False
            if record.cashier_id:
                employee_id = record.cashier_id.barcode
            if record.pos_id:
                record.company_id = record.pos_id.company_id.id
                record.pos_config_id = record.pos_id.session_id.config_id.id
            else:
                record.pos_config_id = False
                record.company_id = False
            record.employee_id = employee_id
