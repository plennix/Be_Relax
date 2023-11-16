odoo.define('tus_pos_scan.RewardButton', function (require) {
    'use strict';

    const RewardButton = require('pos_discount.RewardButton');
    const Registries = require('point_of_sale.Registries');

    const RewardButtonTUS = (RewardButton) =>
        class extends RewardButton {
            onClick() {
                if (!this.env.pos.selectedOrder.boarding && !this.env.pos.selectedOrder.partner) {
                    return true
                }
                return super.onClick();
            }
        };

    Registries.Component.extend(RewardButton, RewardButtonTUS);

    return RewardButton;
});
