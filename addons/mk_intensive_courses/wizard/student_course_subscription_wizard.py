#-*- coding:utf-8 -*-
from odoo import models, fields, api, tools

import logging

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class StudentCourseSubscription(models.TransientModel):
    _name = 'student.course.subscription'

    course_id        = fields.Many2one('mk.course.request', string="الدورة المكثفة")
    branch_id        = fields.Many2one("mk.parts.names", string="الفرع")
    student_ids      = fields.Many2many('mk.student.register', string="الطلاب")
    type_branch_path = fields.Selection([('momorize', 'حفظ'),
                                         ('review', 'مراجعة'),
                                         ('correct_recitation', 'تصحيح تلاوة')], string="المسار")

    @api.onchange('course_id')
    def onchange_course(self):
        course = self.course_id
        return {'domain': {'branch_id': [('id', 'in', course.branches_ids.ids)],
                           'student_ids': [('mosq_id', '=', course.mosque_id.id)]}}

    @api.one
    def action_students_course_register(self):
        student_ids = self.student_ids
        if not student_ids:
            raise ValidationError('الرجاء تحديد الطلاب')
        course_id = self.course_id.id
        branch_id = self.branch_id.id
        type_branch_path = self.type_branch_path
        for student in student_ids:
            vals = { 'student_id': student.id,
                     'request_st_id': course_id,
                     'branch_id': branch_id,
                     'branch_path_type': type_branch_path
            }
            self.env['mk.course.student'].create(vals)
        return True