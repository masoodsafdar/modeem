# -*- coding: utf-8 -*-
{
    'name': "MK Contests Modules",

    'summary': """      
        """,

    'description': """
        
    """,

    'author': "Masa",
    'website': "http://www.odoo.com",
    'category': 'custom',
    'version': '1.0',
    'depends': ['base', 'mk_master_models','mk_student_register','mk_tests','mk_episode_management','maknon_tests'],
    'data': [
             'security/contests_security_groups.xml',
             'security/contest_groups2.xml',
             'security/csv/ir.model.access.csv',
             'data/notify_supervisor_cron.xml',
             'views/main_menus.xml',
             'views/contest_prepration.xml',
             'views/Branches.xml',
             'views/regulations.xml',
             'views/nominations_types.xml',
             'views/contest_calender.xml' ,
             'views/nominations_process_view.xml',
             'views/nomination_request_managment_view.xml',
             'views/result_managment_view.xml',
             'views/contest_types.xml',
             'views/contest_fields.xml',
             'views/diff_items.xml',
             'views/contest_test_names.xml',
             'security/contest_record_rules.xml',
             'security/menus_rules.xml',
                 ],    
}
