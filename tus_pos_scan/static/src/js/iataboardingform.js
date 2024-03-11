odoo.define('tus_pos_scan.IteaBoardingForm', function(require) {
    'use strict';
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const {
        _lt
    } = require('@web/core/l10n/translation');

    class IteaBoardingForm extends AbstractAwaitablePopup {
        async confirm() {
            if(document.getElementById('departure') && document.getElementById('departure').value)
            {
                this.env.pos.selectedOrder.boarding[this.props.index]['departure'] =document.getElementById('departure').value;
             }
            this.env.pos.selectedOrder.boarding[this.props.index]['passenger_name'] = document.getElementById('passenger_name').value;
            this.env.pos.selectedOrder.boarding[this.props.index]['destination'] = document.getElementById('destination').value;
            this.env.pos.selectedOrder.boarding[this.props.index]['flight_company'] = document.getElementById('flight_company').value;
            this.env.pos.selectedOrder.boarding[this.props.index]['flight_number'] = document.getElementById('flight_number').value;
            this.env.pos.selectedOrder.boarding[this.props.index]['flight_phone'] = document.getElementById('flight_phone').value;
            this.env.pos.selectedOrder.boarding[this.props.index]['flight_email'] = document.getElementById('flight_email').value;

            let partnerId = await this.rpc({
                model: 'res.partner',
                method: 'create_from_ui',
                args: [{'id':this.env.pos.get_order().boarding[this.props.index].partner_id,'name': document.getElementById('passenger_name').value,'email':document.getElementById('flight_email').value,'phone':document.getElementById('flight_phone').value}],
            });
            await this.env.pos.load_new_partners();
            this.env.pos.get_order().set_partner(this.env.pos.db.get_partner_by_id(partnerId))
            super.confirm();
        }
        cancel() {
            super.cancel();
        }
    };

    IteaBoardingForm.template = 'IteaBoardingForm';
    IteaBoardingForm.defaultProps = {
        confirmText: _lt('Confirm'),
        title: _lt('Boarding Form'),
    };
    Registries.Component.add(IteaBoardingForm);
    return IteaBoardingForm;
});