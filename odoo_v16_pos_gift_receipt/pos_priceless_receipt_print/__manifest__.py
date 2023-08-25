# -*- coding: utf-8 -*-
#
# Idea:
# in receipt screen: add a gift checkbox,handle onclick
# if clicked, show another template without prices,
# if unchecked, show original order receipt template
#
# hint:used rerendering the receipt screen onclick of gift checkbox
#
{
    'name': 'POS Gift Receipt Without Prices',
    'version': '16.0.1',
    'summary': """""",
    'description': """""",
    'category': 'Point Of Sale',
    'author': 'Mahmoud ALaa',
    'company': 'Plennix Technologies',
    'website': "www.plennix.com",
    'depends': ['base', 'point_of_sale'],
    'data': [
    ],
    'assets': {
            'point_of_sale.assets': [
                'pos_priceless_receipt_print/static/src/xml/order_receipt_without_prices.xml',
                'pos_priceless_receipt_print/static/src/xml/receipt_screen_inherit.xml',
                'pos_priceless_receipt_print/static/src/js/receipt_screen_inherit.js',
                'pos_priceless_receipt_print/static/src/js/order_receipt_without_prices.js',
            ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,

}

