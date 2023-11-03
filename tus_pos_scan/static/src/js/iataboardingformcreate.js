odoo.define('tus_pos_scan.IataBoardingFormCreate', function(require) {
    'use strict';
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const {
        _lt
    } = require('@web/core/l10n/translation');

    class IataBoardingFormCreate extends AbstractAwaitablePopup {
        async confirm() {
            var p_name = document.getElementById('p_name').value;
            var dep = document.getElementById('dep').value;
            var des = document.getElementById('des').value;
            var f_company = document.getElementById('f_company').value;
            var f_number = document.getElementById('f_number').value;
            var f_email = document.getElementById('f_email').value;
            var f_phone = document.getElementById('f_phone').value;
            if (p_name == '' || dep == '' || des == '' || f_company == '' || f_number == '' || f_email == '' || f_phone == '') {
                $('.error_msg').css('display', 'block')
            } else {
                $('.error_msg').css('display', 'none')
                var vv = {};
                vv['passenger_name'] = p_name;
                vv['departure'] = dep;
                vv['destination'] = des;
                vv['flight_company'] = f_company;
                vv['flight_number'] = f_number;
                vv['flight_phone'] = f_phone;
                vv['flight_email'] = f_email;
                if (this.env.pos.selectedOrder.boarding) {
                    this.env.pos.selectedOrder.boarding.push(vv)
                } else {
                    this.env.pos.selectedOrder.boarding = [vv]
                }
                let partnerId = await this.rpc({
                    model: 'res.partner',
                    method: 'create_from_ui',
                    args: [{'name': vv['passenger_name']}],
                });
                await this.env.pos.load_new_partners();
                vv['partner_id'] = partnerId;
                this.env.pos.get_order().set_partner(this.env.pos.db.get_partner_by_id(partnerId))
                super.confirm();
            }
        }
        cancel() {
            super.cancel();
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