from odoo import models, api


class PosSessionExt(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        new_model = 'iata.code'
        if new_model not in result:
            result.append(new_model)
        return result

    def _loader_params_iata_code(self):
        return {
            'search_params': {
                'fields': [
                    'code'
                ],
            }
        }

    def _get_pos_ui_iata_code(self, params):
        return self.env['iata.code'].search_read(**params['search_params'])
