odoo.define('point_of_sale_ext.TipsButton', function(require) {
    'use strict';

    const {
        useListener
    } = require("@web/core/utils/hooks");
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { parse } = require('web.field_utils');


    class TipsButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick() {
            if (!this.props.order) return;
            const tip = this.props.order.get_tip()
            const change = this.props.order.get_change();
            let value = tip === 0 && change > 0 ? change : tip;
            const {
                confirmed,
                payload
            } = await this.showPopup('NumberPopup', {
                title: tip ? this.env._t('Change Tip') : this.env._t('Add Tip'),
                startingValue: value,
                isInputSelected: true,
                isEachTip: true,
                order: this.props.order ? this.props.order : this.currentOrder,
            });
            if (confirmed) {
                this.props.order.set_tip(parse.float(payload));
            }
        }
    }
    TipsButton.template = 'TipsButton';
    Registries.Component.add(TipsButton);

    return TipsButton;
});