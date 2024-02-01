odoo.define('point_of_sale_tip.PaymentMethodPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    class PaymentMethodPopup extends AbstractAwaitablePopup {
         setup() {
            super.setup();
            this.paymentMethods = this.env.pos.payment_methods.filter(method => this.env.pos.config.payment_method_ids.includes(method.id))
         }
         async updateTipPayment(paymentLine) {
            let order = this.env.pos.get_order();
//            order.get_paymentlines()
            if(order.get_paymentlines().length) {
                var has_tip_line = order.get_paymentlines().filter(line => line.is_tip)
//                console.log(">>>>>has_tip_line>>>>",has_tip_line)
                _.each(has_tip_line, function(tip_line){
                    order.remove_paymentline(tip_line)
                })
            }
			order.add_paymentline(paymentLine);
			let selected_paymentline = order.selected_paymentline;
			selected_paymentline.set_tip(true)
			selected_paymentline.set_amount(this.props.tip_amount)
			this.cancel();
//			 this.currentOrder.remove_paymentline(line);
//this.currentOrder.get_paymentlines();
         }
    }
    PaymentMethodPopup.template = 'PaymentMethodPopup';
    PaymentMethodPopup.defaultProps = {
        title: _lt('Payment Methods'),
    };

    Registries.Component.add(PaymentMethodPopup);

    return PaymentMethodPopup;
});