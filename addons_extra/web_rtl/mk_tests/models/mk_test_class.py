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

class MkTestClass(models.Model):
    _name = 'mk.test.class'
    
    @api.depends('test_type_id')
    def _type_compute(self):
        self.test_type = self.test_type_id.test_type
        
    @api.depends('test_type_id')
    def _test_scope_compute(self):
        self.test_scope = self.test_type_id.test_scope
        
    @api.onchange('test_type')
    def onchange_test_type(self):
        if self.test_type == 'o':
            self.name = _('Select Difference Parts') 
        else:
            self.name = None
            
    @api.multi
    def get_year_default(self):
        academic_year = self.env['mk.study.year'].search([('is_default','=',True)], limit=1)
        return academic_year and academic_year.id or False 

    @api.multi
    def get_study_class(self):
        study_class_ids=self.env['mk.study.class'].search([('study_year_id', '=', self.get_year_default().ids[0]),('is_default', '=', True)])
        if study_class_ids:
            return study_class_ids[0]        	
    name = fields.Char('Name')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self:self.env.user.company_id.id)
    test_type_id = fields.Many2one('mk.test.type', string='Test Type')
    study_year_id = fields.Many2one('mk.study.year', string='Study Year', default=get_year_default)
    study_class_id = fields.Many2one('mk.study.class', string='Study Class Year', default=get_study_class, readonly=True ,)
    active = fields.Boolean('Active', default=True)
    
    question_number = fields.Integer('Number of Questions Per Part')
    line_number = fields.Integer('Number of Lines Per Question')
    max_score = fields.Float('Maximum Score')
    min_score = fields.Float('Minimum Score')
    
    applied_score = fields.Float('Applied Tajweed Score')
    general_score = fields.Float('General Performance Score')
    theoretical_score = fields.Float('Theoretical Tajweed Score')
    
    part_ids = fields.Many2many('mk.parts', 'test_class_parts_rel', 'test_class_id', 'part_id', string="Parts")
    
    test_type = fields.Char(compute='_type_compute', string='Test Type')
    test_scope = fields.Char(compute='_test_scope_compute', string='Test Scope')
    
    """
    @api.model    
    def fields_view_get(self, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(MkTestClass, self).fields_view_get(view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='company_id']")
        company_ids = []
        company_recs= self.env['mk.study.year'].search([])
        company_ids = [x.company_id.id for x in company_recs]
        domain = "[('id', 'in', " + str(company_ids) + ")]"
	   for node in nodes:
		node.set('domain', domain)
        res['arch'] = etree.tostring(doc)
        return res
    """

