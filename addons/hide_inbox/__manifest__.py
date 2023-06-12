# -*- coding: utf-8 -*-
# module template
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hide Inbox Chatter',
    'version': '10.0',
    'category': 'Base',
    'license': 'AGPL-3',
    'author': "Odoo Tips",
    'website': 'http://www.gotodoo.com/',
    'depends': ['base', 'mail'
                ],

    'images': ['images/main_screenshot.png'],
    'data': [
             'views/mail_views.xml',
             ],
    'qweb': [
            'static/src/xml/systray.xml',
        ],

    'installable': True,
    'application': True,
}
