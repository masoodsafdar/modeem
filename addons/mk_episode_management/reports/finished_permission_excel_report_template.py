from odoo import models, api, _
from datetime import datetime, date


class FinishedPermissionReportXlsx(models.AbstractModel):
    _inherit = 'report.report_xlsx.abstract'
    _name = 'report.mk_episode_management.finished_permission_excel_report'

    def get_report_values(self, docids, data):
        docs = []
        permissions_dep = []
        permission_mosques = []
        departments = self.env['hr.department'].search([])
        for department in departments:
            permissions = self.env['mosque.permision'].search([('id', 'in', docids.ids),
                                                               ('center_id', '=', department.id),
                                                               ('is_valid', '=', True),
                                                               ('permision_end_date','!=', None)], order="permision_end_date desc")
            if permissions:
                for permission in permissions:
                    if permission.masjed_id.id not in permission_mosques:
                        permission_mosques.append(permission.masjed_id.id)
                    permissions_dep.append(permission.id)
                docs.append({'center': department,
                             'permission_mosques': permission_mosques,
                             'permissions_dep': permissions_dep})
            permissions_dep = []
            permission_mosques = []
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'mosque.permision',
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
            sheet.write(0, 3, _('تقرير التصاريح المنتهية '), report_format)
            sheet.write(4, 0, _('تم اصدارها في       %s') % (datetime.now()).strftime("%Y-%m-%d"))
            sheet.right_to_left()

        def body_report(sheet):
            sheet.write(row, 0, doc['center'].name, bold)

        def get_permissions(sheet):
            permision_type = permission.permision_type
            perm_type = False
            if permision_type == 'pe':
                perm_type = 'دائم'
            elif permision_type == 'te':
                perm_type = 'مؤقت'
            sheet.write((i - 1), 2, permission.name, topVertAlign)
            sheet.write((i - 1), 3, perm_type, topVertAlign)
            sheet.write((i - 1), 4, permission.permision_date, topVertAlign)
            sheet.write((i - 1), 5, permission.permision_end_date, topVertAlign)


        table = []
        values = self.get_report_values(docids,data)
        docs = values['docs']

        sheet = workbook.add_worksheet('تقرير التصاريح المنتهية ')
        head = [
            {'name': 'المركز',
             'larg': 20,
             'col': {}},
            {'name': 'المسجد',
             'larg': 35,
             'col': {}},
            {'name': 'اسم التصريح',
             'larg': 35,
             'col': {}},
            {'name': 'نوع التصريح',
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
                mosques = self.env['mk.mosque'].search(active_inactive_mosq_domain +[('id', 'in', doc['permission_mosques']),
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
                    permissions = self.env['mosque.permision'].search([('id', 'in', doc['permissions_dep']),
                                                                       ('masjed_id', '=', mosque.id)])
                    for permission in permissions:
                        get_permissions(sheet)
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