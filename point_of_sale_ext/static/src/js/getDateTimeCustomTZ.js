/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { getFormattedValue } from "@web/views/utils";
import { formatDateTime } from "@web/core/l10n/dates";
import { localization } from "@web/core/l10n/localization";
const { Settings } = luxon;
import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";


export function formatDateTimeCustom(value, options = {}) {
    console.log('formatDateTimeCustom called----')

    if (value === false) {
        return "";
    }
    const format = options.format || localization.dateTimeFormat;
    const numberingSystem = options.numberingSystem || Settings.defaultNumberingSystem || "latn";

    // customisation: show datetime as per timezone set at company level.
    if (options && options.timezone){
            return value.setZone(options.timezone).toFormat(format, { numberingSystem });
    }
    if (options && options.data && options.data.timezone){
        return value.setZone(options.data.timezone).toFormat(format, { numberingSystem });
    }

    return value.setZone("default").toFormat(format, { numberingSystem });  // default
}

registry.category("formatters").remove("datetime", formatDateTime)
registry.category("formatters").add("datetime", formatDateTimeCustom)