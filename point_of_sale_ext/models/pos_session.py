from odoo import api, fields, models, _, Command
from itertools import groupby
from operator import itemgetter
from datetime import datetime, date
from collections import defaultdict
from odoo.exceptions import AccessError, UserError, ValidationError


class PosSessionExt(models.Model):
    _inherit = 'pos.session'

    attendance_record_ids = fields.One2many('attendance.record','session_id',string='Attend Record(s)')
    start_cash_register_currency_line_ids = fields.One2many('cash.register.currency.line','session_id',string="Cash Register Currency Line Start")
    end_real_cash_register_currency_line_ids = fields.One2many('cash.register.currency.line','pos_session_id',string="Cash Register Currency Line End")


    def post_closing_cash_details(self, counted_cash):
        """
        Calling this method will try store the cash details during the session closing.

        :param counted_cash: float, the total cash the user counted from its cash register
        If successful, it returns {'successful': True}
        Otherwise, it returns {'successful': False, 'message': str, 'redirect': bool}.
        'redirect' is a boolean used to know whether we redirect the user to the back end or not.
        When necessary, error (i.e. UserError, AccessError) is raised which should redirect the user to the back end.
        """
        self.ensure_one()
        check_closing_session = self._cannot_close_session()
        if check_closing_session:
            return check_closing_session

        if not self.cash_journal_id:
            # The user is blocked anyway, this user error is mostly for developers that try to call this function
            raise UserError(_("There is no cash register in this session."))

        self.cash_register_balance_end_real = counted_cash

        for line in self.start_cash_register_currency_line_ids:
            default_cash_payment_method_id = self.payment_method_ids.filtered(lambda pm: pm.type == 'cash')[0]
            end_real_cash_register_currency_line = self.end_real_cash_register_currency_line_ids.filtered(
                lambda x: x.currency_name == line.currency_name)
            orders = self.order_ids.filtered(lambda o: o.state == 'paid' or o.state == 'invoiced')
            currency_cash_payments = orders.payment_ids.filtered(
                lambda
                    p: p.payment_method_id == default_cash_payment_method_id and p.currency_name == line.currency_name)
            if end_real_cash_register_currency_line:
                end_real_cash_register_currency_line.write({
                    'account_currency': end_real_cash_register_currency_line.account_currency + sum(
                        currency_cash_payments.mapped('account_currency'))})
            else:
                self.write({'end_real_cash_register_currency_line_ids': [(0, 0, {
                    'currency_name': line.currency_name,
                    'account_currency': line.account_currency + sum(
                        currency_cash_payments.mapped('account_currency'))})]})

        return {'successful': True}

    def action_pos_session_closing_control(self, balancing_account=False, amount_to_balance=0,
                                           bank_payment_method_diffs=None):
        bank_payment_method_diffs = bank_payment_method_diffs or {}
        for session in self:
            if any(order.state == 'draft' for order in session.order_ids):
                raise UserError(_("You cannot close the POS when orders are still in draft"))
            if session.state == 'closed':
                raise UserError(_('This session is already closed.'))
            session.write({'state': 'closing_control', 'stop_at': fields.Datetime.now()})
            if not session.config_id.cash_control:
                return session.action_pos_session_close(balancing_account, amount_to_balance, bank_payment_method_diffs)
            # If the session is in rescue, we only compute the payments in the cash register
            # It is not yet possible to close a rescue session through the front end, see `close_session_from_ui`
            if session.rescue and session.config_id.cash_control:
                default_cash_payment_method_id = self.payment_method_ids.filtered(lambda pm: pm.type == 'cash')[0]
                orders = self.order_ids.filtered(lambda o: o.state == 'paid' or o.state == 'invoiced')
                total_cash = sum(
                    orders.payment_ids.filtered(lambda p: p.payment_method_id == default_cash_payment_method_id).mapped(
                        'amount')
                ) + self.cash_register_balance_start

                session.cash_register_balance_end_real = total_cash

                # orders = self.order_ids.filtered(lambda o: o.state == 'paid' or o.state == 'invoiced')
                for line in session.start_cash_register_currency_line_ids:
                    default_cash_payment_method_id = self.payment_method_ids.filtered(lambda pm: pm.type == 'cash')[0]
                    end_real_cash_register_currency_line = session.end_real_cash_register_currency_line_ids.filtered(
                        lambda x: x.currency_name == line.currency_name)
                    currency_cash_payments = orders.payment_ids.filtered(
                        lambda
                            p: p.payment_method_id == default_cash_payment_method_id and p.currency_name == line.currency_name)
                    if end_real_cash_register_currency_line:
                        end_real_cash_register_currency_line.write({
                                                                       'account_currency': end_real_cash_register_currency_line.account_currency + sum(
                                                                           currency_cash_payments.mapped(
                                                                               'account_currency'))})
                    else:
                        session.write({'start_cash_register_currency_line_ids': [(0, 0, {
                            'currency_name': line.currency_name,
                            'account_currency': line.account_currency + sum(
                                currency_cash_payments.mapped('account_currency'))})]})

            return session.action_pos_session_validate(balancing_account, amount_to_balance, bank_payment_method_diffs)

    def action_pos_session_open(self):
        # we only open sessions that haven't already been opened
        for session in self.filtered(lambda session: session.state == 'opening_control'):
            values = {}
            if not session.start_at:
                values['start_at'] = fields.Datetime.now()
            if session.config_id.cash_control and not session.rescue:
                last_session = self.search([('config_id', '=', session.config_id.id), ('id', '!=', session.id)], limit=1)
                session.cash_register_balance_start = last_session.cash_register_balance_end_real  # defaults to 0 if lastsession is empty

                poscurrency = self.env['res.currency'].search([('id', 'in', session.config_id.selected_currency.ids)])

                if not last_session:
                    session.write({
                        'start_cash_register_currency_line_ids' : [(0,0,{'currency_name':currency.name, 'account_currency': 0}) for currency in poscurrency]
                    })
                else:
                    for currency in poscurrency:
                        start_cash_register_currency_line = session.start_cash_register_currency_line_ids.filtered(lambda x:x.currency_name == currency.name)
                        end_real_cash_register_currency_line = last_session.end_real_cash_register_currency_line_ids.filtered(lambda x:x.currency_name == currency.name)

                        if start_cash_register_currency_line and end_real_cash_register_currency_line:
                            start_cash_register_currency_line.write({'account_currency':end_real_cash_register_currency_line.account_currency})
                        else:
                            if end_real_cash_register_currency_line:
                                session.write({'start_cash_register_currency_line_ids':[(0,0,{'currency_name':currency.name, 'account_currency': end_real_cash_register_currency_line.account_currency})]})
                            else:
                                session.write({'start_cash_register_currency_line_ids': [(0, 0, {
                                    'currency_name': currency.name if currency else '',
                                    'account_currency': 0.0})]})

            else:
                values['state'] = 'opened'
            session.write(values)
        return True

    def get_closing_control_data(self):
        result = super().get_closing_control_data()
        orders = self.order_ids.filtered(lambda o: o.state == 'paid' or o.state == 'invoiced')
        payments = orders.payment_ids.filtered(lambda p: p.payment_method_id.type != "pay_later")
        pay_later_payments = orders.payment_ids - payments
        cash_payment_method_ids = self.payment_method_ids.filtered(lambda pm: pm.type == 'cash')
        default_cash_payment_method_id = cash_payment_method_ids[0] if cash_payment_method_ids else None
        other_payment_method_ids = self.payment_method_ids - default_cash_payment_method_id if default_cash_payment_method_id else self.payment_method_ids
        last_session = self.search([('config_id', '=', self.config_id.id), ('id', '!=', self.id)], limit=1)
        cash_in_count = 0
        cash_out_count = 0
        cash_in_out_list = []
        for cash_move in self.sudo().statement_line_ids.sorted('create_date'):
            if cash_move.amount > 0:
                cash_in_count += 1
                name = f'Cash in {cash_in_count}'
            else:
                cash_out_count += 1
                name = f'Cash out {cash_out_count}'
            cash_in_out_list.append({
                'name': cash_move.payment_ref if cash_move.payment_ref else name,
                'amount': cash_move.amount
            })

        cash_lst = []
        for currency_name in list(
                set(payments.filtered(lambda p: p.payment_method_id == default_cash_payment_method_id).mapped(
                        'currency_name'))):
            currency_cash_payments = payments.filtered(
                lambda p: p.payment_method_id == default_cash_payment_method_id and p.currency_name == currency_name)
            statement_total_amount = sum(self.sudo().statement_line_ids.filtered(lambda s: s.currency_name == currency_name).mapped('account_currency'))
            cash_register_balance_end_real_currencywise = sum(last_session.end_real_cash_register_currency_line_ids.filtered(lambda x:x.currency_name == currency_name).mapped('account_currency'))

            currency = self.env['res.currency'].sudo().search([('name','=',currency_name)],limit=1)

            cash_lst.append({
                'name': default_cash_payment_method_id.name + '(' + currency_name + ')',
                'amount': cash_register_balance_end_real_currencywise
                          + sum(currency_cash_payments.mapped('account_currency'))
                          + statement_total_amount,
                'opening': cash_register_balance_end_real_currencywise,
                'payment_amount': sum(currency_cash_payments.mapped('account_currency')),
                'amount_org': sum(currency_cash_payments.mapped('amount')),
                'moves': cash_in_out_list,
                'id': default_cash_payment_method_id.id,
                'currency_name': currency_name,
                'currency_symbol': currency.symbol if currency else currency_name,
            })

        other_payment_methods_cuurency = []
        for pm in other_payment_method_ids:
            if list(set(orders.payment_ids.filtered(lambda p: p.payment_method_id == pm).mapped('currency_name'))):
                for currency_name in list(
                        set(orders.payment_ids.filtered(lambda p: p.payment_method_id == pm).mapped('currency_name'))):
                    currency_cash_payments = orders.payment_ids.filtered(
                        lambda p: p.payment_method_id == pm and p.currency_name == currency_name)
                    currency = self.env['res.currency'].sudo().search([('name', '=', currency_name)], limit=1)

                    other_payment_methods_cuurency.append({
                        'name': pm.name + '(' + currency_name + ')',
                        'amount': sum(currency_cash_payments.mapped('amount')),
                        'number': len(currency_cash_payments),
                        'id': pm.id,
                        'type': pm.type,
                        'currency_symbol': currency.symbol if currency else currency_name,
                    })
            else:
                other_payment_methods_cuurency.append({
                    'name': pm.name,
                    'amount': sum(orders.payment_ids.filtered(lambda p: p.payment_method_id == pm).mapped('amount')),
                    'number': len(orders.payment_ids.filtered(lambda p: p.payment_method_id == pm)),
                    'id': pm.id,
                    'type': pm.type,
                    'currency_symbol': False,
                })
        result.update({
            'cash_lst': cash_lst,
            'other_payment_methods_cuurency': other_payment_methods_cuurency,
        })
        return result

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
                    labor_surcharge_total = 0.0
                    if line.tax_ids_after_fiscal_position:
                        tax_ids = line.tax_ids_after_fiscal_position.filtered(lambda x: x.name == 'Labor Surcharge')
                        if tax_ids:
                            labor_surcharge_total += (line.price_subtotal * tax_ids.amount) / 100
                    sale_by_staff[line.employee_id.id].update({
                        'amount': round(therapist_vals.get('amount', 0) + line.price_subtotal_incl, 2),
                        'amount_tax': round(therapist_vals.get('amount_tax', 0) + line.price_subtotal_incl - line.price_subtotal, 2),
                        'amount_without': round(therapist_vals.get('amount_without', 0) + line.price_subtotal, 2),
                        'labor_surcharge': round(therapist_vals.get('labor_surcharge', 0) + labor_surcharge_total, 2)
                    })
                else:
                    labor_surcharge_total = 0.0
                    if line.tax_ids_after_fiscal_position:
                        tax_ids = line.tax_ids_after_fiscal_position.filtered(lambda x: x.name == 'Labor Surcharge')
                        if tax_ids:
                            labor_surcharge_total += (line.price_subtotal * tax_ids.amount) / 100
                    sale_by_staff.update({line.employee_id.id: {
                        'employee': line.employee_id,
                        'amount': round(line.price_subtotal_incl, 2) or 0,
                        'amount_tax': round(line.price_subtotal_incl - line.price_subtotal, 2) or 0,
                        'amount_without': round(line.price_subtotal, 2) or 0,
                        'labor_surcharge': round(labor_surcharge_total, 2) or 0,
                    }})
            # used_lines = []
            rewards_applied = []
            for reward_line in order.lines.filtered(lambda l: l.is_reward_line):
                reward = reward_line.reward_id
                if reward.id not in rewards_applied and reward.reward_type == 'discount':
                    rewards_applied.append(reward.id)
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
                            # if discount_line.id not in used_lines:
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
                            # used_lines.append(discount_line.id)

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
                        'labor_surcharge': float(0),
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
                    'tax_ids_after_fiscal_position': s.get('order_lines', False).mapped('tax_ids_after_fiscal_position'),
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
