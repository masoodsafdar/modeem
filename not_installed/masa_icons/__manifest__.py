# -*- coding: utf-8 -*-
{
    'name': "Masa Theme",

    'description': """
        Change backend icons and background
    """,

    'author': "Masa",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'masa_backend',
                'event',
                'mk_student_register',
                'mk_episode_management',
                'mk_program_management',
                'mk_master_models',
                'hr',
                'hr_recruitment',
                'contacts',
                'hr_holidays',
                'base_user_role',
                'calendar',
                'website_support',
                'mail',
                'maknon_tests',                
                'web',
                'utm',
                'mk_user_guide',
                'odoo_web_login_10',
                'mk_user_guide',
                'contests',
                'mk_virtual_room',
                ],

    # always loaded
    'data': ['views/assets.xml',
             'views/menu.xml',
             'views/templates.xml',
             'views/episode_kanban_view.xml',
             'views/episode_kanban_view2.xml',],
    
    # only loaded in demonstration mode
    'demo': [

    ],
}