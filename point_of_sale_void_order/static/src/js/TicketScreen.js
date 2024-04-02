odoo.define('point_of_sale_void_order.TicketScreen', function(require){
    'use strict';

    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');

    const TicketScreenVoidOrder = (TicketScreen) => class extends TicketScreen {
         async _voidOrder(){
            const orderToRefund = this.getSelectedSyncedOrder()
            if (orderToRefund && orderToRefund.orderlines && orderToRefund.orderlines[0]){
                 const orderline = orderToRefund.orderlines[0]
                 if(orderline){
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: "Void Order",
                        body: this.env._t('Do you want to void the order completely?'),
                    });
                     debugger;
                    if (confirmed) {
                          await this.rpc({
                               model: 'pos.order.line',
                               method: 'call_void_order',
                               args: [[orderline.id]],
                           })
                          this.showNotification(
                            _.str.sprintf(this.env._t('Your void order has been created!.')),
                            3000
                        );
                     }
                 }
            }
         }
    }

    Registries.Component.extend(TicketScreen, TicketScreenVoidOrder);

    return TicketScreen;
})