odoo.define('point_of_sale_tip.models', function (require) {
    "use strict";

var { Order } = require('point_of_sale.models');
var Registries = require('point_of_sale.Registries');

const PosSaleOrder = (Order) => class PosSaleOrder extends Order {
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json['cashier_tip']= this.CashierTip
        json['is_user']= this.IsUser
        return json;
    }
    set_cashier_tip(tip){
        this.CashierTip = tip
    }
    is_user(){
        this.IsUser = true
    }
}
Registries.Model.extend(Order, PosSaleOrder);

});