odoo.define('point_of_sale_tip.PaymentScreentip', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { parse } = require('web.field_utils');

    const PaymentScreentip = PaymentScreen =>
        class extends PaymentScreen {
        async addTip() {
            // click_tip
            const tip = this.currentOrder.get_tip();
            const change = this.currentOrder.get_change();
            let value = tip === 0 && change > 0 ? change : tip;

            const { confirmed, payload } = await this.showPopup('NumberPopup', {
                title: tip ? this.env._t('Change Tip') : this.env._t('Add Tip'),
                startingValue: value,
                isInputSelected: true,
                isEachTip: true,
            });
            if (confirmed) {
                this.currentOrder.set_tip(parse.float(payload));
            }
        }
        }
    Registries.Component.extend(PaymentScreen, PaymentScreentip);

    return PaymentScreentip;


});