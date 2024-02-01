odoo.define('point_of_sale_ext.BarcodeReader', function (require) {
"use strict";

var BarcodeReader = require('point_of_sale.BarcodeReader');

BarcodeReader.include({
    scan: async function (code) {
        if (!code) return;

        const callbacks = Object.keys(this.exclusive_callbacks).length
            ? this.exclusive_callbacks
            : this.action_callbacks;
        let parsed_result;
        try {
            parsed_result = this.barcode_parser.parse_barcode(code);
            if (Array.isArray(parsed_result) && !parsed_result.some(element => element.type === 'product')) {
                throw new GS1BarcodeError('The GS1 barcode must contain a product.');
            }
        } catch (error) {
            if (this.fallbackBarcodeParser && error instanceof GS1BarcodeError) {
                parsed_result = this.fallbackBarcodeParser.parse_barcode(code);
            } else {
                throw error;
            }
        }
        if (Array.isArray(parsed_result)) {
            [...callbacks.gs1].map(cb => cb(parsed_result));
        } else {
            if (callbacks[parsed_result.type]) {
                for (const cb of callbacks[parsed_result.type]) {
                    await cb(parsed_result);
                }
            } else if (callbacks.error) {
                [...callbacks.error].map(cb => cb(parsed_result));
            } else {
                if(parsed_result.type == "product"){
                    parsed_result.type == "cashier"
                    if (callbacks["cashier"]) {
                        for (const cb of callbacks["cashier"]) {
                            await cb(parsed_result);
                        }
                    }
                }else {
                    console.warn('Ignored Barcode Scan:', parsed_result);
                }
            }
        }
    },
});

});
