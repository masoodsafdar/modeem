# -*- coding: utf-8 -*-
{
    'name': "MK Notification",

    'summary': """ 
        This module allowed to manage notification """,

    'description': """

    """,

    'author': "Masa",
    'website': "http://www.odoo.com",
    'category': 'custom',
    'version': '1.0',
    'depends': ['hr'],
    'data': [
        ##security
        'security/mk_notifications_groups.xml',
        'security/ir.model.access.csv',
        ##data

        ## views
        'views/mk_notification_view.xml',
        'views/mk_employee_notification_view.xml',
        'views/news.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': False,
    'auto_install': False,

}
