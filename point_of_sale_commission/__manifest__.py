{
    'name': 'POS Commission',
    'version': '16.0.0',
    'description': '',
    'category': 'Point of Sale',
    'author': '',
    'depends': ['point_of_sale'],
    'data':[
        'security/ir.model.access.csv',
        'wizard/commission_report.xml',
        'views/commission.xml',
    ],

'assets': {
        'point_of_sale.assets': [
            'point_of_sale_commission/static/src/js/**/*.js',
        ],
    },

    'installable': True,
    'auto_install': False,
}