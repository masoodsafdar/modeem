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

class MkTestClassQuestionsConfiguration(models.Model):
    _name = 'mk.test.class.questions.configuration'
    

    @api.depends('test_type_id')
    def _type_compute(self):
        self.test_type = self.test_type_id.test_type
        
    @api.depends('test_type_id','test_class_id')
    def _test_scope_compute(self):
        self.test_scope = self.test_type_id.test_scope
    
    @api.onchange('test_type_id','test_class_id')
    def _test_type_class_onchange(self):
        lst= []
        if self.test_type_id.test_scope == 'a':
            parts= self.env['mk.parts'].search([])
            for p in parts:
                lst.append((0,0,{'part_id':p.id}))
            self.part_ids = lst
        elif self.test_type_id.test_scope == 's':
            for p in self.test_class_id.part_ids:
                lst.append((0,0,{'part_id':p.id}))
            self.part_ids = lst	
        else:
            self.part_ids = lst
		
    @api.onchange('test_type')
    def onchange_test_type(self):
        if self.test_type == 'o':
        	self.name = _('Select Difference Parts')
        else :
        	self.name = None



    @api.multi
    def get_year_default(self):
        academic_year = self.env['mk.study.year'].search([('is_default','=',True)], limit=1)
        return academic_year and academic_year.id or False 

    @api.onchange('study_year_id')

    @api.onchange('study_year_id')

    @api.multi

    def get_study_class(self):
        """
        for rec in self:
            study_class_ids=self.env['mk.study.class'].search([('study_year_id', '=', self.academic_id.id)])
            return  study_class_ids[0]
        """
        study_class_ids=self.env['mk.study.class'].search([('study_year_id', '=', self.study_year_id.id),('is_default', '=', True)])
        if study_class_ids:
            self.study_class_id=study_class_ids[0]

        	
    name = fields.Char('Name')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mk.test.class.questions.configuration'))
    test_type_id = fields.Many2one('mk.test.type', string='Test Type')
    study_year_id = fields.Many2one('mk.study.year', string='Study Year', default=get_year_default)
    study_class_id = fields.Many2one('mk.study.class', string='Study Class Year', readonly=True , default=get_study_class,)
    test_class_id = fields.Many2one('mk.test.class', string='Test Class',)
    
    line_number = fields.Integer('Number of Lines Per Question')
    max_score = fields.Float('Maximum Score')
    min_score = fields.Float('Minimum Score')
    
    applied_score = fields.Float('Applied Tajweed Score')
    general_score = fields.Float('General Performance Score')
    theoretical_score = fields.Float('Theoretical Tajweed Score')
    
    part_ids = fields.One2many('mk.test.class.parts', 'config_id', string="Parts")
    
    test_type = fields.Char(compute='_type_compute', string='Test Type')
    test_scope = fields.Char(compute='_test_scope_compute', string='Test Scope')
    
    """
    @api.model    
    def fields_view_get(self, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(MkTestClassQuestionsConfiguration, self).fields_view_get(view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
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
        
class MkTestClassParts(models.Model):
    _name = 'mk.test.class.parts'
    
    @api.depends('easy','middle','difficult')
    def get_question_numbers(self):
        self.question_number = (self.easy or 0) + (self.middle or 0) + (self.difficult or 0)

    @api.onchange('easy','middle','difficult','part_id')
    @api.constrains('easy','middle','difficult','part_id')
    def onchange_constraints(self):
        if self.part_id:
            verses_obj = self.env['mk.surah.verses']
            if self.easy:
                verses= verses_obj.search([('part_id','=',self.part_id.id),('difficulty_level','=','easy')])
                counter= 0
                for v in verses:
                	counter += 1
                if self.easy > counter:
                	self.easy = 0
                	raise ValidationError(_('Invalid Number of Easy Questions'))
                	self.easy = 0
            if self.middle:
                verses= verses_obj.search([('part_id','=',self.part_id.id),('difficulty_level','=','middle')])
                counter= 0
                for v in verses:
                	counter += 1
                if self.middle > counter:
                	self.middle = 0
                	raise ValidationError(_('Invalid Number of Middle Questions'))
            if self.difficult:
                verses= verses_obj.search([('part_id','=',self.part_id.id),('difficulty_level','=','difficult')])
                counter= 0
                for v in verses:
                	counter += 1
                if self.difficult > counter:
                	self.difficult = 0
                	raise ValidationError(_('Invalid Number of Difficult Questions'))

    config_id = fields.Many2one('mk.test.class.questions.configuration', string='Config', ondelete="cascade")
    part_id = fields.Many2one('mk.parts', string="Parts")
    easy = fields.Integer('Easy')
    middle = fields.Integer('Middle')
    difficult = fields.Integer('Difficult')
    question_number = fields.Integer(compute='get_question_numbers', string='Number of Questions Per Part')
    

