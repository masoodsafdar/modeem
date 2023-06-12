# -*- coding: utf-8 -*-
{
    'name': "Virtual Room",

    'summary': """ Virtual Room """,

    'description': """  Virtual Room """,

    'author': "Masa",
    'website': "http://www.odoo.com",
    'category': 'custom',
    'version': '0.1',
    'depends': ['base','mail','mk_master_models','mk_episode_management'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/main_menus_view.xml',
        'views/mk_virtual_room_provider_view.xml',
        'views/mk_virtual_room_type.xml',
        'views/mk_virtual_room.xml',
        'views/mk_virtual_room_subscription.xml',
    ],
}
