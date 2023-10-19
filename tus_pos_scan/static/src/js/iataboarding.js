odoo.define('tus_pos_scan.IteaBoarding', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');
    const { isConnectionError } = require('point_of_sale.utils');
    class IteaBoarding extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick() {
            if(this.env.pos.selectedOrder.boarding){
                var a = await this.showPopup('IteaBoardingList');
            }
            else{
                await this.showPopup('IataBoardingFormCreate');
            }
        }
    };
    IteaBoarding.template = 'IteaBoarding';

    ProductScreen.addControlButton({
        component: IteaBoarding,
    });
    Registries.Component.add(IteaBoarding);
    return IteaBoarding;
});
