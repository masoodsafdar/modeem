# -*- coding: utf-8 -*-
{
    'name': "Student Motivation",

    'summary': """
        This module Manage Student motivation process""",

    'author': "Masa",
    'website': "http://www.masa.technology",
    'category': 'custom',
    'version': '1.0',
    'depends': ['base', 'mk_student_managment', 'sale', 'product','mk_student_register','report_xlsx'],
    'data': [
        ##security
        'security/students_motivation_groups.xml',
        'security/ir.model.access.csv',

        #views
        'views/motivation_configuration_view.xml',
        'views/custom_product_view.xml',
        'views/custom_sale_order.xml',
        'views/add_markdown_points_view.xml',

        ##wizard
        'wizard/order_sale_wizard_view.xml',

        ##reports
        'reports/reports.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
