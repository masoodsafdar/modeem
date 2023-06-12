# -*- coding: utf-8 -*-
# Copyright Anubía, soluciones en la nube,SL (http://www.anubia.es)
# Alejandro Santana <alejandrosantana@anubia.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hide link to database manager in login screen',
    'version': "11",
    'category': 'Web',
    'license': 'AGPL-3',
    'author': 'Alejandro Santana, Odoo Community Association (OCA)',
    'website': 'http://anubia.es',
    'summary': 'Hide link to database manager in login screen',
    'depends': ['web','base'],
   'data': ['views/webclient_templates.xml',
            'views/res_user.xml',],
   'installable': True,
}
