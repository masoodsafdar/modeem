# -*- coding: utf-8 -*-
{
    'name': "MK Meqraa",

    'summary': """ 
    
    """,

    'description': """

    """,

    'author': "Masa",
    'website': "http://www.odoo.com",
    'category': 'custom',
    'version': '1.0',
    'depends': ['mk_student_register','mk_student_managment','mk_episode_management','mk_program_management','mk_master_models', 'maknon_tests'],
    'data': [
            #Security
            'security/security.xml',
            'security/ir.model.access.csv',
            #Data
#             'data/program_data.xml',
            
            #Views
            'views/mq_student_register_view.xml',
            'views/mq_student_management_view.xml',
            'views/mq_annual_vacation_view.xml',
            'views/mq_time_view.xml',
            'views/mq_episode_view.xml',
            'views/mq_programs_view.xml',
            'views/mq_approaches_view.xml',
            'views/menu.xml',
            'views/mq_student_link_view.xml',
            'views/meqraa_student_test_session.xml',

            #Wizard
            'wizard/import_student_views.xml',
            'wizard/view_meqraa_student_request_multi_form.xml',


    ],    
    'demo': [

    ],
    'application':True,

}
