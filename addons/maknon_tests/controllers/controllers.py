# -*- coding: utf-8 -*-
import operator
import sys, json
import logging
import urllib.parse

from cryptography.fernet import Fernet
import base64

from odoo.addons.maknon_tests.models import student_test_session

from odoo.exceptions import UserError
from odoo.http import content_disposition
_logger = logging.getLogger(__name__)
from odoo.http import request
from odoo import http, _
from odoo.addons.web.controllers.main import ExcelExport,CSVExport,serialize_exception


class internalTestController(http.Controller):


    @http.route('/test/start_student_session/<int:session_id>', type='json', auth='public',  csrf=False)
    def st_session(self, session_id=False,**args):
        session=request.env['student.test.session'].sudo().search([('id','=',session_id)])
        
        if session:
            #session[0].sudo().write({'controller_flag':True})
            session[0].sudo().write({'branch_duration':session[0].sudo().branch.duration})
            session[0].sudo().start_exam()
            return str({'start_date':session[0].start_date,'status':True})
        else:
            return str({'status':False})

    @http.route('/test/end_student_session/<int:session_id>', type='json', auth='public',  csrf=False)
    def std_end_session(self, session_id=False,**args):
        session=request.env['student.test.session'].sudo().search([('id','=',session_id)])
        
        if session:
            #session[0].sudo().write({'controller_flag':True})
            #session[0].sudo().write({'branch_duration':session[0].sudo().branch.duration})
            session[0].sudo().end_exam()
            return str({'done_date':session[0].done_date,'status':True})
        else:
            return str({'status':False})

    @http.route('/certificate/<string:encoded_id>', type='http', auth='public', website=True)
    def view_certificate(self, encoded_id, **args):
        key = args.get('key')
        decoded = base64.b64decode(encoded_id.encode())
        cipher = Fernet(key.encode())

        decrypted_id = cipher.decrypt(decoded).decode()

        record = request.env['student.test.session'].sudo().search([('id', '=', decrypted_id)], limit=1)
        report = request.env['ir.actions.report'].sudo()._get_report_from_name('maknon_tests.final_test_certificate_report')
        context = dict(request.env.context)
        pdf = report.with_context(context).sudo().render_qweb_pdf(record.sudo().id, data={})[0]
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)


class ExcelExportInherit(ExcelExport):
    @http.route('/web/export/xls', type='http', auth="user")
    @serialize_exception
    def index(self, data, token):
        params = json.loads(data)
        model, fields, ids, domain, import_compat = \
            operator.itemgetter('model', 'fields', 'ids', 'domain', 'import_compat')(params)

        Model = request.env[model].with_context(import_compat=import_compat, **params.get('context', {}))
        records = Model.browse(ids) or Model.search(domain, offset=0, limit=False, order=False)
        if self.max_rows and len(records) > self.max_rows:
            raise UserError(
                _('There are too many records (%s records, limit: %s) to export as this format. Consider splitting the export.') % (
                len(records), self.max_rows))

        if not Model._is_an_ordinary_table():
            fields = [field for field in fields if field['name'] != 'id']

        field_names = [f['name'] for f in fields]
        import_data = records.sudo().export_data(field_names, self.raw_data).get('datas', [])

        if import_compat:
            columns_headers = field_names
        else:
            columns_headers = [val['label'].strip() for val in fields]

        return request.make_response(self.from_data(columns_headers, import_data),
                                     headers=[('Content-Disposition',
                                               content_disposition(self.filename(model))),
                                              ('Content-Type', self.content_type)],
                                     cookies={'fileToken': token})
        # return self.sudo().base(data, token)

class CSVExportInherit(CSVExport):
    @http.route('/web/export/csv', type='http', auth="user")
    @serialize_exception
    def index(self, data, token):
        params = json.loads(data)
        model, fields, ids, domain, import_compat = \
            operator.itemgetter('model', 'fields', 'ids', 'domain', 'import_compat')(params)

        Model = request.env[model].with_context(import_compat=import_compat, **params.get('context', {}))
        records = Model.browse(ids) or Model.search(domain, offset=0, limit=False, order=False)
        if self.max_rows and len(records) > self.max_rows:
            raise UserError(
                _('There are too many records (%s records, limit: %s) to export as this format. Consider splitting the export.') % (
                len(records), self.max_rows))

        if not Model._is_an_ordinary_table():
            fields = [field for field in fields if field['name'] != 'id']

        field_names = [f['name'] for f in fields]
        import_data = records.sudo().export_data(field_names, self.raw_data).get('datas', [])

        if import_compat:
            columns_headers = field_names
        else:
            columns_headers = [val['label'].strip() for val in fields]

        return request.make_response(self.from_data(columns_headers, import_data),
                                     headers=[('Content-Disposition',
                                               content_disposition(self.filename(model))),
                                              ('Content-Type', self.content_type)],
                                     cookies={'fileToken': token})
        # return self.sudo().base(data, token)


