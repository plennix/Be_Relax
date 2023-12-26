from odoo import models, api
from datetime import datetime, date



class PosSessionExt(models.Model):
    _inherit = 'pos.session'

    def _get_pos_ui_hr_employee(self, params):
        res = super(PosSessionExt, self)._get_pos_ui_hr_employee(params)
        for emp in res:
            employee_id = self.env['hr.employee'].sudo().browse(emp['id'])
            emp['job_bool'] = self.env['hr.job'].sudo().browse(emp['job_id']).is_supervisor
            # emp['remove_pos_order_line'] = employee_id.remove_pos_order_line
            # emp['allow_pos_order_line_disc'] = employee_id.allow_pos_order_line_disc
        return res

    def print_report_ext(self):
        currency_aed = self.currency_id.search([('name', '=', 'AED')])
        data = {
            'rec_id': self.id,
            'opening_date': self.start_at,
            'location': self.config_id.name,
            'is_us': self.config_id.is_us,
            'orderlines': self.order_ids.mapped('lines').ids,
            'total_with_tax_aed': self.currency_id._convert(sum(self.order_ids.mapped('lines').mapped('price_subtotal_incl')), currency_aed, self.company_id, datetime.now()),
            'total_without_tax_aed': self.currency_id._convert(sum(self.order_ids.mapped('lines').mapped('price_subtotal')), currency_aed, self.company_id, datetime.now()),
            'sale_by_staff': self.env['pos.order.line'].read_group([('id', 'in', self.order_ids.mapped('lines').ids)], fields=['price_subtotal_incl', 'tax_ids_after_fiscal_position', 'price_subtotal'], groupby=['employee_id']),
            'payment_modes': self.env['pos.payment'].read_group([('session_id', '=', self.id)], fields=['pos_order_id'], groupby=['payment_method_id']),
        }
        return self.env.ref('point_of_sale_ext.pos_ord_session_reprt').report_action(docids=self, data=data)

    def get_print_report(self):
        data = {
            'opening_date': self.start_at,
            'location': self.config_id.name,
            'orderlines': self.order_ids.mapped('lines').ids,
            'sale_by_staff': self.env['pos.order.line'].read_group([('id', 'in', self.order_ids.mapped('lines').ids)], fields=['order_id'], groupby=['employee_id']),
            # 'payment_modes': self.env['pos.payment'].read_group(['session_id', '=', self.id], fields=['pos_order_id'], groupby=['payment_method_id']),
            # 'total': self.order_ids.mapped('lines').,
        }
        return self.env.ref('point_of_sale_ext.pos_ord_session_reprt').report_action([], data=data)

    def get_discount(self):
        total = 0
        for line in self.order_ids.lines.filtered(lambda o: o.discount):
            total += round((line.price_unit * line.discount) / 100)
        return total

    def _loader_params_hr_employee(self):
        res = super()._loader_params_hr_employee()
        if res.get('search_params') and res.get('search_params').get('fields'):
            res.get('search_params').get('fields').append('job_id')
        return res

