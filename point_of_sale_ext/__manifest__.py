{
    'name': 'POS Commission',
    'version': '16.0.1',
    'description': '',
    'category': 'Point of Sale',
    'author': '',
    'depends': ['pos_hr', 'pos_loyalty'],
    'data': [
        'views/pos_order.xml',
    ],

    'assets': {
            'point_of_sale.assets': [
                'point_of_sale_ext/static/src/js/SelectionPopup.js',
                'point_of_sale_ext/static/src/js/TipsButton.js',
                'point_of_sale_ext/static/src/js/PromoCodePopups.js',
                'point_of_sale_ext/static/src/js/PosLoyaltyExt.js',
                'point_of_sale_ext/static/src/xml/SelectionPopup.xml',
                'point_of_sale_ext/static/src/xml/PosOrder.xml',
                'point_of_sale_ext/static/src/xml/PromoCodePopups.xml',
                'point_of_sale_ext/static/src/xml/TipsButton.xml',
            ],
        },

    'installable': True,
    'auto_install': False,
}
