odoo.define("pos_customer_form.loadmodels", function (require) {
    "use strict";

    var { PosGlobalState, Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    const CustomerSource = (PosGlobalState) => class CustomerSource extends PosGlobalState {
        async _processData(loadedData) {
            await super._processData(...arguments);
            this.bank_id = loadedData['res.bank'];
        }
    }
    Registries.Model.extend(PosGlobalState, CustomerSource);
});