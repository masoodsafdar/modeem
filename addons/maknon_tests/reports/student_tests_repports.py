from odoo import models, api, _
from datetime import datetime


class TestsReportXlsx(models.AbstractModel):
    _inherit = 'report.report_xlsx.abstract'
    _name = 'report.maknon_tests.test_excel_report_template'

    def get_report_values(self, data):

        academic_id = data['form']['episode_academic_id']
        academic_name = data['form']['episode_academic_name']
        exam_academic_id = data['form']['exam_academic_id']
        exam_academic_name = data['form']['exam_academic_name']

        domain_filter = data['form']['domain']
        teacher_id = data['form']['teacher_id']
        mosque_id = data['form']['mosque_id']
        mosque_category_id = data['form']['mosque_category_id']
        supervisor = data['form']['supervisor_id']
        center_id = data['form']['center_id']
        gender_type = data['form']['gender_type']

        study_class_id = data['form']['episode_study_class_id']
        study_class_name = data['form']['episode_study_class_name']
        exam_study_class_id = data['form']['exam_study_class_id']
        exam_study_class_name = data['form']['exam_study_class_name']

        type_test_id = data['form']['type_test_id']
        is_test_session = data['form']['is_test_session']
        type_test_name = data['form']['type_test_name']
        branch_id = data['form']['branch_id']
        branch_name = data['form']['branch_name']
        report_name = data['form']['report_name']

        student_ids = []

        if teacher_id:
            episode_ids = self.env['mk.episode'].search([('teacher_id', '=', teacher_id)])

            if episode_ids:
                link_ids = self.env['mk.link'].search([('episode_id', 'in', episode_ids.ids)])

                for link_id in link_ids:
                    student_ids += [link_id.student_id.id]

        else:
            if mosque_id:
                domain = [('mosq_id', 'in', [mosque_id])]
            else:
                mosque_domain = []
                if center_id:
                    mosque_domain.append(('center_department_id', '=', center_id))

                if mosque_category_id:
                    mosque_domain.append(('categ_id', '=', mosque_category_id))

                elif gender_type:
                    mosque_domain += [('categ_id.mosque_type', '=', gender_type)]

                if supervisor:
                    emp_supervisor = self.env['hr.employee'].search([('id', '=', supervisor)], limit=1)
                    mosque_domain += [('id', 'in', emp_supervisor.mosque_sup.ids)]

                mosque_ids = self.env['mk.mosque'].search(mosque_domain)
                domain = [('mosq_id', 'in', [mosque_id.id for mosque_id in mosque_ids])]
            student_ids = self.env['mk.student.register'].search(domain).ids

        student_ids = list(set(student_ids))

        docs = []

        domain = [('academic_id', '=', academic_id),
                  ('is_pass', '=', True),
                  ('state', '=', 'done'),
                  ('student_id', 'in', student_ids),
                  ('study_class_id', '=', study_class_id)]

        active_inactive_mosq_domain = ['|', ('active', '=', True), ('active', '=', False)]
        domain_filter += ['|', ('active', '=', True), ('active', '=', False)]
        domain_test = []
        if type_test_id:
            domain_test += [('test_name', '=', type_test_id)]

        if branch_id:
            domain_test += [('branch', '=', branch_id)]

        if exam_study_class_id:
            domain_test += [('study_class_id', '=', exam_study_class_id)]

        if center_id:
            domain_test += [('mosque_id.center_department_id', '=', center_id)]
        elif report_name == 'passed_student_tests_report':
            domain_test += [('is_pass', '=', True)]

        if data['form']['report_type'] != 'detailed':
            domain_success_students = domain + [('is_pass', '=', True)]
            success_students = len(self.env['student.test.session'].sudo().search(domain_success_students))

            domain_failed_students = domain + [('is_pass', '=', False)]
            failed_students = len(self.env['student.test.session'].sudo().search(domain_failed_students))

        mosque_sessions = []
        episode_sessions = []
        test_sessions_list = []
        dep_list = []

        if teacher_id:
            episodes = self.env['mk.episode'].search(domain_filter + [('teacher_id', '=', teacher_id)])
            link_ids = []
            if episodes:
                for episode in episodes:
                    for link in episode.link_ids:
                        link_ids += [link.id]

                test_sessions = self.env['student.test.session'].search(domain_test + [('student_id', 'in', link_ids),
                                                                                       ('state', '!=', 'cancel')])

                if not is_test_session or (is_test_session and test_sessions):
                    for test_session in test_sessions:
                        test_sessions_list += [test_session.id]
                        mosque_session_id = test_session.mosque_id.id
                        if mosque_session_id not in mosque_sessions:
                            mosque_sessions += [mosque_session_id]

                        episode_session_id = test_session.episode_id.id
                        if episode_session_id not in episode_sessions:
                            episode_sessions += [episode_session_id]

                    for mosque in mosque_sessions:
                        mosq = self.env['mk.mosque'].search([('id', '=', mosque)])
                        mosque_dep = mosq.center_department_id
                        if mosque_dep not in dep_list:
                            dep_list.append(mosque_dep)
                docs.append({'dep_sessions': dep_list,
                             'mosque_sessions': mosque_sessions,
                             'episode_sessions': episode_sessions,
                             'test_sessions': test_sessions_list})

        elif mosque_id:
            mosque = self.env['mk.mosque'].search([('id', '=', mosque_id)])
            department = mosque.center_department_id
            episodes = self.env['mk.episode'].search(domain_filter + [('mosque_id', '=', mosque_id)])
            link_ids = []
            for episode in episodes:
                for link in episode.link_ids:
                    link_ids += [link.id]

            test_sessions = self.env['student.test.session'].search(domain_test + [('mosque_id', '=', mosque_id),
                                                                                   ('state', '!=', 'cancel')])
            if not is_test_session or (is_test_session and test_sessions):
                for test_session in test_sessions:
                    test_sessions_list += [test_session.id]

                    episode_session_id = test_session.episode_id.id
                    if episode_session_id not in episode_sessions:
                        episode_sessions += [episode_session_id]

                docs.append({'department_id': department,
                             'mosque_id': mosque,
                             'episode_sessions': episode_sessions,
                             'test_sessions': test_sessions_list, })

        elif supervisor:
            supervisor_id = self.env['hr.employee'].search([('id', '=', supervisor)], limit=1)
            link_ids = []
            for mosque in supervisor_id.mosque_sup:
                mosque_id = mosque.id
                episodes = self.env['mk.episode'].search(domain_filter + [('mosque_id', '=', mosque_id)])
                for episode in episodes:
                    for link in episode.link_ids:
                        link_ids += [link.id]

            test_sessions = self.env['student.test.session'].search(domain_test + [('student_id', 'in', link_ids), ('state', '!=', 'cancel')])

            if not is_test_session or (is_test_session and test_sessions):
                for test_session in test_sessions:
                    test_sessions_list += [test_session.id]
                    mosque_session_id = test_session.mosque_id.id
                    if mosque_session_id not in mosque_sessions:
                        mosque_sessions += [mosque_session_id]

                    episode_session_id = test_session.episode_id.id
                    if episode_session_id not in episode_sessions:
                        episode_sessions += [episode_session_id]

                for mosque in mosque_sessions:
                    mosq = self.env['mk.mosque'].search([('id', '=', mosque)])
                    mosque_dep = mosq.center_department_id
                    if mosque_dep not in dep_list:
                        dep_list.append(mosque_dep)

            docs.append({'supervisor': supervisor_id.name,
                         'dep_sessions': dep_list,
                         'mosque_sessions': mosque_sessions,
                         'episode_sessions': episode_sessions,
                         'test_sessions': test_sessions_list})

        elif mosque_category_id:
            mosques = self.env['mk.mosque'].search(
                active_inactive_mosq_domain + [('categ_id', '=', mosque_category_id)])
            link_ids = []
            for mosque in mosques:
                mosque_id = mosque.id
                episodes = self.env['mk.episode'].search(domain_filter + [('mosque_id', '=', mosque_id)])
                for episode in episodes:
                    for link in episode.link_ids:
                        link_ids += [link.id]

            test_sessions = self.env['student.test.session'].search(
                domain_test + [('student_id', 'in', link_ids), ('state', '!=', 'cancel')])
            if not is_test_session or (is_test_session and test_sessions):
                for test_session in test_sessions:
                    test_sessions_list += [test_session.id]
                    mosque_session_id = test_session.mosque_id.id
                    if mosque_session_id not in mosque_sessions:
                        mosque_sessions += [mosque_session_id]

                    episode_session_id = test_session.episode_id.id
                    if episode_session_id not in episode_sessions:
                        episode_sessions += [episode_session_id]

                for mosque in mosque_sessions:
                    mosq = self.env['mk.mosque'].search([('id', '=', mosque)])
                    mosque_dep = mosq.center_department_id
                    if mosque_dep not in dep_list:
                        dep_list.append(mosque_dep)

            docs.append({'dep_sessions': dep_list,
                         'mosque_sessions': mosque_sessions,
                         'episode_sessions': episode_sessions,
                         'test_sessions': test_sessions_list})

        elif gender_type:
            mosques = self.env['mk.mosque'].search(active_inactive_mosq_domain + [('gender_mosque', '=', gender_type)])
            link_ids = []
            for mosque in mosques:
                mosque_id = mosque.id
                episodes = self.env['mk.episode'].search(domain_filter + [('mosque_id', '=', mosque_id)])
                for episode in episodes:
                    for link in episode.link_ids:
                        link_ids += [link.id]

            test_sessions = self.env['student.test.session'].search(domain_test + [('student_id', 'in', link_ids),
                                                                                   ('state', '!=', 'cancel')])
            if not is_test_session or (is_test_session and test_sessions):
                for test_session in test_sessions:
                    test_sessions_list += [test_session.id]
                    mosque_session_id = test_session.mosque_id.id
                    if mosque_session_id not in mosque_sessions:
                        mosque_sessions += [mosque_session_id]

                for mosque in mosque_sessions:
                    mosq = self.env['mk.mosque'].search([('id', '=', mosque)])
                    mosque_dep = mosq.center_department_id
                    if mosque_dep not in dep_list:
                        dep_list.append(mosque_dep)

                    episode_session_id = test_session.episode_id.id
                    if episode_session_id not in episode_sessions:
                        episode_sessions += [episode_session_id]

            docs.append({'dep_sessions': dep_list,
                         'mosque_sessions': mosque_sessions,
                         'episode_sessions': episode_sessions,
                         'test_sessions': test_sessions_list})

        elif center_id:
            mosques = self.env['mk.mosque'].search(active_inactive_mosq_domain + [('center_department_id', '=', center_id)])
            link_ids = []
            for mosque in mosques:
                mosque_id = mosque.id
                episodes = self.env['mk.episode'].search(domain_filter + [('mosque_id', '=', mosque_id)])
                for episode in episodes:
                    for link in episode.link_ids:
                        link_ids += [link.id]

            test_sessions = self.env['student.test.session'].search(domain_test + [('student_id', 'in', link_ids),
                                                                                   ('state', '!=', 'cancel')])
            if not is_test_session or (is_test_session and test_sessions):
                for test_session in test_sessions:
                    mosque_session_id = test_session.mosque_id.id
                    if mosque_session_id not in mosque_sessions:
                        mosque_sessions += [mosque_session_id]
                    episode_session_id = test_session.episode_id.id
                    if episode_session_id not in episode_sessions:
                        episode_sessions += [episode_session_id]

                docs.append({'center': mosque.center_department_id.name,
                             # 'mosques': mosque.name,
                             'mosque_sessions': mosque_sessions,
                             'episode_sessions': episode_sessions,
                             'test_sessions': test_sessions})

        elif study_class_id:
            departments = self.env['hr.department'].search([])
            for department in departments:
                department_id = department.id
                mosques = self.env['mk.mosque'].search(active_inactive_mosq_domain + [('center_department_id', '=', department_id)])
                episodes = self.env['mk.episode'].search(domain_filter + [('mosque_id', 'in', mosques.ids)])

                link_ids = []
                for episode in episodes:
                    for link in episode.link_ids:
                        link_ids += [link.id]

                test_sessions = self.env['student.test.session'].search(domain_test + [('student_id', 'in', link_ids),
                                                                                       ('state', '!=', 'cancel')])
                if not is_test_session or (is_test_session and test_sessions):
                    for test_session in test_sessions:
                        mosque_session_id = test_session.mosque_id.id
                        if mosque_session_id not in mosque_sessions:
                            mosque_sessions += [mosque_session_id]

                        episode_session_id = test_session.episode_id.id
                        if episode_session_id not in episode_sessions:
                            episode_sessions += [episode_session_id]

                    docs.append({'center':          department.name,
                                 'mosque_sessions': mosque_sessions,
                                 'episode_sessions': episode_sessions,
                                 'test_sessions':   test_sessions})
                mosque_sessions = []
                episode_sessions = []

        return {'doc_ids': data['ids'],
                'doc_model': data['model'],
                'docs': docs,
                'report_name': report_name,
                'type_filter': data['form']['type_filter'],
                'branch_id': data['form']['branch_id'],
                'branch_name': data['form']['branch_name'],
                'episode_academic_name': academic_name,
                'exam_academic_name': exam_academic_name,
                'episode_study_class_id': study_class_id,
                'episode_study_class_name': study_class_name,
                'exam_study_class_id': exam_study_class_id,
                'exam_study_class_name': exam_study_class_name,
                'center_name': data['form']['center_name'],
                'mosque_id_name': data['form']['mosque_id_name'],
                'mosque_id': data['form']['mosque_id']}

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
            if report_name == 'subscribed_student_tests_report':
                sheet.write(0, 3, _('تقرير المسجلين في الاختبارات'), report_format)
            elif report_name == 'passed_student_tests_report':
                sheet.write(0, 3, _('تقرير المجتازبن في الاختبارات'), report_format)
            elif report_name == 'center_test_report':
                sheet.write(0, 3, _('تقرير مراكز الاختبارات'), report_format)
            sheet.write(4, 1, _('تم اصدار التقرير في:  %s') % (datetime.now()).strftime("%Y-%m-%d"))
            sheet.right_to_left()

        def body_report(sheet):
            if type_filter == 'episode_study_class':
                sheet.write(row, 0, doc['center'], bold)
            elif type_filter == 'center':
                sheet.write(row, 0, center_name, bold)
            elif type_filter in ['gender_type', 'category', 'supervisor', 'teacher']:
                sheet.write(i, 0, dep.name, bold)
            elif type_filter == 'mosque':
                sheet.write(row, 0, docs[0]['department_id'].name, bold)

        def get_mosques(sheet):
            if type_filter == 'mosque':
                sheet.write(row, 1, mosque_id_name, topVertAlign)
            else:
                sheet.write(i - 1, 1, mosque.name, topVertAlign)

        def get_students(sheet):
            if report_name == 'subscribed_student_tests_report':
                sheet.write((i - 1), 3, test_session.student_id.student_id.display_name, topVertAlign)
                sheet.write((i - 1), 4, test_session.student_id.student_id.birthdate, topVertAlign)
                if test_session.student_id.student_id.no_identity:
                    sheet.write((i - 1), 5, test_session.student_id.student_id.passport_no, topVertAlign)
                else:
                    sheet.write((i - 1), 5, test_session.student_id.student_id.identity_no, topVertAlign)
                sheet.write((i - 1), 6, test_session.branch.display_name, topVertAlign)
                sheet.write((i - 1), 7, test_session.student_id.academic_id.name, topVertAlign)
                sheet.write((i - 1), 8, test_session.student_id.study_class_id.name, topVertAlign)

            elif report_name == 'passed_student_tests_report':
                sheet.write((i - 1), 2, test_session.student_id.student_id.display_name, topVertAlign)
                sheet.write((i - 1), 3, test_session.student_id.student_id.birthdate, topVertAlign)
                if test_session.student_id.student_id.no_identity:
                    sheet.write((i - 1), 4, test_session.student_id.student_id.passport_no, topVertAlign)
                else:
                    sheet.write((i - 1), 4, test_session.student_id.student_id.identity_no, topVertAlign)
                sheet.write((i - 1), 5, test_session.student_id.student_id.mobile, topVertAlign)
                sheet.write((i - 1), 6, test_session.branch.display_name, topVertAlign)
                sheet.write((i - 1), 7, test_session.student_id.academic_id.name, topVertAlign)
                sheet.write((i - 1), 8, test_session.student_id.study_class_id.name, topVertAlign)

                sheet.write((i - 1), 9, test_session.final_degree, topVertAlign)
                apprec = test_session.appreciation
                appreciation = False
                if apprec == 'excellent':
                    appreciation = 'ممتاز'
                elif apprec == 'v_good':
                    appreciation = 'جيد جدا'
                elif apprec == 'good':
                    appreciation = 'جيد'
                elif apprec == 'acceptable':
                    appreciation = 'مقبول'
                elif apprec == 'fail':
                    appreciation = 'راسب'
                sheet.write((i - 1), 10, appreciation, topVertAlign)

        table = []
        values = self.get_report_values(data)
        docs = values['docs']
        exam_academic_name = values['exam_academic_name']
        exam_study_class_name = values['exam_study_class_name']
        report_name = values['report_name']
        type_filter = values['type_filter']
        center_name = values['center_name']
        mosque_id_name = values['mosque_id_name']

        if report_name == 'subscribed_student_tests_report':
            sheet = workbook.add_worksheet('تقرير المسجلين في الاختبارات')
            head = [
                {'name': 'المركز',
                 'larg': 20,
                 'col': {}},
                {'name': 'المسجد',
                 'larg': 35,
                 'col': {}},
                {'name': 'عدد الطلاب',
                 'larg': 15,
                 'col': {}},
                {'name': 'اسم الطالب',
                 'larg': 35,
                 'col': {}},
                {'name': 'تاريخ الميلاد',
                 'larg': 20,
                 'col': {}},
                {'name': 'الهوية',
                 'larg': 20,
                 'col': {}},
                {'name': 'الفرع',
                 'larg': 40,
                 'col': {}},
                {'name': 'العام الدراسي',
                 'larg': 20,
                 'col': {}},
                {'name': 'الفصل الدراسي',
                 'larg': 40,
                 'col': {}},
                {'name': 'العدد',
                 'larg': 10,
                 'col': {}}, ]
        elif report_name == 'passed_student_tests_report':
            sheet = workbook.add_worksheet('تقرير المجتازبن في الاختبارات')
            head = [
                {'name': 'المركز',
                 'larg': 20,
                 'col': {}},
                {'name': 'المسجد',
                 'larg': 35,
                 'col': {}},
                {'name': 'اسم الطالب',
                 'larg': 35,
                 'col': {}},
                {'name': 'تاريخ الميلاد',
                 'larg': 20,
                 'col': {}},
                {'name': 'الهوية',
                 'larg': 20,
                 'col': {}},
                {'name': 'رقم الجوال',
                 'larg': 35,
                 'col': {}},
                {'name': 'الفرع',
                 'larg': 40,
                 'col': {}},
                {'name': 'العام الدراسي',
                 'larg': 20,
                 'col': {}},
                {'name': 'الفصل الدراسي',
                 'larg': 40,
                 'col': {}},
                {'name': 'الدرجة',
                 'larg': 40,
                 'col': {}},
                {'name': 'التقدير',
                 'larg': 40,
                 'col': {}},
                {'name': 'المكافئات',
                 'larg': 10,
                 'col': {}}, ]
        elif report_name == 'center_test_report':
            sheet = workbook.add_worksheet('تقرير مراكز الاختبارات ')
            head = [
                {'name': 'المركز',
                 'larg': 20,
                 'col': {}},
                {'name': 'المسجد',
                 'larg': 40,
                 'col': {}},
                {'name': 'الحلقة/المعلم',
                 'larg': 50,
                 'col': {}},
                {'name': 'عدد الطلاب',
                 'larg': 20,
                 'col': {}},
                {'name': 'الفرع',
                 'larg': 40,
                 'col': {}},
                {'name': 'عدد المتقدمين',
                 'larg': 20,
                 'col': {}},
                {'name': 'عدد المختبرين',
                 'larg': 20,
                 'col': {}},
                {'name': 'نوع الاختبار',
                 'larg': 40,
                 'col': {}},
                {'name': 'عدد اللجان',
                 'larg': 20,
                 'col': {}}]
            sheet.write(2, 1, _('العام الدراسي: %s') % exam_academic_name)
            sheet.write(3, 1, _('الفصل الدراسي: %s') % exam_study_class_name)
        _header_sheet(sheet)

        row = 7
        i = 7
        start_row = row

        if docs:
            row += 1
            start_row = row
            if type_filter == 'episode_study_class':
                for i, doc in enumerate(docs):
                    i = row
                    body_report(sheet)
                    i += 1
                    for mosq_session in doc['mosque_sessions']:
                        mosque = self.env['mk.mosque'].search([('id', '=', mosq_session)])

                        if report_name == 'center_test_report':
                            get_mosques(sheet)
                            row = i
                            episodes = self.env['mk.episode'].search([('id', '=', doc['episode_sessions']),
                                                                      ('mosque_id', '=', mosque.id)])

                            for episode in episodes:
                                sheet.write(i - 1, 2, episode.name + '/' + episode.teacher_id.name, topVertAlign)
                                sheet.write(i - 1, 3, len(episode.link_ids), topVertAlign)
                                row = i

                                branches = self.env['mk.branches.master'].search([])
                                for branch in branches:
                                    test_sessions = self.env['student.test.session'].search([('id', 'in', doc['test_sessions'].ids),
                                                                                             ('episode_id', '=', episode.id),
                                                                                             ('branch', '=', branch.id),])
                                    if test_sessions:
                                        sheet.write(i - 1, 4, branch.display_name, topVertAlign)
                                        sheet.write(i - 1, 5, len(test_sessions), topVertAlign)
                                        sheet.write(i - 1, 6, len(test_sessions.filtered(lambda s: s.state == 'done')), topVertAlign)
                                        sheet.write(i - 1, 7,branch.test_name.name , topVertAlign)
                                        i += 1
                                row = i
                            row = i

                        else:
                            test_sessions = self.env['student.test.session'].search([('id', 'in', doc['test_sessions'].ids),
                                                                                     ('mosque_id', '=', mosque.id)])
                            if test_sessions:
                                get_mosques(sheet)
                                row = i
                            if report_name == 'subscribed_student_tests_report':
                                sheet.write(i - 1, 2, len(test_sessions), bold)
                            for test_session in test_sessions:
                                get_students(sheet)
                                i += 1
                            row = i
                    row = i
                row = i

            elif type_filter == 'center':
                body_report(sheet)
                for i, doc in enumerate(docs):
                    i = row
                    i += 1
                    for mosq_session in doc['mosque_sessions']:
                        mosque = self.env['mk.mosque'].search([('id', '=', mosq_session)])

                        if report_name == 'center_test_report':
                            get_mosques(sheet)
                            row = i
                            episodes = self.env['mk.episode'].search([('id', '=', doc['episode_sessions']),
                                                                      ('mosque_id', '=', mosque.id)])
                            for episode in episodes:
                                sheet.write(i - 1, 2, episode.name + '/' + episode.teacher_id.name, topVertAlign)
                                sheet.write(i - 1, 3, len(episode.link_ids), topVertAlign)
                                row = i

                                branches = self.env['mk.branches.master'].search([])
                                for branch in branches:
                                    test_sessions = self.env['student.test.session'].search([('id', 'in', doc['test_sessions'].ids),
                                                                                             ('episode_id', '=', episode.id),
                                                                                             ('branch', '=', branch.id),])
                                    if test_sessions:
                                        sheet.write(i - 1, 4, branch.display_name, topVertAlign)
                                        sheet.write(i - 1, 5, len(test_sessions), topVertAlign)
                                        sheet.write(i - 1, 6, len(test_sessions.filtered(lambda s: s.state == 'done')), topVertAlign)
                                        sheet.write(i - 1, 7, branch.test_name.name, topVertAlign)
                                        i += 1
                                row = i
                            row = i

                        else:
                            test_sessions = self.env['student.test.session'].search([('id', 'in', doc['test_sessions'].ids),
                                                                                     ('mosque_id', '=', mosque.id)])
                            if test_sessions:
                                get_mosques(sheet)
                                row = i
                                if report_name == 'subscribed_student_tests_report':
                                    sheet.write(i - 1, 2, len(test_sessions), bold)
                                for test_session in test_sessions:
                                    get_students(sheet)
                                    i += 1
                                row = i
                    row = i
                row = i

            elif type_filter in ['gender_type', 'category', 'supervisor', 'teacher']:
                for i, doc in enumerate(docs):
                    i = row
                    for dep in doc['dep_sessions']:
                        body_report(sheet)
                        i += 1
                        mosques = self.env['mk.mosque'].search([('id', 'in', doc['mosque_sessions']),
                                                                ('center_department_id', '=', dep.id)])
                        for mosque in mosques:
                            get_mosques(sheet)
                            row = i

                            if report_name == 'center_test_report':
                                get_mosques(sheet)
                                row = i
                                episodes = self.env['mk.episode'].search([('id', '=', doc['episode_sessions']),
                                                                          ('mosque_id', '=', mosque.id)])
                                for episode in episodes:
                                    sheet.write(i - 1, 2, episode.name + '/' + episode.teacher_id.name, topVertAlign)
                                    sheet.write(i - 1, 3, len(episode.link_ids), topVertAlign)
                                    row = i

                                    branches = self.env['mk.branches.master'].search([])
                                    for branch in branches:
                                        test_sessions = self.env['student.test.session'].search(
                                            [('id', 'in', doc['test_sessions'].ids),
                                             ('episode_id', '=', episode.id),
                                             ('branch', '=', branch.id), ])
                                        if test_sessions:
                                            sheet.write(i - 1, 4, branch.display_name, topVertAlign)
                                            sheet.write(i - 1, 5, len(test_sessions), topVertAlign)
                                            sheet.write(i - 1, 6, len(test_sessions.filtered(lambda s: s.state == 'done')), topVertAlign)
                                            sheet.write(i - 1, 9, branch.test_name.name, topVertAlign)
                                            i += 1
                                    row = i
                                row = i

                            else:
                                test_sessions = self.env['student.test.session'].search([('id', 'in', doc['test_sessions']),
                                                                                         ('mosque_id', '=', mosque.id)])
                                if report_name == 'subscribed_student_tests_report':
                                    sheet.write(i - 1, 2, len(test_sessions), bold)
                                for test_session in test_sessions:
                                    get_students(sheet)
                                    i += 1
                                row = i
                        row = i
                    row = i
                row = i

            elif type_filter == 'mosque':
                body_report(sheet)
                get_mosques(sheet)
                for i, doc in enumerate(docs):
                    i = row
                    i += 1
                    if report_name == 'center_test_report':
                        get_mosques(sheet)
                        row = i
                        episodes = self.env['mk.episode'].search([('id', '=', doc['episode_sessions']),
                                                                  ('mosque_id', '=', doc['mosque_id'].id)])
                        for episode in episodes:
                            sheet.write(i - 1, 2, episode.name + '/' + episode.teacher_id.name, topVertAlign)
                            sheet.write(i - 1, 3, len(episode.link_ids), topVertAlign)
                            row = i

                            branches = self.env['mk.branches.master'].search([])
                            for branch in branches:
                                test_sessions = self.env['student.test.session'].search([('id', 'in', doc['test_sessions'].ids),
                                                                                         ('episode_id', '=', episode.id),
                                                                                         ('branch', '=', branch.id), ])
                                if test_sessions:
                                    sheet.write(i - 1, 4, branch.display_name, topVertAlign)
                                    sheet.write(i - 1, 5, len(test_sessions), topVertAlign)
                                    sheet.write(i - 1, 6, len(test_sessions.filtered(lambda s: s.state == 'done')), topVertAlign)
                                    sheet.write(i - 1, 9, branch.test_name.name, topVertAlign)
                                    i += 1
                            row = i
                        row = i
                    else:
                        if report_name == 'subscribed_student_tests_report':
                            sheet.write(i - 1, 2, len(docs[0]['test_sessions']), bold)
                        for test_session in docs[0]['test_sessions']:
                            test_session = self.env['student.test.session'].search([('id', '=', test_session)])
                            get_students(sheet)
                            i += 1
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
        workbook.close()