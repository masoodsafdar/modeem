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
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from odoo.tools.translate import _

class MkTestType(models.Model):
    _name = 'mk.test.type'
        
    name = fields.Char('Name')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mk.test.type'))
    duration = fields.Integer('Duration')
    test_type = fields.Selection([('s','Specific'),('o','Open')],string='Test Type')
    test_scope = fields.Selection([('a','All Quran'),('s','Specific Parts'),('e','Ending')],default='s', string='Test Scope')
    target = fields.Selection([('s','Student'),('t','Teacher'),('u','Supervisor')],string='Target')
    test_methodology = fields.Selection([('a','From Start to End'),('d','From End to Start'),('r','Random')],string='Test Methodology')
    follow_super = fields.Selection([('test_cmp','Company Tests'), ('test_mosq','Tests Mosque/School ')])
    test_error_ids = fields.One2many('test.type.error', 'order_id', string='Type Error Tests')
    type_test_ids = fields.Many2one('mk.test.type', string="Test Type")
    #Line Test Branche 
    test_branche_ids = fields.One2many('test.branch.line', 'line_id', string='Branche Tests')
    check_img = fields.Boolean('Image fro student')
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "موجود مسبقاً !"),
    ]

class test_type_error(models.Model):
    _name = 'test.type.error'
    _rec_name = 'order_id'

    order_id = fields.Many2one('mk.test.type', 'Order', ondelete='cascade')
    type_error = fields.Many2one('mk.test.error', string='Type Error')
    degree_deduct = fields.Float(string='Degree Deduct')


class test_branch_line(models.Model):
    _name = 'test.branch.line'
    _rec_name = 'branch'

    line_id = fields.Many2one('mk.test.type','Line Branch')
    branch = fields.Char('Name Branch')
    branch_type = fields.Selection([('ic','Intensive Course'),('com','Competitions')], string='Branch Type')
    check = fields.Boolean('all Quran')
    age_categ_ids = fields.Many2many('mk.age.category', string='Age Category')
    part_ids = fields.Many2many('mk.parts', string="Parts")


    @api.onchange('check')
    def check_all_quran(self):

        if self.check:
            part_lst = self.env['mk.parts'].search([])
            self.update({'part_ids':part_lst.ids})




    


    

