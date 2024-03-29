/** @odoo-module **/

import { DatePicker } from "@web/core/datepicker/datepicker";
import { patch } from "@web/core/utils/patch";
import { formatDateTimeCustom } from "./getDateTimeCustomTZ";


DatePicker.props = {
    ...DatePicker.props,
    record: { type: Object, optional: true },
};

patch(DatePicker.prototype, 'point_of_sale_ext.DatePicker', {

        /**
     * Updates the input element with the current formatted date value.
     *
     * @param {DateTime} value
     */
    updateInput(value) {
        debugger;
        value = value || false;
        const options = this.getOptions();
        let [formattedValue, error] = this.formatValue(value, options);

        // Customisation: show datetime as per timezone set at company level.
        if (value && this.props && this.props.record && this.props.record.resModel === 'attendance.record' && this.props.record.data && this.props.record.data.timezone)
        {
            formattedValue = formatDateTimeCustom(value, {...options, timezone: this.props.record.data.timezone})
            this.inputRef.el.value = formattedValue;
            [this.hiddenInputRef.el.value] = formatDateTimeCustom(value, {
                ...options,
                format: this.staticFormat,
                timezone: this.props.record.data.timezone,
            });
            this.props.onUpdateInput(formattedValue);
        }

        // Default odoo native flow, in case timezone not set in employee's company
        else {
            if (!error) {
                this.inputRef.el.value = formattedValue;
                [this.hiddenInputRef.el.value] = this.formatValue(value, {
                    ...options,
                    format: this.staticFormat,
                });
                this.props.onUpdateInput(formattedValue);
            }
        }
        return formattedValue;
    }

});

