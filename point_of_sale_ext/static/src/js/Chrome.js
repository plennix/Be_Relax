odoo.define('point_of_sale_ext.chrome', function (require) {
    'use strict';

    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');

    const PosHrChromeExt = (Chrome) => class extends Chrome {
        get headerButtonIsShown() {
            return !this.env.pos.config.module_pos_hr || this.env.pos.get_cashier().job_bool || this.env.pos.get_cashier_user_id() === this.env.pos.user.id;
        }
    }
    Registries.Component.extend(Chrome, PosHrChromeExt);

    return Chrome;
});