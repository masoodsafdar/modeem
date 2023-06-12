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
    
class MkBranches(models.Model):
    _name = 'mk.branches'
        
    name = fields.Char('Name')
    path = fields.Selection([('a','Ascending'),('d','Descending')],string='Path')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    age_category = fields.Selection([('s','Specific'),('o','Open')],string='Age Category')
    from_age = fields.Integer('From Age')
    to_age = fields.Integer('To Age')
    from_surah = fields.Many2one('mk.surah', string='From Surah')
    to_surah = fields.Many2one('mk.surah', string='to Surah')
    
    

