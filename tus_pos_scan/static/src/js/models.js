odoo.define('tus_pos_scan.models', function (require) {
    "use strict";

var { Order } = require('point_of_sale.models');
var Registries = require('point_of_sale.Registries');

const PosSaleOrder = (Order) => class PosSaleOrder extends Order {
    export_as_JSON() {
        var boarding = [];
            if (this.pos && this.pos.selectedOrder && this.pos.selectedOrder.boarding){
                this.pos.selectedOrder.boarding.forEach(item => {
                    boarding.push(item);
                });
            }

        if(boarding){
            const json = super.export_as_JSON(...arguments);
            json['boarding']= boarding;
            return json;
            }
        }
    }
Registries.Model.extend(Order, PosSaleOrder);

});