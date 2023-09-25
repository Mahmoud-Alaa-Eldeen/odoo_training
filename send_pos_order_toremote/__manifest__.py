# -*- coding: utf-8 -*-
{
    'name': "send_pos_order_toremote",

    'summary': """
        Once POS order is paid, sending it to remote API""",

    'description': """
        
    """,

    'author': "",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point of Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale'],

    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}