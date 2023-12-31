# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo RTL support
#    Copyright (C) 2016 Mohammed Barsi.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Report RTL',
    'version': '1.0',
    'author': 'Mohammed Barsi',
    'sequence': 4,
    'summary': 'Report RTL (Right to Left) layout',
    'description':
        """
Adding RTL (Right to Left) Support for Reports.
===============================================

This module provides a propper RTL support for Odoo's new report engine.
        """,
    'depends': ['web_rtl', 'report'],
    'auto_install': True,
    'installable': False,
    'data': ['views/layout.xml',],
}
