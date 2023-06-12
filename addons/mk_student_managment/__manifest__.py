{    
    "version": '1.0',
    "name": "Maknoon Student Management",
    "depends": ["base",
        "hr",
        "hr_holidays",
        "mk_student_register",
        
        ],
    "author" : "Masa Technology",
    'description': """Maknoon Student Management""",
    "category" : "Student",


    "data" :[

        'security/student_management_group.xml',
        'security/models_rules.xml',
        'security/security/ir.model.access.csv',
        'views/student_behavior.xml',
        'views/student_management.xml',
        #'views/student_manage_view2.xml',
        'views/student_transfer_search_episodes.xml',
        #'views/mk_student_internal_transfer_workflow.xml',
        #'views/mk_student_clearance_workflow.xml',
        'views/student_transfer.xml',
        'views/student_absence.xml',
        #'views/mk_student_absence_workflow.xml',
        #'views/mk_student_attendace.xml',
        'views/mk_comments_and_behavior.xml',
        #'views/mk_student_suspend_resume.xml',
        'views/external_transfer.xml',
        'views/clearance.xml',
        'report/report_wizerd.xml',
        'wizard/student_prepare_report_wizerd.xml',
        'report/attendance_report.xml',
        'report/student_prepare_report.xml',
        'report/student_attendance_report_temp.xml',
        'report/student_prepare_report_template.xml',
        #'data/report_purpose_data.xml'
        'data/auto_accept_student_clearance_cron.xml',
        'data/mail_templates.xml',
        'views/mosque_and_episode_views.xml',
        ],
    'installable':True,
    'auto_install':False,
    'application':True,
    

}
