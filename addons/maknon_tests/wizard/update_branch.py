from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class PopupUpdate(models.TransientModel):

    _name = 'update.branch.wizard'

    @api.onchange('session_id')
    def show_branch(self):
        session_id = self.session_id
        study_class_id = session_id.study_class_id
        branches = self.env['mk.branches.master'].search([('study_class_id', '=', study_class_id.id)])
        return {'domain': {'branch': [('id', 'in', branches.ids)]}}

    branch = fields.Many2one("mk.branches.master", string="الفرع" ,required=True)
    session_id = fields.Many2one('student.test.session')

    @api.multi
    def update_branch_action(self):
        session_id = self.session_id
        current_branch =  session_id.branch
        current_branch_type = current_branch.test_name.type_test
        updated_branch = self.branch
        updated_branch_type = updated_branch.test_name.type_test

        test_session_same_branch = self.env['student.test.session'].search([('id', '!=', session_id.id),
                                                                            ('student_id.student_id', '=', session_id.student_id.student_id.id),
                                                                            ('branch', '=', updated_branch.id),
                                                                            '|', ('state', 'not in',['cancel', 'absent', 'done']),
                                                                            '&', ('state', '=', 'done'),
                                                                                 ('is_pass', '=', True)], limit=1)

        test_session_diff_trackk = self.env['student.test.session'].search([('id', '!=', session_id.id),
                                                                            ('student_id.student_id', '=', session_id.student_id.student_id.id),
                                                                            ('branch.trackk', '!=', updated_branch.trackk),
                                                                            '|', ('state', 'not in', ['cancel', 'absent', 'done']),
                                                                                '&', ('state', '=', 'done'),
                                                                                      ('is_pass', '=', True)], limit=1)

        test_session_correct_citation = self.env['student.test.session'].search([('student_id.student_id', '=', session_id.student_id.id),
                                                                                 ('test_name.type_test', '=', 'correct_citation'),
                                                                                 '|', ('state', 'not in', ['cancel', 'absent', 'done']),
                                                                                 '&', ('state', '=', 'done'),
                                                                                 ('is_pass', '=', True)], order="id desc", limit=1)

        if test_session_same_branch:
            msg = 'عذرا توجد جلسة اختبار أخرى للطالب في نفس الفرع'
            raise ValidationError(msg)

        elif updated_branch_type not in ['final', 'correct_citation']:
            if test_session_diff_trackk:
                msg = 'عذرا لا يسمح بتغيير مسار الطالب'
                raise ValidationError(msg)

        elif updated_branch_type == 'correct_citation':
            if test_session_correct_citation:
                if session_id.is_pass and session_id.state == 'done':
                    msg = 'اجتاز الطالب فرع تصحيح التلاوة' + ' ' + 'بنجاح خلال' + ' ' + session_id.academic_id.name + ' ' + session_id.study_class_id.name
                else:
                    msg = ' الطالب  مسجل في فرع تصحيح التلاوة' + ' ' + 'خلال' + ' ' + session_id.academic_id.name + ' ' + session_id.study_class_id.name
                raise ValidationError(msg)
        session_id.sudo().write({'branch': updated_branch.id})