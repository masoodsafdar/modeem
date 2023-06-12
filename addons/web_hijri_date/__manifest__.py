# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Web Hijri Date",
    "category": "Web",
    "description":
        """
        Odoo Web Display Hijri Calendar.
        """,
    "version": "0.1",
    "depends": ['web'],
    'data':    ['views/templates.xml',],
    'qweb' :   ["static/src/xml/*.xml",],
    
    'installable': False,
    'auto_install': False,
}
