{
    'name': 'POS VOID ORDER',
    'version': '16.0.0',
    'description': '',
    'category': 'Point of Sale',
    'author': '',
    'depends': ['point_of_sale', 'point_of_sale_tip'],
    'data':[
        'views/pos_order_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'point_of_sale_void_order/static/src/js/**/*.js',
            'point_of_sale_void_order/static/src/xml/**/*.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
}