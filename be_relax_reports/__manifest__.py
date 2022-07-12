{
    'name': 'Be Relax- Invoice Report',
    'version': '2.0',
    'category': 'Hidden',
    'summary': 'Invoice report',
    'depends': ['sale', 'purchase', 'account', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'data/purchase_mail_template.xml',
        'data/sale_invoice_mail_template.xml',
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
