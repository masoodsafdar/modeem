# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class StudentReportWizard(models.TransientModel):
    _name = "student.report.wizard"

    # @api.one
    @api.depends('study_class_id', 'center_id', 'mosque_category_id', 'supervisor_id', 'mosque_id', 'teacher_id','gender_type')
    def get_type_filter(self):
        center_id             = self.center_id.id
        mosque_category_id    = self.mosque_category_id.id
        supervisor            = self.supervisor_id
        study_class           = self.study_class_id
        mosque_id             = self.mosque_id.id
        teacher_id            = self.teacher_id.id
        gender_type            = self.gender_type

        if study_class:
            self.type_filter = 'study_class'
        if center_id:
            self.type_filter = 'center'
        if mosque_category_id:
            self.type_filter = 'category'
        if supervisor:
            self.type_filter = 'supervisor'
        if mosque_id:
            self.type_filter = 'mosque'
        if teacher_id:
            self.type_filter = 'teacher'
        if gender_type:
            self.type_filter = 'gender_type'

    academic_id             = fields.Many2one('mk.study.year', required=True)
    study_class_id          = fields.Many2one('mk.study.class', required=True)
    center_id               = fields.Many2one("hr.department", string="center")
    gender_type             = fields.Selection([('male', 'Male'),
                                                ('female', 'Female')], string="Gender Type")
    supervisor_id           = fields.Many2one("hr.employee", string="المشرف التربوي")
    mosque_id               = fields.Many2one("mk.mosque", string="Mosque")
    mosque_category_id      = fields.Many2one("mk.mosque.category", string="Mosque Category")
    teacher_id              = fields.Many2one("hr.employee", string="Teacher")

    episode_ids             = fields.Many2many("mk.episode", string="Episode")

    type_filter             = fields.Selection([('study_class', 'Study class'),
                                                ('center', 'Center'),
                                                ('category', 'Category'),
                                                ('mosque', 'Mosque'),
                                                ('supervisor', 'Supervisor'),
                                                ('teacher', 'Teacher'),
                                                ('gender_type', 'Gender')], string="Type filter", compute=get_type_filter)

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

    @api.onchange('study_class_id', 'center_id', 'gender_type', 'mosque_category_id', 'supervisor_id')
    def change_supervisor(self):
        self.mosque_id = False
        domain = []

        center_id = self.center_id.id
        mosque_category_id = self.mosque_category_id.id
        supervisor = self.supervisor_id
        gender_type = self.gender_type
        study_class = self.study_class_id

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
        teacher_ids = []
        episode_list_ids = []

        self.teacher_id = False
        mosque_id = self.mosque_id.id
        teacher_id = self.teacher_id.id
        center_id = self.center_id.id
        mosque_category_id = self.mosque_category_id.id
        gender_type = self.gender_type
        supervisor = self.supervisor_id
        study_class = self.study_class_id

        if study_class:
            domain += [('study_class_id', '=', study_class.id)]

        if center_id:
            domain += [('mosque_id.center_department_id', '=', center_id)]

        if mosque_category_id:
            domain += [('mosque_id.categ_id', '=', mosque_category_id)]

        elif gender_type:
            domain += [('categ_id.mosque_type', '=', gender_type)]

        if supervisor:
            domain += [('mosque_id', 'in', supervisor.mosque_sup.ids)]

        if mosque_id:
            domain += [('mosque_id', '=', mosque_id)]
            episode_list = self.env['mk.episode'].search(domain)
            for episode in episode_list:
                teacher_id = episode.teacher_id.id
                if teacher_id not in teacher_ids:
                    teacher_ids += [teacher_id]
                    episode_list_ids.append(episode.id)
            domain += ['|', ('active', '=', True), ('active', '=', False)]
        else:
            domain += ['|', ('active', '=', True), ('active', '=', False)]

            mosque_ids = self.env['mk.mosque'].search(domain).ids
            teacher_ids = self.env['hr.employee'].search([('mosqtech_ids', 'in', mosque_ids)]).ids

        return {'domain': {'teacher_id': [('id', 'in', teacher_ids)]}}

    def print_report(self):
        self.ensure_one()
        study_class = self.study_class_id

        domain = [('study_class_id', '=', study_class.id)]

        data = {'ids':                           self.ids,
                'model':                         self._name,

                'form': {'academic_id':          self.academic_id.id,
                         'academic_name':        self.academic_id.name,

                         'study_class_id':       self.study_class_id.id,
                         'study_class_name':     self.study_class_id.name,

                         'gender_type':          self.gender_type,

                         'center_id':            self.center_id.id,
                         'center_name':          self.center_id.name,

                         'supervisor_id':        self.supervisor_id.id,
                         'supervisor_name':      self.supervisor_id.name,

                         'mosque_category_id':   self.mosque_category_id.id,
                         'mosque_category_name': self.mosque_category_id.name,

                         'mosque_id':            self.mosque_id.id,
                         'mosque_id_name':       self.mosque_id.name,

                         'teacher_id':           self.teacher_id.id,
                         'teacher_name':         self.teacher_id.name,

                         'domain':               domain,
                         'type_filter':          self.type_filter, }, }
        return self.env.ref('mk_student_register.students_report').report_action(self, data=data)