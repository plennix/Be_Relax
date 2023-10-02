import base64
from odoo.exceptions import UserError
import xlsxwriter
from odoo import fields, models, api, _


class CommissionReport(models.TransientModel):
    _name = 'commission.report'
    _description = 'CommissionReport'

    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Therapist',
    )

    start_date = fields.Datetime(
        string='From',
        required=False
    )
    to_date = fields.Datetime(
        string='To',
    )

    @api.constrains('start_date', 'to_date')
    def _onchange_start_date_validation(self):
        if self.to_date and self.start_date:
            if self.start_date > self.to_date:
                self.to_date = self.start_date
                raise UserError(_('From date must be smaller than to date.'))

    def export_xlsx_report(self):
        attch_obj = self.env['ir.attachment']
        workbook = xlsxwriter.Workbook('Commission.xlsx')
        worksheet = workbook.add_worksheet('Commission report')
        header = workbook.add_format({'font_size': 11,
                                      'font_name': 'Calibri',
                                      'bold': True,
                                      'align': 'center'})
        body = workbook.add_format({'font_size': 10,
                                    'font_name': 'Calibri',
                                    'bold': False,
                                    'align': 'right'})

        worksheet.set_column(0, 0, 25)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 2, 40)
        worksheet.set_column(3, 3, 40)
        worksheet.set_column(4, 4, 40)
        worksheet.set_column(5, 5, 50)
        worksheet.set_column(6, 6, 50)
        worksheet.set_column(7, 7, 50)
        worksheet.set_column(8, 8, 40)
        worksheet.set_column(9, 9, 40)
        worksheet.set_column(10, 10, 40)

        row = 0
        worksheet.write(row, 0, 'Employee', header)
        worksheet.write(row, 1, 'Total Sales Amount', header)
        worksheet.write(row, 2, 'Total Sales Amount of Consumable Product', header)
        worksheet.write(row, 3, 'Total Sales Amount of Service Product', header)
        worksheet.write(row, 4, 'Total Sales Amount of Storable Product', header)
        worksheet.write(row, 5, 'Total Commission of Consumable Product', header)
        worksheet.write(row, 6, 'Total Commission of Service Product', header)
        worksheet.write(row, 7, 'Total Commission of Storable Product', header)
        worksheet.write(row, 8, 'Commission for of Consumable Product (%)', header)
        worksheet.write(row, 9, 'Commission for of Service Product (%)', header)
        worksheet.write(row, 10, 'Commission for of Storable Product (%)', header)
        row += 1
        domain = []
        if self.start_date:
            domain += [('order_id.date_order', '>=', self.start_date)]
        if self.to_date:
            domain += [('order_id.date_order', '<=', self.to_date)]

        existing_emp = []
        total_amount = 0
        total_commission_amount = 0
        total_commission_amount_consu = 0
        total_commission_amount_service = 0
        total_commission_amount_product = 0
        employee_ids = False
        if self.employee_ids:
            employee_ids = self.employee_ids
        else:
            new_commission_ids = self.env['pos.commission'].sudo().search([])
            if new_commission_ids:
                employee_ids = new_commission_ids.employee_ids
        if employee_ids:
            for emp_id in employee_ids:
                if emp_id.id not in existing_emp:
                    consu_prod_commission_ex_emp = self.env['pos.commission'].sudo().search(
                        [('employee_ids', 'in', [emp_id.id]),('pos_commission_line_id.detailed_type', '=', 'consu')],
                        limit=1)
                    service_pro_commission_ex_emp = self.env['pos.commission'].sudo().search(
                        [('employee_ids', 'in', [emp_id.id]),('pos_commission_line_id.detailed_type', '=', 'service')],
                        limit=1)
                    storable_pro_commission_ex_emp = self.env['pos.commission'].sudo().search(
                        [('employee_ids', 'in', [emp_id.id]),('pos_commission_line_id.detailed_type', '=', 'product')],
                        limit=1)
                    if consu_prod_commission_ex_emp or service_pro_commission_ex_emp or storable_pro_commission_ex_emp:
                        c_amount_consu = consu_prod_commission_ex_emp.commission if consu_prod_commission_ex_emp else 0
                        c_amount_service = service_pro_commission_ex_emp.commission if service_pro_commission_ex_emp else 0
                        c_amount_product = storable_pro_commission_ex_emp.commission if storable_pro_commission_ex_emp else 0
                        domain += [('employee_id', '=', emp_id.id)]
                        consu_pro_line = self.env['pos.order.line'].sudo().search(domain+ [('product_id.detailed_type', '=', 'consu')])
                        service_pro_line = self.env['pos.order.line'].sudo().search(domain+ [('product_id.detailed_type', '=', 'service')])
                        storable_pro_line = self.env['pos.order.line'].sudo().search(domain+ [('product_id.detailed_type', '=', 'product')])
                        pos_order = self.env['pos.order.line'].sudo().search(domain)
                        # amount = sum(pos_order.mapped('price_subtotal_incl'))
                        consumable_total = sum(consu_pro_line.mapped('price_subtotal_incl')) if consu_prod_commission_ex_emp else 0
                        service_total = sum(service_pro_line.mapped('price_subtotal_incl')) if service_pro_commission_ex_emp else 0
                        storable_total = sum(storable_pro_line.mapped('price_subtotal_incl')) if storable_pro_commission_ex_emp else 0
                        amount = consumable_total + storable_total + service_total

                        if pos_order:
                            worksheet.write(row, 0, emp_id.name, header)
                            worksheet.write(row, 1, amount, body)
                            worksheet.write(row, 2, consumable_total, body)
                            worksheet.write(row, 3, service_total, body)
                            worksheet.write(row, 4, storable_total, body)
                            worksheet.write(row, 5, (consumable_total * c_amount_consu / 100), body)
                            worksheet.write(row, 6, (service_total * c_amount_service / 100), body)
                            worksheet.write(row, 7, (storable_total * c_amount_product / 100), body)
                            worksheet.write(row, 8, str(c_amount_consu) + ' ' + '%', workbook.add_format({
                                'font_size': 10,
                                'font_name': 'Calibri',
                                'bold': False,
                                'align': 'right'
                            }))
                            worksheet.write(row, 9, str(c_amount_service) + ' ' + '%', workbook.add_format({
                                'font_size': 10,
                                'font_name': 'Calibri',
                                'bold': False,
                                'align': 'right'
                            }))
                            worksheet.write(row, 10, str(c_amount_product) + ' ' + '%', workbook.add_format({
                                'font_size': 10,
                                'font_name': 'Calibri',
                                'bold': False,
                                'align': 'right'
                            }))
                            row += 1
                            domain.pop()
                            existing_emp.append(emp_id.id)
                            total_amount += amount
                            total_commission_amount_consu += consumable_total * c_amount_consu / 100
                            total_commission_amount_service += service_total * c_amount_service / 100
                            total_commission_amount_product += storable_total * c_amount_product / 100
                        else:
                            domain.pop()


        if total_amount:
            worksheet.write(row, 1, total_amount, body)
        if total_commission_amount_consu:
            worksheet.write(row, 5, total_commission_amount_consu, body)
        if total_commission_amount_service:
            worksheet.write(row, 6, total_commission_amount_service, body)
        if total_commission_amount_product:
            worksheet.write(row, 7, total_commission_amount_product, body)

        workbook.close()

        f1 = open('Commission.xlsx', 'rb')
        xls_data = f1.read()
        buf = base64.encodebytes(xls_data)
        att_id = attch_obj.sudo().create({'name': '%s.xlsx' % ('Commission'),
                                          'datas': buf,
                                          })
        return {'type': 'ir.actions.act_url',
                'url': 'web/content/%s?download=true' % (att_id.id),
                'target': 'current',
                }
