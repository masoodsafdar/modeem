#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from num2words import num2words
from odoo.tools.translate import _


class MkApproaches(models.Model):
    _name = 'mk.approaches'
    _inherit=['mail.thread','mail.activity.mixin']

    company_id 				= fields.Many2one('res.company',   string='Company', default=lambda self: self.env['res.company']._company_default_get('mk.approaches'))  
    center_department_id 	= fields.Many2one('hr.department', string='Center')
    mosque_id 				= fields.Many2one('mk.mosque',     string='Mosque')
    name 					= fields.Char('Name',                    tracking=True)
    code 					= fields.Char('Code',                    tracking=True)
    active 					= fields.Boolean('Active', default=True, tracking=True)
    state 					= fields.Selection([('draft', 'Draft'), 
												('active', 'Active')], 'Status', default='active', index=True, required=True, readonly=True, copy=False, tracking=True)
    program_id 				= fields.Many2one('mk.programs',        string='Program', tracking=True)
    program_type			= fields.Selection([('open','open'),
											    ('close','close')], string="program type", tracking=True)
    minimum_audit 			= fields.Boolean(related='program_id.minimum_audit', string='Minimum Audit')
    maximum_audit 			= fields.Boolean(related='program_id.maximum_audit', string='Maximum Audit')
    reading					= fields.Boolean(related='program_id.reading',       string='Reading')
    memorize 				= fields.Boolean(related='program_id.memorize',      string='Memorize')
    
    age_category_ids 		= fields.Many2many('mk.age.category', string='Age Category')
    job_ids 				= fields.Many2many('mk.job',          string='Target Job')
    stage_ids 				= fields.Many2many('mk.grade',        string='Target Stages')
    is_previous_approach 	= fields.Boolean('Previous Approach?', tracking=True)
    approach_id 			= fields.Many2one('mk.approaches',    string='approach', tracking=True)
    required_mosques 		= fields.Boolean('Required for All Mosques', tracking=True)
    #Small Review
    lessons_minimum_audit 	= fields.Float('Lessons Minimum Audit',   tracking=True)
    quantity_minimum_audit  = fields.Float('Quantity Minimum Audit',  tracking=True)
    deduct_qty_small_review = fields.Float('مقدار الخصم',             tracking=True)
    memorize_minimum_audit  = fields.Float('Memorize Minimum Audit',  tracking=True)
    deduct_memor_sml_review = fields.Float('مقدار الخصم',             tracking=True)
    mastering_minimum_audit = fields.Float('Mastering Minimum Audit', tracking=True)
    deduct_tjwd_sml_review  = fields.Float('مقدار الخصم',             tracking=True)
    #Big Review
    lessons_maximum_audit 	= fields.Float('Lessons Maximum Audit',   tracking=True)
    quantity_maximum_audit  = fields.Float('Quantity Maximum Audit',  tracking=True)
    deduct_qty_big_review   = fields.Float('مقدار الخصم',             tracking=True)
    memorize_maximum_audit  = fields.Float('Memorize Maximum Audit',  tracking=True)
    deduct_memor_big_review = fields.Float('مقدار الخصم',             tracking=True)
    mastering_maximum_audit = fields.Float('Mastering Maximum Audit', tracking=True)
    deduct_tjwd_big_review  = fields.Float('مقدار الخصم',             tracking=True)
    #Tlawa
    lessons_reading 		= fields.Float('Lessons Reading',   tracking=True)
    quantity_reading        = fields.Float('Quantity Reading',  tracking=True)
    deduct_qty_reading      = fields.Float('مقدار الخصم',       tracking=True)
    memorize_reading        = fields.Float('Memorize Reading',  tracking=True)
    deduct_memor_reading    = fields.Float('مقدار الخصم',       tracking=True)
    mastering_reading       = fields.Float('Mastering Reading', tracking=True)
    deduct_tjwd_reading     = fields.Float('مقدار الخصم',       tracking=True)
    #Memorize
    lessons_memorize 		= fields.Float('Lessons Memorize',   tracking=True)
    quantity_memorize       = fields.Float('Quantity Memorize',  tracking=True)
    deduct_qty_memorize     = fields.Float('مقدار الخصم',        tracking=True)
    memorize_degree         = fields.Float('Memorize Degree',    tracking=True)
    deduct_memor_memorize   = fields.Float('مقدار الخصم',        tracking=True)
    mastering_memorize      = fields.Float('Mastering Memorize', tracking=True)
    deduct_tjwd_memorize    = fields.Float('مقدار الخصم',        tracking=True)
    #Attendance
    preparation_degree 		= fields.Float('Prepartion Degree',           tracking=True)
    late_deduct 			= fields.Float('Late Deduct',                 tracking=True)
    excused_absence_deduct 	= fields.Float('Excused Absence Deduct',      tracking=True)
    no_excused_absence_deduct = fields.Float('No Excused Absence Deduct', tracking=True)
    behavior_degree         = fields.Float('درجة السلوك',                 tracking=True)
    #Test
    test_degree 			= fields.Float('Test Degree',  tracking=True)
    nbr_question_test       = fields.Integer('عدد الأسئلة', tracking=True)
    qty_question_test       = fields.Selection([('qty001','آية'),
                                                ('qty025','ربع صفحة'),
                                                ('qty050','نصف صفحة'),
                                                ('qty075','ثلاثة ارباع صفحة'),
                                                ('qty100','صفحة واحدة'),
                                                ('qty125','صفحة وربع'),
                                                ('qty150','صفحة ونصف'),
                                                ('qty175','صفحة وثلاثة ارباع'),
                                                ('qty200','صفحتان'),], string='مقدار السؤال', tracking=True)     
    deduction_test          = fields.Float('مقدار الخصم', tracking=True)
    #Exam
    exam_degree             = fields.Float('درجة الإختبار', tracking=True)
    nbr_question_exam       = fields.Integer('عدد الأسئلة', tracking=True)
    qty_question_exam       = fields.Selection([('qty001','آية'),
                                                ('qty025','ربع صفحة'),
                                                ('qty050','نصف صفحة'),
                                                ('qty075','ثلاثة ارباع صفحة'),
                                                ('qty100','صفحة واحدة'),
                                                ('qty125','صفحة وربع'),
                                                ('qty150','صفحة ونصف'),
                                                ('qty175','صفحة وثلاثة ارباع'),
                                                ('qty200','صفحتان')], string='مقدار السؤال', tracking=True)
    deduction_exam          = fields.Float('مقدار الخصم', tracking=True)

    tajweed_degree 			= fields.Float('Tajweed Degree', tracking=True)

    part_ids 				= fields.Many2many('mk.parts', string='Parts')
    surah_ids 				= fields.Many2many('mk.surah', string='surah')
    program_purpose 		= fields.Selection([('memorize_quran',    'Memorize all Quran'),
												('memorize_part',     'Memorize Specific Parts'),
												('memorize_surah',    'Memorize Specific Surah'),
												('mastering_reading', 'Mastering Reading Only')], string='Program Purpose', tracking=True)
    subject_id 				= fields.Many2one('mk.memorize.method', string='Subjects', tracking=True)
    is_test 				= fields.Boolean('Test After End of Subject', tracking=True)

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
