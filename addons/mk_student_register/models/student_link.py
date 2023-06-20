# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import Warning, ValidationError
import collections

import logging

from lxml import etree
# from odoo.osv.orm import setup_modifiers
_logger = logging.getLogger(__name__)


class link_student(models.Model):
    _name = 'mk.link'
    _description = 'link students to stages'
    _rec_name = "student_id"
        
    """ The summary line for a class docstring should fit on one line.
    Fields:
      name (Char): Human readable name which will identify each record.
    """

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(link_student, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     context = self._context
    #     if context.get('active_model') == 'mk.student.register' and context.get('active_id'):
    #         student = self.env['mk.student.register'].browse(context['active_id'])
    #         student_vals = student.action_request()
    #         if 'domain' in student_vals:
    #             doc = etree.XML(res['arch'])
    #             for node in doc.xpath("//field[@name='episode_id']"):
    #                 node.set('domain', repr(student_vals.get('domain')))
    #                 setup_modifiers(node, res['fields']['episode_id'])
    #             res['arch'] = etree.tostring(doc, encoding='utf-8')
    #     return res

    @api.model
    def _getDefault_academic_year(self):
        academic_year = self.env['mk.study.year'].search([('is_default','=',True)], limit=1)
        return academic_year and academic_year.id or False

    # @api.one
    # @api.depends('episode_id')
    # def get_episode_days(self):
    #     self.ensure_one()
    #     days = set()
    #     for episode_day in self.episode_id.episode_days:
    #         days.add(episode_day.id)
    #     self.domain_days = list(days)

    def _default_error_msg(self):
        return "طلب الانظمام لحلقة منتهية الرجاء استخدام اجراء الية تنسيب الطالب لحلقة"

    @api.onchange('episode_id')
    def _get_program_domain(self):
        if self.episode_id.women_or_men == 'men':
            return {'value': {'program_id': self.episode_id.program_id, 'approache': self.episode_id.approache_id},
                    'domain': {'program_id': [('program_gender', '=', 'men')]}}

        if self.episode_id.women_or_men == 'women':
            return {'value': {'program_id': self.episode_id.program_id, 'approache': self.episode_id.approache_id},
                    'domain': {'program_id': [('program_gender', '=', 'women')]}}

    student_id         = fields.Many2one('mk.student.register', string="Student", ondelete='cascade', index=True)
    year               = fields.Many2one('mk.study.year',       string='Study Year', readonly=True, default=_getDefault_academic_year, ondelete="restrict", copy=False)    
    registeration_date = fields.Date(default=datetime.today().strftime('%Y-%m-%d'), string='التاريخ', copy=False)
    mosq_id            = fields.Many2one('mk.mosque',      string='Mosque',  ondelete="restrict")
    episode_id         = fields.Many2one('mk.episode',     string="Episode", ondelete="restrict", required=True, copy=False, index=True)
    # domain_days        = fields.Many2many('mk.work.days', 'mk_link_mk_work_days_rel', 'mk_link_id', 'mk_work_days_id', string='أيام الحلقة', compute=get_episode_days, store=True)
    # domain_days        = fields.Many2many('mk.work.days', 'mk_link_mk_work_days_rel', 'mk_link_id', 'mk_work_days_id', string='أيام الحلقة')
    student_days       = fields.Many2many('mk.work.days', 'mk_link_student_days_rel', 'mk_link_id', 'mk_work_days_id', string='أيام الطالب',  ondelete="restrict")
    
    academic_id        = fields.Many2one('mk.study.year',  string='العام الدراسي', related='episode_id.academic_id', copy=False)
    study_class_id     = fields.Many2one('mk.study.class', string='الفصل الدراسي', related='episode_id.study_class_id', copy=False)
    department_id      = fields.Many2one('hr.department',  string='المركز',        related='mosq_id.center_department_id')
    teacher_id         = fields.Many2one('hr.employee',    string='المعلم',        related='episode_id.teacher_id')
    # grade_id           = fields.Many2one('mk.grade',       string='المرحلة', compute='get_student_grade', store=True, related=False)
    qty_memor_total    = fields.Float(                     string='المقدار',       related='approach_id.memorize_minimum_audit')
    start_date_episode = fields.Date('تاريخ البداية', related='episode_id.start_date')
    end_date_episode   = fields.Date('تاريخ الإنتهاء', related='episode_id.end_date')
    type_order         = fields.Selection([('principal', 'إنضمام للجمعية'),
                                           ('assign',    'تنسيب للحلقة'),
                                           ('internal',  'نقل داخلي'),
                                           ('external',  'نقل خارجي'),
                                           ('assign_ep', 'تنسيب للحلقة'),], string='النوع', default='principal')
    action_done        = fields.Selection([('internal',  'نقل داخلي'),
                                           ('external',  'نقل خارجي'),
                                           ('ep_done',   'نهاية الحلقة'),
                                           ('clear',     'إخلاء طرف'),], string='إجراء الإنهاء', copy=False)
    #Program
    program_type       = fields.Selection([('open',  'مفتوح'),
                                           ('close', 'محدد')], string="program type", default='open')
    program_id         = fields.Many2one("mk.programs",      string="program name")
    approach_id        = fields.Many2one('mk.approaches',      string='Approach', ondelete="restrict")
    #Memorize
    is_memorize        = fields.Boolean("الحفظ",               default=True)
    page_id            = fields.Many2one('mk.memorize.method', string='Page',     ondelete="restrict")
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
    is_min_review      = fields.Boolean("المراجعة الصغرى", default=True)
    #Reading
    is_tlawa           = fields.Boolean('التلاوة')
    qty_read_id        = fields.Many2one('mk.memorize.method', string='مقدار التلاوة')
    surah_from_read_id = fields.Many2one("mk.surah",           string="من السورة")
    aya_from_read_id   = fields.Many2one("mk.surah.verses",    string="من الآية")    
    read_direction     = fields.Selection([('up',   'من الفاتحة للناس'), 
                                           ('down', 'من الناس للفاتحة')],  string='نقطة بداية التلاوة')
    read_start_point   = fields.Many2one("mk.subject.page",    string="مسار التلاوة")    
    preparation_id     = fields.Many2one('mk.student.prepare', string='التحضير', copy=False)
    state              = fields.Selection([('draft',  'Draft'),
                                           ('accept', 'Accept'),
                                           ('stopped', 'Stopped'),
                                           ('done',   'منتهي'),
                                           ('reject', 'Reject'),
                                           ('cancel', 'Canceled'),], string="State", default='draft', index=True)
    selected_period    = fields.Selection([('subh',  'subh'), 
                                           ('zuhr',  'zuhr'),
                                           ('aasr',  'aasr'),
                                           ('magrib','magrib'),
                                           ('esha','esha')],   string='period')
    period_id          = fields.Many2one('mk.periods',         string='Period',   ondelete="restrict")    
    subh               = fields.Boolean('Subh')
    zuhr               = fields.Boolean('Zuhr')
    aasr               = fields.Boolean('Aasr')
    magrib             = fields.Boolean('Magrib')
    esha               = fields.Boolean('Esha')    
    approache          = fields.Many2one("mk.approaches", string="Approaches", ondelete="restrict")    
    gender             = fields.Selection([('men',   'رجالية'),
                                           ('women', 'نسائية')], string='النوع', default='men')
    part_id            = fields.Many2many("mk.parts",           string="part", related='student_id.part_id')
    registeration_code = fields.Char(related='student_id.registeration_code', size=12, readonly=True)
    mosque_id          = fields.Many2one('mk.mosque',          string='Mosque',   ondelete="restrict")
    msg_error          = fields.Char(default=_default_error_msg)

    # @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "%s/ %s" % (record.student_id.display_name, record.episode_id.name)))

        return result

    # @api.depends('student_id')
    # def get_student_grade(self):
    #     for rec in self:
    #         student_id = rec.student_id
    #         rec.sudo().write({'grade_id': student_id.grade_id and student_id.grade_id.id or False})

    @api.onchange('episode_id')
    def onchange_episode(self):
        self.student_days = ()
        
        subh = False
        zuhr = False
        aasr = False
        magrib = False
        esha = False
        selected_period = False         
        
        episode = self.episode_id
        
        if episode:
            self.student_days = episode.episode_days  
            subh = episode.subh
            zuhr = episode.zuhr
            aasr = episode.aasr
            magrib = episode.magrib
            esha = episode.esha
            selected_period = episode.selected_period
            
        self.subh = subh
        self.zuhr = zuhr
        self.aasr = aasr
        self.magrib = magrib
        self.esha = esha
        self.selected_period = selected_period                        
    
    @api.onchange('program_type')
    def onchange_program_type(self):
        self.program_id = False
        self.approache = False

    @api.onchange('program_id')
    def onchange_program(self):
        if self.student_id and not self.student_id.is_student_meqraa:

            self.page_id = False
            self.surah_from_mem_id = False
            self.memory_direction = False

            self.qty_review_id = False
            self.surah_from_rev_id = False
            self.review_direction = False

            self.qty_read_id = False
            self.surah_from_read_id = False
            self.read_direction = False
            program = self.program_id
            if program:
                self.is_tlawa = program.reading
                self.is_big_review = program.maximum_audit
                self.is_min_review = program.minimum_audit
                self.is_memorize = program.memorize

    @api.onchange('memory_direction')
    def onchange_memory_direction(self):
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

    @api.onchange('mosq_id')
    def onchange_mosq(self):
        self.episode_id = False
        mosque = self.mosq_id
        episodes = []
        domain = []
        if mosque:
            if self.student_id.is_online_student:
                domain += [('is_online', '=', True)]
            episodes = self.env['mk.episode'].search(domain + [('mosque_id','=',mosque.id),
                                                               ('state','in',['draft','accept'])]).ids
        return {'domain':{'episode_id': [('id', 'in', episodes)]}}

    # @api.one  
    @api.constrains('student_id', 'selected_period','episode_id','episode_id.active','episode_id.state','type_order')
    def _check_date(self):
        episode = self.episode_id
        student = self.student_id
        student_id = self.student_id.id
        #if self.type_order != 'external':
        if not student.category:
            link = self.env['mk.link'].search([('id','!=',self.id),
                                               ('student_id','=',student_id),
                                               ('episode_id.study_class_id','=',episode.study_class_id.id),
                                               ('episode_id.active','=',True),
                                               ('episode_id.state','=','accept'),
                                               ('selected_period','=',self.selected_period),
                                               ('state', 'not in', ['done', 'reject', 'cancel'])], limit=1)#check type of episode and Days

            if link:
                msg = 'الطالب'
                msg += ' "' + student.display_name + '" '
                msg += 'يدرس في حلقة في نفس الفترة' + ' ! '
                raise ValidationError(msg)

    @api.model
    def get_listen_line(self, order, date_listen, subject_line_from, subject_line_to, type_follow, link_id, is_test):
        return (0,0,{'order':       order,
                     'date':        date_listen,
                     'from_surah':  subject_line_from.from_surah.id,
                     'from_aya':    subject_line_from.from_verse.id if self.program_type == 'open' else subject_line_from.from_aya.id,  #using self.program_type in api.model
                     'to_surah':    subject_line_to.to_surah.id,
                     'to_aya':      subject_line_to.to_verse.id if self.program_type == 'open' else subject_line_to.to_aya.id,  #using self.program_type in api.model
                     'type_follow': type_follow,
                     'student_id':  link_id,
                     'is_test':     is_test})
    
    @api.model        
    def get_history_line(self, start_date,is_memorize, is_min_review, is_big_review, is_tlawa ,subject_line, direction, program_id,approache_id):
        return (0,0,{'date_start':     start_date,
                     'is_memorize':    is_memorize,
                     'is_min_review':  is_min_review,
                     'is_big_review':  is_big_review,
                     'is_tlawa':       is_tlawa,
                     'qty_id':         self.student_id.is_student_meqraa and subject_line.subject_page_id.id if self.program_type == 'open' else False,
                     'surah_from_id':  self.student_id.is_student_meqraa and  subject_line.from_surah.id or False,
                     'aya_from_id':    self.student_id.is_student_meqraa and subject_line.from_verse.id if self.program_type == 'open' else subject_line.from_aya.id,
                     'direction':      direction,
                     'start_point_id': self.student_id.is_student_meqraa and subject_line.id if self.program_type == 'open' else False,
                      'program_id'  :program_id,
                      'approache_id': approache_id})
        
    @api.model
    def get_next_date(self, student_days, start_date, start, nbr_days):
        
        for d in range(start, nbr_days):
            next_date = start_date + timedelta(d)
            
            if next_date.weekday() not in student_days:
                continue
            
            return next_date
        
        return False

    # @api.multi
    def create_student_preparation(self):
        for rec in self:
            episode = rec.episode_id
            episode_id = episode.id
            episode_name = episode.name

            student = rec.student_id
            student_name = student.display_name

            link_id = rec.id

            program_type = rec.program_type
            program = rec.program_id
            program_id = program.id
            approach = rec.approache

            # if not approach:
            #     msg = 'يجب تحديد المنهج بالنسبة للطالب' + ' "' + student_name + '" ' + ' ' + 'في حلقة' + ' ' + episode_name + '" ' + '!'
            #     raise ValidationError(msg)

            is_memorize = rec.is_memorize
            start_memor = ((program_type == 'open') and rec.save_start_point) or False
            # if is_memorize and not start_memor and program_type != 'close':
            #     msg = 'يجب تحديد نقطة بداية الحفظ بالنسبة للطالب' + ' "' + student_name + '" ' + ' ' + 'في حلقة' + ' ' + episode_name + '" ' + '!'
            #     raise ValidationError(msg)
            #
            # subject_memor_id = start_memor and start_memor.subject_page_id.id or False
            # last_memor = (subject_memor_id and self.env['mk.subject.page'].search([('subject_page_id','=',subject_memor_id)], order="order desc", limit=1)) or False
            # last_memor_order = last_memor and last_memor.order or False
            # nbr_memor = approach.lessons_memorize
            #
            is_min_review = rec.is_min_review
            # start_first_s_review = start_memor
            # start_first_s_review_order = start_first_s_review and start_first_s_review.order or 0
            # nbr_s_review = ((program_type == 'open') and approach.lessons_minimum_audit) or False
            #
            is_big_review = rec.is_big_review
            start_review = ((program_type == 'open') and rec.start_point) or False
            # if is_big_review and not start_review and program_type != 'close':
            #     msg = 'يجب تحديد نقطة بداية المراجعة الكبرى بالنسبة للطالب' + ' "' + student_name + '" ' + ' ' + 'في حلقة' + ' ' + episode_name + '" ' + '!'
            #     raise ValidationError(msg)
            # subject_review_id = start_review and start_review.subject_page_id.id or False
            # last_review = (subject_review_id and self.env['mk.subject.page'].search([('subject_page_id','=',subject_review_id)], order="order desc", limit=1)) or False
            # last_review_order = last_review and last_review.order or False
            # nbr_review = ((program_type == 'open') and approach.lessons_maximum_audit) or False
            #
            is_tlawa = rec.is_tlawa
            start_read = ((program_type == 'open') and rec.read_start_point) or False
            # if is_big_review and not start_review and program_type != 'close':
            #     msg = 'يجب تحديد نقطة بداية التلاوة بالنسبة للطالب' + ' "' + student_name + '" ' + ' ' + 'في حلقة' + ' ' + episode_name + '" ' + '!'
            #     raise ValidationError(msg)
            # subject_read_id = start_read and start_read.subject_page_id.id or False
            # last_read = (subject_read_id and self.env['mk.subject.page'].search([('subject_page_id','=',subject_read_id)], order="order desc", limit=1)) or False
            # last_read_order = last_read and last_read.order or False
            # nbr_read = ((program_type == 'open') and approach.lessons_reading) or False
            #

            if not (is_memorize or is_min_review or is_big_review or is_tlawa):
                raise ValidationError(_('عذرا ! لابد من اختيار اعدادات البرنامج'))

            memor_close_sbjs = ((program_type == 'close') and approach.sudo().listen_ids) or []
            start_subject_memor = memor_close_sbjs and memor_close_sbjs[0] or start_memor
            # nbr_memor_close = len(memor_close_sbjs)
            #
            # s_rev_close_sbjs = ((program_type == 'close') and approach.small_reviews_ids) or []
            #
            # nbr_s_rev_close = len(s_rev_close_sbjs)
            #
            b_rev_close_sbjs = ((program_type == 'close') and approach.sudo().big_review_ids) or []
            start_subject_b_review = b_rev_close_sbjs and b_rev_close_sbjs[0] or start_review
            # nbr_b_rev_close = len(b_rev_close_sbjs)
            #
            tlawa_close_sbjs = ((program_type == 'close') and approach.sudo().tlawa_ids) or []
            start_subject_tlawa = tlawa_close_sbjs and tlawa_close_sbjs[0] or start_read
            # nbr_tlawa_close = len(tlawa_close_sbjs)

            start_date = rec.registeration_date
            start_date = datetime.strptime(start_date, "%Y-%m-%d")

            # if program_type == 'close':
            #     if is_memorize and not memor_close_sbjs:
            #             raise Warning(_('لم يتم تحديد خطة الحفظ لهذا البرنامج'))
            #
            #     if is_big_review and not b_rev_close_sbjs:
            #             raise Warning(_('لم يتم تحديد خطة  المراجعة الكبرى لهذا البرنامج'))
            #
            #     if is_tlawa and not tlawa_close_sbjs:
            #             raise Warning(_('لم يتم تحديد خطة  التلاوة لهذا البرنامج'))


            # end_date = episode and episode.end_date or self.study_class_id.end_date
            # end_date = datetime.strptime(end_date, "%Y-%m-%d")

            # student_days = []
            # for student_day in self.student_days:
            #     order_day = student_day.order
            #     if order_day == 0:
            #         student_days += [6]
            #     else:
            #         student_days += [order_day-1]

            vals_prepa = {'name':         episode.teacher_id.id,
                          'prepare_date': start_date,
                          'link_id':      link_id,
                          'program_id':   program_id,
                          'stage_pre_id': episode_id,
                          }

            # memor_pages = []
            # s_rev_pages = []
            # b_rev_pages = []
            # tlawa_pages = []
            #
            # i = 1
            # end = True
            # next_date = False
            # nbr_days = 17 #(end_date - start_date).days + 1
            #
            # for d in range(nbr_days):
            #     date_listen = start_date + timedelta(d)
            #     if date_listen.weekday() not in student_days:
            #         continue
            #
            #     if is_min_review:
            #         next_date = self.get_next_date(student_days, start_date, d+1, nbr_days)
            #
            #     if is_memorize:
            #         if start_memor:
            #             start_order = start_memor.order
            #             end_order = min((start_order + nbr_memor - 1), last_memor_order)
            #             end_memor = self.env['mk.subject.page'].search([('subject_page_id','=',subject_memor_id),
            #                                                             ('order','=',end_order)], limit=1)
            #             memor_pages += [self.get_listen_line(i, date_listen, start_memor, end_memor, 'listen', link_id, (start_memor.is_test or end_memor.is_test))]
            #
            #             if next_date:
            #                 start_s_review_order = end_order - nbr_s_review + 1
            #                 start_s_review = start_first_s_review
            #                 if start_s_review_order > start_first_s_review_order:
            #                     start_s_review = self.env['mk.subject.page'].search([('subject_page_id','=',subject_memor_id),
            #                                                                          ('order','=',start_s_review_order)], limit=1)
            #                 s_rev_pages += [self.get_listen_line(i, next_date, start_s_review, end_memor, 'review_small', link_id, (start_s_review.is_test or end_memor.is_test))]
            #
            #             start_memor = self.env['mk.subject.page'].search([('subject_page_id','=',subject_memor_id),
            #                                                               ('order','=',(end_order+1))], limit=1)
            #             end = False
            #         elif nbr_memor_close:
            #             memor_close = memor_close_sbjs[i-1]
            #             memor_pages += [self.get_listen_line(i, date_listen, memor_close, memor_close, 'listen', link_id, False)]
            #             end = False
            #             if nbr_memor_close == i:
            #                 nbr_memor_close = 0
            #
            #     if next_date and nbr_s_rev_close:
            #         s_rev_close = s_rev_close_sbjs[i-1]
            #         s_rev_pages += [self.get_listen_line(i, next_date, s_rev_close, s_rev_close, 'review_small', link_id, False)]
            #         end = False
            #         if nbr_s_rev_close == i:
            #             nbr_s_rev_close = 0
            #
            #     if is_big_review:
            #         if start_review:
            #             start_order = start_review.order
            #             end_order = min((start_order + nbr_review - 1), last_review_order)
            #             end_review = self.env['mk.subject.page'].search([('subject_page_id','=',subject_review_id),
            #                                                              ('order','=',end_order)], limit=1)
            #             memor_pages += [self.get_listen_line(i, date_listen, start_review, end_review, 'review_big', link_id, (start_review.is_test or end_review.is_test))]
            #             start_review = self.env['mk.subject.page'].search([('subject_page_id','=',subject_review_id),
            #                                                               ('order','=',end_order+1)], limit=1)
            #             end = False
            #         elif nbr_b_rev_close:
            #             b_rev_close = b_rev_close_sbjs[i-1]
            #             b_rev_pages += [self.get_listen_line(i, date_listen, b_rev_close, b_rev_close, 'review_big', link_id, False)]
            #             end = False
            #             if nbr_b_rev_close == i:
            #                 nbr_b_rev_close = 0
            #
            #     if is_tlawa:
            #         if start_read:
            #             start_order = start_read.order
            #             end_order = min((start_order + nbr_read - 1), last_read_order)
            #             end_read = self.env['mk.subject.page'].search([('subject_page_id','=',subject_read_id),
            #                                                            ('order','=',end_order)], limit=1)
            #             tlawa_pages += [self.get_listen_line(i, date_listen, start_read, end_read, 'tlawa', link_id, (start_read.is_test or end_read.is_test))]
            #             start_read = self.env['mk.subject.page'].search([('subject_page_id','=',subject_read_id),
            #                                                               ('order','=',end_order+1)], limit=1)
            #             end = False
            #         elif nbr_tlawa_close:
            #             tlawa_close = tlawa_close_sbjs[i-1]
            #             tlawa_pages += [self.get_listen_line(i, date_listen, tlawa_close, tlawa_close, 'tlawa', link_id, False)]
            #             end = False
            #             if nbr_tlawa_close == i:
            #                 nbr_tlawa_close = 0
            #
            #     i += 1
            #     if end:
            #         break
            #     end = True

            history = []
            # if is_memorize:
            #     history += [self.get_history_line(start_date, 'm', start_subject_memor, self.memory_direction)]
                # vals_prepa.update({'std_save_ids': memor_pages})

            # if is_min_review:
                # vals_prepa.update({'smal_review_ids': s_rev_pages})

            # if is_big_review:
            #     history += [self.get_history_line(start_date, 'r', start_subject_b_review, self.review_direction)]
                # vals_prepa.update({'big_review_ids': b_rev_pages})

            # if is_tlawa:
            #     history += [self.get_history_line(start_date, 't', start_subject_tlawa, self.read_direction)]
                # vals_prepa.update({'recitation_ids': tlawa_pages})

            # vals_prepa.update({'history_ids': history})
            start_subject = start_subject_tlawa or start_subject_memor or start_subject_b_review or False
            history = [rec.get_history_line(start_date, is_memorize, is_min_review, is_big_review, is_tlawa, start_subject,rec.read_direction, program_id, approach.id)]
            vals_prepa.update({'history_ids': history})

            prepa = self.env['mk.student.prepare'].sudo().create(vals_prepa)
            rec.preparation_id = prepa.id

    # @api.multi
    def action_accept(self):
        self.ensure_one()
        episode = self.episode_id
        if episode.teacher_id:
            self.create_student_preparation()
            self.sudo().write({'state': 'accept'})
            has_link = self.env[('mk.link')].search([('id', '!=', self.id), ('student_id', '=', self.student_id.id)], limit=1)
            if not has_link:
                self.student_id.send_passwd()
            return True
        else:
            raise Warning(_('عذرا ! لابد من اختيار معلم للحلقة أولا'))
            # self.write({'state': 'accept'})

        return {"type": "ir.actions.do_nothing",}

    # @api.one
    def action_cancel(self):
        student_test_session = self.env['student.test.session'].search([('student_id', '=', self.id),
                                                                         ('state', '!=', 'cancel')], limit=1)
        if student_test_session:
            raise Warning(_('لا يمكنك حذف الطالب لارتباطه بجلسات اختبار'))
        else:
            student_preparation = self.env['mk.student.prepare'].search([('link_id', '=', self.id)], limit=1)
            if student_preparation:
                student_preparation.write({'active': False})
            # student_preparation.sudo().unlink()
            self.write({'state': 'cancel'})
        return True

    def action_update_student_prepare(self):
        preparation_id = self.preparation_id
        student_prepare_update_form = self.env.ref('mk_student_managment.view_student_prepare_update_form')
        action_vals = {
            'name': _('تعديل المنهج'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mk.student.prepare.update',
            'views': [(student_prepare_update_form.id, 'form')],
            'view_id': student_prepare_update_form.id,
            'target': 'new',
            'context': {'default_preparation_id': preparation_id.id,
                        'default_program_type': self.program_type,
                        'default_program_id': self.episode_id.program_id.id,
                        'default_approache_id': self.episode_id.approache_id.id,
                        'episode_gender'      : self.episode_id.women_or_men,
                        'default_type_order': 'assign'}
        }
        return action_vals
        
    # @api.one
    def action_reject(self):
        self.write({'state': 'reject'})
        student_prepare = self.env['mk.student.prepare'].search([('link_id','=',self.id)])
        if len(student_prepare.ids):
            student_prepare.write({'archived':True})
        self.student_id.write({'active': False,
                               # 'mosq_id': False
                               })

    # @api.one
    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    # @api.multi
    def action_stop(self):
        self.write({'state': 'stopped'})

    # @api.multi
    def action_return_to_accept(self):
        self.write({'state': 'accept'})

    # @api.multi
    def revise_registration(self):
        self.write({'state': 'draft'})
        resource = self.env['resource.resource'].search([('user_id','=',self.env.user.id)])
        if resource.ids:
            employee_id = self.env['hr.employee'].search([('resource_id','in',resource.ids)])
            
            if not employee_id:
                raise Warning(_('you do not have permission to do this operation'))
            
            else:
                if self.student_id.email:
                    msjd_id=self.env['mk.mosque'].search([('supervisor', 'in',employee_id.ids)])
                    if msjd_id:
                        msjd_name=msjd_id.name
                        msjd_name=msjd_name.encode('utf-8','ignore')
                        email_message='شكرا لتسجيلكم بمسجد %s سيتم إشعاركم قريبا بعد مراجعة طلبكم' %msjd_name
                        decoded_mess=email_message.decode("utf-8")
                        values = {'subject': 'Student registration ',
                                  'body_html': decoded_mess,
                                  'email_to': self.student_id.email}
                        self.env['mk.general_sending'].send(values)
                        
                to=self.env['mk.general_sending'].get_phone(self.student_id.mobile, self.student_id.country_id)
                message= "تم تلقي طلبكم وسيتم اشعاركم بعد مراجعته".decode("utf-8")
                if to:
                    self.env['mk.general_sending'].send_sms(to, message)
                    
                return True
            
    # @api.one
    def unlink(self):
        # try:
        student_absence = self.env['mk.student_absence'].search([('student_id', '=', self.id)])
        if student_absence:
            student_absence.unlink()
        return super(link_student, self).unlink()
        # except:
        #     raise ValidationError(_('لا يمكنك حذف هذا  '+'  لإرتباطه بسجلات أخرى'))
        
    @api.model
    def create(self, vals):
        student_id = vals.get('student_id', False)
        type_order = vals.get('type_order', 'principal')

        if type_order == 'principal' and student_id:
            student = self.env['mk.student.register'].sudo().search([('id','=',student_id)], limit=1)
            

            if not student.mosq_id:
                student.sudo().write({'mosq_id': vals.get('mosq_id', False)})
                mosque_responsible = student.mosq_id.responsible_id.user_id.partner_id

                if mosque_responsible:
                    vals = {'message_type': "notification",
                            "subtype": self.env.ref("mail.mt_comment").id,
                            'body': "تم تسجيل طالب جديد",
                            'subject': "تسجيل طالب جديد",
                            'needaction_partner_ids': [(4, mosque_responsible.id)],
                            'model': 'mk.student.register',
                            'res_id': student.id,
                            }
                    notif = self.env['mail.message'].create(vals)
                    # send email to mosq supervisor
                    template = self.env['mail.template'].search(
                        [('name', '=', 'mk_send_mosq_responsible_for_new_student')], limit=1)
                    if template:
                        b = template.sudo().send_mail(student.id, force_send=True)


        prev_link_id = vals.get('prev_link_id', False)
        if prev_link_id:
            last_listen = self.env['mk.listen.line'].sudo().search([('preparation_id','=',prev_link_id),
                                                                    ('type_follow','=','listen'),
                                                                    ('state','=','done')], order="order desc", limit=1)
            page_id = vals.get('page_id', False)                        
            if last_listen and page_id:
                domain_subject = [('subject_page_id','=',page_id)]
                
                memory_direction = vals.get('memory_direction', False)
                if memory_direction == 'down':
                    domain_subject += [('from_verse.original_accumalative_order','<',last_listen.to_aya.original_accumalative_order)]
                else:
                    domain_subject += [('from_verse.original_accumalative_order','>',last_listen.to_aya.original_accumalative_order)]
                    
                new_start = self.env['mk.subject.page'].sudo().search(domain_subject, order="order", limit=1)
                if new_start:
                    vals.update({'surah_from_mem_id': new_start.from_surah.id,
                                 'aya_from_mem_id':   new_start.from_verse.id,
                                 'save_start_point':  new_start.id,})
                    
            last_max_review = self.env['mk.listen.line'].sudo().search([('preparation_id','=',prev_link_id),
                                                                        ('type_follow','=','review_big'),
                                                                        ('state','=','done')], order="order desc", limit=1)
            qty_review_id = vals.get('qty_review_id', False)            
            if last_max_review and qty_review_id:                
                domain_subject = [('subject_page_id','=',qty_review_id)]
                
                review_direction = vals.get('review_direction', False)
                if review_direction == 'down':
                    domain_subject += [('from_verse.original_accumalative_order','<',last_max_review.to_aya.original_accumalative_order)]
                else:
                    domain_subject += [('from_verse.original_accumalative_order','>',last_max_review.to_aya.original_accumalative_order)]
                                    
                new_start = self.env['mk.subject.page'].sudo().search(domain_subject, order="order", limit=1)
                if new_start:
                    vals.update({'surah_from_rev_id': new_start.from_surah.id,
                                 'aya_from_rev_id':   new_start.from_verse.id,
                                 'start_point':  new_start.id,})
                    
            last_tlawa = self.env['mk.listen.line'].sudo().search([('preparation_id','=',prev_link_id),
                                                                   ('type_follow','=','tlawa'),
                                                                   ('state','=','done')], order="order desc", limit=1)
            qty_read_id = vals.get('qty_read_id', False)            
            if last_tlawa and qty_read_id:
                domain_subject = [('subject_page_id','=',qty_read_id)]
                
                read_direction = vals.get('read_direction', False)
                if read_direction == 'down':
                    domain_subject += [('from_verse.original_accumalative_order','<',last_tlawa.to_aya.original_accumalative_order)]
                else:
                    domain_subject += [('from_verse.original_accumalative_order','>',last_tlawa.to_aya.original_accumalative_order)]
                                    
                new_start = self.env['mk.subject.page'].sudo().search(domain_subject, order="order", limit=1)
                if new_start:
                    vals.update({'surah_from_read_id': new_start.from_surah.id,
                                 'aya_from_read_id':   new_start.from_verse.id,
                                 'read_start_point':   new_start.id,})
        
        return super(link_student, self).create(vals)

    @api.model
    def set_student_link_state_cron_fct(self):
        student_link_ids = self.env['mk.link'].search([('study_class_id.is_default', '=', True),
                                                       ('state', '=', 'draft')])
        for link in student_link_ids:
            link.state = 'mosque_accept'

    @api.model
    def student_transport_mosque_location(self, link_id):
        try:
            link_id = int(link_id)
        except:
            pass

        query_string = ''' 
        select m.id mosque_id, 
               m.name name_mosque, 
               m.latitude latitude_mosque, 
               m.longitude longitude_mosque,

               s.id student_id, 
               s.name name_student, 
               s.latitude latitude_student, 
               s.longitude longitude_student,

               s.area_id id_area_student,
               a.name name_area_student,
               a.latitude latitude_area_student, 
               a.longitude longitude_area_student,

               s.district_id id_district_student,
               d.name name_district_student,
               d.latitude latitude_district_student, 
               d.longitude longitude_district_student,

               s.city_id id_city_student,
               c.name name_city_student,
               c.latitude latitude_city_student, 
               c.longitude longitude_city_student

        from mk_link l
             left join mk_student_register s on l.student_id=s.id
             left join mk_episode e on e.id=l.episode_id
             left join mk_mosque m on m.id=e.mosque_id
             left join res_country_state a on a.id=s.area_id
             left join res_country_state d on d.id=s.district_id
             left join res_country_state c on c.id=s.city_id

        where l.id={};
        '''.format(link_id)

        self.env.cr.execute(query_string)
        links = self.env.cr.dictfetchall()
        return links

    @api.model
    def link_with_different_mosq(self):
        query_1 = ''' select count(distinct link.episode_id) from mk_link link
                      join mk_episode ep on ep.id = link.episode_id
                      where link.mosq_id <> ep.mosque_id; '''
        self.env.cr.execute(query_1)
        count_episode = self.env.cr.dictfetchall()

        query_2 = ''' select link.episode_id, count(*) from mk_link link
                           join mk_episode ep on ep.id = link.episode_id
                           where link.mosq_id <> ep.mosque_id
                           group by link.episode_id; '''
        self.env.cr.execute(query_2)
        episode_link = self.env.cr.dictfetchall()

    @api.model
    def episode_with_same_mosq_link(self):
        query = ''' select distinct link.id
                           from mk_link link
                           join mk_episode ep on ep.id = link.episode_id
                           join mk_mosque mosq_ep on mosq_ep.id = ep.mosque_id
                           join mk_mosque mosq_link on mosq_link.id = link.mosque_id
                           where mosq_ep.gender_mosque <> mosq_link.gender_mosque; '''
        self.env.cr.execute(query)
        ep_links = self.env.cr.dictfetchall()

        links = [lk['id'] for lk in ep_links]
        nbr_links = len(links)
        nbr_unlk_links = 0
        i = 0
        for link in links:
            i += 1
            student_test = self.env['student.test.session'].search([('student_id', '=', link),
                                                                    ('state', '!=', 'cancel')], limit=1)
            if not student_test:
                link_id = self.env['mk.link'].search([('id', '=', link)], limit=1)
                link_id.unlink()
                nbr_unlk_links += 1

    @api.model
    def add_lines_to_preparation_43_C3(self):
        students_preparations = self.env['mk.student.prepare'].search([('stage_pre_id.study_class_id.is_default', '=', True),
                                                                       ('stage_pre_id.is_episode_meqraa', '=', False),
                                                                       ('link_id.program_type', '=', 'open'),
                                                                       ('link_id', '!=', False),
                                                                       ('link_id.action_done', '=', False),
                                                                        ('active', '=', True),
                                                                        ('history_ids', '!=', False)])
        total = len(students_preparations)
        line = 0
        x = 0
        no_draft_line = []
        for preparation in students_preparations:
            x += 1
            draft_line = self.env['mk.listen.line'].search([('preparation_id', '=', preparation.id),
                                                           ('state', '=', 'draft')], limit=1)
            if not (draft_line):
                line += 1
                no_draft_line.append(preparation.id)

    @api.model
    def verify_add_lines_to_preparation_43_C3_2(self):
        students_preparations = self.env['mk.student.prepare'].search([('stage_pre_id.study_class_id.is_default', '=', True),
                                                                       ('stage_pre_id.is_episode_meqraa', '=', False),
                                                                       ('link_id', '!=', False),
                                                                        ('active', '=', True),
                                                                        ('history_ids', '!=', False)])
        total = len(students_preparations)
        x = 0
        list_not_added = []
        for preparation in students_preparations:
            x += 1
            if len(preparation.std_save_ids) < 5 and preparation.link_id.program_type == 'open':
                list_not_added.append(preparation.id)

    @api.model
    def cron_change_state_mosque_accept(self):
        student_links = self.env['mk.link'].search([('state','=','mosque_accept')])
        total = len(student_links)
        i =0
        for link in student_links:
            i+=1
            link.write({'state': 'draft'})

                                    
class Mkepisode(models.Model):
    _inherit = 'mk.episode'

    @api.model
    def cron_get_current_students(self):
        episode_ids = self.env['mk.episode'].search([('link_ids', '!=', False),
                                                     '|',('active', '=', True),
                                                         ('active', '=', False)])
        total = len(episode_ids)
        i = 0
        for episode in episode_ids:
            i+=1
            episode.current_students = len(episode.current_link_ids)


    @api.depends('current_link_ids','current_link_ids.state')
    def get_current_students(self):
        for rec in self :
            rec.current_students = len(rec.current_link_ids)

    # @api.one
    @api.depends('expected_students','current_students')
    def get_unoccupied(self):
        unoccupied_no = self.expected_students - self.current_students
        self.unoccupied_no = unoccupied_no
        if unoccupied_no == 0:
            self.write({'color':9})

    # @api.one
    @api.depends('episode_type.students_no')
    def _get_expected_student(self):
        self.expected_students = self.episode_type.students_no

    current_link_ids    = fields.One2many('mk.link', 'episode_id', string='Links', domain=[('state', '=', 'accept')])
    canceled_link_ids   = fields.One2many('mk.link', 'episode_id', string='Links', domain=[('state', '=', 'cancel')])
    link_ids            = fields.One2many('mk.link', 'episode_id', string='Links', domain=[('state', '!=', 'cancel')])
    unoccupied_no       = fields.Integer('unoccupied number of Students',          compute=get_unoccupied)
    expected_students   = fields.Integer('Expected number of Students', default=0, compute=_get_expected_student, store=True)
    current_students    = fields.Integer(compute=get_current_students, store=True)
    unoccupied_no       = fields.Integer(compute=get_unoccupied)

    # @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        new_episode = super(Mkepisode, self).copy(default)
        new_episode_id = new_episode.id
        for link in self.students_list:
            if link.student_id.category == False:
                new_link = link.copy(default={'episode_id':   new_episode_id,
                                              'prev_link_id': link.preparation_id.id,
                                              'state':        'draft'})
                #link.preparation_id.active = False
                new_link.action_accept()
        return new_episode    

    # @api.one
    def action_done(self):
        super(Mkepisode, self).action_done()
        links = self.env['mk.link'].sudo().search([('episode_id','=',self.id),
                                                   '|',('action_done','=','ep_done'),
                                                       ('action_done','=',False)])
        if links:
            links.write({'action_done': 'ep_done'})
            
    # @api.one
    def action_reopen(self):
        super(Mkepisode, self).action_reopen()
        links = self.env['mk.link'].sudo().search([('episode_id','=',self.id),
                                                   '|',('action_done','=','ep_done'),
                                                       ('action_done','=',False)])
        if links:
            links.write({'action_done': False})