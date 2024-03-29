from odoo import fields, models
from odoo.addons.base.models.res_partner import _tz_get


class ResCompany(models.Model):
    _inherit = 'res.company'

    timezone = fields.Selection(_tz_get, string='Timezone')
