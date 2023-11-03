from odoo import models, _, fields
from odoo.exceptions import ValidationError


class PosConfigExt(models.Model):
    _inherit = 'pos.config'

    def open_ui(self):
        if self.env.user.employee_id.attendance_state == 'checked_out':
            raise ValidationError(_('Please first Check in before open session.'))
        return super(PosConfigExt, self).open_ui()
