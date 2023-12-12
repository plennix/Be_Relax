// ProductCategoriesWidget
odoo.define('bi_pos_combo.ProductCategoriesWidget', function(require) {
	"use strict";

	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const ProductsWidget = require('point_of_sale.ProductsWidget');

	const ProductCategoriesWidget = (ProductsWidget) =>
		class extends ProductsWidget {
			setup() {
				super.setup();
			}
			_updateSearch(event) {
            	this.state.searchWord = event.detail;
        	}
		};

	Registries.Component.extend(ProductsWidget, ProductCategoriesWidget);

	return ProductsWidget;

});
