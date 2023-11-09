from odoo import fields, models, api


class ResPartnerTus(models.Model):
    _inherit = 'res.partner'

    bank_id = fields.Many2one('res.bank')
    bank_partner_id = fields.Many2one('res.partner.bank')
    acc_number = fields.Char('Acc. No.')
    allow_out_payment = fields.Boolean('Send Money')

    @api.model
    def create_from_ui(self, partner):
        res = super().create_from_ui(partner)
        partner_rec = self.browse(res)
        if partner.get('bank_id') or partner.get('acc_number'):
            if not partner_rec.bank_partner_id:
                partner_rec.bank_partner_id = self.env['res.partner.bank'].sudo().create(
                    {'bank_id': int(partner.get('bank_id')), 'acc_number': partner.get('acc_number'), 'partner_id': res,
                     'allow_out_payment': True, }).id
            else:
                partner_rec.bank_partner_id.write({
                    'bank_id': int(partner.get('bank_id')),
                    'acc_number': partner.get('acc_number'),
                    'allow_out_payment': True,
                })
        return res
