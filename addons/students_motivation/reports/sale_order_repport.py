from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import _, api
from odoo import models

class SaleOrdersReportXlsx(models.AbstractModel):
    _inherit = 'report.report_xlsx.abstract'
    _name = 'report.students_motivation.report_sale_order'


    def generate_xlsx_report(self, workbook, data, order):
        num_format = _('_ * #,##0.00_) ;_ * - #,##0.00_) ;_ * "-"??_) ;_ @_ ')
        bold = workbook.add_format({'bold': True})
        bold.set_align('top')
        currency_format = workbook.add_format({'num_format': _(num_format)})
        currency_format.set_align('top')
        report_format = workbook.add_format({'font_size': 24})
        topVertAlign = workbook.add_format()
        topVertAlign.set_align('top')

        def _header_sheet(sheet):
            sheet.write(0, 3, _('قائمة طلبات التحفيز'), report_format)
            sheet.write(4, 0, _('تم اصدارها في       %s') % (datetime.now()).strftime("%Y-%m-%d"))
            sheet.right_to_left()

        def body_report(sheet):
            sheet.write(i, 0, line.name, bold)
            sheet.write(i, 1, line.order_date, bold)
            sheet.write(i, 3, line.student_id.display_name, bold)
            sheet.write(i, 4, line.mosque_id.name, bold)
            sheet.write(i, 5, line.total_prize_points, bold)
            if line.state == 'draft':
                sheet.write(i, 2, 'جديد', bold)
            elif line.state == 'mosque_approve':
                sheet.write(i, 2, 'تمت الموافقة عليه', bold)
            elif line.state == 'deliverd':
                sheet.write(i, 2, 'تم تسليمه', bold)
            elif line.state == 'refused':
                sheet.write(i, 2, 'مرفوض', bold)

        def product_lines(sheet):
            product_name = l.product_id.name
            product_qty = str(l.product_uom_qty)
            total_points = str(l.total_points)
            sheet.write(i - 1, 6, product_name, topVertAlign)
            sheet.write(i - 1, 7, product_qty, topVertAlign)
            sheet.write(i - 1, 8, total_points, topVertAlign)

        sheet = workbook.add_worksheet('Sale order list')
        _header_sheet(sheet)

        study_year_id = data['form']['study_year_id']

        study_class_id = data['form']['study_class_id']

        center_id = data['form']['center_id']

        gender_type = data['form']['gender_type']

        mosque_category_id = data['form']['mosque_category_id']

        mosque_id = data['form']['mosque_id']

        student_id = data['form']['student_id']

        table = []
        if student_id:
            order_ids = self.env['sale.order'].search( [('student_id', '=', student_id)])
        elif mosque_id:
            order_ids = self.env['sale.order'].search([('mosque_id', '=', mosque_id)])
        elif mosque_category_id:
            order_ids = self.env['sale.order'].search([('mosque_id.categ_id', '=', mosque_category_id)])
        elif gender_type:
            order_ids = self.env['sale.order'].search([('mosque_id.gender_mosque', '=', gender_type)])
        elif center_id:
            order_ids = self.env['sale.order'].search([('mosque_id.center_department_id', '=', center_id)])
        else:
            order_ids = self.env['sale.order'].search([])

        row = 7
        i=7
        start_row = row
        head = [
            {'name': 'مرجع الأمر',
             'larg': 20,
             'col': {}},
            {'name': 'التاريخ',
             'larg': 25,
             'col': {}},
            {'name': 'الحالة',
             'larg': 20,
             'col': {}},
            {'name': 'اسم الطالب',
             'larg': 35,
             'col': {}},
            {'name': 'المسجد',
             'larg': 45,
             'col': {}},
            {'name': 'اجمالي نقاط الجوائز',
             'larg': 30,
             'col': {}},
            {'name': 'الجائزة',
             'larg': 25,
             'col': {}},
            {'name': 'الكميات المطلوبة',
             'larg': 20,
             'col': {}},
            {'name': 'اجمالي النقاط',
             'larg': 20,
             'col': {}}, ]
        if order_ids:
            row += 1
            start_row = row
            for i, line in enumerate(order_ids):
                i = row
                body_report(sheet)

                for l in line.order_line:
                    body_report(sheet)
                    i += 1
                    product_lines(sheet)
                row = i

            row = i
        for j, h in enumerate(head):
            sheet.set_column(j, j, h['larg'])

        for h in head:
            col = {}
            col['header'] = h['name']
            col.update(h['col'])
            table.append(col)

        sheet.add_table(start_row - 1, 0, row + 1, len(head) - 1,{'total_row': 10,
                                                                  'columns': table,
                                                                  'style': 'Table Style Light 9'})
