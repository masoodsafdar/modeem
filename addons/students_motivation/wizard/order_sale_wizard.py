# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrderWizard(models.TransientModel):
    _name = "sale.order.wizard"

    @api.one
    @api.depends('center_id', 'gender_type', 'mosque_category_id', 'mosque_id', 'student_id')
    def get_type_filter(self):
        center_id = self.center_id.id
        gender_type = self.gender_type
        mosque_category_id = self.mosque_category_id.id
        mosque_id = self.mosque_id.id
        student_id = self.student_id.id

        if center_id:
            self.type_filter = 'center'
        if gender_type:
            self.type_filter = 'gender_type'
        if mosque_category_id:
            self.type_filter = 'category'
        if mosque_id:
            self.type_filter = 'mosque'
        if student_id:
            self.type_filter = 'student'

    study_year_id      = fields.Many2one('mk.study.year',  string='Study year')
    study_class_id     = fields.Many2one('mk.study.class', string='Study class')
    center_id          = fields.Many2one("hr.department",  string="center")
    gender_type        = fields.Selection([('male', 'Male'),
                                           ('female', 'Female')], string="Gender Type")
    mosque_category_id = fields.Many2one("mk.mosque.category",    string="Mosque Category")
    mosque_id          = fields.Many2one("mk.mosque",             string="Mosque")
    student_id         = fields.Many2one("mk.student.register",   string="Student")
    type_filter        = fields.Selection([('center', 'Center'),
                                            ('gender_type', 'Gender'),
                                            ('category', 'Category'),
                                            ('mosque', 'Mosque'),
                                            ('student', 'Student')], string="Type filter", compute=get_type_filter)

    @api.onchange('gender_type')
    def change_gender_type(self):
        self.mosque_category_id = False
        self.mosque_id = False
        gender = self.gender_type

        if gender:
            mosque_category_ids = self.env['mk.mosque.category'].sudo().search([('mosque_type', '=', gender)]).ids
            return {'domain': {'mosque_category_id': [('id', 'in', mosque_category_ids)]}}

    @api.onchange('center_id', 'gender_type', 'mosque_category_id')
    def change_mosque(self):
        self.mosque_id = False
        domain = []

        center_id = self.center_id.id
        mosque_category_id = self.mosque_category_id.id
        gender_type = self.gender_type

        if center_id:
            domain += [('center_department_id', '=', center_id)]

        if mosque_category_id:
            domain += [('categ_id', '=', mosque_category_id)]

        elif gender_type:
            domain += [('categ_id.mosque_type', '=', gender_type)]

        domain += ['|', ('active', '=', True), ('active', '=', False)]

        mosque_ids = self.env['mk.mosque'].search(domain).ids
        return {'domain': {'mosque_id': [('id', 'in', mosque_ids)],}}

    @api.onchange('mosque_id')
    def change_student(self):
        domain = []
        domain_mosque = []

        self.student_id = False
        mosque_id = self.mosque_id.id
        center_id = self.center_id.id
        mosque_category_id = self.mosque_category_id.id
        gender_type = self.gender_type

        if center_id:
            domain += [('mosq_id.center_department_id', '=', center_id)]
            domain_mosque += [('center_department_id', '=', center_id)]

        if mosque_category_id:
            domain += [('mosq_id.categ_id', '=', mosque_category_id)]
            domain_mosque += [('categ_id', '=', mosque_category_id)]

        elif gender_type:
            domain += [('mosq_id.categ_id.mosque_type', '=', gender_type)]
            domain_mosque += [('categ_id.mosque_type', '=', gender_type)]

        if mosque_id:
            domain += [('mosq_id', '=', mosque_id)]
            domain += ['|', ('active', '=', True), ('active', '=', False)]
            student_ids = self.env['mk.student.register'].search(domain).ids

        else:
            domain_mosque += ['|', ('active', '=', True), ('active', '=', False)]

            mosque_ids = self.env['mk.mosque'].search(domain_mosque).ids
            student_ids = self.env['mk.student.register'].search([('mosq_id', 'in', mosque_ids)]).ids

        return {'domain': {'student_id': [('id', 'in', student_ids)]}}

    def print_report(self):
        self.ensure_one()
        data = {'ids': self.ids,
                'model': self._name,

                'form': {'study_year_id': self.study_year_id.id,
                         'study_year_name': self.study_year_id.name,
                         'study_class_id': self.study_class_id.id,
                         'study_class_name': self.study_class_id.name,

                         'center_id': self.center_id.id,
                         'center_name': self.center_id.name,

                         'gender_type': self.gender_type,

                         'mosque_category_id': self.mosque_category_id.id,
                         'mosque_category_name': self.mosque_category_id.name,

                         'mosque_id': self.mosque_id.id,
                         'mosque_name': self.mosque_id.name,

                         'student_id': self.student_id.id,
                         'student_name': self.student_id.display_name,

                         'type_filter': self.type_filter, },
                }
        return self.env.ref('students_motivation.sale_order_report').report_action(self, data=data)