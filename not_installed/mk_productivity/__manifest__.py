# -*- coding: utf-8 -*-
{
    'name': "MK Productivity",

    'summary': """ 
        This module allowed to manage productivity """,

    'description': """

    """,

    'author': "Masa",
    'website': "http://www.odoo.com",
    'category': 'custom',
    'version': '1.0',
    'depends': ['mk_master_models','mk_tests','mk_episode_management'],
    'data': [
        ##security
        'security/mk_productivity_groups.xml',
        'security/ir.model.access.csv',

        ##data
        'data/incentive_data.xml',
        'data/episode_type_data.xml',
        'data/productivity_incentive_data.xml',

        ## views
        'views/productivity_menues.xml',
        'views/mk_productivity_incentive.xml',
        'views/mk_incentive.xml',
        'views/mk_productivity.xml',
        'views/mk_episode_type.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': False,
    'auto_install': False,

}
