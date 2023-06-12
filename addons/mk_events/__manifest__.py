# -*- coding: utf-8 -*-
{
    'name': "Events Management",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','mk_master_models','event'],

    # always loaded
    'data': [
        
        'security/mk_event_groups.xml',
        'security/menus.xml',
        'security/ir.model.access.csv',
        'security/model_rules.xml',
        'views/event_config.xml',
        'views/event_status.xml',
        'views/views.xml',
        'wizards/mail_compose_message_view.xml',
        'views/event_register.xml',
        'data/sms_template_data.xml',
        'views/company.xml',
        #'security/menu.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
