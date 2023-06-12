from odoo import models, api, _
from datetime import datetime, date


class AlmostFinishedSupervisorRequestReportXlsx(models.AbstractModel):
    _inherit = 'report.report_xlsx.abstract'
    _name = 'report.mk_episode_management.almost_finished_super_req_report'

    def get_report_values(self, docids, data):
        docs = []

        departments = self.env['hr.department'].search([])
        for department in departments:
            supervisor_requests_dep = []
            supervisor_requests_mosques = []
            supervisor_requests = self.env['mosque.supervisor.request'].search([('id', 'in', docids.ids),
                                                               ('center_id', '=', department.id),
                                                               ('is_valid', '=', True),
                                                               ('permision_end_date','!=', None)], order="permision_end_date desc")
            if supervisor_requests:
                for request in supervisor_requests:
                    if request.mosque_id.id not in supervisor_requests_mosques:
                        supervisor_requests_mosques.append(request.mosque_id.id)
                    supervisor_requests_dep.append(request.id)
                docs.append({'center': department,
                             'supervisor_requests_mosques': supervisor_requests_mosques,
                             'supervisor_requests_dep': supervisor_requests_dep})
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'mosque.supervisor.request',
            'docs': docs,}
        return docargs


    def generate_xlsx_report(self, workbook,  data, docids):
        num_format = _('_ * #,##0.00_) ;_ * - #,##0.00_) ;_ * "-"??_) ;_ @_ ')
        bold = workbook.add_format({'bold': True})
        bold.set_align('top')
        currency_format = workbook.add_format({'num_format': _(num_format)})
        currency_format.set_align('top')
        report_format = workbook.add_format({'font_size': 24})
        topVertAlign = workbook.add_format()
        topVertAlign.set_align('top')

        active_inactive_mosq_domain = ['|', ('active', '=', True), ('active', '=', False)]


        def _header_sheet(sheet):
            sheet.write(0, 3, _('تقرير التكاليف المقاربة للنهاية (3 أشهر وأقل) '), report_format)
            sheet.write(4, 0, _('تم اصدارها في       %s') % (datetime.now()).strftime("%Y-%m-%d"))
            sheet.right_to_left()

        def body_report(sheet):
            sheet.write(row, 0, doc['center'].name, bold)

        def get_supervisor_requests(sheet):
            request_type = request.permision_type
            req_type = False
            if request_type == 'pe':
                req_type = 'دائم'
            elif request_type == 'te':
                req_type = 'مؤقت'
            sheet.write((i - 1), 2, request.name, topVertAlign)
            sheet.write((i - 1), 3, req_type, topVertAlign)
            if request.type_request == 'supervisor_request':
                sheet.write((i - 1), 4, request.employee_id.name, topVertAlign)
                sheet.write((i - 1), 5, request.identification_id, topVertAlign)
                sheet.write((i - 1),  6, request.employee_id.mobile_phone, topVertAlign)
            elif request.type_request == 'admin_request':
                sheet.write((i - 1), 4, request.mosque_admin_id.name, topVertAlign)
                sheet.write((i - 1), 5, request.admin_identification_id, topVertAlign)
                sheet.write((i - 1), 6, request.mosque_admin_id.mobile_phone, topVertAlign)
            sheet.write((i - 1), 7, request.date_request, topVertAlign)
            sheet.write((i - 1), 8, request.permision_end_date, topVertAlign)


        table = []
        values = self.get_report_values(docids,data)
        docs = values['docs']

        sheet = workbook.add_worksheet('تقرير التكاليف المقاربة للنهاية (3 أشهر وأقل)')
        head = [
            {'name': 'المركز',
             'larg': 20,
             'col': {}},
            {'name': 'المسجد',
             'larg': 45,
             'col': {}},
            {'name': 'اسم التكليف',
             'larg': 45,
             'col': {}},
            {'name': 'نوع التكليف',
             'larg': 35,
             'col': {}},
            {'name': 'اسم المشرف',
             'larg': 35,
             'col': {}},
            {'name': 'رقم الهوية',
             'larg': 35,
             'col': {}},
            {'name': 'رقم الجوال',
             'larg': 35,
             'col': {}},
            {'name': 'تاريخ البداية',
             'larg': 20,
             'col': {}},
            {'name': 'تاريخ النهاية',
             'larg': 20,
             'col': {}},]

        _header_sheet(sheet)

        row = 7
        i = 7
        start_row = row
        if docs:
            row += 1
            start_row = row
            for i, doc in enumerate(docs):
                i = row
                body_report(sheet)
                i += 1
                mosques = self.env['mk.mosque'].search(active_inactive_mosq_domain +[('id', 'in', doc['supervisor_requests_mosques']),
                                                                                     ('center_department_id', '=', doc['center'].id)])
                for mosque in mosques:
                    if mosque.categ_id.mosque_type == 'female':
                        ep_val = ''
                        if mosque.episode_value == 'mo':
                            ep_val = 'صباحية'
                        elif mosque.episode_value == 'ev':
                            ep_val = 'مسائية'
                        sheet.write(i - 1, 1, mosque.name + ' [' + ep_val + ']', topVertAlign)
                    else:
                        sheet.write(i - 1, 1, mosque.name, topVertAlign)
                    row = i
                    supervisor_requests = self.env['mosque.supervisor.request'].search([('id', 'in', doc['supervisor_requests_dep']),
                                                                                        ('mosque_id', '=', mosque.id)])
                    for request in supervisor_requests:
                        get_supervisor_requests(sheet)
                        i += 1
                row = i
            row = i
        row = i

        for j, h in enumerate(head):
            sheet.set_column(j, j, h['larg'])

        for h in head:
            col = {'header': h['name']}
            col.update(h['col'])
            table.append(col)

        sheet.add_table(start_row - 1, 0, row + 1, len(head) - 1, {'total_row': 10,
                                                                   'columns': table,
                                                                   'style': 'Table Style Light 9'})