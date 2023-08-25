{
    'name': 'ebs_pos_extended',
    'version': '1.0.0',
    'author': "Plennix Technology",
    'website': "http://ever-bs.com",
    'description': """

    """,
    'depends': ['point_of_sale',],
    'data': [
    ],
    'assets': {
        'point_of_sale.assets': [
            'ebs_pos_extended/static/src/libs/jquery-barcode-last.min.js',
            'ebs_pos_extended/static/src/js/GiftReceipt.js',
            'ebs_pos_extended/static/src/js/ReceiptScreen.js',
        ],
        'web.assets_qweb': [
            'ebs_pos_extended/static/src/xml/GiftReceipt.xml',
            'ebs_pos_extended/static/src/xml/ReceiptScreen.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}
