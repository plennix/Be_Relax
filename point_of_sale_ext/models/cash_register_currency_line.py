from odoo import models, fields, api


class CashRegisterCurrencyLine(models.Model):
    _name = "cash.register.currency.line"

    currency_name = fields.Char('currency_name')
    account_currency = fields.Float("Amount currency")
    session_id = fields.Many2one('pos.session',string="Session")
    pos_session_id = fields.Many2one('pos.session',string="Session")