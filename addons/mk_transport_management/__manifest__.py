# -*- coding: utf-8 -*-
{
    'name': "MK Transport Management",

    'summary': """
        This module allowed to Transport Management""",

    'description': """
        This module allowed to Transport Management
    """,

    'author': "Masa",
    'website': "http://www.odoo.com",
    'category': 'custom_transport',
    'version': '1.0',
    'depends': ['fleet', 'account_asset', 'mk_student_register', 'web_rtl',],
    
    'data': [
        'security/mk_transport_management_groups.xml',
        'security/mk_model_rules.xml',
        'data/accept_email.xml',
        'data/biding_email.xml',
        'security/csv/ir.model.access.csv',
        #'security/transport_rules.xml',
        'views/mk_main_menus.xml',
        'views/mk_transport_management_view.xml',
        'views/drivers_records_view.xml',
        'views/vehicle_types_view.xml',
        'views/vehicle_records_view.xml',
        'views/transportation_request_view.xml',
        'views/apology_request_view.xml',
        'views/mk_attendance_students_view.xml',
        #'views/vehicle_management.xml',
        'views/vehicle_assets.xml',
        'security/menus.xml',
        #'security/gateway/ir.model.access.csv'

    ],    
}
