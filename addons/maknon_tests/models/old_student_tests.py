#-*- coding:utf-8 -*-
from odoo import models, fields, api,_

import logging
_logger = logging.getLogger(__name__)

class OldStudentTests(models.Model):
    _name = 'old.student.test'
    _inherit = ['mail.thread']
    _rec_name='student_name'

    student_name = fields.Char('الطالب')
    identity_nbr = fields.Char('رقم الهوية/جواز السفر')
    branch       = fields.Char('الفرع')
    appreciation = fields.Char('التقدير')
    mosque_name   = fields.Char('المسجد/المدرسة')
    degree        = fields.Char('الدرجة المستحقة')
    department_id = fields.Char('اسم المركز')
    nationality   = fields.Char('الجنسية')
    mobile        = fields.Char('الجوال')
    commitee      = fields.Char('عضو اللجنة')
    episode_name = fields.Char('اسم الحلقة')
    date_test    = fields.Char('تاريخ الاختبار')
    date_birth   = fields.Char('تاريخ الميلاد')
    year         = fields.Char('العام الدراسي')
    email    = fields.Char('البريد الالكتروني')
    district = fields.Char('الحي')
    notes    = fields.Text('ملحوظات')