odoo.define('tus_pos_scan.RefundButton', function (require) {
    'use strict';

    const RefundButton = require('point_of_sale.RefundButton');
    const Registries = require('point_of_sale.Registries');

    const InviRefundButton = (RefundButton) =>
        class extends RefundButton {
            _onClick() {
                if (!this.env.pos.selectedOrder.boarding) {
                    return true
                }
                return super._onClick();
            }
        };

    Registries.Component.extend(RefundButton, InviRefundButton);

    return RefundButton;
});
