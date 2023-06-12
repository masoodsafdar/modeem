# -*- coding: utf-8 -*-
{
    'name': "MK Master Programs Integration",

    'summary': """
        This module allowed to Integrate the Master with Programs """,

    'description': """
        This module allowed to manage the Master
    """,

    'author': "Masa",
    'website': "http://www.odoo.com",
    'category': 'custom',
    'version': '1.0',
    'depends': ['base','mk_master_models','mk_program_management','mk_episode_management'],
    'data': ['security/ir.model.access.csv',        
             'views/mk_master_programs_integration_view.xml',
    ],    

    'installable':True,
	'auto_install':False,
	'application':True,
}
