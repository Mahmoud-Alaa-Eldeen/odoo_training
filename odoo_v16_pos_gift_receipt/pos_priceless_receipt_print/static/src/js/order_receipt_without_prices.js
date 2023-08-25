odoo.define('point_of_sale.OrderReceipt_without_prices', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    const { onWillUpdateProps } = owl;

    class OrderReceipt_without_prices extends PosComponent {
        setup() {
            super.setup();
            this._receiptEnv = this.props.order.getOrderReceiptEnv();

            onWillUpdateProps((nextProps) => {
                this._receiptEnv = nextProps.order.getOrderReceiptEnv();
            });
        }
        get receipt() {
            return this.receiptEnv.receipt;
        }
        get orderlines() {
            return this.receiptEnv.orderlines;
        }
        get paymentlines() {
            return this.receiptEnv.paymentlines;
        }
        get isTaxIncluded() {
            return Math.abs(this.receipt.subtotal - this.receipt.total_with_tax) <= 0.000001;
        }
        get receiptEnv () {
          return this._receiptEnv;
        }
        isSimple(line) {
            return (
                line.discount === 0 &&
                line.is_in_unit &&
                line.quantity === 1 &&
                !(
                    line.display_discount_policy == 'without_discount' &&
                    line.price < line.price_lst
                )
            );
        }
    }
    OrderReceipt_without_prices.template = 'OrderReceipt_without_prices';

    Registries.Component.add(OrderReceipt_without_prices);

    return OrderReceipt_without_prices;
});
//omara 2 all file