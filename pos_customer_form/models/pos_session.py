from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = "pos.session"


    @api.model
    def _pos_ui_models_to_load(self):
        models_to_load = super()._pos_ui_models_to_load()
        models_to_load.append('res.bank')
        return models_to_load

    def _loader_params_res_bank(self):
        return {
            'search_params': {
                'domain': [],
                'fields': ['name', 'id'],
            },
        }

    def _get_pos_ui_res_bank(self, params):
        return self.env['res.bank'].search_read(**params['search_params'])
    
    def _loader_params_res_partner(self):
        res = super()._loader_params_res_partner()
        if res.get('search_params').get('fields'):
            res.get('search_params').get('fields').append('bank_id')
            res.get('search_params').get('fields').append('acc_number')
            # res.get('search_params').get('fields').append('allow_out_payment')
        return res

