/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { formatDateTime } from "@web/core/l10n/dates";
import { DateTimeField } from '@web/views/fields/datetime/datetime_field';
import { formatDateTimeCustom } from "./getDateTimeCustomTZ";


patch(DateTimeField.prototype, 'point_of_sale_ext.DateTimeField', {
     // Customisation: show datetime as per timezone set at company level.
     // For readonly datetime field
     get formattedValue() {
        debugger;
        const modelNames = ['attendance.record', 'hr.attendance']
        if (this.props && this.props.record && modelNames.includes(this.props.record.resModel) && this.props.record.data && this.props.record.data.timezone){
            return formatDateTimeCustom(this.props.value, {
                timezone: this.props.record.data.timezone,
            });
        }
        return formatDateTime(this.props.value);
    }
})