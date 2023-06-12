from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class StudentTestSession(models.Model):
    _inherit = 'student.test.session'

    is_student_meqraa = fields.Boolean(string='Student Meqraa', default=False)


class TestRegister(models.TransientModel):
    _inherit="test.register"

    @api.multi
    def ok(self):
        test_center = self.test_time.center_id
        study_class_id = self.study_class_id
        current_date = datetime.now().date()
        registration_end__date = datetime.strptime(test_center.registeration_end_date, '%Y-%m-%d').date()
        if study_class_id.is_default and current_date > registration_end__date:
            raise ValidationError(_('عذرا لايمكنك تسجيل الطلاب بعد تاريخ نهاية التسجيل في الاختبارات'))
        else:
            for student in self.student_id:
                if student.flag == True and student.student_id and student.test_name and student.branch:
                    vals = {'student_id': student.student_id.id,
                            'test_name': student.test_name.id,
                            'test_time': self.test_time.id,
                            'branch': student.branch.id,
                            'center_name': self.test_time.center_id.center_id.display_name,
                            'masjed_name': student.student_id.sudo().mosq_id.display_name,
                            'mosque_id': student.student_id.sudo().mosq_id.id,
                            'category': student.student_id.student_id.category}
                    if test_center.committee_assign_type == 'supervisor_assign':
                        student_mosque = student.student_id.mosq_id
                        commitee_member = self.env['committe.member'].search([('center_id', '=', test_center.id),
                                                                              ('member_id.category', '=',
                                                                               'edu_supervisor'),
                                                                              ('member_id.mosque_sup', 'in',
                                                                               [student_mosque.id])], limit=1)
                        vals.update({'committe_id': commitee_member.committe_id.id,
                                     'user_id': commitee_member.member_id.user_id.id})

                    self.env['student.test.session'].create(vals)