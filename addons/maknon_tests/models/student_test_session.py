#-*- coding:utf-8 -*-
import urllib.parse
from odoo import models, fields, api
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

import random
import math

import logging
import qrcode
from io import BytesIO
_logger = logging.getLogger(__name__)

from cryptography.fernet import Fernet
import base64

class session(models.Model):
    _name = 'student.test.session'
    _inherit = ['mail.thread']
    _rec_name='student_name'

    @api.depends('center_id')
    def cheack_user_logged_in(self):
        for rec in self:
            rec.editable=True
        if (self.env.user.has_group('maknon_tests.select_exiaminer_session') or self.env.user.has_group('maknon_tests.create_student_test_session'))and not self.env.user.has_group('maknon_tests.group_Student_tests_full')  :
            for rec in self:
                center_id = rec.sudo().center_id.center_id.center_id
                department_ids = rec.sudo().center_id.center_id.department_ids
                if rec.sudo().center_id.center_id.main_company==True:
                    # rec.editable=False
                    if self.env.user.department_id.id in department_ids.ids:
                        rec.editable=True
                    else:
                        rec.editable=False
                else:
                    if center_id.id in [self.env.user.department_id.id] or center_id.id in self.env.user.department_ids.ids or self.env.user.department_id.id in department_ids.ids:
                        rec.editable=True
                    else:
                        rec.editable=False

    @api.depends('center_id')
    def cheack_user_logged_in2(self):
        for rec in self:
            rec.flag = False
            
        for rec in self:
            user_id = self.env.user.id
            if user_id == rec.user_id.id or user_id in [user.id for user in rec.user_ids]:
                rec.flag = True

    @api.multi
    def get_study_class(self):
        study_class_ids=self.env['mk.study.class'].search([('study_year_id', '=', self.get_year_default()),
                                                           ('is_default', '=', True)])
        if study_class_ids:
            return study_class_ids.ids[0]

    @api.multi
    def get_year_default(self):
        academic_year = self.env['mk.study.year'].search([('is_default', '=', True)], limit=1)
        return academic_year and academic_year.id or False
    
    @api.one
    @api.depends('academic_id','academic_id.is_default')
    def get_is_current_year(self):
        self.is_current_year = self.academic_id.is_default

    @api.model
    def cron_fix_student_fields_compute(self):
        _logger.info('\n\n\n _____ cron_fix_student_fields_compute')
        test_sessions = self.env['student.test.session'].search([('category','=',False),
                                                                 ('state','!=','cancel'),
                                                                 ('student_name', '=', False),
                                                                 ('student_id','!=',False),])
        total = len(test_sessions)
        _logger.info('\n\n\n _____ total   : %s', total)
        i = 0
        for session in test_sessions:
            link = session.student_id
            studnt_id = link.sudo().student_id
            _logger.info('\n\n\n _____ link   : %s |  studnt_id   : %s', link ,studnt_id)

            session.studnt_id = studnt_id.id
            session.student_name = studnt_id.display_name
            session.episode_id = link.sudo().episode_id.id
            session.class_epsd_id = link.sudo().episode_id.study_class_id.id

            if studnt_id.sudo().no_identity:
                session.identity_nbr = studnt_id.passport_no
            else:
                session.identity_nbr = studnt_id.identity_no

            session.mobile_nbr = studnt_id.mobile
            session.nationality = studnt_id.nationality
            _logger.info('\n\n\n _____ student_name   : %s | identity_nbr   : %s |  mobile_nbr   : %s|  nationality   : %s', session.student_name, session.identity_nbr, session.mobile_nbr, session.nationality)
            i += 1
            _logger.info('\n\n\n _____ %s|%s', i, total)
        _logger.info('\n\n\n _____ END')

    @api.model
    def _fix_student_name_test_session(self):
        test_sessions = self.env['student.test.session'].search([('student_id', '!=', False)])
        i = 0
        updated = 0
        total = len(test_sessions)
        for session in test_sessions:
            i += 1
            link_id = session.sudo().student_id
            if link_id:
                if session.category:
                    student_name = session.sudo().employee_id.display_name
                else:
                    student_name = link_id.display_name
            session.sudo().write({'student_name': student_name})
            updated += 1
                
    @api.one
    @api.depends('test_name')
    def get_type_test(self):
        self.type_test = self.test_name.type_test

    @api.model
    def set_type_test_cron_fct(self,test_name_id):
        student_test_session_ids = self.env['student.test.session'].search([('test_name', '=', test_name_id)])
        for test in student_test_session_ids:
            test.get_type_test()

    @api.model
    def set_type_test_cron_fct_2(self, branch_id):
        branch = self.env['mk.branches.master'].search([('id', '=', branch_id)])
        test_name = branch.test_name
        student_test_session_ids = self.env['student.test.session'].search([('branch', '=', branch_id)])
        for test in student_test_session_ids:
            test.test_name = test_name

    @api.one
    @api.depends('center_id')
    def get_test_center_id(self):
        center = self.center_id.center_id
        self.test_center_id = center.id
        self.department_id  = center.center_id.id
                
    @api.one
    @api.depends('center_id.committee_assign_type','center_id.committee_test_ids','committe_id','center_id.committee_test_ids.members_ids')
    def get_users_committe(self):
        center = self.center_id
        user_ids = []
        if center and center.committee_assign_type == 'all_committee_assign':
            committees = [committee for committee in center.committee_test_ids]

            committe = self.committe_id
            if committe:
                committees = [committe]
            
            for committee in committees:
                for member in committee.members_ids:
                    if not member.main_member:
                        continue
                    user_employee = member.member_id.sudo().user_id
                    if user_employee:
                        user_ids += [user_employee.id]
                        break

        if self.user_ids:
            self.user_ids = [(5,0,0)]
            
        self.user_ids = user_ids
    
    @api.depends('center_id')    
    def _get_avilable_techer(self):
        for rec in self:
            rec.avalible_teacher = [(4, teacher_id) for teacher_id in []]

    @api.one
    @api.depends('start_date')
    def _compute_start_date(self):
        for rec in self:
            start_date = rec.start_date
            if start_date:
                rec.start_date_filter = datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S").date()

    @api.one
    @api.depends('done_date')
    def _compute_done_date(self):
        for rec in self:
            done_date = rec.done_date
            if done_date:
                rec.done_date_filter = datetime.strptime(done_date,"%Y-%m-%d %H:%M:%S").date()


    editable         = fields.Boolean(string="show", compute='cheack_user_logged_in')
    flag             = fields.Boolean(string="show", compute='cheack_user_logged_in2', default=False)
    active           = fields.Boolean(string="active", default=True, track_visibility='onchange')
    academic_id      = fields.Many2one('mk.study.year',  string='Academic Year', required=True,ondelete='restrict', default=get_year_default,                    track_visibility='onchange')
    study_class_id   = fields.Many2one('mk.study.class', string='Study class', default=get_study_class, domain=[('is_default', '=', True)], ondelete='restrict', track_visibility='onchange')
    is_current_year  = fields.Boolean('العام الحالي', compute=get_is_current_year, store=True)
    controller_flag  = fields.Boolean(string="controller", default=False)        
    state            = fields.Selection([('draft', 'Draft'),
                                         ('absent','absent'),
                                         ('start', 'start'),
                                         ('pasue', 'إيقاف'),
                                         ('done',  'Done test'),
                                         ('cancel','إلغاء')], default="draft", string="status", index=True, track_visibility='onchange')
    student_id       = fields.Many2one("mk.link",      string="student", track_visibility='onchange')
    branch_duration  = fields.Integer(string="branch duration",            track_visibility='onchange')
    test_name        = fields.Many2one("mk.test.names",string="Test Name", track_visibility='onchange')
    type_test        = fields.Selection([('final',   'الخاتمين'),
                                        ('parts',   'الأجزاء'),
                                        ('contest', 'مسابقات'),
                                         ('correct_citation', 'تصحيح تلاوة'),
                                         ('indoctrination', 'تلقين'),
                                         ('vacations', 'اجازات'),], string="النوع", compute='get_type_test', store=True)

    test_time        = fields.Many2one("center.time.table",       string="Test Time",     track_visibility='onchange')
    branch           = fields.Many2one("mk.branches.master",      string="Branch",        track_visibility='onchange')
    center_id        = fields.Many2one("mk.test.center.prepration", string="Test center", track_visibility='onchange')
    test_center_id   = fields.Many2one("mak.test.center", string="مركز الاختبار",  compute='get_test_center_id', store=True)
    department_id    = fields.Many2one("hr.department",   string="مركز الاشراف", compute='get_test_center_id', store=True)
    center_name      = fields.Char(string="center name",                track_visibility='onchange')
    teacher          = fields.Many2one("hr.employee", string="Teacher", track_visibility='onchange')
    user_id          = fields.Many2one("res.users",   string="users",   track_visibility='onchange')
    user_ids         = fields.Many2many("res.users", compute=get_users_committe, store=True)
    test_question    = fields.One2many("test.questions","session_id","session questions")
    start_date       = fields.Datetime(string="exam start at",         track_visibility='onchange')
    done_date        = fields.Datetime(string="exam done at",          track_visibility='onchange')
    is_pass          = fields.Boolean(string='is pass', default=False, track_visibility='onchange', compute='get_final_degree', store=True)
    committe_id      = fields.Many2one("committee.tests", "committe",  track_visibility='onchange')
    mosque_id        = fields.Many2one('mk.mosque', string="Mosque",   track_visibility='onchange')
    avalible_teacher = fields.Many2many("hr.employee", string="available",               compute='_get_avilable_techer', store=True)
    branch_order     = fields.Integer(related='branch.order', string="branch order")
    degree           = fields.Float(string="Deserved degree", track_visibility='onchange')
    force_degree  = fields.Float(string="Force degree",       track_visibility='onchange')
    final_degree     = fields.Float(string="Final degree",    track_visibility='onchange', compute='get_final_degree', store=True)
    appreciation     = fields.Selection([('excellent',  'Excellent'),
                                         ('v_good',     'Very good'),
                                         ('good',       'Good'),
                                         ('acceptable', 'Acceptable'),
                                         ('fail',       'Fail')], string="appreciation", track_visibility='onchange', compute='get_final_degree', store=True)
    maximum_degree   = fields.Integer(related='branch.maximum_degree', string="Maximum degree")
    duration         = fields.Integer(related='branch.duration',       string="exam duration")
    active           = fields.Boolean(string="Active", default=True, track_visibility='onchange')
    category         = fields.Selection([('teacher', 'المعلمين'),
                                         ('center_admin','مدراء / مساعدي مدراء المركز'),
                                         ('bus_sup','مشرف الباص'),
                                         ('supervisor', 'مشرفين وإداريين المسجد / المدرسة'),
                                         ('admin', 'المشرف العام للمسجد /المدرسة'),
                                         ('edu_supervisor', 'مشرف تربوي'),
                                         ('managment','إداري\إداريين'),
                                         ('others','خدمات مساعدة')], string="التصنيف", default=False)
    employee_id      = fields.Many2one('hr.employee',     string='الموظف')
    start_date_filter = fields.Date('Start date filter',compute='_compute_start_date', store=True)
    done_date_filter = fields.Date('Done date filter',compute='_compute_done_date', store=True)
    is_printed     = fields.Boolean(string="Is printed", default=False)
    is_get_diploma = fields.Boolean(string="Is get diploma", default=False)

    studnt_id        = fields.Many2one("mk.student.register", string="student", compute='get_student_link', store=True, track_visibility='onchange')
    episode_id = fields.Many2one("mk.episode", string="الحلقة", index=True,          compute='get_student_episode', store=True, track_visibility='onchange')
    class_epsd_id = fields.Many2one("mk.study.class", string="الفصل الدراسي للحلقة", compute='get_student_episode', store=True, track_visibility='onchange')
    episode_teacher = fields.Many2one('hr.employee', string='معلم الحلقة',           compute='get_student_episode', store=True)
    episode_type = fields.Many2one('mk.episode_type', string='نوع الحلقة',           compute='get_student_episode', store=True)

    mosque_id     = fields.Many2one("mk.mosque",     string="المسجد",      compute='get_student_episode', store=True, track_visibility='onchange')
    deprt_mosq_id = fields.Many2one("hr.department", string="مركز المسجد", compute='get_student_episode', store=True, track_visibility='onchange')

    masjed_name     = fields.Char(string="masjed", compute='get_mosque_name', store=True, track_visibility='onchange')
    gender_mosque   = fields.Selection([('male', 'رجالي'),
                                      ('female', 'نسائي')], string="Mosque gender", compute='get_categ_gender', store=True)
    categ_mosque_id = fields.Many2one('mk.mosque.category', string="Mosque category", compute='get_categ_gender', store=True)

    student_name = fields.Char(string="student name", compute='get_student_link', store=True, track_visibility='onchange')
    identity_nbr = fields.Char("رقم الهوية/جواز السفر", compute='get_student_link', store=True, track_visibility='onchange')
    nationality = fields.Char("الجنسية", compute='get_student_link', store=True, track_visibility='onchange')
    mobile_nbr       = fields.Char("الجوال", compute='get_student_link', store=True, track_visibility='onchange')
    attachment_id   = fields.Many2one('ir.attachment', string='المرفقات')

    #region Student compute data
    @api.one
    @api.depends('student_id', 'studnt_id', 'studnt_id.display_name','studnt_id.identity_no', 'studnt_id.passport_no','studnt_id.nationality',
                  'studnt_id.mobile', 'employee_id.mobile_phone', 'employee_id','employee_id.display_name','employee_id.country_id')
    def get_student_link(self):
        link_id = self.student_id
        employee_id = self.employee_id
        student_id = link_id.sudo().student_id
        self.studnt_id  = student_id.id
        if employee_id:
            self.student_name = employee_id.display_name
            self.identity_nbr = employee_id.identification_id
            self.nationality = employee_id.country_id.nationality
            self.mobile_nbr = employee_id.mobile_phone
        else:
            self.student_name = student_id.display_name
            if student_id.sudo().no_identity:
                self.identity_nbr = student_id.sudo().passport_no
            else:
                self.identity_nbr = student_id.sudo().identity_no
            self.nationality = student_id.nationality
            self.mobile_nbr = student_id.mobile

    # @api.depends('student_id','studnt_id','studnt_id.identity_no', 'studnt_id.passport_no')
    # def get_identity_nbr(self):
    #     for rec in self:
    #         rec = rec.sudo()
    #         if rec.category:
    #             employee = rec.employee_id
    #             rec.identity_nbr = employee.identification_id
    #         else:
    #             student = rec.sudo().studnt_id
    #             if student.sudo().no_identity:
    #                 rec.identity_nbr = student.sudo().passport_no
    #             else:
    #                 rec.sudo().identity_nbr = student.sudo().identity_no


    # @api.depends('student_id','studnt_id','studnt_id.nationality','employee_id.country_id')
    # def get_nationality(self):
    #     for rec in self:
    #         rec = rec.sudo()
    #         if rec.category:
    #             rec.nationality = rec.employee_id.country_id.nationality
    #         else:
    #             rec.nationality = rec.sudo().studnt_id.nationality

    # @api.depends('student_id','studnt_id','studnt_id.mobile','employee_id.mobile_phone')
    # def get_mobile_nbr(self):
    #     for rec in self:
    #         rec = rec.sudo()
    #         if rec.category:
    #             rec.mobile_nbr = rec.employee_id.mobile_phone
    #         else:
    #             rec.mobile_nbr = rec.sudo().studnt_id.mobile

    @api.one
    @api.depends('student_id')
    def get_student_episode(self):
        link = self.student_id
        episode = link.sudo().episode_id
        mosque = episode.mosque_id

        self.episode_id = episode.id
        self.class_epsd_id = episode.study_class_id.id
        self.episode_teacher = episode.teacher_id.id
        self.episode_type = episode.episode_type.id
        self.mosque_id = mosque.id
        self.deprt_mosq_id = mosque.center_department_id.id

    @api.depends('mosque_id','mosque_id.name', 'mosque_id.district_id')
    def get_mosque_name(self):
        for rec in self:
            rec.masjed_name = rec.mosque_id and rec.mosque_id.display_name or False

    @api.one
    @api.depends('mosque_id', 'mosque_id.categ_id')
    def get_categ_gender(self):
        categ_mosque = self.mosque_id.categ_id
        self.categ_mosque_id = categ_mosque.id
        self.gender_mosque   = categ_mosque.mosque_type
    #endregion

    def action_get_diploma(self):
        self.is_get_diploma=True

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.editable==False:
                raise ValidationError(_('عفوا , لايمكنك حذف هذه الجلسة'))

        return super(session, self).unlink()

    @api.multi
    def write(self, vals):
        if 'active' in vals:
            for rec in self:
                if vals['active'] == False and rec.editable == False:
                    raise ValidationError(_('عذرا ! لايمكنك ارشفة  هذه الجلسة'))
                else:
                    if vals['active'] == True and rec.editable == False:
                        raise ValidationError(_('عذرا لايمكنك الغاء ارشفة هذه الجلسة'))
        res = super(session, self).write(vals)
        return res
    
    @api.model
    def start_student_session(self, session_id, user_portal_id):
        session = self.env['student.test.session'].search([('id','=',session_id)], limit=1)
        user = self.env.ref('mk_student_register.portal_user_id')

        if session:
            session.branch_duration = session.branch.duration
            session.sudo(user.id).start_exam()
            
            committee_member = self.env['committe.member'].search([('member_id.user_id','=', user_portal_id),
																   ('center_id','=', session.center_id.id)], limit=1)

            session.sudo(user.id).write({'user_id': user_portal_id,
						                 'committe_id': committee_member.committe_id.id})

            return {'start_date': session.start_date,
                    'status':     True}
        else:
            return {'status': False}
        
    @api.model
    def end_student_session(self, session_id):
        session = self.env['student.test.session'].search([('id','=',session_id)], limit=1)
        
        if session:
            user = self.env.ref('mk_student_register.portal_user_id')
            session.sudo(user.id).end_exam()
            
            return {'done_date': session.done_date,
                    'status':    True}
        else:
            return {'status': False}        

    @api.multi
    def start_exam(self):
        current_date = datetime.now().date()
        exam_end_date = datetime.strptime(self.center_id.exam_end_date, '%Y-%m-%d').date()
        if self.study_class_id and self.study_class_id.is_default and current_date > exam_end_date:
            raise ValidationError(_('عذرا لايمكنك بدأ الإختبار بعد تاريخ نهاية الاختبارات'))
        else:
            user_id = self.env.user.id
            center = self.center_id
            vals_start = {'state': 'start',
                          'start_date': datetime.today()}
            if center.committee_assign_type == 'all_committee_assign' and not self.user_id:
                committee_member = self.env['committe.member'].search([('member_id.user_id','=',user_id),
                                                                        ('center_id','=',center.id)], limit=1)
                if committee_member:
                    vals_start.update({'user_id':     user_id,
                                       'committe_id': committee_member.committe_id.id})
                else:
                    raise ValidationError(_('هذا المستخدم لا ينتمي لأي لجنة اختبار'))
            elif not self.user_id or not self.committe_id :
                raise ValidationError(_('الرجاء تحديد لجنة الاختبار و العضو الرئيسي للجنة'))

            if self.branch.quations_method == 'subject':
                pages_number = 0
                quations_range = 0
                possible_quations_list = []
                selected_quations = []

                if self.branch.sudo().select_parts == False:
                    if self.branch.sudo().from_aya.original_accumalative_order < self.branch.sudo().to_aya.original_accumalative_order:
                        possible_quations_list = self.env['mk.subject.page'].sudo().search([('subject_page_id','=',self.branch.sudo().subject_id.id),
                                                                                            ('from_verse','>=',self.branch.sudo().from_aya.original_accumalative_order),
                                                                                            ('to_verse','<=',self.branch.sudo().to_aya.original_accumalative_order),
                                                                                            ('create_uid','=',1)])
                    else:
                        possible_quations_list = self.env['mk.subject.page'].sudo().search([('subject_page_id','=',self.branch.sudo().subject_id.id),
                                                                                            ('from_verse','<=',self.branch.sudo().from_aya.original_accumalative_order),
                                                                                            ('to_verse','>=',self.branch.sudo().to_aya.original_accumalative_order),
                                                                                            ('create_uid','=',1)])
                    pages_number = len(possible_quations_list)

                else:
                    possible_quations_list = self.env['mk.subject.page'].sudo().search([('subject_page_id','=',self.branch.sudo().subject_id.id),
                                                                                        ('part_id','in',self.branch.sudo().parts_ids.ids)])
                    pages_number = len(possible_quations_list)

                if pages_number <= 0 :
                    raise UserError(_('لم يتمكن النظام من توليد اسئلة لهذا الفرع الرجاء مراجعة اعدادات الاسئلة المتعلقة بهذا الفرع'))

                if possible_quations_list:
                    qu_number_per_part = self.branch.sudo().qu_number_per_part
                    if qu_number_per_part != 0:
                        quations_range = int(pages_number / qu_number_per_part)
                    x = quations_range
                    i = 0
                    l = []

                    while(x <= len(possible_quations_list)) :
                        if x + quations_range > len(possible_quations_list):
                            selected_ids = random.sample(possible_quations_list[i:len(possible_quations_list)-1], 1)
                            selected_quations.extend(selected_ids)
                        else:
                            selected_ids = random.sample(possible_quations_list[i:x], 1)
                            selected_quations.extend(selected_ids)
                        i = x
                        x = x + quations_range

                    if len(selected_quations) != 0:
                        for subject in selected_quations:
                            self.env['test.questions'].create({'session_id': self.id,
                                                               'from_surah': subject.from_surah.id,
                                                               'from_aya':   subject.from_verse.id,
                                                               'to_surah':   subject.to_surah.id,
                                                               'to_aya':     subject.to_verse.id})
                        self.sudo(user_id).write(vals_start)
                    else:
                        raise ValidationError(_('لم يتمكن النظام من توليد اسئلة لهذا الفرع الرجاء مراجعة اعدادات الفرع'))
            else:
                raise ValidationError(_('لم يتمكن النظام من توليد اسئلة لهذا الفرع الرجاء مراجعة اعدادات الفرع'))

    @api.model
    def stop_exam(self, session_id, question_id):
        session = self.env['student.test.session'].search([('id','=',session_id)], limit=1)
        
        if session:
            #add to api "test/test_questions_session?session_id" "order by test_questions.id;"
            user = self.env.ref('mk_student_register.portal_user_id')
            fail_questions = self.env['test.questions'].sudo().search([('session_id','=',session_id),
                                                                       ('id','>=',question_id)], order="id")
            if fail_questions:
                fail_questions.write({'set_fail': True})
            session.sudo(user.id).end_exam()
            
            if session.is_pass:
                degree_fail = session.branch.minumim_degree - 1
                # appreciation = self.env['mk.passing.items'].sudo().search([('branches','in',session.branch.id),
                #                                                            ('from_degree','<=',degree_fail),
                #                                                            ('to_degree','>=',degree_fail)], limit=1)
                self.sudo(user.id).write({'degree':       degree_fail,
                            'force_degree':       0})

            return {'done_date': session.done_date,
                    'status':    True}
        else:
            return {'status': False}               

    # @api.one

    @api.multi
    @api.depends('force_degree','degree','branch.minumim_degree')
    def get_final_degree(self):
        for rec in self:
            force_degree = rec.force_degree
            if force_degree > 0:
                final_degree = force_degree
            else :
                final_degree = rec.degree
            rec.final_degree = final_degree

            apprec = self.env['mk.passing.items'].sudo().search([('branches', 'in', rec.branch.sudo().id),
                                                                 ('to_degree', '>=', final_degree)], order="to_degree", limit=1)
            is_pass = False
            if final_degree >= rec.branch.sudo().minumim_degree:
                is_pass = True

            rec.is_pass = is_pass
            rec.appreciation = apprec and apprec.appreciation or False

    @api.model
    def set_is_pass_appreciation(self,last_id):
        student_test_session_ids = self.env['student.test.session'].search([('state', '=', 'done'),
                                                                            ('id', '>', last_id)], limit=500)
        for test in student_test_session_ids:
            test.get_final_degree()

    @api.model
    def set_appreciation(self):
        student_test_session_ids = self.env['student.test.session'].search([('state', '=', 'done'),
                                                                            ('appreciation', '=', False),
                                                                            ('branch', '!=', False)])
        for session in student_test_session_ids:
            apprec = self.env['mk.passing.items'].sudo().search([('branches', 'in', session.branch.sudo().id),
                                                                 ('to_degree', '>=', session.final_degree)], order="to_degree",limit=1)
            session.appreciation = apprec and apprec.appreciation or False

    @api.model
    def set_branch_cron_fct(self,branch_id):
        branch = self.env['mk.branches.master'].search([('id', '=', branch_id)], limit=1)

        student_test_session_ids = self.env['student.test.session'].search([('branch', '=', False),
                                                                            ('study_class_id.is_default', '=', True)])
        for test in student_test_session_ids:
            test.branch = branch

    @api.model
    def set_mosque_name_cron_fct(self):
        student_test_session_ids = self.env['student.test.session'].search([('academic_id.is_default', '=', True)])
        for session in student_test_session_ids:
            mosque_id = session.mosque_id
            session.masjed_name = mosque_id.display_name

    @api.multi
    def end_exam(self):
        current_date = datetime.now().date()
        exam_end_date = datetime.strptime(self.center_id.exam_end_date, '%Y-%m-%d').date()
        if self.study_class_id and self.study_class_id.is_default and current_date > exam_end_date:
            raise ValidationError(_('عذرا لايمكنك إنهاء الإختبار بعد تاريخ نهاية الاختبرات'))
        else:
            total = 0
            last_degree = self.maximum_degree
            member_count = 0
            members = self.committe_id.sudo().members_ids

            for member_info in members:
                errors = self.env['question.error'].search([('value', '!=', 0),
                                                            ('question_id.set_fail', '=', False),
                                                            ('question_id', 'in', self.test_question.ids),
                                                            ('member', '=', member_info.sudo().member_id.id)])
                if errors:
                    member_count = member_count + 1
                    discount_value = 0
                    for error in errors:
                        discount_value = discount_value + (error.value * error.item.amount)

                    total = total + self.branch.sudo().maximum_degree - discount_value
            if not member_count:
                member_count = 1
                total = 100

            fail_q = self.env['test.questions'].sudo().search([('session_id', '=', self.id),
                                                               ('set_fail', '=', True)])
            q_weight = 0
            nbr_test_question = len(self.test_question)
            if fail_q and nbr_test_question:
                q_weight = ((len(fail_q) / len(self.test_question)) * self.maximum_degree)

            if member_count:
                last_degree = total / member_count
            last_degree = last_degree - q_weight
            if self.branch.sudo().round_frag:
                last_degree = math.ceil(last_degree)

            self.write({'degree': last_degree,
                        'force_degree':   0,
                        'done_date': datetime.today(),
                        'state':     'done'})

    @api.model
    def cron_end_exam(self, session_id):
        test = self.search([('id','=',session_id)], limit=1)
        total = 0
        last_degree = test.maximum_degree
        is_pass = False
        member_count = 0
        members = test.committe_id.sudo().members_ids
        for member_info in members:
            member_count = member_count + 1
            errors = self.env['question.error'].search([('value','!=',0),
                                                        ('question_id.set_fail','=',False),
                                                        ('question_id','in',test.test_question.ids),
                                                        ('member','=',member_info.sudo().member_id.id)])
            discount_value = 0
            for error in errors:
                discount_value = discount_value + (error.value * error.item.amount)

            total = total + test.branch.sudo().maximum_degree - discount_value

        fail_q = self.env['test.questions'].sudo().search([('session_id','=',test.id),
                                                           ('set_fail','=',True)])
        q_weight = 0
        nbr_test_question = len(test.test_question)
        if fail_q and nbr_test_question:
            q_weight = ((len(fail_q) / len(test.test_question)) * test.maximum_degree)

        if member_count:
            last_degree = total / member_count
        last_degree = last_degree - q_weight

        if test.branch.sudo().round_frag:
            last_degree = math.ceil(last_degree)

        if last_degree >= test.branch.sudo().minumim_degree:
            is_pass = True

        test.write({'is_pass':    is_pass,
                     'degree':    last_degree,
                     'done_date': test.done_date or datetime.today(),
                     'state':     'done'})
        
        appreciation_ids = self.env['mk.passing.items'].sudo().search([('branches','in',test.branch.sudo().id),
                                                                       ('from_degree','<=',last_degree),
                                                                       ('to_degree','>=',last_degree)])
        appreciation = ""
        if appreciation_ids:
            test.appreciation = appreciation_ids[0].appreciation

    @api.model
    def add_student_test_session(self, link_id, test_name_id, test_time_id, branch_id, trackk):
        link = self.env['mk.link'].search([('id','=',link_id)], limit=1)
        mosque = link.student_id.mosq_id
        
        test_name = self.env['mk.test.names'].search([('id','=',test_name_id)], limit=1)
        
        test_time = self.env['center.time.table'].search([('id','=',test_time_id)], limit=1)
        avalible_minutes = test_time.avalible_minutes
        test_center_preparation = test_time.center_id
        academic_id = test_center_preparation.academic_id.id
        study_class_id = test_center_preparation.study_class_id.id
        
        branch = self.env['mk.branches.master'].search([('id','=',branch_id)], limit=1)
        flag, msg = self.env['select.students'].action_student_validate(branch, trackk, academic_id, study_class_id, link_id, test_name, avalible_minutes, 1, test_time)

        session_id = False
        if flag:
            session = self.env['student.test.session'].sudo().create({'student_id':  link_id,
                                                                             'test_name':   test_name_id,
                                                                             'test_time':   test_time_id,
                                                                             'branch':      branch_id,
                                                                             'center_name': test_time.center_id.center_id.display_name,
                                                                             'center_id':   test_time.center_id.id,
                                                                             'masjed_name': mosque.name,
                                                                             'mosque_id':   mosque.id,})
            session_id = session.id
            msg = False
        
        vals = {'session_id': session_id,
                'msg': msg}
        return vals

    @api.model
    def cancel_student_test_session(self, session_id):
        session = self.search([('id','=',session_id)], limit=1)
        session.write({'state':'cancel'})
        return True
    
    @api.multi
    def cancel_exam(self):
        self.write({'state':'cancel'})
        
    @api.model
    def set_mosque_id(self):
        test_sessions = self.env['student.test.session'].search([])
        for test_session in test_sessions:
            test_session.mosque_id = test_session.episode_id.mosque_id.id

    @api.multi
    def set_draft(self):
        current_date = datetime.now().date()
        exam_end_date = datetime.strptime(self.center_id.exam_end_date, '%Y-%m-%d').date()
        if self.study_class_id and self.study_class_id.is_default and current_date > exam_end_date:
            raise ValidationError(_('عذرا لايمكنك إرجاع الإختبار الي مبدئي بعد تاريخ نهاية الاختبرات'))
        else:
            self.write({'state':'draft'})

    @api.multi
    def set_upsent(self):
        current_date = datetime.now().date()
        exam_end_date = datetime.strptime(self.center_id.exam_end_date, '%Y-%m-%d').date()
        if self.study_class_id and self.study_class_id.is_default and current_date > exam_end_date:
            raise ValidationError(_('عذرا لايمكنك تسجيل غياب في إختبار بعد تاريخ نهاية الاختبارات'))
        else:
            self.write({'state':'absent'})
    
    @api.model
    def set_users_committe(self, recalc):
        sessions = self.env['student.test.session'].search([])
        i = 0
        for session in sessions:
            center = session.center_id
            user_ids = []
            a = session.user_ids
            session.write({'user_ids': [(5,0,0)]})
            if a:
                i += 1

            if recalc:
                    
                if center and center.committee_assign_type == 'all_committee_assign':
                    committees = [committee for committee in center.committee_test_ids]
                    
                    committe = session.committe_id
                    if committe:
                        committees = [committe]

                    for committee in committees:
                        for member in committee.members_ids:
                            if not member.main_member:
                                continue
                            
                            user_employee = member.member_id.user_id
                            if user_employee:
                                user_ids += [user_employee.id]
                                break
                
                session.user_ids = user_ids

    @api.multi
    def print_parts_certification(self):
        self.is_printed=True
        return self.env.ref('maknon_tests.parts_certificate_report_id').report_action(self)

    @api.multi
    def print_final_test_certification(self):
        self.is_printed=True
        return self.env.ref('maknon_tests.final_test_certificate_report_id').report_action(self)

    @api.multi
    def print_licence_test_certification(self):
        self.is_printed=True
        return self.env.ref('maknon_tests.licence_test_certification_report').report_action(self)

    @api.multi
    def generate_qr_code(self):
        # Generate a random encryption key
        key = Fernet.generate_key()
        # Create an instance of the Fernet cipher using the key
        cipher = Fernet(key)

        encrypted = cipher.encrypt(str(self.id).encode())
        encrypted_id = base64.b64encode(encrypted).decode('utf-8')

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        params = {'key': key.decode()}
        encoded_params = urllib.parse.urlencode(params)
        qr_code_url = f"{base_url}/certificate/{encrypted_id}?{encoded_params}"
        qr_code = qrcode.QRCode(version=1, box_size=10, border=1)
        qr_code.add_data(qr_code_url)
        qr_code.make(fit=True)
        qr_img = qr_code.make_image(fill_color="#3b917c", back_color="#b38f70" ,quiet_zone="8")
        buffered = BytesIO()
        qr_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('ascii')
        return img_str

    @api.model
    def get_student_test_sessions(self,center_id,episode_id):
        students = []
        try:
            episode_id = int(episode_id)
            center_id = int(center_id)
        except:
            pass

        center = self.env['center.time.table'].sudo().search([('id', '=', center_id)],limit=1)
        period_id = center.period_id

        links = self.env['mk.link'].sudo().search([('episode_id', '=', episode_id),
                                                   ('state', '=', 'accept')])

        for link in links:
            link_id = link.id

            test_session = self.env['student.test.session'].sudo().search([('student_id', '=', link_id),
                                                                           ('test_time', '=', center_id),
                                                                           ('state', '!=', 'cancel')], limit=1)

            if not test_session:
                test_session_any = self.env['student.test.session'].sudo().search([('student_id', '=', link_id),
                                                                                   ('state', '!=', 'cancel')], limit=1)
                if test_session_any:
                    continue
            students += [{'id': link.id,
                          'student_id': link.student_id.id,
                          'name': link.student_id.display_name,

                          'test_register': test_session and True or False,
                          'session_id': test_session and test_session.id or False,

                          'type_exam_id': test_session and test_session.test_name.id or False,
                          'track': test_session and test_session.branch.trackk or False,
                          'branch_id': test_session and test_session.branch.id or False,
                          'period_id': center_id or False, #period_id.id
                          }]
        # students = sorted(students, key=lambda k: k[flter])

        return str(students)
    
    @api.model
    def _notify_for_upcoming_test_session(self):
        tomorrow_date = (date.today() + timedelta(days=1))
        upcoming_test_sessions = self.env['student.test.session'].search([('test_time.date', '=', tomorrow_date),
                                                                          ('mosque_id', '!=', False),
                                                                          ('state', '=', 'draft')])
        for rec in upcoming_test_sessions:
            supervisor = rec.mosque_id.responsible_id.user_id.partner_id
            if supervisor:
                notif = self.env['mail.message'].create({'message_type': "notification",
                                                         "subtype": self.env.ref("mail.mt_comment").id,
                                                         'body': "جلسة الاختبار ستبدأ غدا",
                                                         'subject': "اشعار بدء جلسة اختبار",
                                                         'needaction_partner_ids': [(4, supervisor.id)],
                                                         'model': self._name,
                                                         'res_id': rec.id,
                                                        })

    @api.model
    def member_nbr_student_sessions(self, employee_id):
        try:
            employee_id = int(employee_id)
        except:
            pass

        query_string = ''' 
                   SELECT mk_test_center_prepration.id as center_id,
                   mak_test_center.display_name as center_name,
                   center_time_table.date as session_date,
                   center_time_table.period_id as period_id,
                   test_period.name as period_name,
                   count(student_test_session.student_id) as no_students

                   FROM student_test_session
                   left join committee_tests on student_test_session.committe_id = committee_tests.id
                   left join committe_member on committe_member.committe_id = committee_tests.id
                   left join center_time_table on student_test_session.test_time = center_time_table.id
                   left join mk_test_center_prepration on center_time_table.center_id = mk_test_center_prepration.id
                   left join mak_test_center on mk_test_center_prepration.center_id = mak_test_center.id
                   left join test_period on center_time_table.period_id = test_period.id

                   WHERE committe_member.member_id = {} AND 
                   student_test_session.state not in ('absent','cancel','done') AND 
                   student_test_session.active = True AND 
                   student_test_session.center_id is not null AND 
                   center_time_table.date <= current_date

                   Group by  mk_test_center_prepration.id,
                   mak_test_center.display_name, 
                   center_time_table.date,
                   center_time_table.period_id,
                   test_period.name

                   Order by center_time_table.date,center_time_table.period_id;
                   '''.format(employee_id)
        self.env.cr.execute(query_string)
        member_nbr_student_sessions = self.env.cr.dictfetchall()
        return member_nbr_student_sessions

    @api.model
    def test_teacher_test(self, employee_id, date, period_id):
        try:
            employee_id = int(employee_id)
            date = date
            period_id = int(period_id)
        except:
            pass

        query_string = ''' 
           SELECT distinct student_test_session.id as session_id, 
           center_time_table.day as week_day, 
           center_time_table.date as session_date, 
           test_period.name as period_name, 
           mk_student_register.display_name as student_name,
           mk_student_register.id as id,
           mk_student_register.identity_no as id_student,
           mk_student_register.mobile,
           student_test_session.start_date,
           student_test_session.done_date,
           student_test_session.state,
           mk_branches_master.duration as minutes,
           mk_branches_master.id as branch_id,
           mk_branches_master.name as branch_name,
           mk_branches_master.trackk as branch_track

           FROM 
           student_test_session, 
           mk_link, 
           mk_student_register, 
           center_time_table, 
           test_period,
           mk_branches_master

           WHERE 
           student_test_session.student_id = mk_link.id AND
           student_test_session.branch = mk_branches_master.id AND
           student_test_session.test_time = center_time_table.id AND
           student_test_session.user_id = {} AND
           student_test_session.state != 'done' AND  

           mk_link.student_id = mk_student_register.id AND

           center_time_table.period_id = test_period.id AND 
           center_time_table.date <= current_date AND
           center_time_table.date = '{}' AND
           center_time_table.period_id = {};
           '''.format(employee_id, date, period_id)

        self.env.cr.execute(query_string)
        test_teacher_test = self.env.cr.dictfetchall()
        return test_teacher_test

    @api.model
    def student_test_sessions(self, link_id):
        try:
            link_id = int(link_id)
        except:
            pass

        query_string = ''' 

                SELECT exam.id id, 
                   episode.name || '/' || student.display_name test_name,
                   to_char(center_exam.date, 'YYYY-MM-DD') test_date,
                   period.name period,
                   exam.state,
           		exam.appreciation,
           		exam.final_degree degree,
           		branch_exam.name branch,
           		branch_exam.trackk trackk,
           		test_name.name test_type,
           		test_center.display_name test_center,
           		test_center_prepare.place_options exam_place,
           		mosque.name mosque


                   FROM student_test_session exam
                   LEFT JOIN mk_link link ON (exam.student_id=link.id)
                   LEFT JOIN mk_episode episode ON (link.episode_id=episode.id)
           		LEFT JOIN mk_student_register student ON (link.student_id=student.id)
                   LEFT JOIN center_time_table center_exam ON (exam.test_time=center_exam.id)
                   LEFT JOIN test_period period ON (center_exam.period_id=period.id)
           		LEFT JOIN mk_branches_master branch_exam ON (exam.branch=branch_exam.id)
           		LEFT JOIN mk_test_names test_name ON (exam.test_name=test_name.id)
           		LEFT JOIN mak_test_center test_center ON (exam.test_center_id=test_center.id)
           		LEFT JOIN mk_test_center_prepration test_center_prepare ON (exam.center_id=test_center_prepare.id)
           		LEFT JOIN mk_mosque mosque ON (test_center_prepare.internal_place=mosque.id)

                   WHERE link.id={}
                   order by center_exam.date;
                   '''.format(link_id)
        self.env.cr.execute(query_string)
        test_session_episode = self.env.cr.dictfetchall()
        return test_session_episode

    @api.model
    def test_session_episode(self, episode_id):
        try:
            episode_id = int(episode_id)
        except:
            pass

        query_string = ''' 

           SELECT exam.id id, 
           episode.name || '/' || student.display_name test_name, 
           center_exam.date test_date

           FROM student_test_session exam
           LEFT JOIN mk_link link ON (exam.student_id=link.id)
           LEFT JOIN mk_episode episode ON (link.episode_id=episode.id)
           LEFT JOIN mk_student_register student ON (link.student_id=student.id)
           LEFT JOIN center_time_table center_exam ON (exam.test_name=center_exam.id)

           WHERE link.episode_id={}
           order by center_exam.date;
           '''.format(episode_id)

        self.env.cr.execute(query_string)
        test_session_episode = self.env.cr.dictfetchall()
        return test_session_episode

    @api.multi
    def assign_committee(self):
        sessions = self.env['student.test.session'].search([('id', 'in', self.env.context.get('active_ids', []))])
        centers = []
        msg_error = False
        for session in sessions:
            center_id = session.center_id.id
            if center_id not in centers:
                centers.append(center_id)
                if len(centers) >1:
                    msg_error = (_('Selected student test sessions must have same center.'))
                    centers = []
                    break

            current_date = datetime.now().date()
            exam_end_date = datetime.strptime(session.center_id.exam_end_date, '%Y-%m-%d').date()
            if session.study_class_id and session.study_class_id.is_default and current_date > exam_end_date:
                raise ValidationError(_('عذرا لايمكنك إسناد لجنة إختبار بعد تاريخ نهاية الاختبارات'))
            if session.state == 'done':
                raise ValidationError(_('عذرا لايمكنك إسناد لجنة إختبار لجلسة اختبار منتهية'))
            if not session.editable or not session.active:
                raise ValidationError(_('عذرا لايمكنك إسناد لجنة إختبار'))

        if self.env.user.has_group('maknon_tests.select_exiaminer_session'):
            committee_obj = self.env['committee.tests'].search([('commitee_id', 'in', centers)])
            view_id = self.env.ref('maknon_tests.committe_migration_wizard_view_form').id
            vals ={'name': _('Assign committee'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'add.comittee.wizard',
                    'views': [(view_id, 'form')],
                    'view_id': view_id,
                    'target': 'new',
                    'domain':[('id', 'in', committee_obj.ids)],
                    'context': {'default_session_ids': self.env.context.get('active_ids', []),
                                'default_msg_error': msg_error}}
            return vals

    @api.multi
    def update_branch_wizard_action(self):
        update_form = self.env.ref('maknon_tests.branch_form_wizard')
        vals = {
            'name': _(' تصحيح الفرع '),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'update.branch.wizard',
            'views': [(update_form.id, 'form')],
            'view_id': update_form.id,
            'context': {'default_branch': self.branch.id,
                        'default_session_id': self.id},
            'target': 'new',
        }
        return vals

    @api.model
    def cron_get_wrong_employee_sessions(self):
        employee_sessions = self.env['student.test.session'].search([('category','!=',False)])
        wrong_sessions = []
        for rec in employee_sessions:
            st = rec.studnt_id
            if st.no_identity:
                identification_id = st.passport_no
            else:
                identification_id = st.identity_no
            if rec.employee_id.identification_id != identification_id:
                employee = self.env['hr.employee'].sudo().search([('identification_id','=',identification_id)] ,limit=1)
                rec.write({'employee_id':employee.id})
                wrong_sessions.append(rec.id)


class inheritedlink(models.Model):
    _inherit='mk.link'

    company_tests = fields.One2many("student.test.session","student_id","company tests")
    category      = fields.Selection(related='student_id.category', readonly=True, store=True)
    

class mk_student_register(models.Model):
    _inherit = 'mk.student.register'
    
    test_session_ids = fields.One2many("student.test.session", "studnt_id", "Student test session")
    archived_test_session_ids = fields.One2many("student.test.session", "studnt_id", "Student test session", domain=[('active', '!=', True)])
    category         = fields.Selection([('teacher', 'المعلمين'),
                                         ('center_admin','مدراء / مساعدي مدراء المركز'),
                                         ('bus_sup','مشرف الباص'),
                                         ('supervisor', 'مشرفين وإداريين المسجد / المدرسة'),
                                         ('admin', 'المشرف العام للمسجد /المدرسة'),
                                         ('edu_supervisor', 'مشرف تربوي'),
                                         ('managment','إداري\إداريين'),
                                         ('others','خدمات مساعدة')], string="التصنيف", default=False)


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    test_session_ids = fields.One2many("student.test.session", "employee_id", "Employee test session")