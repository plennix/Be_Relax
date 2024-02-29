odoo.define('point_of_sale_commission.ProductScreen', function (require) {
  'use strict';

  const ProductScreen = require('point_of_sale.ProductScreen');
  const Registries = require('point_of_sale.Registries');
  const { useBarcodeReader } = require('point_of_sale.custom_hooks');
  const NumberBuffer = require('point_of_sale.NumberBuffer');


  const ProductScreenAddEmp = (ProductScreen) =>
    class extends ProductScreen {

      async _barcodeProductAction(code) {
        debugger;
        const product = await this._getProductByBarcode(code);
         if (!product) {
          return;
        }
//         var options = {}
//        if (product) {
         const options = await this._getAddProductOptions(product, code);

        const cashier = this.env.pos.cashier
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
        const other_employeesList = employeesList.filter(function (ol) {
          return ol.id != cashier.id;
        });
        const cashier_employee = employeesList.filter(function (ol) {
          return ol.id == cashier.id;
        });
        const sorted_employee = cashier_employee.concat(other_employeesList)
        let { confirmed, payload: employee } = await this.showPopup('SelectionPopup', {
          title: this.env._t('Therapist'),
          list: sorted_employee,
        });
        if (confirmed) {
          options['employee_id'] = employee.id;
          options['line_emp_pin'] = employee.line_emp_pin || '';
        }
//        }


        // Do not proceed on adding the product when no options is returned.
        // This is consistent with _clickProduct.
        if (!options) return;

        // update the options depending on the type of the scanned code
        if (code.type === 'price') {
          Object.assign(options, {
            price: code.value,
            extras: {
              price_manually_set: true,
            },
          });
        } else if (code.type === 'weight' || code.type === 'quantity') {
          Object.assign(options, {
            quantity: code.value,
            merge: false,
          });
        } else if (code.type === 'discount') {
          Object.assign(options, {
            discount: code.value,
            merge: false,
          });
        }
        this.currentOrder.add_product(product, options);
        NumberBuffer.reset();
      }
      async _clickProduct(event) {

        if (!this.partner) {
          // prevent adding product if customer not selected
          this.showPopup('ErrorPopup', {
            title: this.env._t('Error'),
            body: this.env._t('Please select a customer first to add product!'),
          });
          return
        }

        if (!this.currentOrder) {
          this.env.pos.add_new_order();
        }
        const product = event.detail;
        const options = await this._getAddProductOptions(product);
        if (!options) return;
        if (this.env.pos.employees) {
          var self = this;
          const cashier = this.env.pos.cashier
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
          const other_employeesList = employeesList.filter(function (ol) {
            return ol.id != cashier.id;
          });
          const cashier_employee = employeesList.filter(function (ol) {
            return ol.id == cashier.id;
          });
          const sorted_employee = cashier_employee.concat(other_employeesList)
          let { confirmed, payload: employee } = await this.showPopup('SelectionPopup', {
            title: this.env._t('Therapist'),
            list: sorted_employee,
          });
          if (confirmed) {
            options['employee_id'] = employee.id;
            options['line_emp_pin'] = employee.line_emp_pin || '';
          }
        }
        await this._addProduct(product, options);
        NumberBuffer.reset();
      }
      async _onClickPay() {

        // prevent proceeding with payment if customer not selected and products added
        if (!this.partner) {
          this.showPopup('ErrorPopup', {
            title: this.env._t('Error'),
            body: this.env._t('Please select a customer first to add product!'),
          });
          return
        }
        debugger;
        const { confirmed, payload } = await this.showPopup('ConfirmPopup', {
          'title': this.env._t('Add Product'),
          'body': this.env._t('Add more products?'),
        });
        if (confirmed) {
          this.showScreen('ProductScreen');
        } else {
          //                    this.showScreen('PaymentScreen');
          super._onClickPay();
        }
      }
    };

  Registries.Component.extend(ProductScreen, ProductScreenAddEmp);

  return ProductScreen;
});
