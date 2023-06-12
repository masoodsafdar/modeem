{
    'name': "Website Help Desk / Support Ticket",
    'version': "1.0.6",
    'author': "Masa",
    'category': "Tools",
    'summary': "A helpdesk / support ticket system for your website",
    'description': "A helpdesk / support ticket system for your website",
    'license':'LGPL-3',

    'data': [
        #'data/res.groups.csv',
        'security/support_security.xml',
	    'security/ir.model.access.csv',
        'views/website_support_ticket_menu_views.xml',
        'views/email_templates.xml',
        'views/website_support_ticket_compose_views.xml',
        'views/website_support_ticket_close_views.xml',
        'views/website_support_ticket_views.xml',
        'views/website_support_ticket_categories_views.xml',
        'views/website_support_ticket_subcategory_views.xml',
        'views/website_support_ticket_states_views.xml',
        'views/website_support_ticket_priority_views.xml',
        'views/res_company_views.xml',

        'data/website.support.ticket.categories.xml',
        'data/website.support.ticket.categories_suite.xml',

        'data/website.support.ticket.priority.xml',
        'data/website.support.settings.xml',

        'data/sms_template_data.xml',
        
        'data/website.support.ticket.states.xml',
    ],
    'demo': [],
    'depends': ['mail',
        'mk_master_models','general_sending','hr','mk_student_register'],


    'installable': True,
}
