# -*- coding: utf-8 -*-
{
    'name': "receiver_external_apis",
    "version": "15.0.1",

    "author": "https://cityart.my/",
    "license": "AGPL-3",
    "website": "https://cityart.my/",

    #'category': 'Accounting & Finance',

    # any module necessary for this one to work correctly
    'depends': ['base','odoo-rest-api-master' ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,

}
