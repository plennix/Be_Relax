odoo.define('point_of_sale_ext.SelectionPopupTus', function(require) {
    'use strict';

    const SelectionPopup = require('point_of_sale.SelectionPopup');
    const Registries = require('point_of_sale.Registries');

    const SelectionPopupTus = (SelectionPopup) =>
        class extends SelectionPopup {
            setup() {
                super.setup();
                this.state = {
                    EmpList: this.props.list,
                };
            }
            async updateEmployeeList(event) {
                if (event) {
                    this.state.query = event.target.value;
                }
                if (this.state.query) {
                    let result = this.state.EmpList.filter(emp => emp.label.trim().toLowerCase().startsWith(this.state.query.toLowerCase()))
                    this.props.list = result
                } else {
                    this.props.list = this.state.EmpList
                }
                this.render(true);
                return this.props.list
            }
            async _onPressEnterKey() {
                if (!this.state.query) return;
                const result = await this.updateEmployeeList();
                if (result.length > 0) {
                    this.showNotification(
                        _.str.sprintf(
                            this.env._t('%s customer(s) found for "%s".'),
                            result.length,
                            this.state.query
                        ),
                        3000
                    );
                } else {
                    this.showNotification(
                        _.str.sprintf(
                            this.env._t('No more customer found for "%s".'),
                            this.state.query
                        ),
                        3000
                    );
                }
            }
        }
    Registries.Component.extend(SelectionPopup, SelectionPopupTus);
    return SelectionPopup;
});