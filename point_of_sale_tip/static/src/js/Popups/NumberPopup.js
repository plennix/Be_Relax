odoo.define('point_of_sale_tip.NumberPopuptip', function(require) {
    'use strict';

    const NumberPopup = require('point_of_sale.NumberPopup');
    const Registries = require('point_of_sale.Registries');
    const NumberBuffer = require('point_of_sale.NumberBuffer');

    const NumberPopuptip = NumberPopup =>
        class extends NumberPopup {
         confirm(event) {
            if (NumberBuffer.get()) {
                super.confirm();
            }
            if (this.props.isEachTip && Number(this.inputBuffer) !== 0){
                this.showPopup('CashierTip',{
                    tipValue: Number(this.inputBuffer),
                    query: '',
                    order: this.props.order ? this.props.order : this.currentOrder,
                })
            }
        }
    }
    Registries.Component.extend(NumberPopup, NumberPopuptip);

    return NumberPopuptip;
});