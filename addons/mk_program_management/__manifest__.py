# -*- coding: utf-8 -*-
{
    'name': "MK Programs Modules",

    'summary': """
        This module allowed to manage the Programs""",

    'description': """
        This module allowed to manage the Programs
    """,

    'author': "Masa",
    'website': "http://www.odoo.com",
    'category': 'custom',
    'version': '1.0',
    'depends': ['mk_master_models','hr_recruitment'],
    'data': [
        'security/mk_program_management.xml',
        # 'security/ir.model.access.csv',
    	'views/mk_main_menus.xml',
    	# 'views/mk_plan_view.xml',
    	# 'views/mk_plan_share_view.xml',
    	#'views/mk_program_view.xml',
    	# 'views/mk_punishment_view.xml',
    	# 'views/mk_comment_behavior_view.xml',
    	# 'views/mk_programs_view.xml',
    	# 'views/mk_approaches_view.xml',
    	# 'views/mk_subject_process_view.xml',
    	# 'views/mk_subject_configuration_view.xml',

        'security/model_rules.xml',


    ],    
}
