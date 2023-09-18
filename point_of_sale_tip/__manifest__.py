{
    'name': 'POS TIP',
    'version': '16.0.0',
    'description': '',
    'category': 'Point of Sale',
    'author': '',
    'depends': ['point_of_sale'],
    'data':[
        # 'security/ir.model.access.csv',
        'views/cashier_tip.xml',
        'views/tips.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'point_of_sale_tip/static/src/js/**/*.js',
            'point_of_sale_tip/static/src/xml/**/*.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
}