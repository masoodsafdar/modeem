#-*- coding:utf-8 -*-

##############################################################################
#
#    Copyright (C) Appness Co. LTD **hosam@app-ness.com**. All Rights Reserved
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from odoo import models, fields, api
from datetime import datetime


class MkPlanShare(models.Model):
    _name = 'mk.plan.share'
    
    
    mosque_id = fields.Many2one('mk.mosque', string="Mosque")
    center_id = fields.Many2one('mk.center', string="Center")
    plan_id = fields.Many2one('mk.plan', string="Plan")
    date = fields.Date("Date")
    state = fields.Selection([
	('draft', 'Draft'),
	('confirmed', 'Confirmed'),
	], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
    
