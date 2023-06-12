# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

from lxml import etree
# from odoo.osv.orm import setup_modifiers


class InternalTransfer(models.TransientModel):
    _name = 'mk.student.internal_transfer'
    
    @api.model
    def _getDefault_academic_year(self):
        academic_year = self.env['mk.study.year'].search([('is_default', '=', True)], limit=1)
        return academic_year and academic_year.id or False

    student_ids        = fields.Many2many('mk.student.register', string="الطلاب")
    gender             = fields.Selection([('men',   'رجالية'),
                                           ('women', 'نسائية')], string='جنس الحلقة', default='men')  
    next_action_pdsd   = fields.Selection([('sbj','إتمام إعدادات المقررات'),
                                           ('pgm','تحرير إعدادات البرامج')], string='تحديد العملية اللاحقة')
    year               = fields.Many2one('mk.study.year',      string='العام الدراسي', readonly=True, default=_getDefault_academic_year, ondelete="restrict")    
    registeration_date = fields.Date('التاريخ', default=fields.Date.today() )

    mosq_from_id       = fields.Many2one('mk.mosque',  string='تحويل من المسجد')
    mosq_id            = fields.Many2one('mk.mosque',  string='المسجد')
    episode_fr_id      = fields.Many2one('mk.episode', string="تحويل من الحلقة")
    episode_id         = fields.Many2one('mk.episode', string="الحلقة")
    episode_assign_id  = fields.Many2one('mk.episode') 
    type_setting_ps    = fields.Selection([('psss', 'نقل الطالب مع الحفاظ على نفس البرنامج'),
                                           ('pusu', 'برنامج موحد ومقررات موحدة لكل الطلاب'),], default='pusu', string='إعدادات البرامج والمقررات')
                                           # ('pusd', 'برنامج موحد ومقررات مفصلة لكل طالب'),
                                           # ('pdsd', 'برامج مفصلة ومقررات مفصلة لكل طالب')
    type_setting       = fields.Selection([('pusu', 'برنامج موحد ومقررات موحدة لكل الطلاب'),
                                           ('pusd', 'برنامج موحد ومقررات مفصلة لكل طالب'),
                                           # ('pdsd', 'برامج مفصلة ومقررات مفصلة لكل طالب')
                                           ], string='إعدادات البرامج والمقررات' ,default="pusu", help=' we make it read only field because -pusd- option no more exist')
    msg_error          = fields.Char()
    msg_error2         = fields.Char()
    #Program
    program_type       = fields.Selection([('open',  'مفتوح'),
                                           ('close', 'محدد')], default='open', string="نوع البرنامج")
    program_id         = fields.Many2one("mk.programs",  required="1"   ,        string="البرنامج")
    approach_id        = fields.Many2one('mk.approaches',required="1"  ,    string='المنهج')
    #Memorize
    is_memorize        = fields.Boolean("الحفظ",           default=True)
    page_id            = fields.Many2one('mk.memorize.method', string='Page')
    surah_from_mem_id  = fields.Many2one("mk.surah",           string="من السورة")
    aya_from_mem_id    = fields.Many2one("mk.surah.verses",    string="من الآية")
    memory_direction   = fields.Selection([('up',   'من الفاتحة للناس'), 
                                           ('down', 'من الناس للفاتحة')],  string='مسار الحفظ')
    save_start_point   = fields.Many2one("mk.subject.page",    string="save start point")
    #Max Review
    is_big_review      = fields.Boolean("المراجعة الكبرى")
    qty_review_id      = fields.Many2one('mk.memorize.method', string='مقدار المراجعة')
    surah_from_rev_id  = fields.Many2one("mk.surah",           string="من السورة")
    aya_from_rev_id    = fields.Many2one("mk.surah.verses",    string="من الآية")
    review_direction   = fields.Selection([('up',   'من الفاتحة للناس'), 
                                           ('down', 'من الناس للفاتحة')],  string='Big review direction')
    start_point        = fields.Many2one("mk.subject.page",    string="from subject")
    #Min review
    is_min_review      = fields.Boolean("المراجعة الصغرى",  default=True)
    #Reading
    is_tlawa           = fields.Boolean('التلاوة')
    qty_read_id        = fields.Many2one('mk.memorize.method', string='مقدار التلاوة')
    surah_from_read_id = fields.Many2one("mk.surah",           string="من السورة")
    aya_from_read_id   = fields.Many2one("mk.surah.verses",    string="من الآية")    
    read_direction     = fields.Selection([('up',   'من الفاتحة للناس'), 
                                           ('down', 'من الناس للفاتحة')],  string='نقطة بداية التلاوة')
    read_start_point   = fields.Many2one("mk.subject.page",    string="مسار التلاوة")
    #Programs
    pgm_ids            = fields.One2many('mk.student.internal_transfer.pgm', 'transfer_id', string='برامج الطلاب')
    #Subjects
    subject_ids        = fields.One2many('mk.student.internal_transfer.subject', 'transfer_id', string='مقررات الطلاب')
    #Days
    domain_days        = fields.Many2many('mk.work.days', string='أيام الحلقة')
    student_days       = fields.Many2many('mk.work.days', string='أيام الطلاب')
    selected_period    = fields.Selection([('subh',  'subh'), 
                                           ('zuhr',  'zuhr'),
                                           ('aasr',  'aasr'),
                                           ('magrib','magrib'),
                                           ('esha','esha')],   string='period')     
    #Type
    type_order         = fields.Selection([('principal', 'إنضمام للجمعية'),
                                           ('assign',    'تنسيب للحلقة'),
                                           ('internal',  'نقل داخلي'),
                                           ('external',  'نقل خارجي'),
                                           ('assign_ep', 'تنسيب للحلقة')], string='النوع')

    @api.onchange('episode_id')
    def _get_program_domain(self):
        if self.episode_id.women_or_men == 'men':
            return {'value': {'program_id': self.episode_id.program_id, 'approach_id': self.episode_id.approache_id},
                    'domain': {'program_id': [('program_gender', '=', 'men')]}}

        if self.episode_id.women_or_men == 'women':
            return {'value': {'program_id': self.episode_id.program_id, 'approach_id': self.episode_id.approache_id},
                    'domain': {'program_id': [('program_gender', '=', 'women')]}}

    @api.onchange('student_ids')
    def onchange_students(self):
        students = self.student_ids
        mosq_id = False
        episode_assign_id = False
        msg_error = ''
        msg_error1 = ''
        gender = ''
        type_order = self.type_order
        domain_mosq = []
        vals_domain = {}
        episodes = []
        online_student = self.env['mk.student.register'].search([('id', 'in', students.ids),
                                                                 ('is_online_student', '=', True)])
        if online_student:
            if len(online_student)!= len(students):
                msg_error = 'الطلبة المختارون مختلطون عن بعد و طلاب عاديين' + ' ' + '!'

        for student in students:
            mosq = student.mosq_id
            mosq_student_id = mosq.id

            student_gender = student.gender
            student_age = student.student_age
            if not gender:
                gender = student.gender
            elif self.episode_id.episode_type.id != self.env.ref('mk_episode_management.episode_type1').id :
                if student_gender and gender != student_gender:
                    msg_error = 'الطلبة المختارون مختلطون ذكور وإناث' + ' ' + '!'
                    break
            elif student_age > 6:
                msg_error = 'الطلبة المختارون للتسجيل في حلقة تعليم صغار يجب أن لا يتجاوز عمرهم 6 سنوات' + ' ' + '!'
                break

            if not mosq_student_id:
                continue

            if not mosq_id:
                mosq_id = mosq_student_id
                domain_mosq = [mosq_id]

                if type_order == 'internal':
                    for link in student.link_ids:
                        mosq_link = link.mosq_id
                        episode = link.episode_id
                        episode_id = episode.id
                        if mosq_link and mosq_link.id == mosq_student_id and episode and episode_id not in episodes:
                            episodes += [episode_id]

            elif mosq_id != mosq_student_id:
                domain_mosq = []
                episodes = []
                msg_error = 'الطلاب المختارون لا ينتمون لنفس المسجد' + ' ' + '!'
                break
            
            elif type_order == 'internal' and not msg_error1:
                episodes_link = []
                for link in student.link_ids:
                    mosq_link = link.mosq_id
                    episode = link.episode_id
                    episode_id = episode.id
                    if mosq_link and mosq_link.id == mosq_student_id and episode and episode_id not in episodes_link:
                        episodes_link += [episode_id]

                if episodes_link:
                    if episodes:
                        episodes = list(set(episodes_link) & set(episodes))
                        if not episodes:
                            msg_error1 = 'الطلاب المختارون لا ينتمون لحلقة مشتركة' + ' ' + '!'
                    else:
                        episodes = episodes_link

        if gender == 'male':
            gender = 'men'
        elif gender == 'female':
            gender = 'women'
        
        if type_order in ['assign', 'internal']:
            vals_domain.update({'mosq_id': [('id', 'in', domain_mosq)]})
            if type_order == 'internal':
                vals_domain.update({'episode_fr_id': [('id', 'in', episodes),
                                                      ('state', '=', 'accept')]})

        elif type_order == 'external':
            vals_domain.update({'mosq_from_id': [('id','in',domain_mosq)],
                           'mosq_id':      domain_mosq and [('id', '!=', mosq_id)] or [('id','in',[])]})
            
        elif type_order == 'assign_ep':
            episode_assign = self.episode_assign_id
            episode_assign_id = episode_assign.id
            gender = episode_assign.women_or_men
            mosq_id = episode_assign.mosque_id.id
            vals_domain.update({'mosq_id': [('id','in',[mosq_id])]})
            
        if msg_error:
            vals_value = {'msg_error':        msg_error,
                          'gender':           gender,
                          'mosq_id':          False,
                          'type_setting_ps':  False,
                          'type_setting':     False,
                          'next_action_pdsd': False}
            if type_order == 'external':
                vals_value.update({'mosq_from_id': False})
                
            vals_domain.update({'mosq_from_id':  [('id','=',[])],
                           'mosq_id':       [('id','=',[])],
                           'episode_fr_id': [('id','in',[])],
                           'episode_id':    [('id','in',[])]})
        
        elif msg_error1:
            vals_value = {'mosq_id':          mosq_id,
                          'msg_error':        msg_error1,
                          'gender':           gender,
                          'episode_fr_id':    False,
                          'episode_id':       False,
                          'type_setting_ps':  False,
                          'type_setting':     False,
                          'next_action_pdsd': False}
             
            vals_domain.update({'mosq_id':       [('id','=',[])],
                           'episode_fr_id': [('id','in',[])],
                           'episode_id':    [('id','in',[])]})
        
        else:
            vals_value = {'mosq_from_id':     (type_order == 'external') and mosq_id or False,
                          'mosq_id':          (type_order != 'external') and mosq_id or False,
                          'gender':           gender,
                          'msg_error':        msg_error,
                          'episode_fr_id':    (type_order == 'internal') and episodes and episodes[0] or False,
                          'type_setting':     "pusu",
                          'next_action_pdsd': False}
            domain = [('mosque_id','=',mosq_id),
                      ('women_or_men','=', gender),
                      ('study_class_id.is_default', '=', True),
                      ('state','in',['draft','accept'])]
            if students and students[0].is_online_student:
                domain += [('is_online', '=', True)]
            vals_domain.update({'episode_id': domain})
            
            if type_order == 'assign_ep':
                vals_value.update({'episode_id':      episode_assign_id,
                                   
                                   'domain_days':     episode_assign.episode_days,
                                   'student_days':    episode_assign.episode_days,
                                   'selected_period': episode_assign.selected_period,})
                
                vals_domain.update({'episode_id': [('id','in',[episode_assign_id]),
                                                   ('state','=','accept')]})

        return {'value': vals_value, 'domain': vals_domain}

        
    @api.onchange('mosq_id')
    def onchange_mosq_id(self):
        self.episode_id = False
        domain = []
        if self.student_ids and self.student_ids[0].is_online_student:
            domain += [('is_online', '=', True)]
        episode_ids = self.env['mk.episode'].search(domain +[('mosque_id','=',self.mosq_id.id),
                                                             ('study_class_id.is_default', '=', True),
                                                             ('state','in',['draft','accept'])])
        return {'domain':{'episode_id': [('id', 'in', episode_ids.ids)]}}


    @api.onchange('episode_id','registeration_date','msg_error')
    def onchange_episode(self):
        self.domain_days = ()
        self.student_days = ()
        episode = self.episode_id
        registeration_date = self.registeration_date
        msg_error = ''
        if episode:
            self.domain_days = episode.episode_days
            self.student_days = episode.episode_days
            self.selected_period = episode.selected_period


            start_episode = episode.start_date
            if registeration_date:                
                if start_episode and registeration_date < start_episode:
                    msg_error = 'عذرا، تاريخ العملية يجب أن يكون بعد تاريخ بداية الحلقة' + ' ! '
                    self.registeration_date = False
                
                end_episode = episode.end_date
                if end_episode and registeration_date > end_episode:
                    msg_error = 'عذرا، تاريخ العملية يجب أن يكون قبل تاريخ نهاية الحلقة' + ' ! '
                    self.registeration_date = False
                    
                if not self.msg_error:
                    self.msg_error2 = msg_error
            else:
                self.registeration_date = start_episode
                self.msg_error2 = ''




    @api.onchange('type_setting')
    def onchange_type_setting(self):
        type_setting = "pusu"
        self.pgm_ids = ()
        self.subject_ids = ()
        self.next_action_pdsd = False
        # program_type = False
        
        if type_setting == 'pdsd':
            pgm_ids = []
            for student in self.student_ids:
                pgm_ids += [(0,0,{'student_id':   student.id,
                                  'domain_days':  self.domain_days,
                                  'student_days': self.domain_days,})]
            self.pgm_ids = pgm_ids
            self.student_days = ()
        
        elif type_setting == 'pusd':            
            self.student_days = self.domain_days
            # program_type = 'open'
            
            program_id = self.program_id.id
            
            if program_id:
                subject_ids = []
                for student in self.student_ids:
                    student_id = student.id
                    if self.is_memorize:
                        subject_ids += [(0,0,{'student_id':   student_id,
                                              'program_id':   program_id,
                                              'type_subject': 'm'})]
                    if self.is_big_review:
                        subject_ids += [(0,0,{'student_id':   student_id,
                                              'program_id':   program_id,
                                              'type_subject': 'r'})]
                    if self.is_tlawa:
                        subject_ids += [(0,0,{'student_id':   student_id,
                                              'program_id':   program_id,
                                              'type_subject': 't'})]                                        
                self.subject_ids = subject_ids            
            
        # self.program_type = program_type
        
    @api.onchange('program_type')
    def onchange_program_type(self):
        students = self.student_ids
        if students and not students[0].is_student_meqraa:
            self.program_id = False
            self.approach_id = False
        
    @api.onchange('program_id')
    def onchange_pgm(self):
        students = self.student_ids
        if students and not students[0].is_student_meqraa:

            self.page_id = False
            self.surah_from_mem_id = False
            self.memory_direction = False

            self.qty_review_id = False
            self.surah_from_rev_id = False
            self.review_direction = False

            self.qty_read_id = False
            self.surah_from_read_id = False
            self.read_direction = False

            self.subject_ids = ()
            type_setting = "pusu"
            program = self.program_id

            is_big_review = self.is_big_review
            is_memorize = self.is_memorize
            is_tlawa = self.is_tlawa
            if program:
                program_id = program.id
                if type_setting == 'pusd':
                    self.student_days = self.domain_days
                    subject_ids = []
                    for student in self.student_ids:
                        student_id = student.id
                        if is_memorize:
                            subject_ids += [(0,0,{'student_id':   student_id,
                                                  'program_id':   program_id,
                                                  'type_subject': 'm'})]
                        if is_big_review:
                            subject_ids += [(0,0,{'student_id':   student_id,
                                                  'program_id':   program_id,
                                                  'type_subject': 'r'})]
                        if is_tlawa:
                            subject_ids += [(0,0,{'student_id':   student_id,
                                                  'program_id':   program_id,
                                                  'type_subject': 't'})]
                    self.subject_ids = subject_ids
        program = self.program_id
        if program:
            self.is_tlawa = program.reading
            self.is_big_review = program.maximum_audit
            self.is_min_review = program.minimum_audit
            self.is_memorize = program.memorize


    @api.onchange('memory_direction')
    def onchange_memory_direction(self):
        students = self.student_ids
        if students and not students[0].is_student_meqraa:
            self.page_id = False
            self.surah_from_mem_id = False
        
    @api.onchange('review_direction')
    def onchange_review_direction(self):
        self.qty_review_id = False
        self.surah_from_rev_id = False
        
    @api.onchange('read_direction')
    def onchange_read_direction(self):
        self.qty_read_id = False
        self.surah_from_read_id = False 
                                
    @api.onchange('surah_from_mem_id','page_id')
    def onchange_surah_qty_memorize(self):
        surah_from_mem_id = self.surah_from_mem_id.id
        qty_mem_id = self.page_id.id
        students = self.student_ids
        if students and not students[0].is_student_meqraa:
            aya_ids = []
            start_pt_ids = []
            if surah_from_mem_id and qty_mem_id:
                start_pts = self.env['mk.subject.page'].search([('subject_page_id','=',qty_mem_id),
                                                                ('from_surah','=',surah_from_mem_id)])

                for start_pt in start_pts:
                    start_pt_ids += [start_pt.id]
                    aya_ids += [start_pt.from_verse.id]

            self.aya_from_mem_id = False
            self.save_start_point = False

            return {'domain':{'aya_from_mem_id': [('id', 'in', aya_ids)],
                              'save_start_point': [('id', 'in', start_pt_ids)]}}

        
    @api.onchange('aya_from_mem_id')
    def onchange_aya_from_memory(self):
        aya_from = self.aya_from_mem_id.id
        qty_id = self.page_id.id
        start_pt = False

        if aya_from and qty_id:
            start_pt = self.env['mk.subject.page'].search([('subject_page_id','=',qty_id),
                                                           ('from_verse','=',aya_from)], limit=1)

        self.save_start_point = start_pt and start_pt.id or False            

    @api.onchange('surah_from_rev_id','qty_review_id')
    def onchange_surah_qty_review(self):
        surah_from_rev_id = self.surah_from_rev_id.id
        qty_review_id = self.qty_review_id.id

        aya_ids = []
        start_pt_ids = []
        if surah_from_rev_id and qty_review_id:
            start_pts = self.env['mk.subject.page'].search([('subject_page_id','=',qty_review_id),
                                                            ('from_surah','=',surah_from_rev_id)])
                        
            for start_pt in start_pts:
                start_pt_ids += [start_pt.id]
                aya_ids += [start_pt.from_verse.id]
        
        self.aya_from_rev_id = False
        self.start_point = False
        
        return {'domain':{'aya_from_rev_id': [('id', 'in', aya_ids)],
                          'start_point': [('id', 'in', start_pt_ids)]}}
        
    @api.onchange('aya_from_rev_id')
    def onchange_aya_from_review(self):
        aya_from = self.aya_from_rev_id.id
        qty_id = self.qty_review_id.id
        start_pt = False

        if aya_from and qty_id:
            start_pt = self.env['mk.subject.page'].search([('subject_page_id','=',qty_id),
                                                           ('from_verse','=',aya_from)], limit=1)

        self.start_point = start_pt and start_pt.id or False  
        
    @api.onchange('surah_from_read_id','qty_read_id')
    def onchange_surah_qty_read(self):
        surah_from_read = self.surah_from_read_id
        qty_read = self.qty_read_id

        aya_ids = []
        start_pt_ids = []
        if surah_from_read and qty_read:
            start_pts = self.env['mk.subject.page'].search([('subject_page_id','=',qty_read.id),
                                                            ('from_surah','=',surah_from_read.id)])
                        
            for start_pt in start_pts:
                start_pt_ids += [start_pt.id]
                aya_ids += [start_pt.from_verse.id]
        
        self.aya_from_read_id = False
        self.read_start_point = False
        
        return {'domain':{'aya_from_read_id': [('id', 'in', aya_ids)],
                          'read_start_point': [('id', 'in', start_pt_ids)]}}

    @api.onchange('aya_from_read_id')
    def onchange_aya_from_read(self):
        aya_from = self.aya_from_read_id.id
        qty_id = self.qty_read_id.id
        start_pt = False

        if aya_from and qty_id:
            start_pt = self.env['mk.subject.page'].search([('subject_page_id','=',qty_id),
                                                           ('from_verse','=',aya_from)], limit=1)

        self.read_start_point = start_pt and start_pt.id or False        
    
    @api.onchange('next_action_pdsd')
    def onchange_next_action_pdsd(self):
        next_action_pdsd = self.next_action_pdsd
        if next_action_pdsd == 'sbj':
            subjects = []
            for pgm in self.pgm_ids:
                if pgm.program_type != 'open':
                    continue
                
                program = pgm.program_id
                program_id = program.id
                student_id = pgm.student_id.id
                               
                is_big_review = program.maximum_audit
                is_memorize = program.memorize
                is_tlawa = program.reading                
                vals_subject = {'student_id':   student_id,
                                'program_id':   program_id,
                                'program_type': pgm.program_type,
                                'approach_id':  pgm.approach_id,
                                'student_days': pgm.student_days,}

                if is_memorize:
                    vals_memor = {}
                    vals_memor.update(vals_subject)
                    vals_memor.update({'type_subject': 'm'})                    
                    subjects += [(0,0,vals_memor)]
                    
                if is_big_review:
                    vals_review = {}
                    vals_review.update(vals_subject)
                    vals_review.update({'type_subject': 'r'})                    
                    subjects += [(0,0,vals_review)]
                    
                if is_tlawa:
                    vals_tlawa = {}
                    vals_tlawa.update(vals_subject)
                    vals_tlawa.update({'type_subject': 't'})
                    subjects += [(0,0,vals_tlawa)]
            self.subject_ids = subjects

        else:
            self.subject_ids = ()
    
    @api.model
    def cancel_link(self, type_order, student_id, episode_id, mosq_from_id):
        domain = [('student_id','=',student_id)]
        if type_order == 'internal':
            domain += [('episode_id','=',episode_id)]
        else:
            domain += [('mosq_id','=',mosq_from_id)]
        
        links = self.env['mk.link'].search(domain)
        if links:
            vals_write = {'action_done': type_order}
            for link in links:
                if link.state == 'accept':
                    link.state = 'done'
            
