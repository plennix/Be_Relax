odoo.define('bi_pos_combo.pos', function (require) {
  "use strict";

  var core = require('web.core');
  var utils = require('web.utils');
  var round_pr = utils.round_precision;
  var field_utils = require('web.field_utils');
  const Registries = require('point_of_sale.Registries');
  var { Order, Orderline, PosGlobalState } = require('point_of_sale.models');
  var round_di = utils.round_decimals;

  const POSComboProduct = (PosGlobalState) => class POSComboProduct extends PosGlobalState {

    async _processData(loadedData) {
      await super._processData(...arguments);
      this.product_pack = loadedData['product.pack'] || [];
    }
  }

  Registries.Model.extend(PosGlobalState, POSComboProduct);


  const BiCustomOrderLine = (Orderline) => class BiCustomOrderLine extends Orderline {

    constructor(obj, options) {
      super(...arguments);
      this.pos = options.pos;
      this.order = options.order;
      var self = this;
      if (options.json) {
        this.init_from_JSON(options.json);
        return;
      }
      this.combo_products = this.combo_products;
      var final_data = self.pos.final_products;
      if (final_data) {
        for (var i = 0; i < final_data.length; i++) {
          if (final_data[i] == undefined) {
            i = i + 1;
            if (final_data[i][0] == this.product.id) {
              this.combo_products = final_data[i][1];
              self.pos.final_products = null;
            }
          }
          else {
            if (final_data[i][0] == undefined) {
              return;
            }
            if (final_data[i][0] == this.product.id) {
              this.combo_products = final_data[i][1];
              self.pos.final_products = null;
            }
          }
        }
      }
      this.set_combo_products(this.combo_products);
      this.combo_prod_ids = this.combo_prod_ids || [];
      this.is_pack = this.is_pack;

    }
    clone() {
      const orderline = super.clone(...arguments);
      orderline.is_pack = this.is_pack;
      orderline.price_manually_set = this.price_manually_set;
      orderline.combo_prod_ids = this.combo_prod_ids || [];
      orderline.combo_products = this.combo_products || [];
      return orderline;
    }
    can_be_merged_with(orderline) {
    debugger;
      var price = parseFloat(round_di(this.price || 0, this.pos.dp['Product Price']).toFixed(this.pos.dp['Product Price']));
      var order_line_price = orderline.get_product().get_price(orderline.order.pricelist, this.get_quantity());
      order_line_price = round_di(orderline.compute_fixed_price(order_line_price), this.pos.currency.decimal_places);
      if (this.get_product().id !== orderline.get_product().id) {    //only orderline of the same product can be merged
        return false;
      } else if (!this.get_unit() || !this.get_unit().is_pos_groupable) {
        return false;
      } else if (this.get_discount() > 0) {             // we don't merge discounted orderlines
        return false;
      } else if (!utils.float_is_zero(price - order_line_price - orderline.get_price_extra(),
        this.pos.currency.decimal_places)) {
        return false;
      } else if (this.product.tracking == 'lot' && (this.pos.picking_type.use_create_lots || this.pos.picking_type.use_existing_lots)) {
        return false;
      } else if (this.description !== orderline.description) {
        return false;
      } else if (orderline.get_customer_note() !== this.get_customer_note()) {
        return false;
      } else if (this.refunded_orderline_id) {
        return false;
//        } else if (this.order.orderlines.filter((line) => line.product.id === orderline.product.id && line.employee_id === orderline.employee_id)) {
//        return true;
              } else if (this.order.orderlines.filter((line) => line.product.id === orderline.product.id && line.employee_id !== orderline.employee_id)) {
        return false;
      } else {
        return true;
      }
    }

    init_from_JSON(json) {
      super.init_from_JSON(...arguments);
      this.combo_prod_ids = json.combo_prod_ids;
      this.is_pack = json.is_pack;
    }
    export_as_JSON() {
      const json = super.export_as_JSON(...arguments);
      // json.combo_products = this.get_combo_products();
      json.combo_prod_ids = this.combo_prod_ids;
      json.is_pack = this.is_pack;
      return json;
    }
    export_for_printing() {
      const json = super.export_for_printing(...arguments);
      json.combo_products = this.get_combo_products();
      json.combo_prod_ids = this.combo_prod_ids;
      json.is_pack = this.is_pack;
      return json;
    }
    set_combo_prod_ids(ids) {
      this.combo_prod_ids = ids
    }
    set_combo_products(products) {
      var ids = [];
      if (this.product.is_pack) {
        if (products) {
          products.forEach(function (prod) {
            if (prod != null) {
              ids.push(prod.id)
            }
          });
        }
        this.combo_products = products;
        this.set_combo_prod_ids(ids)
        if (this.combo_prod_ids) {
          this.set_combo_price(this.price);
        }
      }

    }
    set_is_pack(is_pack) {
      this.is_pack = is_pack
    }
    set_unit_price(price) {
      this.order.assert_editable();
      if (this.product.is_pack) {
        this.set_is_pack(true);
        var prods = this.get_combo_products()
        var total = price;

        this.price = round_di(parseFloat(total) || 0, this.pos.dp['Product Price']);
      }
      else {
        this.price = round_di(parseFloat(price) || 0, this.pos.dp['Product Price']);
      }
    }
    set_combo_price(price) {
      var prods = this.get_combo_products()
      var total = 0;
      prods.forEach(function (prod) {
        if (prod) {
          total += prod.lst_price
        }
      });
      if (self.pos.config.combo_pack_price == 'all_product') {
        this.set_unit_price(total);
      }
      else {
        let prod_price = this.product.lst_price;
        this.set_unit_price(prod_price);
      }
    }
    get_combo_products() {
      self = this;
      if (this.product.is_pack) {
        var get_sub_prods = [];
        if (this.combo_prod_ids) {
          this.combo_prod_ids.forEach(function (prod) {
            var sub_product = self.pos.db.get_product_by_id(prod);
            get_sub_prods.push(sub_product)
          });
          return get_sub_prods;
        }
        if (this.combo_products) {
          if (! null in this.combo_products) {
            return this.combo_products
          }
        }
      }
    }


  }
  Registries.Model.extend(Orderline, BiCustomOrderLine);


  const CustomOrder = (Order) => class CustomOrder extends Order {
    constructor(obj, options) {
      super(...arguments);
      this.barcode = this.barcode || "";
    }
    add_product(product, options){
        if(this.pos.doNotAllowRefundAndSales() &&
        this._isRefundAndSaleOrder() &&
        (!options.quantity || options.quantity > 0)) {
            Gui.showPopup('ErrorPopup', {
                title: _t('Refund and Sales not allowed'),
                body: _t('It is not allowed to mix refunds and sales')
            });
            return;
        }
        if(this._printed){
            // when adding product with a barcode while being in receipt screen
            this.pos.removeOrder(this);
            return this.pos.add_new_order().add_product(product, options);
        }
        this.assert_editable();
        options = options || {};
        var line = Orderline.create({}, {pos: this.pos, order: this, product: product});
        this.fix_tax_included_price(line);

        this.set_orderline_options(line, options);

        var to_merge_orderline;
        for (var i = 0; i < this.orderlines.length; i++) {
            if(this.orderlines.at(i).can_be_merged_with(line) && options.merge !== false || (this.orderlines.at(i).product.id === line.product.id && this.orderlines.at(i).employee_id ===line.employee_id)){
                debugger;
                to_merge_orderline = this.orderlines.at(i);
            }
        }
        if (to_merge_orderline){
            to_merge_orderline.merge(line);
            this.select_orderline(to_merge_orderline);
        } else {
            this.add_orderline(line);
            this.select_orderline(this.get_last_orderline());
        }

        if (options.draftPackLotLines) {
            this.selected_orderline.setPackLotLines({ ...options.draftPackLotLines, setQuantity: options.quantity === undefined });
        }
    }


  }
  Registries.Model.extend(Order, CustomOrder);
});
