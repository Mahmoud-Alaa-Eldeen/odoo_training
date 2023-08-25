odoo.define('ebs_pos_extended.ReceiptScreen', function(require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');
    const { Printer } = require('point_of_sale.Printer');
    const { whenReady } = owl.utils;
    const PosResReceiptScreen = ReceiptScreen =>
        class extends ReceiptScreen {
               mounted() {
                  super.mounted()
                    const order = this.currentOrder;
                    const orderName = order.get_name();
                    JsBarcode("#barcode", orderName, {
                            format: "code128",
                            displayValue: true,
                            fontSize: 20
                      });
               }
               async printGiftReceipt(){
                   var html = $('.gift-receipt-container').html()
                   var newWin=window.open('');
                   newWin.document.open();
                   newWin.document.write(html);
                   newWin.print();
                   newWin.document.close();
                   setTimeout(function(){newWin.close();},200);
               }
        };

    Registries.Component.extend(ReceiptScreen, PosResReceiptScreen);

    return ReceiptScreen;

});
