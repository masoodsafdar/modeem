# -*- coding: utf-8 -*-
{
    'name': "MaKnon Tests Modules+privi",

    'summary': """
        This module allowed to manage the Tests""",

    'description': """
        This module allowed to manage the Tests
    """,

    'author': "Masa",
    'website': "http://www.odoo.com",
    'category': 'custom',
    'version': '1.0',
    'depends': [
        'mk_master_models',
        'mk_student_managment',
        'mk_student_register',
        'hr',
        'mk_intensive_courses'],

    'data': [
        'security/test_group.xml',
        'security/test_group_suite.xml',
        'security/module_rules.xml',
        'security/ir.model.access.csv',

        'data/notify_supervisor_cron.xml',
        'data/mail_templates.xml',
        
        'views/test_parent_menus.xml',
        'views/mk_test_branch.xml',
        'views/mk_test_names.xml',
        
        'models/wizerd/add_error.xml',
        
        'views/mk_passing_items.xml',
        'views/mk_reward_items.xml',
        'views/mk_evaluation_items.xml',
        'views/mk_test_center.xml',
        'views/mk_test_periods.xml',
        'views/mk_test_center_prepration.xml',
        
        'models/wizerd/add_teacher.xml',
        'models/wizerd/test_registration.xml',
        'models/wizerd/test_registration_teacher.xml',
        'wizard/teacher_test_subscription_wizard_view.xml',

        'views/center_time_table.xml',

        'wizard/update_degree_wizard_view.xml',
        'wizard/update_branch_form_wizard.xml',
        'views/student_test_session.xml',
        'views/old_student_tests.xml',
        'views/mk_test_employee_items.xml',
        'views/empoyee_test_session.xml',
        'views/hr_employee.xml',
        'views/test_quastion_view.xml',
        'views/inherit_student_register.xml',
        #'views/set_mosque_test_session_cron.xml',
        'wizard/add_committe_wizard_view.xml',
        'wizard/tests_session_wizard_view.xml',

        'reports/reports.xml',
        'reports/report_tests_template.xml',
        'reports/parts_certificate_report.xml',
        'reports/report_parts_certificate_template.xml',
        'reports/final_test_certificate_report.xml',
        'reports/final_test_certificate_template.xml',
    ],
}
