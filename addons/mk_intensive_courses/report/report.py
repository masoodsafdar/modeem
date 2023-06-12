from datetime import datetime
from odoo import models,fields,api, _
from odoo import models, fields, api, exceptions, _


class CourseRequestREPORT(models.AbstractModel):
    _name = 'report.mk_intensive_courses.requist_report_template'

    @api.model
    def get_report_values(self, docids, data):
        docs = self.env['mk.course.request'].search([('id', 'in', docids)])
        setting_obj=self.env['mk.report.config'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)

        with_header = setting_obj.print_with_header
        with_footer = setting_obj.print_with_footer
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'mk.course.request',
            'docs': docs,
            'with_header':with_header,
            'with_footer':with_footer
            }
        return docargs
