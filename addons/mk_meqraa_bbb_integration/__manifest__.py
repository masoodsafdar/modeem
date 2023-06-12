# -*- coding: utf-8 -*-
{
    'name': 'Maqraa Big Blue Button Integration',
    'version': '11.0.0',
    'category': 'Education',
    'depends': ['mk_meqraa'],
    'data': [
        #Security
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        #wizard
        'wizard/update_time_views.xml',

        #view
        'views/res_config_settings.xml',
        'views/mq_episode.xml',
        'views/mq_session.xml',
        'views/menu.xml',
        'view/session_logoutpage.xml',
        'view/assets.xml',
    ],
    'images': [
    ],
    'external_dependencies': {
        'python': [
            'bigbluebutton_api_python',
        ]},
    'demo': [
    ],
    'installable': True,
    'auto_install': False,

}
