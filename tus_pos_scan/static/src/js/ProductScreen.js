odoo.define('tus_pos_scan.ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    const InviProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            async _addProduct(product, options) {
                if (!this.env.pos.selectedOrder.boarding && !this.env.pos.selectedOrder.partner) {
                    return true
                }
                return await super._addProduct(product, options);
            }
            async _onClickPay() {
                if (!this.env.pos.selectedOrder.boarding && !this.env.pos.selectedOrder.partner) {
                    return true
                }
                return await super._onClickPay();
            }
        };

    Registries.Component.extend(ProductScreen, InviProductScreen);

    return ProductScreen;
});
