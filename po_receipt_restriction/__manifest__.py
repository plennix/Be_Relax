{
    'name': 'Purchase Order Receipt Creation Restriction',
    'version': '16.0.0.1',
    'summary': 'Purchase Order Receipt Creation Restriction',
    'description': 'On confirming purchase order, a receipt will be created only if create_receipt boolean is checked',
    'category': '',
    'author': "Plennix Technologies",
    'website': "https://www.plennix.com",
    'license': '',
    'depends': ['purchase_stock'],
    'data': [
        'views/purchase_order.xml',
    ],
    'assets': {

    },
    'installable': True,
    'auto_install': False,
}
