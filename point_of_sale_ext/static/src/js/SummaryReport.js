odoo.define('point_of_sale_ext.SummaryReportButton', function(require) {
    'use strict';

    var core = require('web.core');
    const {
        useListener
    } = require("@web/core/utils/hooks");
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { parse } = require('web.field_utils');


    class SummaryReportButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick() {
            var self = this;
            var order = this.env.pos.get_order();
            debugger;
            await this.rpc({
               model: 'pos.session',
               method: 'print_report_ext',
               args: [[this.env.pos.pos_session.id]],
               context: self.odoo_context,
           }).then(function (result) {
                debugger;
//                result['data']['orderlines'] = parseInt(result['data']['orderlines'])
                return self.env.pos.env.legacyActionManager.do_action(result);

           });
        }
    }
    SummaryReportButton.template = 'SummaryReportButton';
    Registries.Component.add(SummaryReportButton);

    return SummaryReportButton;
});