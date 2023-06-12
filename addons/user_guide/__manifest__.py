# -*- coding: utf-8 -*-
{
    'name': "User Guide",

    'summary': """
    """,

    'description': """
    """,

    'author': "Maknoon Team",
    'website': "https://qk.org.sa",
    'maintainer': 'Maknoon',
    'category': 'Tools',
    'version': '1.0',
    'support': 'support@qk.org.sa',
    'depends': ['base', 'base_setup','hr'],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/user_guide_view.xml',
        'views/category_view.xml',
    ],
    'demo' : [
    ],
    "installable": True,
}
