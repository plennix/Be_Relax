odoo.define('tus_pos_scan.IteaBoardingForm', function(require) {
    'use strict';
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    class IteaBoardingForm extends AbstractAwaitablePopup {
        async confirm() {
            this.env.pos.selectedOrder.boarding[this.props.index]['passenger_name']=document.getElementById('passenger_name').value;
            this.env.pos.selectedOrder.boarding[this.props.index]['departure']=document.getElementById('departure').value;
            this.env.pos.selectedOrder.boarding[this.props.index]['destination']=document.getElementById('destination').value;
            this.env.pos.selectedOrder.boarding[this.props.index]['flight_company']=document.getElementById('flight_company').value;
            this.env.pos.selectedOrder.boarding[this.props.index]['flight_number']=document.getElementById('flight_number').value;
            super.confirm();
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