odoo.define('point_of_sale_ext.CashOpeningPopup_xt', function (require) {
  'use strict';

  const CashOpeningPopup = require('point_of_sale.CashOpeningPopup');
  const Registries = require('point_of_sale.Registries');

  const PosCashOpeningPopupPopupExt = (CashOpeningPopup) =>
    class extends CashOpeningPopup {
      async confirm() {
        if (this.env.pos.pos_session.cash_register_balance_start === this.state.openingCash) {
          return super.confirm();
        } else {
          this.showPopup('ErrorPopup', {
            title: this.env._t('Error'),
            body: _.str.sprintf(this.env._t('Please enter the previous closing amount %s'), this.env.pos.format_currency(this.env.pos.pos_session.cash_register_balance_start)),
          });
          return false
        }
      }
    };
  Registries.Component.extend(CashOpeningPopup, PosCashOpeningPopupPopupExt);
  return CashOpeningPopup;
});