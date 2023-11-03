odoo.define('point_of_sale_tip.CashierTip', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const {
        _lt
    } = require('@web/core/l10n/translation');

    class CashierTip extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            this.state = {
                EmpList: this.cashiers,
            };
        }
        async updateEmployeeList(event) {
            if (event) {
                this.props.query = event.target.value;
            }
            if (this.props.query) {
                let result = this.cashiers.filter(emp => emp.label.trim().toLowerCase().startsWith(this.props.query.toLowerCase()))
                this.state.EmpList = result
            } else {
                this.state.EmpList = this.cashiers
            }
            this.render(true);
            return this.state.EmpList
        }
        async confirm() {
            var x = {};
            var sum = 0.00;
            for (var i = 0; i < this.cashiers.length; i++) {
                sum = Number(sum.toFixed(2))
                x[this.cashiers[i].id] = $('#' + this.cashiers[i].id).val();
                sum += Number($('#' + this.cashiers[i].id).val());
            }
            debugger;
            if (this.props.tipValue == sum) {
                if (this.props.order) {
                    this.props.order.set_cashier_tip(x)
                    if (!this.env.pos.employees) {
                        this.props.order.is_user()
                    }
                    let PosOrder = await this.rpc({
                        model: 'pos.order',
                        method: 'pos_order_paid_tips',
                        args: [{'CashierTip':this.props.order.CashierTip,'order_id':this.props.order.backendId,'name':this.props.order.name}],
                    });
                    this.cancel();
                }else{
                    this.env.pos.get_order().set_cashier_tip(x);
                    if (!this.env.pos.employees) {
                        this.env.pos.get_order().is_user()
                    }
                }
                this.cancel();
            } else {
                this.showPopup('ErrorPopup', {
                    title: this.env._t('Wrong value'),
                    body: this.env._t(
                        'Assigned value must be equals to tip.'
                    ),
                });
            }
        }
        get cashiers() {
            if (!this.env.pos.employees) {
                const CashierList = [{

                    id: this.env.pos.get_cashier().id,
                    label: this.env.pos.get_cashier().name,
                    defaultTip: this.props.tipValue.toFixed(2),

                }];
                return CashierList;
            } else {
                var empCount = this.env.pos.employees.length;
                var firsttip = true;
                var a = 0;
                const employeesList = this.env.pos.employees
                    .map((employee) => {
                        if (firsttip) {
                            a = a + Number(this.props.tipValue)
                            firsttip = false
                        } else {
                            a = 0
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