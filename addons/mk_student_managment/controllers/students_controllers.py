import odoo.http as http
from odoo.http import Response
from odoo import SUPERUSER_ID
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo import http
import logging
_logger = logging.getLogger(__name__)


class StudentsControllers(http.Controller):    
    @http.route('/student_prepare/get_report/<int:link_id>',type='http', auth='public',  csrf=False)
    def get_report(self, link_id, **args):
        obj_student_prepare = request.env['student.prepare.report'].sudo().browse([SUPERUSER_ID])
        pdf = obj_student_prepare.get_pdf(int(link_id))[0]

        pdfhttpheaders = [('Content-Type',        'application/pdf'),
                          ('Content-Length',      len(pdf)),
                          ('Content-Disposition', 'attachment; filename="student_prepare_report.pdf"'),]
        
        return request.make_response(pdf, headers=pdfhttpheaders)
