# -*- coding: utf-8 -*-
{
    'name': "zk Attendance Module",

    'summary': """
        Integration module for zk attendance machines
        """,

    'description': """
        Make sure the following python packages are installed:
        xmltodict
        pytz
        python-dateutil
        
        A text file for processing attendance logs should be placed in the following path:
        /opt/odoo/pharos/custom/zkLogs.txt
    """,

    'author': "",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_attendance'],

    # always loaded
    'data': [
        'views/views.xml',
        'security/ir.model.access.csv',
    ],
    
}