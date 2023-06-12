# -*- coding: utf-8 -*-
{
    'name': "MK episode Management Module",

    'summary': """ 
        This module allowed to manage episode """,

    'description': """

    """,

    'author': "Masa",
    'website': "http://www.odoo.com",
    'category': 'custom',
    'version': '1.0',
    'depends': ['mk_master_models','mk_program_management','base_user_role','hr_recruitment','hr'],
    'data': [
        'data/mk_age_category_data.xml',
        # 'data/mk_grade_data.xml',
        # 'data/mk_grade_data_2.xml',
        # 'data/mk_episode_type_data.xml',
        # 'data/mk_episode_works_data.xml',        
        'data/auto_renouwell_mosque_supervisor_request_cron.xml',
        'data/report_tmplts.xml',
        'data/notify_supervisor_cron.xml',
        # 'data/mail_templates.xml',

        'security/episode_master.xml',
        'security/mk_mosqu_groups.xml',
        'security/episode_groups_suite.xml',
        'security/models_rules.xml',
        # 'security/ir.model.access.csv',
        'security/permisions_and_requests/perm_groups.xml',
        'security/permisions_and_requests/perm_groups_suite.xml',
        'security/permisions_and_requests/ir.model.access.csv',
        'security/permisions_and_requests/security_rule.xml',

        'view/mk_episode_view.xml',
        'view/add_new_period.xml',
        # 'view/mk_episode_master_view.xml',
        # 'view/manage_epsiode_main_menu.xml',
    	# 'view/mk_episode_validation.xml',
	    'view/masjed_perm.xml',
        #'view/mk_supervisor_mosque_view.xml',
        #'workflow/mk_supervisor_workflow.xml',
        # 'view/mk_episode_set_program.xml',
        # 'view/episode_program_archaive.xml',
        # 'view/mk_supervisor_mosque_view.xml',
        'view/mk_masjed_view.xml',
        # 'view/reports_setting_view.xml',
        #'view/productivity.xml',
        # 'view/episode_type.xml',
        # 'view/mk_approaches.xml',
        # 'view/news_event.xml',
	    'view/mk_job.xml',
	    # 'view/hr_user_view.xml',
	    'view/per_sch.xml',
	    'wizard/add_episode_view.xml',
	    'wizard/confirmation_request.xml',
	    'wizard/update_episode_period.xml',
        # 'reports/report_permitions_template_without_background.xml',
        # 'reports/temporary permition.xml',
        # 'reports/permision_reports.xml',
        # 'reports/rep_per_report_template.xml',
        # 'reports/report_permitions_file.xml',
        # 'reports/report_permitions_template.xml',
        # 'reports/reports_menu_view.xml',
        # 'reports/report_status_statement.xml',
        # 'reports/mosque_permission_requests_report.xml',
        'view/sequences.xml',
    ],    
    'demo': [

    ],
    'application':True,

}
