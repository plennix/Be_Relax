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

    def get_sale_by_cashier(self, order_ids):
        orders = self.env['pos.order'].browse(order_ids)
        sale_by_staff = {}
        for order in orders:
            # lines_without_tips = order.lines.filtered(lambda l: l.product_id != l.order_id.session_id.config_id.tip_product_id)
            # therapists = order.lines.mapped('employee_id') + orders.cashier_tip_ids.mapped('cashier_id')
            for line in order.lines.filtered(lambda l: l.product_id != l.order_id.session_id.config_id.tip_product_id and not l.is_reward_line):
                if line.employee_id.id in sale_by_staff.keys():
                    therapist_vals = sale_by_staff[line.employee_id.id]
                    sale_by_staff[line.employee_id.id].update({
                        'amount': round(therapist_vals.get('amount', 0) + line.price_subtotal_incl, 2),
                        'amount_tax': round(therapist_vals.get('amount_tax', 0) + line.price_subtotal_incl - line.price_subtotal, 2),
                        'amount_without': round(therapist_vals.get('amount_without', 0) + line.price_subtotal, 2),
                    })
                else:
                    sale_by_staff.update({line.employee_id.id: {
                        'employee': line.employee_id,
                        'amount': round(line.price_subtotal_incl, 2) or 0,
                        'amount_tax': round(line.price_subtotal_incl - line.price_subtotal, 2) or 0,
                        'amount_without': round(line.price_subtotal, 2) or 0,
                    }})
            used_lines = []
            for reward_line in order.lines.filtered(lambda l: l.is_reward_line):
                reward = reward_line.reward_id
                if reward.reward_type == 'discount':
                    if reward.discount_applicability == 'order':
                        for sales in sale_by_staff:
                            lines_employees = order.lines.mapped('employee_id').ids
                            if sales in lines_employees:
                                therapist_disc_vals = sale_by_staff[sales]
                                if reward.discount_mode == 'percent':
                                    amount_disc_with_tax = (reward.discount / 100) * therapist_disc_vals.get('amount', 0)
                                    amount_disc_wo_tax = (reward.discount / 100) * therapist_disc_vals.get('amount_without', 0)
                                    disc_diff = amount_disc_wo_tax - amount_disc_with_tax
                                    sale_by_staff[sales].update({
                                        'amount': round(therapist_disc_vals.get('amount', 0) - amount_disc_with_tax, 2),
                                        'amount_tax': round(therapist_disc_vals.get('amount_tax', 0) - disc_diff, 2),
                                        'amount_without': round(therapist_disc_vals.get('amount_without', 0) - amount_disc_wo_tax, 2),
                                    })
                                else:
                                    lines_applicable = order.lines.filtered(lambda l: l.product_id != l.order_id.session_id.config_id.tip_product_id and not l.is_reward_line)
                                    fix_reward_amount = reward.discount / len(lines_applicable)
                                    sale_by_staff[sales].update({
                                        'amount': round(therapist_disc_vals.get('amount', 0) - fix_reward_amount, 2),
                                        'amount_without': round(therapist_disc_vals.get('amount_without', 0) - fix_reward_amount, 2),
                                    })
                    elif reward.discount_applicability == 'specific':
                        discountable_line = order.lines.filtered(lambda l: l.product_id.id in reward.discount_product_ids.ids and l.product_id !=
                                                                 l.order_id.session_id.config_id.tip_product_id and not l.is_reward_line)
                        for discount_line in discountable_line:
                            if discount_line.id not in used_lines:
                                if reward.discount_mode == 'percent':
                                    amount_discounted_with_tax = round((reward.discount / 100) * discount_line.price_subtotal_incl, 2)
                                    amount_discounted_wo_tax = round((reward.discount / 100) * discount_line.price_subtotal, 2)
                                    discounted_diff = round(amount_discounted_wo_tax - amount_discounted_with_tax, 2)
                                    if discount_line.employee_id.id in sale_by_staff.keys():
                                        therapist_reward_vals = sale_by_staff[discount_line.employee_id.id]
                                        sale_by_staff[discount_line.employee_id.id].update({
                                            'amount': round(therapist_reward_vals.get('amount', 0) - amount_discounted_with_tax, 2),
                                            'amount_tax': round(therapist_reward_vals.get('amount', 0) - amount_discounted_with_tax, 2) -
                                            round(therapist_reward_vals.get('amount_without', 0) - amount_discounted_wo_tax, 2),
                                            'amount_without': round(therapist_reward_vals.get('amount_without', 0) - amount_discounted_wo_tax, 2),
                                        })
                                else:
                                    therapist_reward_vals = sale_by_staff[discount_line.employee_id.id]
                                    sale_by_staff[discount_line.employee_id.id].update({
                                        'amount': round(therapist_reward_vals.get('amount', 0) - reward.discount, 2),
                                        'amount_without': round(therapist_reward_vals.get('amount_without', 0) - reward.discount, 2),
                                    })
                            used_lines.append(discount_line.id)

            therapists = order.lines.filtered(lambda l: l.product_id != l.order_id.session_id.config_id.tip_product_id and not l.is_reward_line).mapped('employee_id') | order.cashier_tip_ids.mapped('cashier_id')

            for therapist in therapists:
                tip_amount = sum(order.cashier_tip_ids.filtered(lambda t: t.cashier_id.id == therapist.id).mapped('tip'))
                if therapist.id in sale_by_staff.keys():
                    thera_vals = sale_by_staff[therapist.id]
                    sale_by_staff[therapist.id].update({'tip_amount': round(thera_vals.get('tip_amount', 0) + tip_amount, 2)})
                else:
                    sale_by_staff.update({therapist.id: {
                        'employee': therapist,
                        'amount': float(0),
                        'amount_tax': float(0),
                        'amount_without': float(0),
                        'tip_amount': round(tip_amount, 2)
                    }})
        return sale_by_staff

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
        return taxes.values()