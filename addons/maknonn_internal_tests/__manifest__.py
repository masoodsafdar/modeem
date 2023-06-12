# -*- coding: utf-8 -*-
{
    'name': "MaKnon internal Tests Modules",

    'summary': """
        This module allowed to manage internal test the Tests""",

    'description': """
        This module allowed to manage the Tests
    """,

    'author': "Masa",
    'website': "http://www.odoo.com",
    'category': 'custom',
    'version': '1.0',
    'depends': ['maknon_tests'],

    'data': ['wizerd/add_error.xml',
             'views/episode_inherited_view.xml',
             'views/internal_test_session.xml',
             #'security/ir.model.access.csv'
             ],    
    
    'installable': False,
}
