odoo.define("tus_pos_scan.loadmodels", function (require) {
    "use strict";

    var { PosGlobalState, Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    const CustomerSource = (PosGlobalState) => class CustomerSource extends PosGlobalState {
        async _processData(loadedData) {
            await super._processData(...arguments);
            this.iata_code = loadedData['iata.code'] || [];
        }
    }
    Registries.Model.extend(PosGlobalState, CustomerSource);
});