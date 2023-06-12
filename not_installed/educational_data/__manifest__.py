# -*- coding: utf-8 -*-
{
    'name': "Educational Data",

    'summary': """ 
        This module allowed to add model's Data""",

    'description': """

    """,

    'author': "Masa",
    'website': "http:/www.odoo.com",
    'category': 'custom',
    'version': '1.0',
    'depends': ['mk_master_models', 
                'mk_student_managment',
                'mk_program_management',
                'maknon_tests',
                'hr','hr_holidays','hr_recruitment','website_support',
                'mk_virtual_room',
                'mk_events',
                'base_user_role',
                ],
    'data': [
        ##security
        'security/security_add_groups_for_user_root.xml',

        ##data
        'data/Settings/data_01_student_settings/data_01_student_behavior.xml',

        'data/Settings/data_02_location_settings/data_01_mk_area.xml',
        'data/Settings/data_02_location_settings/data_02_mk_city.xml',
        'data/Settings/data_02_location_settings/data_03_mk_hr_department.xml',
        'data/Settings/data_02_location_settings/data_04_mk_district.xml',
        'data/Settings/data_02_location_settings/data_05_mk_hr_department_distict.xml',
        'data/Settings/data_02_location_settings/data_06_res_company.xml',

        'data/Settings/data_03_episode_settings/data_01_mk_work_days.xml',

        'data/Settings/data_04_program_settings/data_01_mk_surah.xml',
        'data/Settings/data_04_program_settings/data_02_mk_parts.xml',
        'data/Settings/data_04_program_settings/data_03_mk_surah_verses.xml',
        'data/Settings/data_04_program_settings/data_04_mk_jobs.xml',
        'data/Settings/data_04_program_settings/data_05_mk_specializations.xml',

        #'data/Settings/data_05_tests_settings/data_01_mk_tests_center.xml',
        #'data/Settings/data_05_tests_settings/data_02_mk_test_type.xml',
        'data/Settings/data_05_tests_settings/data_03_mk_test_error.xml',

        'data/Settings/data_06_associate_settings/data_01_mk_mosque_category.xml',
        'data/Settings/data_06_associate_settings/data_02_mk_study_year.xml',
        'data/Settings/data_06_associate_settings/data_03_mk_study_class.xml',
        'data/Settings/data_06_associate_settings/data_04_mk_periods.xml',
        'data/Settings/data_06_associate_settings/data_05_mk_job.xml',
        'data/Settings/data_06_associate_settings/data_06_mk_building_type.xml',
        'data/Settings/data_06_associate_settings/data_07_mk_memorize_method.xml',

        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_up_1.xml',
        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_up_2.xml',
        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_up_3.xml',
        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_up_4.xml',
        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_up_5.xml',
        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_up_6.xml',
        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_up_7.xml',
        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_up_8.xml',
        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_up_9.xml',

        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_down_1.xml',
        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_down_2.xml',
        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_down_3.xml',
        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_down_4.xml',
        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_down_5.xml',
        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_down_6.xml',
        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_down_7.xml',
        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_down_8.xml',
        'data/Settings/data_06_associate_settings/data_08_mk_subject_page_down_9.xml',

        'data/Settings/data_06_associate_settings/data_09_mk_contral_condition.xml',
        'data/Settings/data_06_associate_settings/data_10_mk_contral_condition_details.xml',
        'data/Settings/data_06_associate_settings/data_11_mk_formal_leave.xml',

        'data/Settings/data_07_sms_settings/data_01_mk_sms_template.xml',

        'data/Settings/data_08_website_support_settings/data_01_mk_website_support_ticket_subcateg.xml',

        'data/Settings/data_09_report_settings/data_01_mk_report_config.xml',

        'data/Demo/demo_01_departements_employee/data_01_hr_employee.xml',
        'data/Demo/demo_01_departements_employee/data_02_mk_hr_department_manager.xml',

        'data/Demo/demo_02_mosque/data_01_mk_mosque.xml',
        'data/Demo/demo_02_mosque/data_02_mk_hr_employee_mosque.xml',
        'data/Demo/demo_02_mosque/data_03_mk_mosque_eval.xml',
        'data/Demo/demo_02_mosque/data_03_mk_mosque_eval_line.xml',
        'data/Demo/demo_02_mosque/data_04_mk_mosque_supervisor_request.xml',
        'data/Demo/demo_02_mosque/data_05_mk_mosque_permission.xml',

        'data/Demo/demo_03_mk_programs_approaches/data_01_mk_programs.xml',
        'data/Demo/demo_03_mk_programs_approaches/data_02_mk_approaches.xml',
        'data/Demo/demo_03_mk_programs_approaches/data_03_mk_manual_plan.xml',

        'data/Demo/demo_04_virtual_room/data_01_mk_virtual_room_type.xml',
        'data/Demo/demo_04_virtual_room/data_02_mk_virtual_room_provider.xml',
        'data/Demo/demo_04_virtual_room/data_03_mk_virtual_room_provider_package.xml',
        'data/Demo/demo_04_virtual_room/data_04_res_bank.xml',
        'data/Demo/demo_04_virtual_room/data_05_mk_virtual_room_subscription.xml',
        'data/Demo/demo_04_virtual_room/data_06_mk_virtual_room.xml',

        'data/Demo/demo_05_mk_episode/data_01_mk_episode_master.xml',
        'data/Demo/demo_05_mk_episode/data_02_mk_episode.xml',
        'data/Demo/demo_05_mk_episode/data_02_mk_episode_many2many_fields.xml',
        'data/Demo/demo_05_mk_episode/data_03_mk_episode_season.xml',
        'data/Demo/demo_05_mk_episode/data_04_mk_news.xml',
        'data/Demo/demo_05_mk_episode/data_05_schedule_test.xml',

        'data/Demo/demo_06_mk_students_management/data_01_mk_parent.xml',
        'data/Demo/demo_06_mk_students_management/data_02_mk_student_register.xml',
        'data/Demo/demo_06_mk_students_management/data_03_mk_student_mosque.xml',
        'data/Demo/demo_06_mk_students_management/data_04_mk_link.xml',
        'data/Demo/demo_06_mk_students_management/data_05_mk_student_prepare.xml',
        'data/Demo/demo_06_mk_students_management/data_06_mk_link_prepare.xml',
        'data/Demo/demo_06_mk_students_management/data_07_mk_student_prepare_history.xml',
        'data/Demo/demo_06_mk_students_management/data_08_mk_student_prepare_behavior.xml',
        'data/Demo/demo_06_mk_students_management/data_09_mk_listen_line.xml',
        'data/Demo/demo_06_mk_students_management/data_10_student_absence.xml',

        'data/Demo/demo_07_test_management/data_01_mk_test_names.xml',
        'data/Demo/demo_07_test_management/data_02_mk_branches_master.xml',
        'data/Demo/demo_07_test_management/data_03_mk_passing_items.xml',
        'data/Demo/demo_07_test_management/data_04_mk_reward_items.xml',
        'data/Demo/demo_07_test_management/data_05_mk_evaluation_items.xml',
        'data/Demo/demo_07_test_management/data_06_mk_discount_item.xml',
        'data/Demo/demo_07_test_management/data_07_test_period.xml',
        'data/Demo/demo_07_test_management/data_08_employee_items.xml',
        'data/Demo/demo_07_test_management/data_09_mak_test_center.xml',
        'data/Demo/demo_07_test_management/data_10_mk_test_center_prepration.xml',
        'data/Demo/demo_07_test_management/data_11_committee_tests.xml',
        'data/Demo/demo_07_test_management/data_12_committe_member.xml',
        'data/Demo/demo_07_test_management/data_13_center_time_table.xml',
        'data/Demo/demo_07_test_management/data_14_mk_branches_master_many2many_fields.xml',
        'data/Demo/demo_07_test_management/data_15_mk_test_center_preparation_many2many_fields.xml',
        'data/Demo/demo_07_test_management/data_16_mak_test_center_many2many_fields.xml',
        'data/Demo/demo_07_test_management/data_17_student_test_session.xml',

    ],
    'demo': [

    ],
    'installable': True,
    'application': False,
    'auto_install': False,

}
