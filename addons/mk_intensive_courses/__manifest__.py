# -*- coding: utf-8 -*-
{
    'name': "MK Intensive Courses",

    'summary': """
        This module allowed to manage the Intensive Course""",

    'description': """
        This module allowed to manage Intensive Course
    """,

    'author': "Masa",
    'category': 'custom',
    'version': '1.0',
    'depends': ['base','mk_master_models','mk_episode_management','hr','mk_student_register', 'report_xlsx'],
    'data': [
        
        'security/mk_course_groups.xml',
        'views/sequence.xml',
        'views/main_menu.xml',
        'wizard/message_wizard_view.xml',
        'wizard/close_course_data_wizard.xml',
        'wizard/update_course_request_data_view.xml',
        'wizard/student_course_subscription_wizard_view.xml',
        'views/mk_branch_courses_view.xml',
        'views/mk_types_courses_view.xml',
        'views/mk_courses_items_view.xml',
        'views/mk_courses_evaluation_view.xml',
        'views/mk_courses_request_view.xml',
        'views/mk_courses_evaluation_view.xml',
        'views/mk_courses_request_view.xml',
        'views/course_calibration.xml',
        'views/mk_certification_view.xml',
        'views/mk_certification_view.xml',
        'views/mk_episode_view.xml',
        'security/ir.model.access.csv',
        'security/courses_rule.xml',
        'data/mail_send_course_request_template.xml',
        'data/data_mk_parts_names.xml',
        #'report/certification_report.xml',
        #'report/report_certificationtemp.xml',
        'report/requist_report_file.xml',
        'report/requist_report_template.xml',
        'report/summer_episode_report.xml',
        'report/close_certificate_report.xml',
        'report/close_certificate_template.xml',
        'report/close_quran_day_certificate_report.xml',
        'report/close_quran_day_certificate_template.xml',


          ],  

 
    
    'installable':True,
	'auto_install':False,
	'application':True,
}
