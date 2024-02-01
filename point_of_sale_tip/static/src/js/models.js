odoo.define('point_of_sale_tip.models', function (require) {
    "use strict";

var { Order, Payment } = require('point_of_sale.models');
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

const PaymentLine = (Payment) => class PaymentLine extends Payment {
		constructor(obj, options) {
			super(...arguments);
			this.is_tip = this.is_tip || false;
		}

		set_tip(is_tip){
			this.is_tip = is_tip;
		}

		init_from_JSON(json){
			super.init_from_JSON(...arguments);
			this.is_tip = json.is_tip || false;
		}

		export_as_JSON(){
			const json = super.export_as_JSON(...arguments);
			json.is_tip = this.is_tip || false;
			return json;
		}

		export_for_printing() {
			const json = super.export_for_printing(...arguments);
			json.is_tip = this.is_tip || false;
			return json;
		}

	}

	Registries.Model.extend(Payment, PaymentLine);

});