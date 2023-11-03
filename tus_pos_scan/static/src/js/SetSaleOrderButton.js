odoo.define('tus_pos_scan.SetOrderNTNButton', function(require) {
    'use strict';

    var security_var = -1;
    var iataFormat = {
                    passenger_name: { length: 20, offset: 22, content: "", explanation: "Passenger Name"},
                    flight_number: { length: 5, offset: 44, content: "", explanation: "Flight Number"},
                    departure: { length: 3, offset: 33, content: "", explanation: "From City Airport Code"}, //departure
                    destination: { length: 3, offset: 36, content: "", explanation: "To City Airport Code"}, //destination
                    flight_company: { length: 3, offset: 39, content: "", explanation: "Operating carrier Designator"}, //flight_company
                };

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');
    const { isConnectionError } = require('point_of_sale.utils');
    class SetOrderNTNButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        };


        submitIata(fromIndex) {
            var textarea = fromIndex;
            var vv = {};
            var results_col_1 = true;
            for (const key in iataFormat) {
                vv[key] = this.displayElement(results_col_1,textarea,key,iataFormat[key]);
            };
            return vv
        };
        displayElement(dom, textarea, i, iataFormat) {
            var element = this.getIataElement(textarea, iataFormat);
            return element
        }

         getIataElement(input, element) {
            if (element.offset <= input.length && input.length <= 158/*because of airline's var field, see below*/) {
                let tmp = input.substring(element.offset - element.length, element.offset);
                return tmp;
            }
        return -1;
        }

        async onClick() {
            const selectedOrder = this.env.pos.get_order();
            var { confirmed, payload: inputNote } = await this.showPopup('TextInputPopup', {
                startingValue: '',
                title: this.env._t('Scan Boarding Pass'),
            });

            if (confirmed && inputNote) {
                selectedOrder.ntn_number = inputNote;
                const a = this.submitIata(inputNote);
                let newPartner = await this.env.pos.load_new_partners();
                let passenger_name = a.passenger_name.trim();
                const partners_names = this.env.pos.partners.map(x => x.name).filter(x => x === passenger_name)
                const new_partners_names = this.env.pos.db.search_partner(passenger_name)
                if (partners_names.length != 0 || new_partners_names.length != 0){
                    var { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Create Partner'),
                        body: this.env._t('This partner already exist if you want create new please confirm.'),
                    });
                }
                if (confirmed || new_partners_names.length == 0){
                    let partnerId = await this.rpc({
                        model: 'res.partner',
                        method: 'create_from_ui',
                        args: [{'name': a.passenger_name.trim()}],
                    });
                    await this.env.pos.load_new_partners();
                    a['partner_id'] = partnerId;
                    this.env.pos.get_order().set_partner(this.env.pos.db.get_partner_by_id(partnerId))
                }
                if (new_partners_names.length > 0 && !confirmed){
                    let lastCreatePartner = new_partners_names[new_partners_names.length - 1]
                    this.env.pos.get_order().set_partner(lastCreatePartner)
                }
                if (selectedOrder.boarding){
                    selectedOrder.boarding.push(a);
                }else{
                    selectedOrder.boarding = [a];
                }
            }
        }

    }
    SetOrderNTNButton.template = 'SetOrderNTNButton';

    ProductScreen.addControlButton({
        component: SetOrderNTNButton,
    });
    Registries.Component.add(SetOrderNTNButton);
    return SetOrderNTNButton;
});
