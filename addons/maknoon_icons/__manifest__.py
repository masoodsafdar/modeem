# -*- coding: utf-8 -*-
{
    'name': "Maknoon_icons",

    'description': """
        Change backend icons and background
    """,

    'author': "Maknoon",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'web',
                'mk_student_register',
                'mk_episode_management',
                'mk_program_management',
                'website_support',
                'mk_master_models',
                'contacts',
                'mk_intensive_courses',
                'calendar',
                'maknon_tests',
                'mail',
                'contests',
                'user_guide',
                'mk_transport_management',
                'educational_supervison',
                'students_motivation',
                'utm',
                'mk_virtual_room',
                'event',
                'hr',
                'hr_recruitment',
                'hr_holidays',
                'fleet',
                'base_user_role',
                'mk_notification',
                ],

    # always loaded
    'data': ['views/assets.xml',
             'views/menu.xml',
             'views/template_mail.xml',
             'views/favicon_debranding.xml',
             ],

    'qweb': [
        'static/src/xml/mail_chat.xml',
    ],

    # only loaded in demonstration mode
    'demo': [

    ],
}
