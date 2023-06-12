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

class MkPassageReward(models.Model):
    _name = 'mk.passage.reward'
    
    @api.model
    def _get_from_score(self):
        lst= []
        counter = 100
        while( counter != -1):
        	lst.append((counter,str(counter)))
        	counter = counter - 1
        return lst


    @api.model
    def _get_to_score(self):
        lst= []
        counter = 0
        while( counter != 101):
            lst.append((counter,str(counter)))
            counter = counter + 1
        return lst
        
    branch_id = fields.Many2one('mk.branches', string='Branch')
    from_score = fields.Selection(_get_from_score ,string='From Score')
    to_score = fields.Selection(_get_to_score ,string='To Score')
    appreciation = fields.Selection([('',''),
						    ('',''),
						    ('',''),
						    ('',''),
						    ('',''),
						    ] ,string='Appreciation')
		    

