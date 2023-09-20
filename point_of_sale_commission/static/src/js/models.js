odoo.define('point_of_sale_commission.models', function (require) {
    "use strict";

var { Order } = require('point_of_sale.models');
var { Orderline } = require('point_of_sale.models');
var Registries = require('point_of_sale.Registries');

const PosSaleOrderLineEmp = (Orderline) => class PosSaleOrderLineEmp extends Orderline {
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json['employee_id']= this.employee_id
        return json;
    }
    set_line_emp(emp){
        this.order.assert_editable();
        this.employee_id = emp;
    }
}
Registries.Model.extend(Orderline, PosSaleOrderLineEmp);


const PosSaleOrderEmp = (Order) => class PosSaleOrderEmp extends Order {

    set_orderline_options(line, options) {
        super.set_orderline_options(...arguments);
        if (options.employee_id){
            line.set_line_emp(options.employee_id)
        }
     }
}
Registries.Model.extend(Order, PosSaleOrderEmp);

});