
{
    'name': 'POS Commission',
    'version': '16.0.1',
    'description': '',
    'category': 'Point of Sale',
    'author': '',
    'depends': ['pos_hr', 'pos_loyalty','point_of_sale'],
    'data': [
        'report/sale_report.xml',
        'views/pos_order.xml',
        'views/pos_config.xml',
        'views/hr_employee_views.xml',
    ],

    'assets': {
            'point_of_sale.assets': [
                'point_of_sale_ext/static/src/js/close_session_button.js',
                'point_of_sale_ext/static/src/js/SelectionPopup.js',
                'point_of_sale_ext/static/src/js/TipsButton.js',
                'point_of_sale_ext/static/src/js/PromoCodePopups.js',
                'point_of_sale_ext/static/src/js/PosLoyaltyExt.js',
                'point_of_sale_ext/static/src/js/SelectCashierMixin.js',
                'point_of_sale_ext/static/src/js/PaymentScreen.js',
                'point_of_sale_ext/static/src/js/NumpadWidget.js',
                'point_of_sale_ext/static/src/js/SummaryReport.js',
                'point_of_sale_ext/static/src/xml/SelectionPopup.xml',
                'point_of_sale_ext/static/src/xml/PosOrder.xml',
                'point_of_sale_ext/static/src/xml/PromoCodePopups.xml',
                'point_of_sale_ext/static/src/xml/TipsButton.xml',
                'point_of_sale_ext/static/src/xml/SummaryReport.xml',
                'point_of_sale_ext/static/src/xml/NumpadWidget.xml',
                'point_of_sale_ext/static/src/xml/chrome.xml',
            ],
        },

    'installable': True,
    'auto_install': False,
}
