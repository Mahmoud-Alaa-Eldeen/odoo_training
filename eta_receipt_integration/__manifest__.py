# -*- coding: utf-8 -*-
{
    'name': "eta_receipt_integration",

    'summary': """""",

    'description': """
    
    """,

    'author': "",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','e_receipt_integration','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_inherit.xml',
        'views/account_journal_inherit.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}