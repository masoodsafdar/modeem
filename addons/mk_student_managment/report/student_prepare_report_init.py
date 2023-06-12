# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class StudentPrepareReport(models.AbstractModel):
    _name = 'report.mk_student_managment.student_prepare_report_template'
       
    @api.model
    def get_report_values(self, docids, data=None):        
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        
        student_prepare_report = self.env['ir.actions.report']._get_report_from_name('mk_student_managment.student_prepare_report_template')
        return {'doc_ids':   self.ids,
                'doc_model': student_prepare_report.model,

                'student':            data['form']['student'],
                'episode':            data['form']['episode'],
                'listen_lines':       data['form']['listen_lines'],
                'review_small_lines': data['form']['review_small_lines'],
                'review_big_records': data['form']['review_big_records'],
                'tlawa_records':      data['form']['tlawa_records'],
                }
