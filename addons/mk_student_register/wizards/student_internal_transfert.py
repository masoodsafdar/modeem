# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError

import logging
_logger = logging.getLogger(__name__)


class StudentInternalTransferWizard(models.TransientModel):
    _name = "student.internal.transfer"

    link_id  = fields.Many2one("mk.link")
    mosq_id  = fields.Many2one(related="link_id.mosq_id",  string="المسجد")
    episode_id = fields.Many2one("mk.episode", string="الحلقة", required=True)

    def transfer_student(self):
        link_id = self.link_id
        student_test = self.env['student.test.session'].search([('student_id', '=', link_id.id),
                                                                ('state', '!=', 'cancel')], limit=1)
        if student_test:
            raise ValidationError(_('لا يمكنك نقل الطالب لارتباطه بجلسات اختبار مبرمجة في الحلقة'))
        elif self.episode_id.teacher_id == False:
            raise ValidationError(_('عذرا ! لابد من اختيار معلم للحلقة أول'))
        else:
            link_id.write({'episode_id': self.episode_id.id})
            preparation_id = self.link_id.preparation_id
            preparation_id.write({'link_id': self.link_id.id,
                                  'name': self.link_id.teacher_id.id,
                                  'stage_pre_id': self.episode_id.id})





