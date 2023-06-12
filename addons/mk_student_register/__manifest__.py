{
	'version': '1.0',
	'name': 'Maknoon Student Registery',
	'category': 'student register',
	'description': """avilable to students rigister""",
	'author' : 'MASA',

	'depends': ['base',
				'account',
				'mk_master_models',
				# 'general_sending',
				'mk_episode_management',
				'mk_program_management',
				# 'mk_master_programs_Integration',
				],

	'data':['data/mk_job_data.xml',
			'data/portal_user.xml',

		    'security/mk_student_registration_group.xml',
	        'security/mk_student_registration_group_suite.xml',
			'security/sms_groups.xml',
			'security/sms_access_rights/ir.model.access.csv',
            'security/mk_student_registration_group_rules.xml',
        	'security/ir.model.access.csv',

			#'views/mk_student_register_view.xml',
			#'views/search_episodes.xml',
			#'views/search_episodes.xml',

        	'views/student_sms.xml',
        	'views/gateway_config.xml',
			'views/employee_sms.xml',
			'views/search_for_episode.xml',

			'views/mk_parent_profile.xml',

			#'views/top_five_.xml',

			'views/sequences.xml',
			'views/mk_episode_inherited_view.xml',
			'views/mk_student_profile.xml',
			'views/wizard.xml',
			'wizards/student_episode_link.xml',
			'wizards/student_report_wizard_view.xml',
			'wizards/import_student_wizard.xml',
			'data/get_top.xml',
			'data/mk_job_data.xml',

			#'wizards/student_send_sms.xml',
			#'mk.student.register.csv',
			'data/general_sending_data.xml',
			#'data/mk_master_data.xml',
			#'data/general_sending_data.xml'

            'reports/reports.xml',
            'reports/report_students_template.xml',
            
            'views/mk_masjed_view.xml',
            'views/gateway_config_view.xml',
	],


	'installable':True,
	'auto_install':False,
	'application':True,

}
