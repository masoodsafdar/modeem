# -*- coding: utf-8 -*-
{
    'name': "MK Master Modules",

    'summary': """
        This module allowed to manage the Master""",

    'description': """
        This module allowed to manage the Master
    """,

    'author': "Zuhaib Hassan (Ecube)",
    'website': "http://www.odoo.com",
    'category': 'custom',
    'version': '1.0',
    # 'depends': ['base','hr','hr_holidays','hr_recruitment'],
    'depends': ['base','hr','hr_holidays','general_sending','hr_recruitment'],
    'data': [
            'security/mk_master_security.xml',
             'security/ir.model.access.csv',
             'security/models_rules.xml',

             'data/sequence.xml',
             'data/hr_department_category_data.xml',
             # 'data/email_employee_register.xml',

             # 'wizerd/mosque_emp_add.xml',
             'wizerd/change_job.xml',
             'wizerd/mosq_reject_cause_view.xml',
             # 'wizerd/import_mosque_wizard.xml',

    	     # 'views/mk_main_menus.xml',
             # 'views/mk_surah_view.xml',
             # 'views/mk_parts.xml',
             # 'views/mk_approach_view.xml', (some of these are depends on mk_associate_management_settings_menu)
             'views/mk_level_view.xml',             
             # 'views/mk_episode_type.xml',
	         # 'views/mk_episode_works.xml',
             'views/mk_center_view.xml',
	         # 'views/mk_contral_condition_view.xml',
             # 'views/mk_study_year_view.xml',
             # 'views/mk_study_class_view.xml',
             # 'views/mk_periods_view.xml',
             'views/mk_hr_department_view.xml',
             # 'views/mk_formal_leave_view.xml',
             # 'views/mk_urgent_leave_view.xml',
	         'views/mk_city_area_district.xml',
             'views/mk_job.xml',
             'views/mk_country.xml',
             'views/mk_grade.xml',
             # 'views/mk_masajed_category.xml',
             # 'views/mk_episode_works.xml',
             # 'views/mk_sms_template.xml',
             # 'views/mk_work_days.xml',
	         # 'views/mk_memorize_method_view.xml',
             # 'views/mk_subject_page_view.xml',
             # 'views/mosque_categ_administrative.xml',

             # 'data/grade_undefined_data.xml',
             
             'data/notify_supervisor_cron.xml',
	         # 'views/mk_specializations_view.xml',
	         'views/mk_age_category_view.xml',
             # 'views/hr_employee2.xml',
             # 'views/hr_employee.xml',
             # 'views/public_job.xml',
             # 'views/building_type.xml',
             'reports/reports_menu_view.xml',
             'reports/renew_assigne_supervisor_report.xml',
             'reports/renew_episode_openning_permition.xml',
             'user.xml',
             # 'reports/general_report_config.xml'
             ],  

    'qweb': ['web.xml'],  
    
    'installable':True,
	'auto_install':True,
	'application':True,
}
