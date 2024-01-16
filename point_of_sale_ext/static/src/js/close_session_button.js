odoo.define('pos_ext.ClosePosPopup_xt', function (require) {
  'use strict';

  const ClosePosPopup = require('point_of_sale.ClosePosPopup');
  const Registries = require('point_of_sale.Registries');

  const PosBlackboxBeClosePopupExt = (ClosePosPopup) =>
    class extends ClosePosPopup {
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
    };

  Registries.Component.extend(ClosePosPopup, PosBlackboxBeClosePopupExt);

  return ClosePosPopup;
});
