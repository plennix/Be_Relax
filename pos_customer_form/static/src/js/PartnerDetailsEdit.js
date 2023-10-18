odoo.define('pos_customer_form.PartnerDetailsEdit', function(require) {
    'use strict';

    const PartnerDetailsEdit = require('point_of_sale.PartnerDetailsEdit');
    const Registries = require('point_of_sale.Registries');

    const PosBlackboxBeSaleDetailsButton = PartnerDetailsEdit => class extends PartnerDetailsEdit {
        setup() {
            super.setup();
            this.intFields = ["bank_id"];
            const partner = this.props.partner;
            debugger
            this.changes['bank_id'] = partner.bank_id && partner.bank_id[0];
            this.changes['acc_number'] = partner.acc_number;
//            this.changes['allow_out_payment'] = partner.allow_out_payment;
        }
    }
    Registries.Component.extend(PartnerDetailsEdit, PosBlackboxBeSaleDetailsButton);

    return PosBlackboxBeSaleDetailsButton;
});
