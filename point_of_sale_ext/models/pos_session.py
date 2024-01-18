from odoo import models, fields, api
from itertools import groupby
from operator import itemgetter
from datetime import datetime, date
from collections import defaultdict


class PosSessionExt(models.Model):
    _inherit = 'pos.session'

    def _get_pos_ui_hr_employee(self, params):
        res = super(PosSessionExt, self)._get_pos_ui_hr_employee(params)
        for emp in res:
            employee_id = self.env['hr.employee'].sudo().browse(emp['id'])
            emp['job_bool'] = self.env['hr.job'].sudo().browse(emp['job_id']).is_supervisor
            emp['allow_refund'] = self.env['hr.job'].sudo().browse(emp['job_id']).is_refund_allow
            # emp['remove_pos_order_line'] = employee_id.remove_pos_order_line
            # emp['allow_pos_order_line_disc'] = employee_id.allow_pos_order_line_disc
        return res

    def convert_amount_to_currency(self, amount, currency_id):
        amount_to_currency = self.env.company.currency_id._convert(amount, self.env['res.currency'].browse(int(currency_id)), self.env.company, fields.Datetime.now())
        return amount_to_currency

    def print_report_ext(self):
        data = {
            'rec_id': self.id,
            'opening_date': self.start_at,
            'location': self.config_id.name,
            'is_us': self.config_id.is_us,
            'order_ids': self.order_ids.ids,
            'orderlines': self.order_ids.mapped('lines').filtered(lambda x: not x.is_reward_line).ids,
            'promotion_lines': self.order_ids.mapped('lines').filtered(lambda x: x.is_reward_line).ids,
            'total_with_tax_aed': sum(self.order_ids.mapped('lines').mapped('price_subtotal_incl')),
            'total_tax': sum(self.order_ids.mapped('amount_tax')),
            'discount_amount': sum(self.order_ids.mapped('lines').filtered(lambda x: x.is_reward_line).mapped('price_subtotal_incl')),
            'total_without_tax_aed': sum(self.order_ids.mapped('lines').mapped('price_subtotal')), #self.currency_id._convert(sum(self.order_ids.mapped('lines').mapped('price_subtotal')), currency_aed, self.company_id, datetime.now()),
            'sale_by_staff': self.env['pos.order.line'].read_group([('id', 'in', self.order_ids.mapped('lines').ids)], fields=['price_subtotal_incl', 'tax_ids_after_fiscal_position', 'price_subtotal'], groupby=['employee_id']),
            'payment_modes': self.env['pos.payment'].read_group([('session_id', '=', self.id)], fields=['pos_order_id'], groupby=['payment_method_id']),
            'currency_id': self.currency_id,
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


class PosLine(models.Model):
    _inherit = 'pos.order.line'

    def get_currency(self):
        return self.env.company.currency_id

    def get_order_line(self, orderlines):
        orderlines = self.browse(orderlines)
        orderline_list = []
        lines_data = defaultdict(dict)
        for product_id, olines in groupby(sorted(orderlines.filtered(lambda s: s.product_id != s.order_id.session_id.config_id.tip_product_id), key=lambda l: l.product_id.id), key=lambda l: l.product_id.id):
            lines_data[product_id].update({'order_lines': self.env['pos.order.line'].concat(*olines)})
        for s in lines_data.values():
            if s.get('order_lines', False):
                orderline_list.append({
                    'full_product_name': s.get('order_lines', False)[0].full_product_name,
                    'qty': sum(s.get('order_lines', False).mapped('qty')),
                    'price_subtotal_incl': sum(s.get('order_lines', False).mapped('price_subtotal_incl')),
                    'price_subtotal': sum(s.get('order_lines', False).mapped('price_subtotal'))
                })
        return orderline_list

    def get_pos_tax(self, orderlines):
        orderlines = self.browse(orderlines)
        taxes = {}
        for line in orderlines:
            if line.tax_ids_after_fiscal_position:
                line_taxes = line.tax_ids_after_fiscal_position.sudo().compute_all(line.price_unit * (1-(line.discount or 0.0)/100.0), line.order_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                for tax in line_taxes['taxes']:
                    if tax['id'] not in taxes.keys():
                        taxes.setdefault(tax['id'], {'name': tax['name'], 'tax_amount':0.0, 'base_amount':0.0})
                    taxes[tax['id']]['tax_amount'] += tax['amount']
                    taxes[tax['id']]['base_amount'] += tax['base']
        print("???????????????line_taxes", taxes)
        return taxes.values()
