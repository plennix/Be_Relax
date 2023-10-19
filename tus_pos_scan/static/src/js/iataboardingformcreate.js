odoo.define('tus_pos_scan.IataBoardingFormCreate', function(require) {
    'use strict';
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    class IataBoardingFormCreate extends AbstractAwaitablePopup {
        async confirm() {
            var p_name = document.getElementById('p_name').value;
            var dep = document.getElementById('dep').value;
            var des = document.getElementById('des').value;
            var f_company = document.getElementById('f_company').value;
            var f_number = document.getElementById('f_number').value;
            if (p_name == '' || dep== '' || des== '' || f_company== '' || f_number== ''){
                $('.error_msg').css('display','block')
            }else{
                $('.error_msg').css('display','none')
                var vv = {};
                vv['passenger_name'] = p_name;
                vv['departure'] = dep;
                vv['destination'] = des;
                vv['flight_company'] = f_company;
                vv['flight_number'] = f_number;
                if(this.env.pos.selectedOrder.boarding){
                    this.env.pos.selectedOrder.boarding.push(vv)
                }
                else{
                   this.env.pos.selectedOrder.boarding = [vv]
                }
                super.confirm();
            }
        }
    };

    IataBoardingFormCreate.template = 'IataBoardingFormCreate';
    IataBoardingFormCreate.defaultProps = {
        confirmText: _lt('Confirm'),
        title: _lt('Boarding Form'),
    };
    Registries.Component.add(IataBoardingFormCreate);
    return IataBoardingFormCreate;
});