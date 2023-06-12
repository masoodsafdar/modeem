# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#     Copyright (C) 2015 SIAT TUNISIE <contact@siat.com.tn>
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

from odoo import _, api, fields, models, tools
class email_template(models.Model):
    _inherit = "mail.template"
    
    sms_template = fields.Boolean(
        string='SMS Template',
    )
    mobile_to = fields.Char(
        string='to (Mobile)',       
        size=256,        
    )
    gateway_id = fields.Many2one(
        'smsclient',
        string='SMS Gateway'
    )