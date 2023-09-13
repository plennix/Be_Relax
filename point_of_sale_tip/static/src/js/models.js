odoo.define('point_of_sale_tip.models', function (require) {
    "use strict";

var { Order } = require('point_of_sale.models');
var Registries = require('point_of_sale.Registries');

const PosSaleOrder = (Order) => class PosSaleOrder extends Order {
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json['cashier_tip']= this.CashierTip
        return json;
    }
    set_cashier_tip(tip){
        this.CashierTip = tip
    }
}
Registries.Model.extend(Order, PosSaleOrder);

});