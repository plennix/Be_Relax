{
    'name': 'Pos Customer Form',
    'version': '16.0.0',
    'author': 'Plennix Technologies',
    'website': "https://www.plennix.com/",
    'summary': ' Changes in POS customer creation form ',
    'depends': ['point_of_sale', 'base', 'contacts'],
    'data': [
        'views/res_partner.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_customer_form/static/src/xml/**/*',
            'pos_customer_form/static/src/js/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
}
