from odoo import fields, models, api


class PosLineAddEmp(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super(PosLineAddEmp, self).create_from_ui(orders, draft)
        for po_order in order_ids:
            po_line = self.env['pos.order.line'].sudo().search([('order_id', '=', po_order.get('id'))])
            for line in po_line:
                if not line.employee_id:
                    # Take therapist from related refunded pos orderline
                    if line.refunded_orderline_id and line.refunded_orderline_id.employee_id:
                        line.employee_id = line.refunded_orderline_id.employee_id.id
                    else:
                        line.employee_id = self.env.user.employee_id.id
        return order_ids


class PosOrderLineEmp(models.Model):
    _inherit = 'pos.order.line'

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Therapist',
        required=False
    )
    line_emp_pin = fields.Char(related='employee_id.barcode', store=True)

    def _export_for_ui(self, orderline):
        res = super()._export_for_ui(orderline=orderline)
        if orderline.employee_id:
            res['employee_id'] = orderline.employee_id.id
        if orderline.line_emp_pin:
            res['line_emp_pin'] = orderline.line_emp_pin
        return res

    def get_emp_line_emp_pin(self):
        employee_id = self.employee_id
        line_emp_pin = False
        if employee_id.barcode:
            line_emp_pin = int(employee_id.barcode)
        return [employee_id.id, line_emp_pin]
