# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class testsSesstionWizard(models.TransientModel):
    _name = "tests.sesstion.wizard"

    @api.one
    @api.depends('episode_study_class_id', 'exam_study_class_id', 'center_id', 'mosque_category_id', 'supervisor_id', 'mosque_id', 'teacher_id','gender_type')
    def get_type_filter(self):
        center_id = self.center_id.id
        mosque_category_id = self.mosque_category_id.id
        supervisor = self.supervisor_id
        episode_study_class = self.episode_study_class_id
        # exam_study_class = self.exam_study_class_id
        mosque_id = self.mosque_id.id
        teacher_id = self.teacher_id.id
        gender_type = self.gender_type

        if episode_study_class:
            self.type_filter = 'episode_study_class'
        if center_id:
            self.type_filter = 'center'
        if gender_type:
            self.type_filter = 'gender_type'
        if mosque_category_id:
            self.type_filter = 'category'
        if supervisor:
            self.type_filter = 'supervisor'
        if mosque_id:
            self.type_filter = 'mosque'
        if teacher_id:
            self.type_filter = 'teacher'

    episode_academic_id     = fields.Many2one('mk.study.year',  string='العام الدراسي الخاص بالحلقات',    required=True)
    episode_study_class_id  = fields.Many2one('mk.study.class', string='الفصل الدراسي الخاص بالحلقات',    required=True)
    exam_academic_id        = fields.Many2one('mk.study.year', string='العام الدراسي الخاص بالإختبارات',  required=True)
    exam_study_class_id     = fields.Many2one('mk.study.class',string='الفصل الدراسي الخاص  بالإختبارات', required=True)
    center_id               = fields.Many2one("hr.department",  string="center")
    gender_type             = fields.Selection([('male', 'Male'),
                                                ('female', 'Female')], string="Gender Type")
    supervisor_id           = fields.Many2one("hr.employee",           string="المشرف التربوي")
    mosque_id               = fields.Many2one("mk.mosque",             string="Mosque")
    mosque_category_id      = fields.Many2one("mk.mosque.category",    string="Mosque Category")
    teacher_id              = fields.Many2one("hr.employee",           string="Teacher")
    report_type             = fields.Selection([('total', 'Totals'),
                                                ('detailed', 'Detailed'), ], string="Report Type", default='total')
    episode_ids             = fields.Many2many("mk.episode", string="Episode")

    type_filter             = fields.Selection([('episode_study_class', 'Episode Study class'),
                                                ('center', 'Center'),
                                                ('category', 'Category'),
                                                ('mosque', 'Mosque'),
                                                ('supervisor', 'Supervisor'),
                                                ('teacher', 'Teacher'),
                                                ('gender_type', 'Gender')], string="Type filter",  compute=get_type_filter)
    type_test_id            = fields.Many2one('mk.test.names',      string='نوع الاختبار',  domain="[('test_group','=','student')]")
    branch_id               = fields.Many2one('mk.branches.master', string='فرع الاختبار',  domain="[('branch_group','=','student')]")
    is_test_session         = fields.Boolean(string="Show only shared episodes", default=True)
    report_name             = fields.Selection([('subscribed_student_tests_report', 'Subscribed student tests report'),
                                               ('passed_student_tests_report', 'Passed student tests report'),
                                               ('center_test_report', 'Center tests report')], default='subscribed_student_tests_report', string="Report name")

    @api.onchange('center_id')
    def change_center(self):
        self.supervisor_id = False

    @api.onchange('gender_type')
    def change_gender_type(self):
        self.mosque_category_id = False
        self.mosque_id = False

        gender = self.gender_type

        if gender:
            mosque_category_ids = self.env['mk.mosque.category'].sudo().search([('mosque_type', '=', gender)]).ids
            return {'domain': {'mosque_category_id': [('id', 'in', mosque_category_ids)]}}

    @api.onchange('type_test_id')
    def change_type_test_id(self):
        self.branch_id = False

        type_test_id = self.type_test_id.id
        if type_test_id:
            return {'domain': {'branch_id': [('test_name', '=', type_test_id),('branch_group','=','student')]}}

    @api.onchange('episode_study_class_id', 'exam_study_class_id', 'center_id', 'gender_type', 'mosque_category_id', 'supervisor_id')
    def change_supervisor(self):
        self.mosque_id = False
        domain = []

        center_id = self.center_id.id
        mosque_category_id = self.mosque_category_id.id
        supervisor = self.supervisor_id
        gender_type = self.gender_type

        if center_id:
            domain += [('center_department_id', '=', center_id)]

        if mosque_category_id:
            domain += [('categ_id', '=', mosque_category_id)]

        elif gender_type:
            domain += [('categ_id.mosque_type', '=', gender_type)]

        if supervisor:
            domain += [('id', 'in', supervisor.mosque_sup.ids)]

        domain += ['|', ('active', '=', True), ('active', '=', False)]

        mosque_ids = self.env['mk.mosque'].search(domain).ids
        teacher_ids = self.env['hr.employee'].search([('mosqtech_ids', 'in', mosque_ids)]).ids

        return {'domain': {'mosque_id': [('id', 'in', mosque_ids)],
                           'teacher_id': [('id', 'in', teacher_ids)]},
                           'values': {'mosque_id': False}}

    @api.onchange('mosque_id')
    def change_mosque_id(self):
        domain = []
        domain_mosque = []
        teacher_ids = []
        episode_list_ids = []

        self.teacher_id = False
        mosque_id = self.mosque_id.id
        center_id = self.center_id.id
        mosque_category_id = self.mosque_category_id.id
        gender_type = self.gender_type
        supervisor = self.supervisor_id
        episode_study_class = self.episode_study_class_id

        if center_id:
            domain += [('mosque_id.center_department_id', '=', center_id)]
            domain_mosque += [('center_department_id', '=', center_id)]

        if mosque_category_id:
            domain += [('mosque_id.categ_id', '=', mosque_category_id)]
            domain_mosque += [('categ_id', '=', mosque_category_id)]

        elif gender_type:
            domain += [('mosque_id.categ_id.mosque_type', '=', gender_type)]
            domain_mosque += [('categ_id.mosque_type', '=', gender_type)]

        if supervisor:
            domain += [('mosque_id', 'in', supervisor.mosque_sup.ids)]
            domain_mosque += [('id', 'in', supervisor.mosque_sup.ids)]

        if mosque_id:
            if episode_study_class:
                domain += [('study_class_id', '=', episode_study_class.id)]
            domain += [('mosque_id', '=', mosque_id)]
            episode_list = self.env['mk.episode'].search(domain)
            for episode in episode_list:
                teacher_id = episode.teacher_id.id
                if teacher_id not in teacher_ids:
                    teacher_ids += [teacher_id]
                    episode_list_ids.append(episode.id)
            domain += ['|', ('active', '=', True), ('active', '=', False)]
        else:
            domain_mosque += ['|', ('active', '=', True), ('active', '=', False)]

            mosque_ids = self.env['mk.mosque'].search(domain_mosque).ids
            teacher_ids = self.env['hr.employee'].search([('mosqtech_ids', 'in', mosque_ids)]).ids

        return {'domain': {'teacher_id': [('id', 'in', teacher_ids)]}}

    def print_report(self):
        self.ensure_one()
        episode_study_class = self.episode_study_class_id

        domain = [('study_class_id', '=', episode_study_class.id)]

        data = {'ids':   self.ids,
                'model': self._name,

                'form': {'episode_academic_id':      self.episode_academic_id.id,
                         'episode_academic_name':    self.episode_academic_id.name,
                         'episode_study_class_id':   self.episode_study_class_id.id,
                         'episode_study_class_name': self.episode_study_class_id.name,
                         'exam_academic_id':         self.exam_academic_id.id,
                         'exam_academic_name':       self.exam_academic_id.name,
                         'exam_study_class_id':      self.exam_study_class_id.id,
                         'exam_study_class_name':    self.exam_study_class_id.name,
                         'gender_type':              self.gender_type,
                         'center_id':                self.center_id.id,
                         'center_name':              self.center_id.name,
                         'supervisor_id':            self.supervisor_id.id,
                         'supervisor_name':          self.supervisor_id.name,
                         'mosque_category_id':       self.mosque_category_id.id,
                         'mosque_category_name':     self.mosque_category_id.name,
                         'mosque_id':                self.mosque_id.id,
                         'mosque_id_name':           self.mosque_id.name,

                         'teacher_id':               self.teacher_id.id,
                         'teacher_name':             self.teacher_id.name,

                         'type_test_id':             self.type_test_id.id,
                         'branch_id':                self.branch_id.id,

                         'type_test_name':           self.type_test_id.name,
                         'branch_name':              self.branch_id.name,

                         'domain':                   domain,
                         'report_type':              self.report_type,
                         'is_test_session':          self.is_test_session,
                         'type_filter':              self.type_filter, }, }
        return self.env.ref('maknon_tests.test_report').report_action(self, data=data)

    def print_excel_report(self):
        self.ensure_one()
        episode_study_class = self.episode_study_class_id

        domain = [('study_class_id', '=', episode_study_class.id)]

        data = {'ids': self.ids,
                'model': self._name,

                'form': {'episode_academic_id': self.episode_academic_id.id,
                         'episode_academic_name': self.episode_academic_id.name,
                         'episode_study_class_id': self.episode_study_class_id.id,
                         'episode_study_class_name': self.episode_study_class_id.name,
                         'exam_academic_id': self.exam_academic_id.id,
                         'exam_academic_name': self.exam_academic_id.name,
                         'exam_study_class_id': self.exam_study_class_id.id,
                         'exam_study_class_name': self.exam_study_class_id.name,
                         'gender_type': self.gender_type,
                         'center_id': self.center_id.id,
                         'center_name': self.center_id.name,
                         'supervisor_id': self.supervisor_id.id,
                         'supervisor_name': self.supervisor_id.name,
                         'mosque_category_id': self.mosque_category_id.id,
                         'mosque_category_name': self.mosque_category_id.name,
                         'mosque_id': self.mosque_id.id,
                         'mosque_id_name': self.mosque_id.name,

                         'teacher_id': self.teacher_id.id,
                         'teacher_name': self.teacher_id.name,

                         'type_test_id': self.type_test_id.id,
                         'branch_id': self.branch_id.id,

                         'type_test_name': self.type_test_id.name,
                         'branch_name': self.branch_id.name,

                         'domain': domain,
                         'report_type': self.report_type,
                         'is_test_session': self.is_test_session,
                         'type_filter': self.type_filter,
                         'report_name': self.report_name, }, }
        return self.env.ref('maknon_tests.test_excel_report').report_action(self, data=data)