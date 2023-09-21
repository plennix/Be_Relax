odoo.define('point_of_sale_commission.ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const { useBarcodeReader } = require('point_of_sale.custom_hooks');
    const NumberBuffer = require('point_of_sale.NumberBuffer');


    const ProductScreenAddEmp = (ProductScreen) =>
        class extends ProductScreen {
            async _clickProduct(event) {
                if (!this.currentOrder) {
                    this.env.pos.add_new_order();
                }
            const product = event.detail;
            const options = await this._getAddProductOptions(product);
            if (!options) return;
            if (this.env.pos.employees){
                const employeesList = this.env.pos.employees
                        .map((employee) => {
                            return {
                                id: employee.id,
                                item: employee,
                                label: employee.name,
                                line_emp_pin: employee.line_emp_pin,
                                isSelected: false,
                            };
                        });
                let {confirmed, payload: employee} = await this.showPopup('SelectionPopup', {
                    title: this.env._t('Therapist'),
                    list: employeesList,
                });
                if(confirmed){
                    options['employee_id']=employee.id;
                    options['line_emp_pin']=employee.line_emp_pin || '';
                }
            }
            await this._addProduct(product, options);
            NumberBuffer.reset();
        }
        };

    Registries.Component.extend(ProductScreen, ProductScreenAddEmp);

    return ProductScreen;
});
