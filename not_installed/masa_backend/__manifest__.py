# -*- coding: utf-8 -*-
{
    'name': "Masa Backend",

    'description': """
        Change backend menus
    """,

    'author': "Masa",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'images': [#'static/description/theme.jpg'
               ],
    'depends': ['web','web_rtl'],

    
    'data': [ #data
             'data/data_res_lang.xml',
             #views
             'views/backend.xml'],
    'qweb': ['static/src/xml/web.xml',],
    
    'installable': True,
    'auto_install': False,
    'application': False,    
}