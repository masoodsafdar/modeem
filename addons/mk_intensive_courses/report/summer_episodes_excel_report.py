from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import _, api
from odoo import models

class SummerEpisodessReportXlsx(models.AbstractModel):
    _inherit = 'report.report_xlsx.abstract'
    _name = 'report.mk_intensive_courses.report_summer_episodes'

    def get_report_values(self, data, docids):
        docs = []
        departments = []
        domain = [('state', '=', 'closed')]
        intensive_course_ids = self.env['mk.course.request'].search(domain + [('id', 'in', docids.ids)])
        first_gender = intensive_course_ids[0].gender_mosque
        course_ids = self.env['mk.course.request'].search(domain + [('id', 'in', intensive_course_ids.ids),
                                                                    ('id', '!=', intensive_course_ids[0].id),
                                                                    ('gender_mosque', '!=', first_gender)], limit=1)
        if not course_ids:
            if first_gender == 'female':
                gender = 'f'
            else:
                gender = 'm'
        else:
            gender = 'mf'
        for course in intensive_course_ids:
            department = course.department_id
            if department not in departments:
                departments.append(department)

        for department in departments:
            intensive_course_department_ids = self.env['mk.course.request'].search([('department_id', '=', department.id),
                                                                                    ('id', 'in', docids.ids)])
            docs.append({'department_id': department,
                         'intensive_course_department_ids': intensive_course_department_ids})
        return {'docs': docs,
                'gender': gender}

    def generate_xlsx_report(self, workbook,  data, docids):
        num_format = _('_ * #,##0.00_) ;_ * - #,##0.00_) ;_ * "-"??_) ;_ @_ ')
        bold = workbook.add_format({'bold': True})
        bold.set_align('center')
        currency_format = workbook.add_format({'num_format': _(num_format)})
        currency_format.set_align('top')
        report_format = workbook.add_format({'font_size': 18})
        topVertAlign = workbook.add_format()
        topVertAlign.set_align('top')
        empty_cell = workbook.add_format({'border': True, 'bg_color': '#70726E', 'font_color': '#70726E'})

        table = []

        values = self.get_report_values(data, docids)
        docs = values['docs']
        gender = values['gender']

        def _header_sheet(sheet):
            sheet.write(3, 3, _('إحصائية الدورات المكثفة '), report_format)
            sheet.write(4, 0, _('تم اصدارها في       %s') % (datetime.now()).strftime("%Y-%m-%d"))
            sheet.right_to_left()

        def body_report(sheet):
            sheet.write(i, 0, doc['department_id'].name, bold)
            sheet.write(i, 1, len(doc['intensive_course_department_ids']), bold)


        def intensive_course_dtails(sheet):
            course_name = course.course_name
            mosque_name = course.mosque_id.display_name
            nbr_episode = course.course_episode_nbr
            nbr_teacher = course.course_teachers_nbr
            nbr_student = course.course_students_nbr
            total_hours = course.close_total_hours
            gender_mosque = course.gender_mosque
            if gender_mosque == 'female':
                parts_nbr   = course.parts_female_total_nbr
            elif gender_mosque == 'male':
                parts_nbr   = course.parts_nbr
            students_finals_nbr        = course.students_finals_nbr
            students_parts_tests_nbr   = course.students_parts_tests_nbr
            students_final_tests_nbr   = course.students_final_tests_nbr
            course_administrators_nbr   = course.course_administrators_nbr
            parts_female_total_done_nbr   = course.parts_female_total_done_nbr

            sheet.write(i - 1, 2, course_name, topVertAlign)
            sheet.write(i - 1, 3, mosque_name, topVertAlign)
            sheet.write(i - 1, 4, nbr_episode, topVertAlign)
            if gender == 'f':
                sheet.write(i - 1, 5, nbr_teacher, topVertAlign)
                sheet.write(i - 1, 6, nbr_student, topVertAlign)
                sheet.write(i - 1, 7, total_hours, topVertAlign)
                sheet.write(i - 1, 8, parts_nbr, topVertAlign)
                sheet.write(i - 1, 9, students_parts_tests_nbr, topVertAlign)
                sheet.write(i - 1, 10, students_final_tests_nbr, topVertAlign)
                sheet.write(i - 1, 11, course_administrators_nbr, topVertAlign)
                sheet.write(i - 1, 12, parts_female_total_done_nbr, topVertAlign)
            if gender == 'm':
                sheet.write(i - 1, 5, nbr_student, topVertAlign)
                sheet.write(i - 1, 6, total_hours, topVertAlign)
                sheet.write(i - 1, 7, parts_nbr, topVertAlign)
                sheet.write(i - 1, 8, students_finals_nbr, topVertAlign)
                sheet.write(i - 1, 9, students_parts_tests_nbr, topVertAlign)
                sheet.write(i - 1, 10, students_final_tests_nbr, topVertAlign)

            if gender == 'mf':
                sheet.write(i - 1, 6, nbr_student, topVertAlign)
                sheet.write(i - 1, 7, total_hours, topVertAlign)
                sheet.write(i - 1, 8, parts_nbr,   topVertAlign)
                sheet.write(i - 1, 10, students_parts_tests_nbr,   topVertAlign)
                sheet.write(i - 1, 11, students_final_tests_nbr,   topVertAlign)
                if gender_mosque == 'female':
                    sheet.write(i - 1, 5, nbr_teacher, topVertAlign)
                    sheet.write(i - 1, 9, students_finals_nbr, empty_cell)
                    sheet.write(i - 1, 12, course_administrators_nbr,   topVertAlign)
                    sheet.write(i - 1, 13, parts_female_total_done_nbr,   topVertAlign)
                elif gender_mosque == 'male':
                    sheet.write(i - 1, 5, nbr_teacher, empty_cell)
                    sheet.write(i - 1, 9, students_finals_nbr, topVertAlign)
                    sheet.write(i - 1, 12, course_administrators_nbr, empty_cell)
                    sheet.write(i - 1, 13, parts_female_total_done_nbr, empty_cell)

        sheet = workbook.add_worksheet('إحصائية الدورات المكثفة ')
        _header_sheet(sheet)

        row = 7
        i=7
        start_row = row
        if gender == 'f':
            head = [
                {'name': 'المركز',
                 'larg': 18,
                 'col': {}},
                {'name': 'عدد الدورات',
                 'larg': 18,
                 'col': {}},
                {'name': 'اسم الدورة',
                 'larg': 30,
                 'col': {}},
                {'name': 'المسجد/المدرسة',
                 'larg': 30,
                 'col': {}},
                {'name': 'عدد الحلقات',
                 'larg': 18,
                 'col': {}},
                {'name': 'عدد المعلمين/المعلمات',
                 'larg': 20,
                 'col': {}},

                {'name': 'عدد طلاب/طالبات الدورة',
                 'larg': 20,
                 'col': {}},
                {'name': 'إجمالي ساعات الفترة',
                 'larg': 18,
                 'col': {}},
                {'name': 'عدد الأوجه المسمعة',
                 'larg': 18,
                 'col': {}},
                {'name': 'عدد الطلاب/الطالبات المشاركين في اختبارات الأجزاء',
                 'larg': 32,
                 'col': {}},
                {'name': 'عدد الطلاب/الطالبات المشاركين في اختبارات الخاتمين',
                 'larg': 32,
                 'col': {}},
                {'name': 'عدد الاداريين/الاداريات',
                 'larg': 28,
                 'col': {}},
                {'name': 'عدد الأجزاء المسمعة',
                 'larg': 20,
                 'col': {}},
            ]

        if gender == 'm':
            head = [
                {'name': 'المركز',
                 'larg': 18,
                 'col': {}},
                {'name': 'عدد الدورات',
                 'larg': 18,
                 'col': {}},
                {'name': 'اسم الدورة',
                 'larg': 30,
                 'col': {}},
                {'name': 'المسجد/المدرسة',
                 'larg': 30,
                 'col': {}},
                {'name': 'عدد الحلقات',
                 'larg': 18,
                 'col': {}},
                {'name': 'عدد طلاب/طالبات الدورة',
                 'larg': 20,
                 'col': {}},
                {'name': 'إجمالي ساعات الفترة',
                 'larg': 18,
                 'col': {}},
                {'name': 'عدد الأوجه المسمعة',
                 'larg': 18,
                 'col': {}},
                {'name': 'عدد الطلاب/الطالبات الخاتمين',
                 'larg': 22,
                 'col': {}},
                {'name': 'عدد الطلاب/الطالبات المشاركين في اختبارات الأجزاء',
                 'larg': 32,
                 'col': {}},
                {'name': 'عدد الطلاب/الطالبات المشاركين في اختبارات الخاتمين',
                 'larg': 32,
                 'col': {}},
            ]

        if gender == 'mf':
            head = [
                {'name': 'المركز',
                 'larg': 18,
                 'col': {}},
                {'name': 'عدد الدورات',
                 'larg': 18,
                 'col': {}},
                {'name': 'اسم الدورة',
                 'larg': 30,
                 'col': {}},
                {'name': 'المسجد/المدرسة',
                 'larg': 30,
                 'col': {}},
                {'name': 'عدد الحلقات',
                 'larg': 18,
                 'col': {}},
                {'name': 'عدد المعلمين/المعلمات',
                 'larg': 20,
                 'col': {}},

                {'name': 'عدد طلاب/طالبات الدورة',
                 'larg': 20,
                 'col': {}},
                {'name': 'إجمالي ساعات الفترة',
                 'larg': 18,
                 'col': {}},
                {'name': 'عدد الأوجه المسمعة',
                 'larg': 18,
                 'col': {}},
                {'name': 'عدد الطلاب/الطالبات الخاتمين',
                 'larg': 22,
                 'col': {}},
                {'name': 'عدد الطلاب/الطالبات المشاركين في اختبارات الأجزاء',
                 'larg': 32,
                 'col': {}},
                {'name': 'عدد الطلاب/الطالبات المشاركين في اختبارات الخاتمين',
                 'larg': 32,
                 'col': {}},
                {'name': 'عدد الاداريين/الاداريات',
                 'larg': 28,
                 'col': {}},
                {'name': 'عدد الأجزاء المسمعة',
                 'larg': 20,
                 'col': {}},
            ]

        if docs:
            row += 1
            start_row = row
            for i, doc in enumerate(docs):
                i = row
                body_report(sheet)
                i += 1
                for course in doc['intensive_course_department_ids']:
                    intensive_course_dtails(sheet)
                    i += 1
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
