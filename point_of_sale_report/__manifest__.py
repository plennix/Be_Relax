{
    'name': "POS Sale Report",
    'summary': """
       POS Sale Report
    """,
    'author': 'Plennix Technologies',
    'website': "https://www.plennix.com/",
    'category': 'pos',
    'version': '16.0',

    'depends': [
        'point_of_sale',
    ],
    'data': [
        "security/ir.model.access.csv",
        "wizard/view_sales_pos_report.xml",

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
