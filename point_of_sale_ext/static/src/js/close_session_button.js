odoo.define('pos_ext.ClosePosPopup_xt', function (require) {
  'use strict';

  const ClosePosPopup = require('point_of_sale.ClosePosPopup');
  const Registries = require('point_of_sale.Registries');
  const { useValidateCashInput } = require('point_of_sale.custom_hooks');
  const { parse } = require('web.field_utils');

  const PosBlackboxBeClosePopupExt = (ClosePosPopup) =>
    class extends ClosePosPopup {
         setup() {
            super.setup();
            if (this.otherPaymentMethodsCurrency && this.otherPaymentMethodsCurrency.length > 0) {
                this.otherPaymentMethodsCurrency.forEach(pm => {
                    if (this._getShowDiff(pm)) {
                        useValidateCashInput("closingCashInput_" + pm.name, this.state.payments[pm.name].counted);
                    }
                })
            }
            if (this.defaultCashList && this.defaultCashList.length > 0) {
                this.defaultCashList.forEach(pm => {
                    useValidateCashInput("closingCashInput_" + pm.name, this.state.payments[pm.name].counted);
                })
            }
        }
        hasDifference() {
            return Object.entries(this.state.payments).find(pm => pm[1].difference != 0 && !pm[1].cash);
        }
        handleInputChangeForCashCurrency(paymentId, event){
            var self = this
            if (event.target.classList.contains('invalid-cash-input')) return;
            let expectedAmount;
            if (this.defaultCashDetails && paymentId === this.defaultCashDetails.id) {
                this.manualInputCashCount = true;
                this.state.notes = '';
                expectedAmount = this.defaultCashDetails.amount;
            } else {
                expectedAmount = this.defaultCashList.find(pm => paymentId === pm.name).amount;
            }
            this.state.payments[paymentId].counted = parse.float(event.target.value);

//            amount = this.format_currency_no_symbol(amount, precision, this.currency);
            let currency = this.env.pos.poscurrency;

            this.state.payments[paymentId].difference =
                this.env.pos.round_decimals_currency(this.state.payments[paymentId].counted - expectedAmount);

            var cash_counted = 0
            this.defaultCashList.forEach(pm => {

                let counted_val = this.state.payments[paymentId].counted
                for(var i=0;i<currency.length;i++){
                    if(currency[i].name==pm.currency_name && paymentId == pm.name){


                        let c_rate = self.env.pos.currency.rate/currency[i].rate;
                        cash_counted = parseFloat(counted_val)*c_rate;
//                        selected_paymentline.amount =parseFloat(tot_amount.toFixed(2));
                    }
                }

//                if(this.state.payments[paymentId].difference == 0){
//                cash_counted = cash_counted + parseFloat(cash_counted.toFixed(2))
//                }
            })
            this.state.payments[this.defaultCashDetails.id].counted = cash_counted
            this.state.payments[this.defaultCashDetails.id].difference =
                this.env.pos.round_decimals_currency(this.state.payments[[this.defaultCashDetails.id]].counted - this.defaultCashDetails.amount);
        }
        handleInputChangeForCurrency(paymentId, event){
             if (event.target.classList.contains('invalid-cash-input')) return;
            let expectedAmount;
            if (this.defaultCashDetails && paymentId === this.defaultCashDetails.id) {
                this.manualInputCashCount = true;
                this.state.notes = '';
                expectedAmount = this.defaultCashDetails.amount;
            } else {
                expectedAmount = this.otherPaymentMethodsCurrency.find(pm => paymentId === pm.name).amount;
            }
            this.state.payments[paymentId].counted = parse.float(event.target.value);
            this.state.payments[paymentId].difference =
                this.env.pos.round_decimals_currency(this.state.payments[paymentId].counted - expectedAmount);
        }
      async confirm() {
        var self = this;
        var order = this.env.pos.get_order();
        await this.rpc({
          model: 'pos.session',
          method: 'print_report_ext',
          args: [[this.env.pos.pos_session.id]],
          context: self.odoo_context,
        }).then(function (result) {
          //                result['data']['orderlines'] = parseInt(result['data']['orderlines'])
          return self.env.pos.env.legacyActionManager.do_action(result);

        });
        return super.confirm();
      }
      async closePos(){
        if(this.env.pos.config.enable_attendance){
        await this.rpc({
            model: 'hr.employee',
            method: 'pos_cashier_checkout',
            args: [[this.env.pos.cashier.id],this.env.pos.pos_session.id],
          });
        }
        return super.closePos();
      }
      async closeSession() {
            if (!this.closeSessionClicked) {
                this.closeSessionClicked = true;
                let response;
                // If there are orders in the db left unsynced, we try to sync.
                await this.env.pos.push_orders_with_closing_popup();
                if (this.cashControl) {
                     response = await this.rpc({
                        model: 'pos.session',
                        method: 'post_closing_cash_details',
                        args: [this.env.pos.pos_session.id],
                        kwargs: {
                            counted_cash: this.state.payments[this.defaultCashDetails.id].counted,
                        }
                    })
                    if (!response.successful) {
                        return this.handleClosingError(response);
                    }
                    else{
                        if(this.env.pos.config.enable_attendance){
                         await this.rpc({
                            model: 'hr.employee',
                            method: 'pos_cashier_checkout',
                            args: [[this.env.pos.cashier.id],this.env.pos.pos_session.id],
                          });
                        }
                    }
                }
                await this.rpc({
                    model: 'pos.session',
                    method: 'update_closing_control_state_session',
                    args: [this.env.pos.pos_session.id, this.state.notes]
                })
                try {
                    const bankPaymentMethodDiffPairs = this.otherPaymentMethods
                        .filter((pm) => pm.type == 'bank')
                        .map((pm) => [pm.id, this.state.payments[pm.id].difference]);
                    response = await this.rpc({
                        model: 'pos.session',
                        method: 'close_session_from_ui',
                        args: [this.env.pos.pos_session.id, bankPaymentMethodDiffPairs],
                        context: this.env.session.user_context,
                    });
                    if (!response.successful) {
                        return this.handleClosingError(response);
                    }
                    else{
                        if(this.env.pos.config.enable_attendance){
                         await this.rpc({
                            model: 'hr.employee',
                            method: 'pos_cashier_checkout',
                            args: [[this.env.pos.cashier.id],this.env.pos.pos_session.id],
                          });
                         }
                    }
                    window.location = '/web#action=point_of_sale.action_client_pos_menu';
                } catch (error) {
                    const iError = identifyError(error);
                    if (iError instanceof ConnectionLostError || iError instanceof ConnectionAbortedError) {
                        await this.showPopup('ErrorPopup', {
                            title: this.env._t('Network Error'),
                            body: this.env._t('Cannot close the session when offline.'),
                        });
                    } else {
                        await this.showPopup('ErrorPopup', {
                            title: this.env._t('Closing session error'),
                            body: this.env._t(
                                'An error has occurred when trying to close the session.\n' +
                                'You will be redirected to the back-end to manually close the session.')
                        })
                        window.location = '/web#action=point_of_sale.action_client_pos_menu';
                    }
                }
                this.closeSessionClicked = false;
            }
        }

    };

  Registries.Component.extend(ClosePosPopup, PosBlackboxBeClosePopupExt);

  return ClosePosPopup;
});
