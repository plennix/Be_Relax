from odoo import models,fields,api


class SessionAmountDiff(models.Model):
    _name = "session.amt.diff"
    _order = "id desc"

    name = fields.Char('Name')
    expected = fields.Float('Expected')
    difference = fields.Char('Difference')
    counted = fields.Char('Counted')
    session_id = fields.Many2one('pos.session')