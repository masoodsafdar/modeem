# -*- coding: utf-8 -*-
{
    'name': "MK Tests Modules",

    'summary': """
        This module allowed to manage the Tests""",

    'description': """
        This module allowed to manage the Tests
    """,

    'author': "Masa",
    'website': "http://www.odoo.com",
    'category': 'custom',
    'version': '1.0',
    'depends': ['mk_master_models',
		'mk_student_register'],
    'data': [
    	'views/mk_main_menus.xml',
        'views/mk_branches_view.xml',
        'views/mk_passage_reward_view.xml',
        'views/mk_test_type_view.xml',
        'views/mk_test_appreciation_view.xml',
        'views/mk_test_center_view.xml',
        'views/mk_test_center_config_view.xml',
        'views/mk_test_class_view.xml',
        'views/mk_test_class_questions_configuration_view.xml',
        'views/mk_test_class_committee_view.xml',
        'views/mk_test_error_view.xml',
        'views/mk_test_deduct_view.xml',
        'views/mk_test_internal_registerations_view.xml',
        'views/mk_test_student_preparation_view.xml',
        'data/errors_data.xml'
    ],    
    'demo': [
        #'demo.xml',
    ],
}
