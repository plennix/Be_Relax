odoo.define('point_of_sale_tip.CashierTip', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    class CashierTip extends AbstractAwaitablePopup{
        async confirm(){
            var x = {};
            var sum = 0;

            for(var i=0;i<this.cashiers.length;i++){
                x[this.cashiers[i].id] = $('#'+this.cashiers[i].id).val();
                sum += Number($('#'+this.cashiers[i].id).val());
            }
            if(this.props.tipValue == sum) {
                this.env.pos.get_order().set_cashier_tip(x);
                this.cancel();
            }
            else{
                this.showPopup('ErrorPopup', {
                        title: this.env._t('Wrong value'),
                        body: this.env._t(
                            'Divided value must be equals to tip.'
                        ),
                    });
            }
        }
         get cashiers(){
             var empCount =this.env.pos.employees
                        .filter((employee) => employee.id !== this.env.pos.get_cashier().id).length;
             var defTip = this.props.tipValue / empCount;
             var firsttip = false;
             var a = 0;
             const employeesList = this.env.pos.employees
                        .filter((employee) => employee.id !== this.env.pos.get_cashier().id)
                        .map((employee) => {
                            if(defTip.toFixed(2) * empCount == this.props.tipValue || firsttip){
                                        a = Number(defTip)
                                    }
                            else{
                                if (defTip.toFixed(2) * empCount <= this.props.tipValue){
                                    a = Number(defTip) + 0.01
                                    firsttip = true
                                }
                                else{
                                    a = Number(defTip) - 0.01
                                    firsttip = true
                                }
                            }
                            return {
                                id: employee.id,
                                label: employee.name,
                                defaultTip: a.toFixed(2),

                            };
                        });


             return employeesList;
         }
        }
    CashierTip.template = 'CashierTip';
    CashierTip.defaultProps = {
        confirmText: _lt('Ok'),
        title: _lt('Tips'),
        body: '',
    };

    Registries.Component.add(CashierTip);

    return CashierTip;
});
