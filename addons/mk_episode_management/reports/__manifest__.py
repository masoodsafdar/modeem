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
    'depends': ['mk_master_models','mk_program_management','base_user_role','hr_recruitment'],
    'data': [
        #'security/episode_master.xml',
        # 'security/mk_mosqu_groups.xml',
        # 'security/models_rules.xml',
        # 'security/ir.model.access.csv',
        'security/permisions_and_requests/perm_groups.xml',
        'security/permisions_and_requests/ir.model.access.csv',

        'security/permisions_and_requests/security_rule.xml',

        'view/mk_episode_view.xml',
        'view/add_new_period.xml',
        'view/mk_episode_master_view.xml',
        'view/manage_epsiode_main_menu.xml',
    	'view/mk_episode_validation.xml',
	'view/masjed_perm.xml',
        #'view/mk_supervisor_mosque_view.xml',

        #'workflow/mk_supervisor_workflow.xml',
        'view/mk_episode_set_program.xml',
        #'view/episode_program_archaive.xml',
        #'view/mk_supervisor_mosque_view.xml',
        'view/mk_masjed_view.xml',
       #'view/productivity.xml',
        'view/episode_type.xml',
        'view/news_event.xml',
	'view/mk_job.xml',
	'view/per_sch.xml',
        'reports/reports_menu_view.xml',
        'reports/temporary permition.xml',

        'reports/permision_reports.xml',
        'reports/rep_per_report_template.xml',

        'reports/report_permitions_template_without_background_old.xml',
        'reports/report_permitions_file.xml',
        'reports/report_permitions_template.xml',
        'reports/inherit_layout.xml',
        'reports/supervisors_report_file.xml',
        'reports/supervisors_report_template.xml',

   


    ],    
    'demo': [

    ],
    'application':True,

}
