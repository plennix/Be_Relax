# Copyright (C) 2021-2023 Artem Shurshilov <shurshilov.a@yandex.ru>
# License OPL-1.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR break and resume attendances",
    "summary": "Module provide to break and resume attendances",
    "description": """
        Module provide to break and resume attendances breaks attendance break attendance breaks
        attendances break breaks attendances hr break hr breaks hr odoo breaks odoo break
        attendances dinner attendance dinner attendance
        attendances timeout attendance timeout attendance timeouts
        attendances interval attendance interval attendance intervals
        hr attendance pause attendances pause
    """,
    "author": "EURO ODOO, Shurshilov Artem",
    "maintainer": "EURO ODOO",
    "website": "https://eurodoo.com",
    "live_test_url": "https://eurodoo.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Human Resources",
    "version": "16.1.0.5",
    "license": "OPL-1",
    "price": 31,
    "currency": "EUR",
    "images": [
        "static/description/preview.png",
    ],
    "depends": ["hr_attendance", "hr_attendance_base","point_of_sale_ext"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_attendance_view.xml",
        "views/hr_employee_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "hr_attendance_break/static/src/js/my_attendances.js",
            "hr_attendance_break/static/src/js/greeting_message.js",
            "hr_attendance_break/static/src/js/kiosk_confirm.js",
            "hr_attendance_break/static/src/js/kiosk_mode.js",
            "hr_attendance_break/static/src/xml/attendance.xml",
        ],
        # "web.assets_qweb": [
        # ],
    },
    "installable": True,
    "application": True,
}
