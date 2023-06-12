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
    'depends': [
        'fleet',
        'students_motivation',
        'mk_transport_management',
        'mk_intensive_courses',
        'educational_supervison',],

    # always loaded
    'data': [
        'data/data_security.xml',

        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
