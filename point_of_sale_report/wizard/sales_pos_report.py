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
                po.date_order >= %s AND po.date_order <= %s;
            """

        params = (self.date_from, self.date_to)
        self.env.cr.execute(sql_q, params)
        for row in self.env.cr.dictfetchall():
            pos_lines[row.pop("id")] = row
        for key in pos_lines.keys():
            res = dict((fn, 0.0) for fn in ["amount_tax", "amount_untaxed", "discount"])
            res["order_id"] = pos_lines[key].get("order_id")
            res["name"] = pos_lines[key].get("name")
            res["date_order"] = pos_lines[key].get("date_order")
            res["employee_id"] = pos_lines[key].get("employee_id")
            res["full_product_name"] = pos_lines[key].get("full_product_name")
            res["product_id"] = pos_lines[key].get("product_id")
            res["qty"] = pos_lines[key].get("qty")
            res["price_unit"] = pos_lines[key].get("price_unit")
            res["discount"] = pos_lines[key].get("discount")

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
        worksheet.set_column(1, 1, 12)
        worksheet.set_column(2, 2, 15)
        worksheet.set_column(3, 3, 15)
        worksheet.set_column(4, 4, 30)
        worksheet.set_column(5, 5, 15)
        worksheet.set_column(6, 6, 10)
        worksheet.set_column(7, 7, 10)
        worksheet.set_column(8, 8, 10)

        float_format = workbook.add_format(
            {
                "align": "right",
                "num_format": "0.00",
                "valign": "bottom",
                "font_name": "Calibri",
                "font_size": "9",
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
        worksheet.write(row, column + 1, "Shop Name", column_titles)
        worksheet.write(row, column + 2, "Receipt Date", column_titles)
        worksheet.write(row, column + 3, "Sales Person", column_titles)
        worksheet.write(row, column + 4, "Name", column_titles)
        worksheet.write(row, column + 5, "Barcode", column_titles)
        worksheet.write(row, column + 6, "Qty", column_titles)
        worksheet.write(row, column + 7, "Price", column_titles)
        worksheet.write(row, column + 8, "Discount", column_titles)

        data = self.get_report_data()
        row = 1
        index = 1

        for rec in data:
            employee_name = (
                self.env["hr.employee"].browse(rec["employee_id"]).name
                if rec["employee_id"]
                else ""
            )
            product_barcode = (
                self.env["product.product"].browse(rec["product_id"]).barcode
                if rec["product_id"]
                else ""
            )
            order_id = (
                self.env["pos.order"].browse(rec["order_id"])
                if rec["order_id"]
                else ""
            )
            discount_amount = (rec["discount"] / 100) * rec["price_unit"]
            worksheet.write(row, column, index, text_format)
            worksheet.write(
                row, column + 1, order_id.name if order_id.name else "", text_format
            )
            worksheet.write(
                row,
                column + 2,
                order_id.date_order if order_id.date_order else "",
                date_format,
            )

            worksheet.write(
                row,
                column + 3,
                "%s %s" % (rec["employee_id"], employee_name)
                if rec["employee_id"]
                else "",
                text_format,
            )
            worksheet.write(
                row,
                column + 4,
                rec["full_product_name"] if rec["full_product_name"] else "",
                text_format,
            )
            worksheet.write(
                row, column + 5, product_barcode if product_barcode else "", text_format
            )
            worksheet.write(
                row, column + 6, rec["qty"] if rec["qty"] else 0.0, float_format
            )
            worksheet.write(
                row,
                column + 7,
                rec["price_unit"] if rec["price_unit"] else 0.0,
                float_format,
            )
            worksheet.write(
                row,
                column + 8,
                discount_amount if discount_amount else 0.0,
                float_format,
            )

            row += 1
            index += 1

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
