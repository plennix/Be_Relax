odoo.define('tus_pos_scan.IteaBoardingList', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');


    class IteaBoardingList extends AbstractAwaitablePopup {
        get getiteaboarding(){
            if (this.env.pos && this.env.pos.selectedOrder && this.env.pos.selectedOrder.boarding){
                var iteaboardinglistNew = this.env.pos.selectedOrder.boarding || [];
            return iteaboardinglistNew;
            }
        };
        selectForm(a_index){
            var a = this.showPopup('IteaBoardingForm', {
                    index: a_index,
                    posmodel: this.env.pos,
                });
        }
        async CreateBoardingPass(){
            await this.showPopup('IataBoardingFormCreate');
        }
    }

    IteaBoardingList.template = 'IteaBoardingList';
    IteaBoardingList.defaultProps = {
        confirmText: _lt('Exit'),
        title: _lt('Boarding List'),
    };
    Registries.Component.add(IteaBoardingList);
    return IteaBoardingList;
});
