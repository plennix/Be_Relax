odoo.define('tus_pos_scan.DiscountButton', function (require) {
    'use strict';

    const DiscountButton = require('pos_discount.DiscountButton');
    const Registries = require('point_of_sale.Registries');

    const DiscountButtonTUS = (DiscountButton) =>
        class extends DiscountButton {
            onClick() {
                if (!this.env.pos.selectedOrder.boarding || !this.env.pos.selectedOrder.partner) {
                    return true
                }
                return super.onClick();
            }
        };

    Registries.Component.extend(DiscountButton, DiscountButtonTUS);

    return DiscountButton;
});
