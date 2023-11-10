odoo.define('point_of_sale_ext.PaymentScreen', function(require) {
    'use strict';


    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const NumberBuffer = require('point_of_sale.NumberBuffer');

    const PaymentScreenExt = (PaymentScreen) =>
        class extends PaymentScreen {
            _updateSelectedPaymentline() {
                if (this.paymentLines.every((line) => line.paid)) {
                    this.currentOrder.add_paymentline(this.payment_methods_from_config[0]);
                }
                if (!this.selectedPaymentLine) return; // do nothing if no selected payment line
                const payment_terminal = this.selectedPaymentLine.payment_method.payment_terminal;
                if (
                    payment_terminal &&
                    !['pending', 'retry'].includes(this.selectedPaymentLine.get_payment_status())
                ) {
                    return;
                }
                if (NumberBuffer.get() === null) {
                    this.deletePaymentLine({
                        detail: {
                            cid: this.selectedPaymentLine.cid
                        }
                    });
                } else {
                    this.selectedPaymentLine.set_amount(NumberBuffer.getFloat());
                    this.props.NumberBuffer = NumberBuffer.getFloat()
                    this.updateCurrencyAmount()
                }
            }
            updateCurrencyAmount() {
                let self = this;
                let order = this.env.pos.get_order();
                let paymentlines = this.env.pos.get_order().get_paymentlines();
                let open_paymentline = false;
                let tot = order.get_curamount();
                let tot_amount = 0;
                let currency = this.env.pos.poscurrency;
                let user_amt = this.props.NumberBuffer;
                let cur = order.selected_paymentline.currency_name;
                let selected_paymentline = order.selected_paymentline;
                for (var i = 0; i < currency.length; i++) {
                    if (cur == currency[i].name) {
                        let c_rate = currency[i].rate;
                        tot_amount = parseFloat(user_amt) * c_rate;
                        selected_paymentline.currency_amount = parseFloat(parseFloat(tot_amount).toFixed(2));
                    }
                }
                order.get_paymentlines();
                if (!order) {
                    return;
                } else if (order.is_paid()) {
                    $('.next').addClass('highlight');
                } else {
                    $('.next').removeClass('highlight');
                }
                $('.edit-amount').val('');
            }
        };
    Registries.Component.extend(PaymentScreen, PaymentScreenExt);
    return PaymentScreen;
});