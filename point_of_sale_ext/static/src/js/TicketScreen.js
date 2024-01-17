odoo.define('point_of_sale_ext.TicketScreen', function(require) {
    'use strict';

    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');

    const TicketScreenExt = (TicketScreen) => class extends TicketScreen {

        async _onDoRefund() {
            if((this.env.pos.get_cashier() && this.env.pos.get_cashier().job_bool) || !this.env.pos.config.module_pos_hr) {
                return super._onDoRefund()
            }else {
                return this.showPopup('ErrorPopup', {
                    body: this.env._t('Only supervisor can refund order.'),
                });
            }
        }

    }

    Registries.Component.extend(TicketScreen, TicketScreenExt);
    return TicketScreen;

})