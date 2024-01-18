from odoo import fields, models, api

class ResUsersTus(models.Model):
    _inherit = 'res.users'

    allowed_pos_configs = fields.Many2many(comodel_name='pos.config', string='Allowed POS Sessions')