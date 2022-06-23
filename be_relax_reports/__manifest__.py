{
    'name': 'Be Relax- Invoice Report',
    'version': '2.0',
    'category': 'Hidden',
    'summary': 'Invoice report',
    'depends': ['purchase','account'],
    'data': [
        # 'security/ir.models.access.csv',
        'report/invoice_report_inherit.xml',
        'report/report.xml',
        'report/purchase_order_inherit.xml',

        'views/inherit_field.xml',
        'views/inherit_res_company_view.xml'
    ],
    'installable': True,
    'auto_install': False,

    'license': 'LGPL-3',
}
