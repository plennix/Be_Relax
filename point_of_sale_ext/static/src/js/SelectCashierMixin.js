odoo.define('point_of_sale_ext.SelectCashierMixin', function (require) {
    'use strict';

    const { patch } = require("@web/core/utils/patch");
    const LoginScreen = require('pos_hr.LoginScreen');

    patch(LoginScreen.prototype, 'point_of_sale_ext/static/src/js/SelectCashierMixin.js',{
        async selectCashier() {
              if (this.env.pos.config.module_pos_hr) {
                const employeesList = this.env.pos.employees
                    .filter((employee) => employee.id !== this.env.pos.get_cashier().id)
                    .map((employee) => {
                        return {
                            id: employee.id,
                            item: employee,
                            label: employee.name,
                            isSelected: false,
                        };
                    });
                let {confirmed, payload: employee} = await this.showPopup('SelectionPopup', {
                    title: this.env._t('Change Cashier'),
                    list: employeesList,
                });

                if (!confirmed) {
                    return;
                }
                let EmpCheckIn = await this.rpc({
                        model: 'hr.employee',
                        method: 'check_pos_cashier_checkin',
                        args: [{'emp_id': employee.id}],
                    });
                if (!EmpCheckIn){
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Wrong value'),
                        body: this.env._t(
                            'This cashier has not checked in.'
                        ),
                });
                 return false
                }

                if (employee && employee.pin) {
                    employee = await this.askPin(employee);
                }
                if (employee) {
                    this.env.pos.set_cashier(employee);
                    this.back();
                }
            }
        }
    });
});