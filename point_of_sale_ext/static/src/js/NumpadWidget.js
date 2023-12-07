odoo.define('point_of_sale_ext.NumpadWidget', function(require) {
    'use strict';

    const NumpadWidget = require('point_of_sale.NumpadWidget');
    const Registries = require('point_of_sale.Registries');

    const DisNumpadWidget = NumpadWidget => class extends NumpadWidget {
       get hasManualDiscount() {
            debugger;
            return (this.env.pos.cashier.remove_pos_order_line && this.env.pos.cashier.allow_pos_order_line_disc) && !this.props.disabledModes.includes('discount');
        }
         get hasPriceControlRights() {
            return (
                this.env.pos.cashier.remove_pos_order_line &&
                !this.props.disabledModes.includes('price')
            );
        }
//        get hasBackspaceControlRights() {
//            return (
//                this.env.pos.cashier.remove_pos_order_line
//            )
//        }
    };

    Registries.Component.extend(NumpadWidget, DisNumpadWidget);

    return NumpadWidget;
 });
