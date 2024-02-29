import xlsxwriter
import io
import base64
from odoo import api, models, fields, _


class SalesPosReport(models.TransientModel):
    _name = "sales.pos.report"

    binary_data = fields.Binary("File")
    date_to = fields.Datetime(
        string="Date To", index=True, default=fields.Datetime.now
    )
    date_from = fields.Datetime(
        string="Date From", index=True, default=fields.Datetime.now
    )

    def get_report_data(self):
        report_lines = []
        pos_lines = {}

        sql_q = """SELECT
                pol.*
            FROM
                pos_order_line AS pol
            JOIN
                pos_order AS po
            ON
                pol.order_id = po.id
            WHERE
                po.date_order >= %s AND po.date_order <= %s AND po.company_id = %s;
            """

        params = (self.date_from, self.date_to, self.env.company.id)
        self.env.cr.execute(sql_q, params)
        for row in self.env.cr.dictfetchall():
            pos_lines[row.pop("id")] = row
        for key in pos_lines.keys():
            res = dict((fn, 0.0) for fn in ["amount_tax", "amount_untaxed", "discount"])
            res['id'] = key
            res["order_id"] = pos_lines[key].get("order_id")
            res["name"] = pos_lines[key].get("name")
            res["date_order"] = pos_lines[key].get("date_order")
            res["employee_id"] = pos_lines[key].get("employee_id")
            res["full_product_name"] = pos_lines[key].get("full_product_name")
            res["product_id"] = pos_lines[key].get("product_id")
            res["qty"] = pos_lines[key].get("qty")
            res["price_unit"] = pos_lines[key].get("price_unit")
            res["discount"] = pos_lines[key].get("discount")
            res["price_subtotal"] = pos_lines[key].get('price_subtotal')

            report_lines.append(res)
        return report_lines

    def generate_xlsx_report(self):
        filename = "SalesReport.xlsx"
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Sales Report")
        worksheet.set_landscape()
        worksheet.fit_to_pages(1, 0)
        worksheet.set_zoom(100)
        worksheet.set_column(0, 0, 5)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 2, 15)
        worksheet.set_column(3, 3, 25)
        worksheet.set_column(4, 4, 18)
        worksheet.set_column(5, 5, 30)
        worksheet.set_column(6, 6, 30)
        worksheet.set_column(7, 7, 40)
        worksheet.set_column(8, 8, 15)
        worksheet.set_column(9, 9, 20)
        worksheet.set_column(10, 10, 10)
        worksheet.set_column(11, 11, 10)
        worksheet.set_column(12, 12, 10)
        worksheet.set_column(13, 13, 10)
        worksheet.set_column(14, 14, 10)
        worksheet.set_column(15, 15, 35)
        worksheet.set_column(16, 16, 15)
        worksheet.set_column(17, 17, 40)
        worksheet.set_column(18, 18, 15)
        worksheet.set_column(19, 19, 15)
        worksheet.set_column(20, 20, 25)
        worksheet.set_column(21, 21, 15)
        worksheet.set_column(22, 22, 15)
        worksheet.set_column(23, 23, 15)
        worksheet.set_column(24, 24, 15)
        worksheet.set_column(25, 25, 15)

        float_format = workbook.add_format(
            {
                "align": "right",
                "num_format": "0.00",
                "valign": "bottom",
                "font_name": "Calibri",
                "font_size": "9",
            }
        )
        total_format = workbook.add_format(
            {
                "bold": True,
                "align": "right",
                "num_format": "0.00",
                "valign": "bottom",
                "font_name": "Calibri",
                "font_size": "10",
                "bg_color": "#D3D3D3",

            }
        )
        text_format = workbook.add_format(
            {
                "align": "left",
                "valign": "bottom",
                "font_name": "Calibri",
                "font_size": "9",
            }
        )
        other_currency_float_format = workbook.add_format(
            {
                "align": "right",
                "num_format": "0.00",
                "valign": "bottom",
                "font_name": "Calibri",
                "font_size": "9",
                "bg_color": "yellow",

            }
        )
        other_currency_text_format = workbook.add_format(
            {
                "align": "left",
                "num_format": "0.00",
                "valign": "bottom",
                "font_name": "Calibri",
                "font_size": "9",
                "bg_color": "yellow",

            }
        )
        column_titles = workbook.add_format(
            {
                "bold": True,
                "align": "left",
                "valign": "bottom",
                "font_name": "Calibri",
                "font_size": "9",
                "bg_color": "#D3D3D3",
            }
        )
        date_format = workbook.add_format(
            {
                "num_format": "mm/dd/yyyy HH:mm:ss",
                "font_name": "Calibri",
                "font_size": "9",
                "valign": "bottom",
            }
        )

        row = 0
        column = 0

        # Add Column Header
        worksheet.write(row, column, "Seq", column_titles)
        worksheet.write(row, column + 1, "Airport Name", column_titles)
        worksheet.write(row, column + 2, "Destination", column_titles)
        worksheet.write(row, column + 3, "Shop Name", column_titles)
        worksheet.write(row, column + 4, "Receipt Date", column_titles)
        worksheet.write(row, column + 5, "Sales Person", column_titles)
        worksheet.write(row, column + 6, "Customer Name", column_titles)
        worksheet.write(row, column + 7, "Name", column_titles)
        worksheet.write(row, column + 8, "Item Code", column_titles)
        worksheet.write(row, column + 9, "Barcode", column_titles)
        worksheet.write(row, column + 10, "Qty", column_titles)
        worksheet.write(row, column + 11, "Price", column_titles)
        worksheet.write(row, column + 12, "Discount", column_titles)
        worksheet.write(row, column + 13, "Tips", column_titles)
        worksheet.write(row, column + 14, "Type", column_titles)
        worksheet.write(row, column + 15, "Product Categories", column_titles)
        worksheet.write(row, column + 16, "Flight number", column_titles)
        worksheet.write(row, column + 17, "Promotions", column_titles)
        worksheet.write(row, column + 18, "Currency", column_titles)
        worksheet.write(row, column + 19, "Payment in AED", column_titles)
        worksheet.write(row, column + 20, "Nb of Receipts", column_titles)
        worksheet.write(row, column + 21, "Tax Amount", column_titles)
        worksheet.write(row, column + 22, "DF (Duty Free)", column_titles)
        worksheet.write(row, column + 23, "DP (Duty Paid)", column_titles)
        worksheet.write(row, column + 24, "Labour surcharge", column_titles)

        data = self.get_report_data()

        order_ids = self.env['pos.order'].browse(sorted(list(set([i['order_id'] for i in data]))))
        row = 1
        index = 1
        total_qty = 0.0
        total_price = 0.0
        total_discount = 0.0
        total_tip = 0.0
        total_reward = 0.0
        total_aed_price = 0.0
        total_labour = 0.0
        total_tax = 0.0
        total_df = 0.0
        total_dp = 0.0
        for rec in order_ids:
            new_line = True

            tip_product = rec.config_id.tip_product_id
            site = ','.join([i for i in [rec.boarding_pass_ids[0].departure_id.code, rec.boarding_pass_ids[0].destination] if i]) if rec.boarding_pass_ids else ''
            flight_no = rec.boarding_pass_ids[0].flight_number if rec.boarding_pass_ids else ''
            currency = rec.currency_id.name
            aed_currency_id = self.env['res.currency'].sudo().search([('symbol', '=', 'AED')], limit=1)
            rate_currency_id = aed_currency_id.rate_ids.filtered(lambda x: x.company_id == rec.company_id)
            product_reward_id = rec.lines.reward_id.filtered(lambda x: x.reward_type == 'discount' and x.discount_applicability == 'specific')
            reward_id = rec.lines.reward_id.filtered(lambda x: x.reward_type == 'discount')
            order_reward_id = rec.lines.reward_id.filtered(lambda x: x.reward_type == 'discount' and x.discount_applicability == 'order')
            for line in rec.lines.filtered(lambda x: x.product_id != tip_product and not x.reward_id):
                # reward = line.reward_id

                aed_convert_rate = 0.0
                labour = 0.0
                if rate_currency_id:
                    company_rate = rate_currency_id[0].company_rate
                    aed_convert_rate = line.price_unit * company_rate

                # Labour charge calculation
                tax_ids_after_fiscal_position = line.tax_ids_after_fiscal_position.filtered(lambda x: x.name == 'Labor Surcharge')
                if tax_ids_after_fiscal_position:
                    labour += (line['price_subtotal'] * tax_ids_after_fiscal_position.amount) / 100
                    total_labour += labour
                if new_line:
                    worksheet.write(row, column, index, text_format)
                    new_line = False

                worksheet.write(row, column + 1,
                                rec.company_id.name if rec.company_id else self.env.company.name,
                                text_format)
                worksheet.write(row, column + 2,
                                site if site else '',
                                text_format)

                worksheet.write(row, column + 3,
                                rec.config_id.name if rec.config_id else "",
                                text_format)

                worksheet.write(row, column + 4,
                                rec.date_order if rec.date_order else "",

                                date_format,
                                )

                employee_id = line.employee_id
                employee_name = "[%s]  %s" % (employee_id.barcode, employee_id.name)
                worksheet.write(row, column + 5,
                                employee_name if employee_name else "",
                                text_format,
                                )

                worksheet.write(row, column + 6,
                                rec.partner_id.name or rec.partner_id.commercial_partner_id.name or ' ',
                                text_format,
                                )

                worksheet.write(row, column + 7,
                                line.product_id.name if line.product_id else "",
                                text_format,
                                )

                worksheet.write(row, column + 8,
                                line.product_id.default_code if line.product_id else "",
                                text_format,
                                )

                worksheet.write(row, column + 9,
                                line.product_id.barcode or '',
                                text_format,
                                )

                total_qty += line.qty
                worksheet.write(row, column + 10,
                                line.qty or 0.00,
                                float_format,
                                )

                worksheet.write(row, column + 11,
                                line.price_unit or 0.00,
                                float_format,
                                )
                total_price += line.price_subtotal

                # discount calculation
                discount_amount = 0.00
                lines_length = len(rec.lines.filtered(lambda x: x.product_id != tip_product and not x.reward_id))
                line_product_amount = line.price_subtotal

                for rew in reward_id:
                    if rew.discount_applicability == 'order':
                        if rew.discount_mode == 'percent':
                            amount = (line.price_subtotal) if discount_amount == 0.00 else discount_amount
                            dis_amount = (rew.discount / 100) * line_product_amount
                            line_product_amount = line.price_subtotal - dis_amount
                            discount_amount += dis_amount
                        else:
                            discount_amount += round(rew.discount / lines_length, 2)

                    if rew.discount_applicability == 'specific':
                        if line.product_id.id in rew.discount_product_ids.ids:
                            if rew.discount_mode == 'percent':
                                discount_amount += (rew.discount / 100) * line_product_amount
                            else:
                                discount_amount += round(rew.discount / lines_length, 2)

                total_discount += discount_amount
                worksheet.write(row, column + 12,
                                discount_amount,
                                float_format,
                                )

                total_reward += discount_amount
                reward_name = ''.join([i.display_name for i in reward_id])
                worksheet.write(row, column + 17,
                                reward_name if discount_amount > 0 else '',
                                text_format,
                                )

                tip = sum(rec.cashier_tip_ids.filtered(lambda x: x.cashier_id == employee_id).mapped('tip'))
                total_tip += tip
                worksheet.write(row, column + 13,
                                tip,
                                float_format,
                                )

                worksheet.write(row, column + 14,
                                line.product_id.detailed_type,
                                text_format,
                                )

                worksheet.write(row, column + 15,
                                line.product_id.categ_id.name,
                                text_format,
                                )

                worksheet.write(row, column + 16,
                                flight_no,
                                text_format,
                                )

                worksheet.write(row, column + 18,
                                currency if currency else '',
                                text_format,
                                )

                worksheet.write(row, column + 19,
                                aed_convert_rate,
                                float_format,
                                )
                total_aed_price += aed_convert_rate

                worksheet.write(row, column + 20,
                                rec.pos_reference or '',
                                text_format,
                                )

                # tax calculation
                tax = round(line.price_subtotal_incl - line.price_subtotal, 2)
                total_tax += tax
                worksheet.write(row, column + 21,
                                round(line.price_subtotal_incl - line.price_subtotal, 2) or 0.00,
                                float_format,
                                )

                total_df += line.price_subtotal
                worksheet.write(row, column + 22,
                                line.price_subtotal or 0.00,
                                float_format,
                                )

                total_dp += line.price_subtotal_incl
                worksheet.write(row, column + 23,
                                line.price_subtotal_incl or 0.00,
                                float_format,
                                )

                worksheet.write(row, column + 24,
                                labour or 0.00,
                                float_format,
                                )
                row += 1
                # index += 1
            other_currency = rec.payment_ids.filtered(lambda x: x.currency_name != rec.currency_id.name)
            if other_currency:
                payments = list(set(other_currency.mapped('currency_name')))
                for val in payments:
                    amount_paid = sum(other_currency.filtered(lambda x: x.currency_name == val).mapped('account_currency'))
                    if amount_paid:
                        worksheet.write(row, column + 11,
                                        amount_paid,
                                        other_currency_float_format,
                                        )
                        worksheet.write(row, column + 18,
                                        val or ' ',
                                        other_currency_text_format,
                                        )
                        row += 1
            index += 1

        # Total Values
        worksheet.write(row + 2, column + 9,
                        'Totals:',
                        total_format,
                        )
        worksheet.write(row + 2, column + 10,
                        total_qty or 0.00,
                        total_format,
                        )
        worksheet.write(row + 2, column + 11,
                        total_price or 0.00,
                        total_format,
                        )
        worksheet.write(row + 2, column + 12,
                        round(total_discount, 2
                              ) or 0.00,
                        total_format,
                        )
        worksheet.write(row + 2, column + 13,
                        total_tip or 0.00,
                        total_format,
                        )
        worksheet.write(row + 2, column + 14,
                        '',
                        total_format,
                        )
        worksheet.write(row + 2, column + 15,
                        '',
                        total_format,
                        )
        worksheet.write(row + 2, column + 16,
                        '',
                        total_format,
                        )

        worksheet.write(row + 2, column + 17,
                        '',
                        total_format,
                        )

        worksheet.write(row + 2, column + 18,
                        '',
                        total_format,
                        )

        worksheet.write(row + 2, column + 19,
                        total_aed_price or 0.00,
                        total_format,
                        )
        worksheet.write(row + 2, column + 20,
                        '',
                        total_format,
                        )

        worksheet.write(row + 2, column + 21,
                        total_tax or 0.00,
                        total_format,
                        )
        worksheet.write(row + 2, column + 22,
                        total_df or 0.00,
                        total_format,
                        )
        worksheet.write(row + 2, column + 23,
                        total_dp or 0.00,
                        total_format,
                        )
        worksheet.write(row + 2, column + 24,
                        total_labour or 0.00,
                        total_format,
                        )

        workbook.close()
        output.seek(0)
        output = base64.encodebytes(output.read())
        self.write({"binary_data": output})
        return {
            "type": "ir.actions.act_url",
            "url": "web/content/?model=sales.pos.report&field=binary_data&download=true&id=%s&filename=%s"
                   % (self.id, filename),
            "target": "new",
        }
