# -*- coding: utf-8 -*-
from odoo import models, api, _


class report_tests_template(models.AbstractModel):
    _name = 'report.maknon_tests.report_tests_template'


    # fct to report values
    def report_values_count(self, test_sessions):
        mosque_sessions =[]
        episode_sessions = []
        nbr_test_absent = 0
        nbr_test_done = 0
        nbr_test_success = 0
        nbr_test_fail = 0
        for test_session in test_sessions:
            mosque_session_id = test_session.mosque_id.id
            if mosque_session_id not in mosque_sessions:
                mosque_sessions += [mosque_session_id]

            episode_session_id = test_session.episode_id.id
            if episode_session_id not in episode_sessions:
                episode_sessions += [episode_session_id]

            state_test_session = test_session.state
            if state_test_session == 'absent':
                nbr_test_absent += 1

            elif state_test_session == 'done':
                nbr_test_done += 1
                if test_session.is_pass:
                    nbr_test_success += 1
                else:
                    nbr_test_fail += 1

        return mosque_sessions, episode_sessions, nbr_test_absent, nbr_test_done, nbr_test_success, nbr_test_fail

    # fct to calculate the test,subscribed and total percentage success
    def percentage_count(self, nbr_test_done, nbr_test_success, nbr_student_session, nbr_student):
        if nbr_test_done != 0:
            percentage_test_success = round((nbr_test_success * 100 / float(nbr_test_done)), 2)
        else:
            percentage_test_success = 0

        if nbr_student_session != 0:
            subsc_percentage_success = round((nbr_test_success * 100 / float(nbr_student_session)), 2)
        else:
            subsc_percentage_success = 0

        if nbr_student != 0:
            percentage_success_total_student = round((nbr_test_success * 100 / float(nbr_student)), 2)
        else:
            percentage_success_total_student = 0

        return percentage_test_success, subsc_percentage_success, percentage_success_total_student

    @api.model
    def get_report_values(self, docids, data):

        academic_id         = data['form']['episode_academic_id']
        academic_name       = data['form']['episode_academic_name']
        exam_academic_id    = data['form']['exam_academic_id']
        exam_academic_name = data['form']['exam_academic_name']

        domain_filter       = data['form']['domain']
        teacher_id          = data['form']['teacher_id']
        mosque_id           = data['form']['mosque_id']
        mosque_category_id  = data['form']['mosque_category_id']
        supervisor          = data['form']['supervisor_id']
        center_id           = data['form']['center_id']
        gender_type         = data['form']['gender_type']

        study_class_id      = data['form']['episode_study_class_id']
        study_class_name    = data['form']['episode_study_class_name']
        exam_study_class_id = data['form']['exam_study_class_id']
        exam_study_class_name = data['form']['exam_study_class_name']

        type_test_id        = data['form']['type_test_id']
        is_test_session     = data['form']['is_test_session']
        type_test_name      = data['form']['type_test_name']
        branch_id           = data['form']['branch_id']
        branch_name         = data['form']['branch_name']

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
                    emp_supervisor = self.env['hr.employee'].search([('id','=',supervisor)], limit=1)
                    mosque_domain += [('id', 'in', emp_supervisor.mosque_sup.ids)]

                mosque_ids = self.env['mk.mosque'].search(mosque_domain)
                domain = [('mosq_id', 'in', [mosque_id.id for mosque_id in mosque_ids])]
            student_ids = self.env['mk.student.register'].search(domain).ids

        student_ids = list(set(student_ids))

        docs = []
        success_students = 0
        failed_students = 0

        nbr_episodes = 0
        nbr_mosques = 0
        nbr_departments = 0

        domain = [('academic_id', '=', academic_id),
                  ('is_pass', '=', True),
                  ('state', '=', 'done'),
                  ('student_id', 'in', student_ids),
                  ('study_class_id', '=', study_class_id)]

        # domain_test = [('episode_study_class_id', '=', episode_study_class_id)]
        active_inactive_mosq_domain = ['|', ('active', '=', True), ('active', '=', False)]
        domain_test = []
        if type_test_id:
            domain_test += [('test_name', '=', type_test_id)]

        if branch_id:
            domain_test += [('branch', '=', branch_id)]

        if exam_study_class_id:
            domain_test += [('study_class_id', '=', exam_study_class_id)]

        if center_id:
            domain_test += [('mosque_id.center_department_id', '=', center_id)]


        if data['form']['report_type'] != 'detailed':

            domain_success_students = domain + [('is_pass', '=', True)]
            success_students = len(self.env['student.test.session'].sudo().search(domain_success_students))

            domain_failed_students = domain + [('is_pass', '=', False)]
            failed_students = len(self.env['student.test.session'].sudo().search(domain_failed_students))

        # reports total with filter
        nbr_mosque_session = 0
        nbr_episode_session = 0
        nbr_student_session = 0

        nbr_test_absent = 0
        nbr_test_done = 0
        nbr_test_success = 0
        nbr_test_fail = 0

        percentage_success_total_student =0
        subsc_percentage_success =0
        percentage_test_success =0

        mosque_sessions = []
        episode_sessions = []
        student_sessions = []

        if teacher_id:
            episodes = self.env['mk.episode'].search(domain_filter + [('teacher_id', '=', teacher_id)])
            nbr_episodes = len(episodes)
            mosque_ids = []
            if episodes:
                for episode in episodes:
                    link_ids = []
                    if episode.mosque_id.id not in mosque_ids:
                        mosque_ids += [episode.mosque_id.id]
                    for link in episode.link_ids:
                        if link.state in ['accept', 'done']:
                            link_ids += [link.id]
                    nbr_student = len(link_ids)
                    nbr_mosques = len(mosque_ids)

                    test_sessions = self.env['student.test.session'].search(domain_test + [('student_id', 'in', link_ids),
                                                                                           ('state', '!=','cancel')])
                    mosque_sessions, episode_sessions, nbr_test_absent, \
                    nbr_test_done, nbr_test_success, nbr_test_fail = self.report_values_count(test_sessions)

                    nbr_mosque_session = len(mosque_sessions)
                    nbr_episode_session = len(episode_sessions)
                    nbr_student_session = len(test_sessions)

                    percentage_test_success, subsc_percentage_success, percentage_success_total_student = self.percentage_count(nbr_test_done,
                                                                                                                                nbr_test_success,
                                                                                                                                nbr_student_session,
                                                                                                                                nbr_student)
                if not is_test_session or (is_test_session and test_sessions):
                    docs.append({'teacher':                      episode.teacher_id.name,
                                 'nbr_mosques':                      nbr_mosques,
                                 'mosques':                          episode.mosque_id.name,
                                 'nbr_mosque_session':               nbr_mosque_session,
                                 'nbr_episode':                      nbr_episodes,
                                 'nbr_episode_session':              nbr_episode_session,
                                 'nbr_student':                      nbr_student,
                                 'nbr_student_session':              nbr_student_session,
                                 'nbr_test_done':                    nbr_test_done,
                                 'nbr_test_success':                 nbr_test_success,
                                 'nbr_test_fail':                    nbr_test_fail,
                                 'nbr_test_absent':                  nbr_test_absent,
                                 'percentage_success_total_student': percentage_success_total_student,
                                 'subsc_percentage_success':         subsc_percentage_success,
                                 'percentage_test_success':          percentage_test_success,
                                 })

        elif mosque_id:
            episodes = self.env['mk.episode'].search(domain_filter + [('mosque_id', '=', mosque_id)])
            nbr_episodes = len(episodes)
            for episode in episodes:
                link_ids = []
                for link in episode.link_ids:
                    if link.state in ['accept', 'done']:
                        link_ids += [link.id]
                nbr_student = len(link_ids)

                test_sessions = self.env['student.test.session'].search(domain_test + [('student_id', 'in', link_ids),
                                                                                       ('state', '!=','cancel')])
                if not is_test_session or (is_test_session and test_sessions):
                    mosque_sessions, episode_sessions, nbr_test_absent, \
                    nbr_test_done, nbr_test_success, nbr_test_fail = self.report_values_count(test_sessions)

                    nbr_episode_session = len(episode_sessions)
                    nbr_student_session = len(test_sessions)

                    percentage_test_success, subsc_percentage_success, percentage_success_total_student = self.percentage_count(nbr_test_done,
                                                                                                                                nbr_test_success,
                                                                                                                                nbr_student_session,
                                                                                                                                nbr_student)

                    docs.append({'mosques':                          episode.mosque_id.name,
                                 'episode':                          episode.name + ' / ' + episode.teacher_id.name,
                                 'nbr_student':                      nbr_student,
                                 'nbr_episode' :                     nbr_episodes,
                                 'nbr_episode_session':              nbr_episode_session,
                                 'nbr_student_session':              nbr_student_session,
                                 'nbr_test_done':                    nbr_test_done,
                                 'nbr_test_success':                 nbr_test_success,
                                 'nbr_test_fail':                    nbr_test_fail,
                                 'nbr_test_absent':                  nbr_test_absent,
                                 'percentage_success_total_student': percentage_success_total_student,
                                 'subsc_percentage_success':         subsc_percentage_success,
                                 'percentage_test_success':          percentage_test_success,
                                 })

        elif supervisor:
            supervisor_id = self.env['hr.employee'].search([('id', '=', supervisor)], limit=1)
            nbr_mosques = len(supervisor_id.mosque_sup)
            for mosque in supervisor_id.mosque_sup:
                mosque_id = mosque.id

                episodes = self.env['mk.episode'].search(domain_filter + [('mosque_id', '=', mosque_id)])
                nbr_episodes = len(episodes)

                link_ids = []
                for episode in episodes:
                    for link in episode.link_ids:
                        if link.state in ['accept','done']:
                         link_ids += [link.id]
                nbr_student = len(link_ids)

                test_sessions = self.env['student.test.session'].search(domain_test + [('student_id', 'in', link_ids),('state', '!=','cancel')])
                if not is_test_session or (is_test_session and test_sessions):

                    mosque_sessions, episode_sessions, nbr_test_absent, \
                    nbr_test_done, nbr_test_success, nbr_test_fail = self.report_values_count(test_sessions)

                    nbr_episode_session = len(episode_sessions)
                    nbr_student_session = len(test_sessions)

                    percentage_test_success, subsc_percentage_success, percentage_success_total_student = self.percentage_count(nbr_test_done,
                                                                                                                                nbr_test_success,
                                                                                                                                nbr_student_session,
                                                                                                                                nbr_student)

                    docs.append({'supervisor':                       supervisor_id.name,
                                 'mosques':                          mosque.name,
                                 'nbr_episode':                      nbr_episodes,
                                 'nbr_episode_session':              nbr_episode_session,
                                 'nbr_student':                      nbr_student,
                                 'nbr_mosques' :                     nbr_mosques,
                                 'nbr_student_session':              nbr_student_session,
                                 'nbr_test_done':                    nbr_test_done,
                                 'nbr_test_success':                 nbr_test_success,
                                 'nbr_test_fail':                    nbr_test_fail,
                                 'nbr_test_absent':                  nbr_test_absent,
                                 'percentage_success_total_student': percentage_success_total_student,
                                 'subsc_percentage_success':         subsc_percentage_success,
                                 'percentage_test_success':          percentage_test_success,
                                 })

        elif mosque_category_id:
            mosques = self.env['mk.mosque'].search(active_inactive_mosq_domain + [('categ_id', '=', mosque_category_id)])
            nbr_mosques = len(mosques)
            for mosque in mosques:
                mosque_id = mosque.id

                episodes = self.env['mk.episode'].search(domain_filter + [('mosque_id', '=', mosque_id)])
                nbr_episodes = len(episodes)

                link_ids = []
                for episode in episodes:
                    for link in episode.link_ids:
                        if link.state in ['accept','done']:
                            link_ids += [link.id]
                nbr_student = len(link_ids)

                test_sessions = self.env['student.test.session'].search(domain_test + [('student_id', 'in', link_ids),('state', '!=','cancel')])
                if not is_test_session or (is_test_session and test_sessions):
                    mosque_sessions, episode_sessions, nbr_test_absent, \
                    nbr_test_done, nbr_test_success, nbr_test_fail = self.report_values_count(test_sessions)

                    nbr_episode_session = len(episode_sessions)
                    nbr_student_session = len(test_sessions)

                    percentage_test_success, subsc_percentage_success, percentage_success_total_student = self.percentage_count(nbr_test_done,
                                                                                                                                nbr_test_success,
                                                                                                                                nbr_student_session,
                                                                                                                                nbr_student)

                    docs.append({'categ_id':                         mosque.categ_id.name,
                                 'mosques':                          mosque.name,
                                 'nbr_episode':                      nbr_episodes,
                                 'nbr_episode_session':              nbr_episode_session,
                                 'nbr_student':                      nbr_student,
                                 'nbr_mosques':                      nbr_mosques,
                                 'nbr_student_session':              nbr_student_session,
                                 'nbr_test_done':                    nbr_test_done,
                                 'nbr_test_success':                 nbr_test_success,
                                 'nbr_test_fail':                    nbr_test_fail,
                                 'nbr_test_absent':                  nbr_test_absent,
                                 'percentage_success_total_student': percentage_success_total_student,
                                 'subsc_percentage_success':         subsc_percentage_success,
                                 'percentage_test_success':          percentage_test_success,
                                 })

        elif gender_type:
            mosques = self.env['mk.mosque'].search(active_inactive_mosq_domain + [('gender_mosque', '=', gender_type)])
            nbr_mosques = len(mosques)
            for mosque in mosques:
                mosque_id = mosque.id

                episodes = self.env['mk.episode'].search(domain_filter + [('mosque_id', '=', mosque_id)])
                nbr_episodes = len(episodes)
                link_ids = []
                for episode in episodes:
                    for link in episode.link_ids:
                        if link.state in ['accept','done']:
                            link_ids += [link.id]
                nbr_student = len(link_ids)

                test_sessions = self.env['student.test.session'].search(domain_test + [('student_id', 'in', link_ids),
                                                                                       ('state', '!=','cancel')])
                if not is_test_session or (is_test_session and test_sessions):

                    mosque_sessions, episode_sessions, nbr_test_absent, \
                    nbr_test_done, nbr_test_success, nbr_test_fail = self.report_values_count(test_sessions)

                    nbr_episode_session = len(episode_sessions)
                    nbr_student_session = len(test_sessions)

                    percentage_test_success, subsc_percentage_success, percentage_success_total_student = self.percentage_count(
                                                                                                                                nbr_test_done,
                                                                                                                                nbr_test_success,
                                                                                                                                nbr_student_session,
                                                                                                                                nbr_student)
                    docs.append({'categ_id':                         mosque.categ_id.name,
                                 'mosques':                          mosque.name,
                                 'nbr_episode':                      nbr_episodes,
                                 'nbr_episode_session':              nbr_episode_session,
                                 'nbr_student':                      nbr_student,
                                 'nbr_mosques':                      nbr_mosques,
                                 'nbr_student_session':              nbr_student_session,
                                 'nbr_test_done':                    nbr_test_done,
                                 'nbr_test_success':                 nbr_test_success,
                                 'nbr_test_fail':                    nbr_test_fail,
                                 'nbr_test_absent':                  nbr_test_absent,
                                 'percentage_success_total_student': percentage_success_total_student,
                                 'subsc_percentage_success':         subsc_percentage_success,
                                 'percentage_test_success':          percentage_test_success,
                                 })

        elif center_id:
            mosques = self.env['mk.mosque'].search(active_inactive_mosq_domain + [('center_department_id', '=', center_id)])
            nbr_mosques = len(mosques)
            for mosque in mosques:
                mosque_id = mosque.id
                episodes = self.env['mk.episode'].search(domain_filter + [('mosque_id', '=', mosque_id)])
                nbr_episodes = len(episodes)
                link_ids = []
                for episode in episodes:
                    for link in episode.link_ids:
                        if link.state in ['accept','done']:
                            link_ids += [link.id]
                nbr_student = len(link_ids)

                test_sessions = self.env['student.test.session'].search(domain_test + [('student_id', 'in', link_ids),('state', '!=','cancel')])
                if not is_test_session or (is_test_session and test_sessions):

                    mosque_sessions, episode_sessions, nbr_test_absent, \
                    nbr_test_done, nbr_test_success, nbr_test_fail = self.report_values_count(test_sessions)

                    nbr_episode_session = len(episode_sessions)
                    nbr_student_session = len(test_sessions)

                    percentage_test_success, subsc_percentage_success, percentage_success_total_student = self.percentage_count(
                                                                                                                                nbr_test_done,
                                                                                                                                nbr_test_success,
                                                                                                                                nbr_student_session,
                                                                                                                                nbr_student)
                    docs.append({'center':                           mosque.center_department_id.name,
                                 'mosques':                          mosque.name,
                                 'nbr_episode':                      nbr_episodes,
                                 'nbr_mosques' :                     nbr_mosques,
                                 'nbr_episode_session':              nbr_episode_session,
                                 'nbr_student':                      nbr_student,
                                 'nbr_student_session':              nbr_student_session,
                                 'nbr_test_done':                    nbr_test_done,
                                 'nbr_test_success':                 nbr_test_success,
                                 'nbr_test_fail':                    nbr_test_fail,
                                 'nbr_test_absent':                  nbr_test_absent,
                                 'percentage_success_total_student': percentage_success_total_student,
                                 'subsc_percentage_success':         subsc_percentage_success,
                                 'percentage_test_success':          percentage_test_success,
                                 })

        elif study_class_id:
            departments = self.env['hr.department'].search([])
            nbr_departments = len(departments)
            for department in departments:
                department_id = department.id
                mosques = self.env['mk.mosque'].search(active_inactive_mosq_domain + [('center_department_id', '=', department_id)])
                nbr_mosques = len(mosques)
                episodes = self.env['mk.episode'].search(domain_filter + [('mosque_id', 'in', mosques.ids)])
                nbr_episodes = len(episodes)

                link_ids = []
                for episode in episodes:
                    for link in episode.link_ids:
                        if link.state in ['accept','done'] :
                           link_ids += [link.id]
                nbr_student = len(link_ids)
                test_sessions = self.env['student.test.session'].search(domain_test + [('student_id', 'in', link_ids),('state', '!=','cancel')])
                if not is_test_session or (is_test_session and test_sessions):
                    mosque_sessions, episode_sessions, nbr_test_absent,\
                    nbr_test_done, nbr_test_success, nbr_test_fail = self.report_values_count(test_sessions)

                    nbr_mosque_session = len(mosque_sessions)
                    nbr_episode_session = len(episode_sessions)
                    nbr_student_session = len(test_sessions)

                    percentage_test_success, subsc_percentage_success, percentage_success_total_student = self.percentage_count(nbr_test_done,
                                                                                                                            nbr_test_success,
                                                                                                                            nbr_student_session,
                                                                                                                            nbr_student)
                    docs.append({'center':                            department.name,
                                 'nbr_mosques':                       nbr_mosques,
                                 'nbr_mosque_session':                nbr_mosque_session,
                                 'nbr_episode':                       nbr_episodes,
                                 'nbr_episode_session':               nbr_episode_session,
                                 'nbr_student':                       nbr_student,
                                 'nbr_departments':                   nbr_departments,
                                 'nbr_student_session':               nbr_student_session,
                                 'nbr_test_done':                     nbr_test_done,
                                 'nbr_test_success':                  nbr_test_success,
                                 'nbr_test_fail':                     nbr_test_fail,
                                 'nbr_test_absent':                   nbr_test_absent,
                                 'percentage_success_total_student' : percentage_success_total_student,
                                 'subsc_percentage_success' :         subsc_percentage_success,
                                 'percentage_test_success' :          percentage_test_success,
                                 })

        return {'doc_ids':                  data['ids'],
                'doc_model':                data['model'],
                'docs':                     docs,
                'report_type':              data['form']['report_type'],
                'type_filter':              data['form']['type_filter'],
                'type_test_id':             data['form']['type_test_id'],
                'type_test_name':           data['form']['type_test_name'],
                'branch_id':                data['form']['branch_id'],
                'branch_name':              data['form']['branch_name'],
                'episode_academic_name':    academic_name,
                'exam_academic_name':       exam_academic_name,
                'episode_study_class_id':   study_class_id,
                'episode_study_class_name': study_class_name,
                'exam_study_class_id':      exam_study_class_id,
                'exam_study_class_name':    exam_study_class_name,
                'center_name':              data['form']['center_name'],
                'supervisor_name':          data['form']['supervisor_name'],
                'mosque_category_name':     data['form']['mosque_category_name'],
                'mosque_id_name':           data['form']['mosque_id_name'],
                'supervisor_name':          data['form']['supervisor_name'],
                'teacher_name':             data['form']['teacher_name'],
                'success_students':         success_students,
                'failed_students':          failed_students,
                'nbr_departments' :         nbr_departments,
                'nbr_mosques' :             nbr_mosques,
                'nbr_episodes' :            nbr_episodes,
                }