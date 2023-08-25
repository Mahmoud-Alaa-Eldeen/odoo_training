# -*- coding: utf-8 -*-
{
    'name': "set therapists on pos orderlines",
    "version": "16.0.1",

    "author": "https://cityart.my/",
    "license": "AGPL-3",
    "website": "https://cityart.my/",

    # 'category': 'Accounting & Finance',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale','hr' ],

    # always loaded
    'data': [
        'views/pos_order_inherit.xml',
    ],

    'assets': {
        'point_of_sale.assets': [
            'set_therapists_on_pos_orderlines/static/src/js/*.js',
            'set_therapists_on_pos_orderlines/static/src/xml/*.xml',
        ]
    },

    'installable': True,
    'application': True,
    'auto_install': False,

}
