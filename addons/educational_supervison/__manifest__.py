# -*- coding: utf-8 -*-
{
    'name': "educational supervision",

    'summary': """ 
        educational supervision
       """,

    'description': """
        educational supervision
    """,

    'author': "Masa",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','hr','mk_master_models','mk_episode_management'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/group_rules.xml',
        #'wizerd/center_distribuation.xml',
        #'wizerd/supervisors_distribuation.xml',
        'views/settings_view.xml',
        'views/distribuation_menu.xml',
#         'data/edu_data.xml',
        'data/edu_criterion_data.xml',
        'data/edu_criterion_item_data.xml'
        #'security/ir.model.access.csv',
        #'security/edu_supervisor_rule.xml'
        #'views/templates.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
