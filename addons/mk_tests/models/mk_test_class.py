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
    _rec_name = 'test_type_id'
    
    @api.depends('test_type_id')
    def _type_compute(self):
        for rec in self:
            rec.test_type = rec.test_type_id.test_type
        
    @api.depends('test_type_id')
    def _test_scope_compute(self):
        for rec in self:
            rec.test_scope = rec.test_type_id.test_scope
    """
    @api.onchange('test_type_id','test_class_id')
    def _test_type_class_onchange(self):
        lst= []
        if self.test_type_id.test_scope == 'a':
            parts= self.env['mk.parts'].search([])
            for p in parts:
                lst.append((0,0,{'part_id':p.id}))
            self.part_question_ids = lst
        elif self.test_type_id.test_scope == 's':
            for p in self.test_class_id.part_ids:
                lst.append((0,0,{'part_id':p.id}))
            self.part_question_ids = lst 
        else:
            self.part_question_ids = lst
        
    @api.onchange('test_type')
    def onchange_test_type(self):
        if self.test_type == 'o': 
        	self.name = _('Select Difference Parts') 
        else :
        	self.name = None
    """
    @api.onchange('test_type_id')
    def _test_type_class_onchange(self):
        ls_parts = []
        for parts in self.test_type_id.part_ids:
            ls_parts.append({'part_id':parts})
        self.part_question_ids = ls_parts 

        #if self.test_type_id.test_scope == 'a':
        #    parts= self.env['mk.parts'].search([])
        #    for p in parts:
        #        lst.append((0,0,{'part_id':p.id}))
        #    self.part_question_ids = lst
        #elif self.test_type_id.test_scope == 's':
        #    for p in self.test_class_id.part_question_ids:
        #        lst.append((0,0,{'part_id':p.id}))
        #    self.part_question_ids = lst 
        #else:
        #    self.part_question_ids = lst
    @api.multi
    def get_year_default(self):
        academic_year = self.env['mk.study.year'].search([('is_default','=',True)], limit=1)
        return academic_year and academic_year.id or False 
    
    """
    @api.multi
    def get_study_class(self):
        study_class_ids=self.env['mk.study.class'].search([('study_year_id', '=', self.get_year_default()),('is_default', '=', True)])
        if study_class_ids:

            return study_class_ids[0]
     """  
    #Functions Passage Reward##################
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

    @api.depends('applied_score','general_score','theoretical_score','mim_static','nun_static',
                 'nun_mim_intencive','Looted','stop_start','confused','safety_letters','start_hesit',
                 'master_letter','save','alhn_gly','allhn_khaffy','good_sound','orig_novel','farsh_latter')
    def _total_lisetning(self):
        for rec in self:
            rec.listen = rec.applied_score+rec.general_score+rec.theoretical_score+rec.mim_static+rec.nun_static+rec.nun_mim_intencive+rec.Looted+rec.stop_start+rec.confused+rec.safety_letters+rec.start_hesit+rec.master_letter+rec.master_letter+rec.save+rec.alhn_gly+rec.allhn_khaffy+rec.good_sound+rec.orig_novel+rec.farsh_latter
            if rec.listen > rec.max_score:
                raise ValidationError("الدرجة الإجمالية اكبر من الدرجة الكبرى")

    name = fields.Char('Name')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mk.test.class'))
    test_type_id = fields.Many2one('test.branch.line', string='Test Type')
    test_class_id = fields.Many2one('mk.test.class', string='Test Class',)
    study_year_id = fields.Many2one('mk.study.year', string='Study Year', default=get_year_default)
    #study_class_id = fields.Many2one('mk.study.class', string='Study Class Year', default=get_study_class, readonly=True ,)
    active = fields.Boolean('Active', default=True)
    
    question_number = fields.Integer('Number of Questions Per Part')
    line_number = fields.Integer('Number of Lines Per Question')
    max_score = fields.Float('Maximum Score')
    min_score = fields.Float('Minimum Score')
    
    applied_score = fields.Float('Applied Tajweed Score')
    general_score = fields.Float('General Performance Score')
    theoretical_score = fields.Float('Theoretical Tajweed Score')

    mim_static = fields.Float('Mim Static')
    nun_static = fields.Float('Nun static')
    nun_mim_intencive = fields.Float('Nun and Mim Intensive')
    Looted = fields.Float('Looted')
    stop_start = fields.Float('Stop and Start')
    confused = fields.Float('Confused')
    safety_letters = fields.Float('Safety of exits and letters')
    start_hesit = fields.Float('Starting and not hesitating')
    master_letter = fields.Float('Mastering letter Movements')
    save = fields.Float('Save')
    alhn_gly = fields.Float('Allhn Algaly')
    allhn_khaffy = fields.Float('Allhan Alkhaffy')
    good_sound = fields.Float('Good Sound')
    orig_novel = fields.Float('Original Novel')
    farsh_latter = fields.Float('Farsh Latter')
    listen = fields.Float(compute='_total_lisetning', string='Listening')
    total_question = fields.Float(compute='_question_num_total', string='Total question number')
    
    part_question_ids = fields.One2many('mk.test.class.parts', 'test_question_id', string="Parts Question")
    #test_type = fields.Char(compute='_type_compute', string='Test Type')
    #test_scope = fields.Char(compute='_test_scope_compute', string='Test Scope')

    #Appreciation Tests line
    apprec_test_ids = fields.One2many('appreciation.test','apprec_id', string='Appreciation Test')
    #passage reward Line
    reward_test_ids = fields.One2many('passage.reward','reward_id', string='Passage Reward')
    
   
    
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

class AppreciationTest(models.Model):
    _name = 'appreciation.test'
    _rec_name = 'apprec_id'

    apprec_id = fields.Many2one('mk.test.class', string='appreci_id', ondelete='cascade')
    appre_name = fields.Char('Appreciation Name')
    appre_test_type_id = fields.Many2one('mk.test.type', string='Test Type',)
    from_score = fields.Integer('From Score')
    to_score = fields.Integer('To Score')

    @api.onchange('to_score')
    @api.constrains('to_score')
    def appreciation_constraints(self):
        if self.from_score > self.to_score:
            raise ValidationError(_('Invalid Number from score bigger than to score'))
        else:
            if self.to_score > self.apprec_id.max_score:
                raise ValidationError(_('Invalid Number to score bigger than max scors'))


class PassageReward(models.Model):
    _name = 'passage.reward'

    reward_id = fields.Many2one('mk.test.class', string='Reward', ondelete='cascade')
    name = fields.Char('Name')
    age_catg_ids = fields.Many2many('mk.age.category', string='Age Category')
    study_class_id = fields.Many2one('mk.study.class', string='Study Class Year')
    award_category = fields.Selection([('ce','Certificate'),('cm','Certificate and amount of money')],string='Award Category')
    amount_money = fields.Float('amount of money')




