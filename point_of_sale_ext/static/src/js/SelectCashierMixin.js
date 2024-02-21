/ global Sha1 /
odoo.define('pos_hr.SelectCashierMixin', function (require) {
  'use strict';

  const SelectCashierMixin = (PosComponent) => class ComponentWithSelectCashierMixin extends PosComponent {
    async askPin(employee) {
      const { confirmed, payload: inputPin } = await this.showPopup('NumberPopup', {
        isPassword: true,
        title: this.env._t('Password ?'),
        startingValue: null,
      });

      if (!confirmed) return;

      if (employee.pin === Sha1.hash(inputPin)) {
        return employee;
      } else {
        await this.showPopup('ErrorPopup', {
          title: this.env._t('Incorrect Password'),
        });
        return;
      }
    }

    /**
     * Select a cashier, the returning value will either be an object or nothing (undefined)
     */
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
        let { confirmed, payload: employee } = await this.showPopup('SelectionPopup', {
          title: this.env._t('Change Cashier'),
          list: employeesList,
        });

        if (!confirmed) {
          return;
        }
        let EmpCheckIn = false

        if (employee) {
          EmpCheckIn = await this.rpc({
            model: 'hr.employee',
            method: 'check_pos_cashier_checkin',
            args: [[employee.id],this.env.pos.pos_session.id],
          });

        }
        if (employee && !EmpCheckIn.emp_attendance_status) {
          this.showPopup('ErrorPopup', {
            title: this.env._t('Wrong value'),
            body: this.env._t(
              'This cashier has not checked in.'
            ),
          });
          return false
        }

//         if (employee && EmpCheckIn.already_checkin_another_session) {
//          this.showPopup('ErrorPopup', {
//            title: this.env._t('Wrong value'),
//            body: this.env._t(
//              'This Cashier Already Logged In Another Session.'
//            ),
//          });
//          return false
//        }


                if (employee && employee.pin) {
                    employee = await this.askPin(employee);
                }
                if (employee) {
                    this.env.pos.set_cashier(employee);
                    if (this.env.pos.config.enable_attendance) {
                        await this.rpc({
                            model: 'hr.employee',
                            method: 'pos_cashier_checkin',
                            args: [[employee.id], this.env.pos.pos_session.id],
                        });
                    }

                    this.back ? this.back() : null;
                }
            }
        }

        async barcodeCashierAction(code) {
            //    code1 = '041' + code.code
            //      console.log(">>>codecodecode>>>>>>",code1)
            const employee = this.env.pos.employees.find(
                (emp) => emp.barcode === Sha1.hash(code.code)
            );
            let EmpCheckIn = false
            debugger;

            if (employee) {
                EmpCheckIn = await this.rpc({
                    model: 'hr.employee',
                    method: 'check_pos_cashier_checkin',
                    args: [[employee.id], this.env.pos.pos_session.id],
                });
            }
            if (employee && employee !== this.env.pos.get_cashier() && EmpCheckIn.emp_attendance_status && !EmpCheckIn.already_checkin_another_session) {

              this.env.pos.set_cashier(employee);
                    if (this.env.pos.config.enable_attendance) {
                        await this.rpc({
                            model: 'hr.employee',
                            method: 'pos_cashier_checkin',
                            args: [[employee.id], this.env.pos.pos_session.id],
                        });
                    }
            }
            return employee;
        }
    }

    return SelectCashierMixin;

});
