#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from num2words import num2words
from odoo.tools.translate import _


class MkApproaches(models.Model):
    _name = 'mk.approaches'
    _inherit = ['mail.thread']

    company_id 				= fields.Many2one('res.company',   string='Company', default=lambda self: self.env['res.company']._company_default_get('mk.approaches'))  
    center_department_id 	= fields.Many2one('hr.department', string='Center')
    mosque_id 				= fields.Many2one('mk.mosque',     string='Mosque')
    name 					= fields.Char('Name',                    track_visibility='onchange')
    code 					= fields.Char('Code',                    track_visibility='onchange')
    active 					= fields.Boolean('Active', default=True, track_visibility='onchange')
    state 					= fields.Selection([('draft', 'Draft'), 
												('active', 'Active')], 'Status', default='active', index=True, required=True, readonly=True, copy=False, track_visibility='onchange')
    program_id 				= fields.Many2one('mk.programs',        string='Program', track_visibility='onchange')
    program_type			= fields.Selection([('open','open'),
											    ('close','close')], string="program type", track_visibility='onchange')
    minimum_audit 			= fields.Boolean(related='program_id.minimum_audit', string='Minimum Audit')
    maximum_audit 			= fields.Boolean(related='program_id.maximum_audit', string='Maximum Audit')
    reading					= fields.Boolean(related='program_id.reading',       string='Reading')
    memorize 				= fields.Boolean(related='program_id.memorize',      string='Memorize')
    
    age_category_ids 		= fields.Many2many('mk.age.category', string='Age Category')
    job_ids 				= fields.Many2many('mk.job',          string='Target Job')
    stage_ids 				= fields.Many2many('mk.grade',        string='Target Stages')
    is_previous_approach 	= fields.Boolean('Previous Approach?', track_visibility='onchange')
    approach_id 			= fields.Many2one('mk.approaches',    string='approach', track_visibility='onchange')
    required_mosques 		= fields.Boolean('Required for All Mosques', track_visibility='onchange')
    #Small Review
    lessons_minimum_audit 	= fields.Float('Lessons Minimum Audit',   track_visibility='onchange')
    quantity_minimum_audit  = fields.Float('Quantity Minimum Audit',  track_visibility='onchange')
    deduct_qty_small_review = fields.Float('مقدار الخصم',             track_visibility='onchange')
    memorize_minimum_audit  = fields.Float('Memorize Minimum Audit',  track_visibility='onchange')
    deduct_memor_sml_review = fields.Float('مقدار الخصم',             track_visibility='onchange')
    mastering_minimum_audit = fields.Float('Mastering Minimum Audit', track_visibility='onchange')
    deduct_tjwd_sml_review  = fields.Float('مقدار الخصم',             track_visibility='onchange')
    #Big Review
    lessons_maximum_audit 	= fields.Float('Lessons Maximum Audit',   track_visibility='onchange')
    quantity_maximum_audit  = fields.Float('Quantity Maximum Audit',  track_visibility='onchange')
    deduct_qty_big_review   = fields.Float('مقدار الخصم',             track_visibility='onchange')
    memorize_maximum_audit  = fields.Float('Memorize Maximum Audit',  track_visibility='onchange')
    deduct_memor_big_review = fields.Float('مقدار الخصم',             track_visibility='onchange')
    mastering_maximum_audit = fields.Float('Mastering Maximum Audit', track_visibility='onchange')
    deduct_tjwd_big_review  = fields.Float('مقدار الخصم',             track_visibility='onchange')
    #Tlawa
    lessons_reading 		= fields.Float('Lessons Reading',   track_visibility='onchange')
    quantity_reading        = fields.Float('Quantity Reading',  track_visibility='onchange')
    deduct_qty_reading      = fields.Float('مقدار الخصم',       track_visibility='onchange')
    memorize_reading        = fields.Float('Memorize Reading',  track_visibility='onchange')
    deduct_memor_reading    = fields.Float('مقدار الخصم',       track_visibility='onchange')
    mastering_reading       = fields.Float('Mastering Reading', track_visibility='onchange')
    deduct_tjwd_reading     = fields.Float('مقدار الخصم',       track_visibility='onchange')
    #Memorize
    lessons_memorize 		= fields.Float('Lessons Memorize',   track_visibility='onchange')
    quantity_memorize       = fields.Float('Quantity Memorize',  track_visibility='onchange')
    deduct_qty_memorize     = fields.Float('مقدار الخصم',        track_visibility='onchange')
    memorize_degree         = fields.Float('Memorize Degree',    track_visibility='onchange')
    deduct_memor_memorize   = fields.Float('مقدار الخصم',        track_visibility='onchange')
    mastering_memorize      = fields.Float('Mastering Memorize', track_visibility='onchange')
    deduct_tjwd_memorize    = fields.Float('مقدار الخصم',        track_visibility='onchange')
    #Attendance
    preparation_degree 		= fields.Float('Prepartion Degree',           track_visibility='onchange')
    late_deduct 			= fields.Float('Late Deduct',                 track_visibility='onchange')
    excused_absence_deduct 	= fields.Float('Excused Absence Deduct',      track_visibility='onchange')
    no_excused_absence_deduct = fields.Float('No Excused Absence Deduct', track_visibility='onchange')
    behavior_degree         = fields.Float('درجة السلوك',                 track_visibility='onchange')
    #Test
    test_degree 			= fields.Float('Test Degree',  track_visibility='onchange')
    nbr_question_test       = fields.Integer('عدد الأسئلة', track_visibility='onchange')
    qty_question_test       = fields.Selection([('qty001','آية'),
                                                ('qty025','ربع صفحة'),
                                                ('qty050','نصف صفحة'),
                                                ('qty075','ثلاثة ارباع صفحة'),
                                                ('qty100','صفحة واحدة'),
                                                ('qty125','صفحة وربع'),
                                                ('qty150','صفحة ونصف'),
                                                ('qty175','صفحة وثلاثة ارباع'),
                                                ('qty200','صفحتان'),], string='مقدار السؤال', track_visibility='onchange')     
    deduction_test          = fields.Float('مقدار الخصم', track_visibility='onchange')
    #Exam
    exam_degree             = fields.Float('درجة الإختبار', track_visibility='onchange')
    nbr_question_exam       = fields.Integer('عدد الأسئلة', track_visibility='onchange')
    qty_question_exam       = fields.Selection([('qty001','آية'),
                                                ('qty025','ربع صفحة'),
                                                ('qty050','نصف صفحة'),
                                                ('qty075','ثلاثة ارباع صفحة'),
                                                ('qty100','صفحة واحدة'),
                                                ('qty125','صفحة وربع'),
                                                ('qty150','صفحة ونصف'),
                                                ('qty175','صفحة وثلاثة ارباع'),
                                                ('qty200','صفحتان')], string='مقدار السؤال', track_visibility='onchange')
    deduction_exam          = fields.Float('مقدار الخصم', track_visibility='onchange')

    tajweed_degree 			= fields.Float('Tajweed Degree', track_visibility='onchange')

    part_ids 				= fields.Many2many('mk.parts', string='Parts')
    surah_ids 				= fields.Many2many('mk.surah', string='surah')
    program_purpose 		= fields.Selection([('memorize_quran',    'Memorize all Quran'),
												('memorize_part',     'Memorize Specific Parts'),
												('memorize_surah',    'Memorize Specific Surah'),
												('mastering_reading', 'Mastering Reading Only')], string='Program Purpose', track_visibility='onchange')
    subject_id 				= fields.Many2one('mk.memorize.method', string='Subjects', track_visibility='onchange')
    is_test 				= fields.Boolean('Test After End of Subject', track_visibility='onchange')

    listen_ids 				= fields.One2many('mk.manual.plan', 'approche_id', 'plan')
    small_reviews_ids		= fields.One2many('mk.manual.plan', 'small_id',    'plan')
    big_review_ids			= fields.One2many('mk.manual.plan', 'big_id',      'plan')
    tlawa_ids				= fields.One2many('mk.manual.plan', 'tlawa_id',    'plan')

    path_ids                = fields.One2many('mk.path', 'approach_id', 'Trajectory')

    _sql_constraints = [('name_uniq', 'unique (name)', "Already Exist!"),]
    
    # @api.one
    def act_draft(self):
        subject_obj = self.env['mk.subject.configuration']
        s_ids = subject_obj.search([('approach_id','=',self.id)])
        for s_id in s_ids:
            self.state = 'draft'    

    # @api.one
    def act_active(self):
        c= 0
        lst=[]
        subject_obj = self.env['mk.subject.configuration']
        sub_obj = self.env['mk.subject.page']
        s_ids = subject_obj.search([('approach_id','=',self.id)])
        subject_page_ids = sub_obj.search([('subject_page_id','=',self.subject_id.id)], order='id desc')

        for ss in subject_page_ids:
            c += 1
            text = num2words(c,lang='ar',ordinal=True)
            num_word = "اليوم"+" "+"ال" + text
            lst.append({'is_test':				self.is_test,
						'order':				c,
						'num_words':			num_word,
						'program_id':			self.program_id.id,
						'approach_id':			self.id,
						'mosque_id':			self.mosque_id.id,
						'center_department_id': self.center_department_id.id,
						
						'detail_id':			ss.id,
						'subject_id': 			self.subject_id.id,
						'name':					str(self.program_id and (self.program_id.name+ '-') or '') + str((self.name + '-')) + str(c),})
        for lin in lst:
            subject_obj.create(lin)
            self.state = 'active'

    @api.onchange('program_id')
    def onchange_program(self):
        self.program_purpose = self.program_id.program_purpose

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(MkApproaches, self).fields_view_get(view_id=view_id,view_type=view_type, toolbar=toolbar, submenu=submenu)
        context=self._context
        doc = etree.XML(res['arch'])        
        #open Approache create view 
        if context.get('default_program_type')=='open' and not self.env.user.has_group('mk_program_management.create_an_open_curriculum_association_level'):
        #and not self.env.user.has_group('mk_program_management.create_an_open_curriculum_center_level') and not self.env.user.has_group('mk_program_management.create_an_open_curriculum_mosque_level'):
            for node_tree in doc.xpath("//tree"):   
                node_tree.set("create", 'false')
                
            for node_tree in doc.xpath("//form"):   
                node_tree.set("create", 'false')

        #open Approache  edit view:
        if context.get('default_program_type')=='open' and not self.env.user.has_group('mk_program_management.update_curriculum_level') :
            for node_tree in doc.xpath("//tree"):   
                node_tree.set("edit", 'false')
                
            for node_tree in doc.xpath("//form"):   
                node_tree.set("edit", 'false')

        #open Approache delete  view:
        if context.get('default_program_type')=='open' and not self.env.user.has_group('mk_program_management.delete'):
            for node_tree in doc.xpath("//tree"):   
                node_tree.set("delete", 'false')
                
            for node_tree in doc.xpath("//form"):   
                node_tree.set("delete", 'false')

        #close Approache :
        if context.get('default_program_type')=='close' and not self.env.user.has_group('mk_program_management.create_an_close_curriculum_association_level'): 
            #and not self.env.user.has_group('mk_program_management.create_an_close_curriculum_center_level') and not self.env.user.has_group('mk_program_management.create_an_close_curriculum_mosque_level'):
            for node_tree in doc.xpath("//tree"):   
                node_tree.set("create", 'false')
                
            for node_tree in doc.xpath("//form"):   
                node_tree.set("edit", 'false')
        
        #close Approache  edit view:
        if context.get('default_program_type')=='close' and not self.env.user.has_group('mk_program_management.update_curriculum_level_close') :
            for node_tree in doc.xpath("//tree"):   
                node_tree.set("edit", 'false')
                
            for node_tree in doc.xpath("//form"):   
                node_tree.set("edit", 'false')
        
        #close Approache delete  view:
        if context.get('default_program_type')=='close' and not self.env.user.has_group('mk_program_management.delete_close'):
            for node_tree in doc.xpath("//tree"):   
                node_tree.set("delete", 'false')
                
            for node_tree in doc.xpath("//form"):   
                node_tree.set("delete", 'false')

        res['arch'] = etree.tostring(doc)
        return res


class MKPath(models.Model):
    _name = 'mk.path'
    _description = 'Paths'

    name            = fields.Char('المسار')
    approach_id     = fields.Many2one('mk.approaches', string="المنهج")
