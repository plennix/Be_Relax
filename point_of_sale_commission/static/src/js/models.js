odoo.define('point_of_sale_commission.models', function (require) {
    "use strict";

var { Order } = require('point_of_sale.models');
var { Orderline } = require('point_of_sale.models');
var Registries = require('point_of_sale.Registries');

const PosSaleOrderLineEmp = (Orderline) => class PosSaleOrderLineEmp extends Orderline {
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json['employee_id']= this.employee_id
        json['line_emp_pin']= this.line_emp_pin
        return json;
    }
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.line_emp_pin = json.line_emp_pin;
        this.employee_id = json.employee_id
     }
    export_for_printing() {
        const json = super.export_for_printing(...arguments);
        json.line_emp_pin = this.line_emp_pin
        return json
    }
    set_line_emp(emp,line_emp_pin){
        this.order.assert_editable();
        this.employee_id = emp;
        this.line_emp_pin = line_emp_pin;
    }
}
Registries.Model.extend(Orderline, PosSaleOrderLineEmp);


const PosSaleOrderEmp = (Order) => class PosSaleOrderEmp extends Order {

    set_orderline_options(line, options) {
        super.set_orderline_options(...arguments);
        if (options.employee_id || options.line_emp_pin){
            line.set_line_emp(options.employee_id,options.line_emp_pin)
        }
     }
}
Registries.Model.extend(Order, PosSaleOrderEmp);

});