#             link_id = link.id            
#             prepa = link.preparation_id            
#             if prepa:
#                 listens = self.env['mk.listen.line'].search([('state','=','draft'),
#                                                              '|',
#                                                              ('save_id','=',link_id),
#                                                              '|',
#                                                              ('sr_line_id','=',link_id),
#                                                              '|',
#                                                              ('br_line_id','=',link_id),
#                                                              ('reci_line_id','=',link_id),])
#                 if listens:
#                     listens.unlink()

            links.write(vals_write)
    
    # @api.one
    def action_assign_episode(self):
        type_setting_ps = self.type_setting_ps
        type_setting = "pusu"
        type_order = self.type_order
        episode_id = self.episode_id.id
        episode_from_id = self.episode_fr_id.id
        mosq_from_id = self.mosq_from_id.id
        mosq_id = self.mosq_id.id
        if not self.episode_id.teacher_id :
            raise ValidationError(_('عذرا ! لابد من اختيار معلم للحلقة أولا'))
        else:
            vals = {'year':               self.year.id,
                    'registeration_date': self.registeration_date,
                    'mosq_id':            mosq_id,
                    'episode_id':         episode_id,
                    'selected_period':    self.selected_period,
                    'domain_days':        self.episode_id.episode_days,
                    'type_order':         type_order,
                    'state':              'accept',
                    'is_memorize': self.is_memorize,
                    'is_min_review': self.is_min_review,
                    'is_big_review': self.is_big_review,
                    'is_tlawa': self.is_tlawa,
                    }
            if not self.student_ids:
                msg = 'الرجاء تحديد قائمة الطلاب' + ' ' + '!'
                raise ValidationError(msg)

            if not type_setting and not type_setting_ps:
                msg = 'الرجاء تحديد نوعية إعدادات البرامج والمقررات' + ' ' + '!'
                raise ValidationError(msg)

            if type_setting_ps == 'psss':
                domain = []
                name_msg = ' '
                if type_order == 'internal':
                    domain = [('episode_id','=',episode_from_id)]
                    name_msg = ' ' + 'حلقة'
                    name_msg = ' "' + self.episode_fr_id.name + '" ' + '!'

                elif type_order == 'external':
                    domain = [('mosq_id','=',mosq_from_id)]
                    name_msg = ' ' + 'مسجد'
                    name_msg = ' "' + self.mosq_from_id.name + '" ' + '!'

                domain += [('program_id','!=',False),
                           ('approach_id','!=',False)]

                for student in self.student_ids:
                    student_id = student.id
                    domain_link = domain + [('student_id','=',student_id)]
                    prev_link = self.env['mk.link'].search(domain_link, limit=1)
                    if not prev_link:
                        msg = 'الطالب'
                        msg += ' "' + student.display_name + '" '
                        msg += 'ليس لديه برنامج محدد في'
                        msg += name_msg

                        raise ValidationError(msg)

                    vals.update({'program_type': prev_link.program_type,
                                 'program_id':   prev_link.program_id.id,
                                 'approache':    prev_link.approach_id.id,
                                 'student_days': [(6,0, [day.id for day in prev_link.student_days])],
                                 'student_id':   student_id})

                    if prev_link.is_memorize:
                        vals.update({'page_id':           prev_link.page_id.id,
                                     'surah_from_mem_id': prev_link.surah_from_mem_id.id,
                                     'aya_from_mem_id':   prev_link.aya_from_mem_id.id,
                                     'memory_direction':  prev_link.memory_direction,
                                     'save_start_point':  prev_link.save_start_point.id,})

                    if prev_link.is_big_review:
                        vals.update({'qty_review_id':     prev_link.qty_review_id.id,
                                     'surah_from_rev_id': prev_link.surah_from_rev_id.id,
                                     'aya_from_rev_id':   prev_link.aya_from_rev_id.id,
                                     'review_direction':  prev_link.review_direction,
                                     'start_point':       prev_link.start_point.id,})

                    if prev_link.is_tlawa:
                        vals.update({'qty_read_id':        prev_link.qty_read_id.id,
                                     'surah_from_read_id': prev_link.surah_from_read_id.id,
                                     'aya_from_read_id':   prev_link.aya_from_read_id.id,
                                     'read_direction':     prev_link.read_direction,
                                     'read_start_point':   prev_link.read_start_point.id,})

                    self.cancel_link(type_order, student_id, episode_from_id, mosq_from_id)
                    prev_mosq = student.mosq_id
                    if type_order == 'external' or not prev_mosq:
                        student.mosq_id = mosq_id

                    link = self.env['mk.link'].create(vals)
                    link.create_student_preparation()

            if type_setting in ['pusu','pusd']:

                vals.update({'program_type': self.program_type,
                             'program_id':   self.program_id.id,
                             'approache':    self.approach_id.id,
                             'student_days': [(6,0, [day.id for day in self.student_days])],})
                if type_setting == 'pusu':
                    if self.is_memorize:
                        vals.update({'page_id':           self.page_id.id,
                                     'surah_from_mem_id': self.surah_from_mem_id.id,
                                     'aya_from_mem_id':   self.aya_from_mem_id.id,
                                     'memory_direction':  self.memory_direction,
                                     'save_start_point':  self.save_start_point.id,})

                    if self.is_big_review:
                        vals.update({'qty_review_id':     self.qty_review_id.id,
                                     'surah_from_rev_id': self.surah_from_rev_id.id,
                                     'aya_from_rev_id':   self.aya_from_rev_id.id,
                                     'review_direction':  self.review_direction,
                                     'start_point':       self.start_point.id,})

                    if self.is_tlawa:
                        vals.update({'qty_read_id':        self.qty_read_id.id,
                                     'surah_from_read_id': self.surah_from_read_id.id,
                                     'aya_from_read_id':   self.aya_from_read_id.id,
                                     'read_direction':     self.read_direction,
                                     'read_start_point':   self.read_start_point.id,})

                    for student in self.student_ids:
                        student_id = student.id
                        if type_order in ['internal','external']:
                            self.cancel_link(type_order, student_id, episode_from_id, mosq_from_id)

                        prev_mosq = student.mosq_id
                        if type_order == 'external' or not prev_mosq:
                            student.mosq_id = mosq_id

                        vals.update({'student_id': student_id})
                        link = self.env['mk.link'].create(vals)
                        link.create_student_preparation()
                else:
                    vals.update({'program_type': 'open'})
                    prev_student = False
                    prev_order = False
                    for subject in sorted(self.subject_ids, key=lambda sbj: sbj.student_id):
                        type_subject = subject.type_subject

                        if type_subject == 'm':
                            vals.update({'page_id':           subject.qty_id.id,
                                         'surah_from_mem_id': subject.surah_from_id.id,
                                         'aya_from_mem_id':   subject.aya_from_id.id,
                                         'memory_direction':  subject.direction,
                                         'save_start_point':  subject.start_point_id.id,})

                        elif type_subject == 'r':
                            vals.update({'qty_review_id':     subject.qty_id.id,
                                         'surah_from_rev_id': subject.surah_from_id.id,
                                         'aya_from_rev_id':   subject.aya_from_id.id,
                                         'review_direction':  subject.direction,
                                         'start_point':       subject.start_point_id.id,})

                        elif type_subject == 't':
                            vals.update({'qty_read_id':        subject.qty_id.id,
                                         'surah_from_read_id': subject.surah_from_id.id,
                                         'aya_from_read_id':   subject.aya_from_id.id,
                                         'read_direction':     subject.direction,
                                         'read_start_point':   subject.start_point_id.id,})
                        student = subject.student_id
                        student_id = student.id
                        if prev_student != student_id:
                            if prev_order:
                                prev_order.create_student_preparation()
                            if type_order in ['internal','external']:
                                self.cancel_link(type_order, student_id, episode_from_id, mosq_from_id)

                            prev_mosq = student.mosq_id
                            if type_order == 'external' or not prev_mosq:
                                student.mosq_id = mosq_id

                            vals.update({'student_id': student_id,})
                            prev_order = self.env['mk.link'].create(vals)
                            prev_student = student_id
                        else:
                            prev_order.write(vals)

                    if prev_order:
                        prev_order.create_student_preparation()

            else:
                prev_student = False
                prev_order = False

                if not self.subject_ids and not self.pgm_ids:
                    msg = 'الرجاء إتمام إعدادات البرامج والمقررات' + ' ' + '!'
                    raise ValidationError(msg)

                for subject in sorted(self.subject_ids, key=lambda sbj: sbj.student_id):
                    type_subject = subject.type_subject
                    if type_subject == 'm':
                        vals.update({'page_id':           subject.qty_id.id,
                                     'surah_from_mem_id': subject.surah_from_id.id,
                                     'aya_from_mem_id':   subject.aya_from_id.id,
                                     'memory_direction':  subject.direction,
                                     'save_start_point':  subject.start_point_id.id,})

                    elif type_subject == 'r':
                        vals.update({'qty_review_id':     subject.qty_id.id,
                                     'surah_from_rev_id': subject.surah_from_id.id,
                                     'aya_from_rev_id':   subject.aya_from_id.id,
                                     'review_direction':  subject.direction,
                                     'start_point':       subject.start_point_id.id,})

                    elif type_subject == 't':
                        vals.update({'qty_read_id':        subject.qty_id.id,
                                     'surah_from_read_id': subject.surah_from_id.id,
                                     'aya_from_read_id':   subject.aya_from_id.id,
                                     'read_direction':     subject.direction,
                                     'read_start_point':   subject.start_point_id.id,})
                    student = subject.student_id
                    student_id = student.id
                    if prev_student != student_id:
                        if prev_order:
                            prev_order.create_student_preparation()
                        if type_order in ['internal','external']:
                            self.cancel_link(type_order, student_id, episode_from_id, mosq_from_id)

                        prev_mosq = student.mosq_id
                        if type_order == 'external' or not prev_mosq:
                            student.mosq_id = mosq_id

                        vals.update({'student_id':   student_id,
                                     'program_type': subject.program_type,
                                     'program_id':   subject.program_id.id,
                                     'approache':    subject.approach_id.id,
                                     'student_days': [(6,0, [day.id for day in subject.student_days])],})
                        prev_order = self.env['mk.link'].create(vals)
                        prev_student = student_id
                    else:
                        prev_order.write(vals)

                if prev_order:
                    prev_order.create_student_preparation()

                if not self.pgm_ids:
                    msg = 'الرجاء إتمام إعدادات البرامج والمقررات' + ' ' + '!'
                    raise ValidationError(msg)

                for pgm in self.pgm_ids:
                    program_type = pgm.program_type
                    if program_type != 'close':
                        continue
                    student = pgm.student_id
                    student_id = student.id

                    vals.update({'student_id':   student_id,
                                 'program_type': 'close',
                                 'program_id':   pgm.program_id.id,
                                 'approache':    pgm.approach_id.id,
                                 'student_days': [(6,0, [day.id for day in pgm.student_days])],})
                    prev_order = self.env['mk.link'].create(vals)
                    prev_order.create_student_preparation()

                    if type_order in ['internal','external']:
                        self.cancel_link(type_order, student_id, episode_from_id, mosq_from_id)

                    if type_order == 'external' or not student.mosq_id:
                        student.mosq_id = mosq_id

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(InternalTransfer, self).fields_view_get(
    #         view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     context = self._context
    #     if context.get('active_model') == 'mk.episode' and context.get('active_id'):
    #         episode = self.env['mk.episode'].browse(context['active_id'])

    #         student_vals = episode.action_assign_student_from_episode()

    #         if 'domain' in student_vals:
    #             doc = etree.XML(res['arch'])
    #             for node in doc.xpath("//field[@name='student_ids']"):
    #                 node.set('domain', repr(student_vals.get('domain')))
    #                 setup_modifiers(node, res['fields']['student_ids'])
    #             res['arch'] = etree.tostring(doc, encoding='utf-8')
    #     return res


class InternalTransferPgm(models.TransientModel):
    _name = 'mk.student.internal_transfer.pgm'

    # @api.one
    @api.depends('student_id')
    def get_student_name(self):
        student = self.student_id
        self.student_name = student and student.display_name or ' '

    
    student_id         = fields.Many2one('mk.student.register', string="الطالب", ondelete='cascade')
    student_name       = fields.Char("الطالب",   compute=get_student_name, store=True)

    transfer_id        = fields.Many2one('mk.student.internal_transfer')
    #Program
    program_type       = fields.Selection([('open',  'مفتوح'),
                                           ('close', 'محدد')], string="نوع البرنامج")
    program_id         = fields.Many2one("mk.programs",        string="البرنامج")
    approach_id        = fields.Many2one('mk.approaches',      string='المنهج')        
    #Days
    domain_days        = fields.Many2many('mk.work.days', string='أيام الحلقة')
    student_days       = fields.Many2many('mk.work.days', string='أيام الطالب')    

    @api.onchange('program_type')
    def onchange_program_type(self):
        self.program_id = False

    @api.onchange('program_id')
    def onchange_pgm(self):
        self.approach_id = False

      
class InternalTransferSubject(models.TransientModel):
    _name = 'mk.student.internal_transfer.subject'
    
    # @api.one
    @api.depends('student_id')
    def get_student_name(self):
        student = self.student_id
        self.student_name = student and student.display_name or ' '
        
    # @api.one
    @api.depends('program_id')
    def get_pgm_name(self):
        program = self.program_id
        self.program_name = program and program.name or ' '
        
    # @api.one
    @api.depends('type_sbj')
    def get_type_sbj(self):
        type_subject = self.type_subject
        type_sbj = ' '
        if type_subject == 'm':
            type_sbj = 'الحفظ'
        elif type_subject == 'r':
            type_sbj = 'المراجعة الكبرى'
        elif type_subject == 't':
            type_sbj = 'التلاوة'
                                    
        self.type_sbj = type_sbj               
        
    student_id     = fields.Many2one('mk.student.register', string="الطالب", ondelete='cascade')
    transfer_id    = fields.Many2one('mk.student.internal_transfer')
    #Program
    program_type   = fields.Selection([('open',  'مفتوح'),
                                       ('close', 'محدد')], string="نوع البرنامج")
    program_id     = fields.Many2one("mk.programs",        string="البرنامج")
    approach_id    = fields.Many2one('mk.approaches',      string='المنهج')  
    #Action    
    type_subject   = fields.Selection([('m','الحفظ'),
                                      ('r','المراجعة الكبرى'),
                                      ('t','التلاوة')],     string='الإجراء')    
    qty_id         = fields.Many2one('mk.memorize.method', string='المقدار')
    surah_from_id  = fields.Many2one("mk.surah",           string="من السورة")
    aya_from_id    = fields.Many2one("mk.surah.verses",    string="من الآية")    
    direction      = fields.Selection([('up',   'من الفاتحة للناس'),
                                       ('down', 'من الناس للفاتحة')], string="المسار")
    start_point_id = fields.Many2one("mk.subject.page", string='نقطة بداية' )
    #Days
    domain_days    = fields.Many2many('mk.work.days', string='أيام الحلقة')
    student_days   = fields.Many2many('mk.work.days', string='أيام الطالب')
    #Compute
    student_name   = fields.Char("الطالب",   compute=get_student_name, store=True)
    program_name   = fields.Char("البرنامج", compute=get_pgm_name,     store=True)
    type_sbj       = fields.Char("الإجراء",   compute=get_type_sbj,     store=True)
    
    @api.onchange('direction')
    def onchange_direction(self):
        self.qty_id = False   
        self.surah_from_id = False    
    
    @api.onchange('surah_from_id','qty_id')
    def onchange_surah_qty_read(self):
        surah_from = self.surah_from_id
        qty = self.qty_id

        aya_ids = []
        start_pt_ids = []
        if surah_from and qty:
            start_pts = self.env['mk.subject.page'].search([('subject_page_id','=',qty.id),
                                                            ('from_surah','=',surah_from.id)])

            for start_pt in start_pts:
                start_pt_ids += [start_pt.id]
                aya_ids += [start_pt.from_verse.id]

        self.aya_from_id = False
        self.start_point_id = False

        return {'domain':{'aya_from_id': [('id', 'in', aya_ids)],
                          'start_point_id': [('id', 'in', start_pt_ids)]}}
        
    @api.onchange('aya_from_id')
    def onchange_aya_from(self):
        aya_from = self.aya_from_id.id
        qty_id = self.qty_id.id
        start_pt = False

        if aya_from and qty_id:
            start_pt = self.env['mk.subject.page'].search([('subject_page_id','=',qty_id),
                                                           ('from_verse','=',aya_from)], limit=1)

        self.start_point_id = start_pt and start_pt.id or False         


class Clearance(models.TransientModel):
    _name = 'mk.student.clearance'
    
    @api.model
    def _getDefault_academic_year(self):
        academic_year = self.env['mk.study.year'].search([('is_default','=',True)], limit=1)
        return academic_year and academic_year.id or False 

    student_ids  = fields.Many2many('mk.student.register', string="الطلاب") 
    year         = fields.Many2one('mk.study.year',        string='العام الدراسي', readonly=True, default=_getDefault_academic_year)
    mosque_id    = fields.Many2one('mk.mosque',            string='المسجد', required=True)
    msg_error    = fields.Char()
    
    @api.onchange('student_ids')
    def onchange_students(self):
        students = self.student_ids
        mosq_id = False
        msg_error = ''
        domain_mosq = []
        for student in students:
            mosq = student.mosq_id
            mosq_student_id = mosq.id

            if not mosq_student_id:
                continue

            if not mosq_id:
                mosq_id = mosq_student_id
                domain_mosq = [mosq_id]
        
            elif mosq_id != mosq_student_id:
                msg_error = 'الطلاب المختارون لا ينتمون لنفس المسجد' + ' ' + '!'
                break
            
        if msg_error:
            vals_value = {'mosque_id': False,
                          'msg_error': msg_error}
             
            vals_domain = {'mosque_id': [('id','in',[])]}
        
        else:
            vals_value = {'mosque_id': mosq_id,
                          'msg_error': msg_error}
            
            vals_domain = {'mosque_id': [('id','in',domain_mosq)]}
            
        return {'value': vals_value, 'domain': vals_domain}    
    
    # @api.one
    def action_create(self):
        vals = {'year':      self.year.id,
                'mosque_id': self.mosque_id.id}
        
        for student in self.student_ids:
            vals_clearance = {'student': student.id}
            vals_clearance.update(vals)
            self.env['mk.clearance'].create(vals_clearance)
