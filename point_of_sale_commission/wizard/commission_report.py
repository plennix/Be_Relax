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
        worksheet.set_column(2, 2, 25)
        worksheet.set_column(3, 3, 15)

        row = 0
        worksheet.write(row, 0, 'Employee', header)
        worksheet.write(row, 1, 'Total Sales Amount', header)
        worksheet.write(row, 2, 'Total Commission Amount', header)
        worksheet.write(row, 3, 'Commission (%)', header)
        row += 1
        domain = []
        if self.start_date:
            domain += [('order_id.date_order', '>=', self.start_date)]
        if self.to_date:
            domain += [('order_id.date_order', '<=', self.to_date)]

        existing_emp = []
        total_amount = 0
        total_commission_amount = 0
        if self.employee_ids:
            for emp_id in self.employee_ids:
                if emp_id.id not in existing_emp:
                    commission_ex_emp = self.env['pos.commission'].sudo().search([('employee_ids', 'in', [emp_id.id])],
                                                                                 limit=1)
                    if commission_ex_emp:
                        c_amount = commission_ex_emp.commission
                        domain += [('employee_id', '=', emp_id.id)]
                        pos_order = self.env['pos.order.line'].sudo().search(domain)
                        amount = sum(pos_order.mapped('price_subtotal_incl'))
                        if pos_order:
                            worksheet.write(row, 0, emp_id.name, header)
                            worksheet.write(row, 1, amount, body)
                            worksheet.write(row, 2, amount * c_amount / 100, body)
                            worksheet.write(row, 3, str(c_amount) + ' ' + '%', workbook.add_format({
                                'font_size': 10,
                                'font_name': 'Calibri',
                                'bold': False,
                                'align': 'right'
                            }))
                            row += 1
                            domain.pop()
                            existing_emp.append(emp_id.id)
                            total_amount += amount
                            total_commission_amount += amount * c_amount / 100
                        else:
                            domain.pop()
        else:
            commission_ids = self.env['pos.commission.line'].sudo().search([])
            for commission in commission_ids:
                for commission_line in commission.pos_commission_ids:
                    c_amount = commission_line.commission
                    for emp in commission_line.employee_ids:
                        if emp.id not in existing_emp:
                            domain += [('employee_id', '=', emp.id)]
                            pos_order = self.env['pos.order.line'].sudo().search(domain)
                            amount = sum(pos_order.mapped('price_subtotal_incl'))
                            if pos_order:
                                worksheet.write(row, 0, emp.name, header)
                                worksheet.write(row, 1, amount, body)
                                worksheet.write(row, 2, amount * c_amount / 100, body)
                                worksheet.write(row, 3, str(c_amount) + ' ' + '%', body)
                                row += 1
                                domain.pop()
                                existing_emp.append(emp.id)
                                total_amount += amount
                                total_commission_amount += amount * c_amount / 100
                            else:
                                domain.pop()
        if total_amount:
            worksheet.write(row, 1, total_amount, body)
        if total_commission_amount:
            worksheet.write(row, 2, total_commission_amount, body)

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
