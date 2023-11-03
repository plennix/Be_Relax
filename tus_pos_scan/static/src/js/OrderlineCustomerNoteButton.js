odoo.define('tus_pos_scan.OrderlineCustomerNoteButton', function (require) {
    'use strict';

    const OrderlineCustomerNoteButton = require('point_of_sale.OrderlineCustomerNoteButton');
    const Registries = require('point_of_sale.Registries');

    const OrderlineCustomerNoteButtonTUS = (OrderlineCustomerNoteButton) =>
        class extends OrderlineCustomerNoteButton {
            onClick() {
                if (!this.env.pos.selectedOrder.boarding) {
                    return true
                }
                return super.onClick();
            }
        };

    Registries.Component.extend(OrderlineCustomerNoteButton, OrderlineCustomerNoteButtonTUS);

    return OrderlineCustomerNoteButton;
});
