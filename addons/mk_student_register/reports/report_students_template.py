# -*- coding: utf-8 -*-
from odoo import models, api, _


class report_students_template(models.AbstractModel):
    _name = 'report.mk_student_register.report_students_template'

    def report_values_count(self, students, study_class_id, nbr_draft_students, nbr_rejected_student, nbr_accepted_student, nbr_inactive_student, nbr_done_student,
                            nbr_moved_student, nbr_cleared_student, nbr_episode_related_student, nbr_seasonal_episode_related_student):
        for student in students:
            state_student = student.request_state

            if state_student == 'draft':
                nbr_draft_students += 1

            elif state_student == 'reject':
                nbr_rejected_student += 1

            elif state_student == 'accept':
                nbr_accepted_student += 1

            if student.active == False:
                nbr_inactive_student += 1

            student_id = student.id

            link_done = self.env['mk.link'].search([('student_id', '=', student_id),
                                                    ('episode_id.study_class_id', '=', study_class_id),
                                                    ('action_done', '=', 'ep_done')], limit=1)
            if link_done:
                nbr_done_student += 1

            link_moved = self.env['mk.link'].search([('student_id', '=', student_id),
                                                     ('episode_id.study_class_id', '=', study_class_id),
                                                     ('action_done', 'in', ['internal', 'external'])], limit=1)
            if link_moved:
                nbr_moved_student += 1

            link_cleared = self.env['mk.link'].search([('student_id', '=', student_id),
                                                       ('episode_id.study_class_id', '=', study_class_id),
                                                       ('action_done', '=', 'clear')], limit=1)
            if link_cleared:
                nbr_cleared_student += 1

            link_episode_related = self.env['mk.link'].search([('student_id', '=', student_id),
                                                               ('episode_id.study_class_id', '=', study_class_id),
                                                               ('state', '=', 'accept'),
                                                               ('action_done', '=', False)], limit=1)
            if link_episode_related:
                nbr_episode_related_student += 1

            link_seasonal_episode_related = self.env['mk.link'].search([('student_id', '=', student_id),
                                                                        ('episode_id.study_class_id', '=', study_class_id),
                                                                        ('state', '=', 'accept'),
                                                                        ('action_done', '=', False),
                                                                        ('episode_id.episode_season', '=','seasonal')], limit=1)
            if link_seasonal_episode_related:
                nbr_seasonal_episode_related_student += 1

        return nbr_draft_students, nbr_rejected_student, nbr_accepted_student, nbr_inactive_student, nbr_done_student, nbr_moved_student, nbr_cleared_student, nbr_episode_related_student, nbr_seasonal_episode_related_student

    @api.model
    def get_report_values(self, docids, data ):
        academic_id = data['form']['academic_id']
        academic_name = data['form']['academic_name']

        domain_filter = data['form']['domain']
        teacher_id = data['form']['teacher_id']
        teacher_name = data['form']['teacher_name']
        mosque_id = data['form']['mosque_id']
        mosque_name = data['form']['mosque_id_name']
        mosque_category_id = data['form']['mosque_category_id']
        supervisor = data['form']['supervisor_id']
        center_id = data['form']['center_id']
        gender_type = data['form']['gender_type']
        study_class_id = data['form']['study_class_id']

        study_class_name = data['form']['study_class_name']

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
        success_students = 0
        failed_students = 0

        nbr_draft_students = 0
        nbr_accepted_student = 0
        nbr_rejected_student = 0
        nbr_moved_student = 0
        nbr_done_student = 0
        nbr_inactive_student = 0
        nbr_cleared_student = 0
        nbr_episode_related_student = 0
        nbr_seasonal_episode_related_student = 0

        domain = [('academic_id', '=', academic_id),
                  ('is_pass', '=', True),
                  ('state', '=', 'done'),
                  ('student_id', 'in', student_ids)]

        if study_class_id:
            domain.append(('study_class_id', '=', study_class_id))

        # reports with filter
        if teacher_id:
            episodes = self.env['mk.episode'].search(domain_filter + [('teacher_id', '=', teacher_id)])
            for episode in episodes:
                for link in episode.link_ids:
                    student = link.student_id
                    state_student = student.request_state

                    if state_student == 'draft':
                        nbr_draft_students += 1

                    elif state_student == 'reject':
                        nbr_rejected_student += 1

                    elif state_student == 'accept':
                        nbr_accepted_student += 1

                    if student.active == False:
                        nbr_inactive_student += 1

                    student_id = student.id

                    link_done = self.env['mk.link'].search([('student_id', '=', student_id),
                                                            ('episode_id.study_class_id', '=', study_class_id),
                                                            ('action_done', '=', 'ep_done')], limit=1)
                    if link_done:
                        nbr_done_student += 1

                    link_moved = self.env['mk.link'].search([('student_id', '=', student_id),
                                                             ('episode_id.study_class_id', '=', study_class_id),
                                                             ('action_done', 'in', ['internal', 'external'])], limit=1)
                    if link_moved:
                        nbr_moved_student += 1

                    link_cleared = self.env['mk.link'].search([('student_id', '=', student_id),
                                                               ('episode_id.study_class_id', '=', study_class_id),
                                                               ('action_done', '=', 'clear')], limit=1)
                    if link_cleared:
                        nbr_cleared_student += 1

                    link_episode_related = self.env['mk.link'].search([('student_id', '=', student_id),
                                                                       ('episode_id.study_class_id', '=',
                                                                        study_class_id),
                                                                       ('state', '=', 'accept'),
                                                                       ('action_done', '=', False)], limit=1)
                    if link_episode_related:
                        nbr_episode_related_student += 1

                    link_seasonal_episode_related = self.env['mk.link'].search([('student_id', '=', student_id),
                                                                                ('episode_id.study_class_id', '=',
                                                                                 study_class_id),
                                                                                ('state', '=', 'accept'),
                                                                                ('action_done', '=', False),
                                                                                ('episode_id.episode_season', '=',
                                                                                 'seasonal')],
                                                                               limit=1)
                    if link_seasonal_episode_related:
                        nbr_seasonal_episode_related_student += 1

            docs.append({'teacher':                             teacher_name,
                        'nbr_draft_students':                   nbr_draft_students,
                        'nbr_accepted_student':                 nbr_accepted_student,
                        'nbr_rejected_student':                 nbr_rejected_student,
                        'nbr_done_student':                     nbr_done_student,
                        'nbr_moved_student':                    nbr_moved_student,
                        'nbr_inactive_student':                 nbr_inactive_student,
                        'nbr_cleared_student':                  nbr_cleared_student,
                        'nbr_episode_related_student':          nbr_episode_related_student,
                        'nbr_seasonal_episode_related_student': nbr_seasonal_episode_related_student,})

        elif mosque_id:
            students = self.env['mk.student.register'].search([('mosq_id', '=', mosque_id)])
            nbr_draft_students, nbr_rejected_student, nbr_accepted_student, nbr_inactive_student, nbr_done_student,nbr_moved_student, nbr_cleared_student,\
            nbr_episode_related_student, nbr_seasonal_episode_related_student = self.report_values_count(students,
                                                                                                         nbr_draft_students,
                                                                                                         nbr_rejected_student,
                                                                                                         nbr_accepted_student,
                                                                                                         nbr_inactive_student,
                                                                                                         nbr_done_student,
                                                                                                         nbr_moved_student,
                                                                                                         nbr_cleared_student,
                                                                                                         nbr_episode_related_student,
                                                                                                         nbr_seasonal_episode_related_student)

            docs.append({
                     'mosques':                               mosque_name,
                     'nbr_draft_students':                   nbr_draft_students,
                     'nbr_accepted_student':                 nbr_accepted_student,
                     'nbr_rejected_student':                 nbr_rejected_student,
                     'nbr_done_student':                     nbr_done_student,
                     'nbr_moved_student':                    nbr_moved_student,
                     'nbr_inactive_student':                 nbr_inactive_student,
                     'nbr_cleared_student':                  nbr_cleared_student,
                     'nbr_episode_related_student':          nbr_episode_related_student,
                     'nbr_seasonal_episode_related_student': nbr_seasonal_episode_related_student,
                     })

        elif supervisor:
            supervisor_id = self.env['hr.employee'].search([('id', '=', supervisor)], limit=1)
            mosques = self.env['mk.mosque'].search([('id', 'in', supervisor_id.mosque_sup.ids)])
            for mosque in mosques:
                students = self.env['mk.student.register'].search([('mosq_id', '=', mosque.id)])
                nbr_draft_students, nbr_rejected_student, nbr_accepted_student, nbr_inactive_student, nbr_done_student,nbr_moved_student, nbr_cleared_student,\
                nbr_episode_related_student, nbr_seasonal_episode_related_student = self.report_values_count(students,
                                                                                                             nbr_draft_students,
                                                                                                             nbr_rejected_student,
                                                                                                             nbr_accepted_student,
                                                                                                             nbr_inactive_student,
                                                                                                             nbr_done_student,
                                                                                                             nbr_moved_student,
                                                                                                             nbr_cleared_student,
                                                                                                             nbr_episode_related_student,
                                                                                                             nbr_seasonal_episode_related_student, )

                docs.append({'supervisor':                           supervisor_id.name,
                             'mosques':                              mosque.name,
                             'nbr_draft_students':                   nbr_draft_students,
                             'nbr_accepted_student':                 nbr_accepted_student,
                             'nbr_rejected_student':                 nbr_rejected_student,
                             'nbr_done_student':                     nbr_done_student,
                             'nbr_moved_student':                    nbr_moved_student,
                             'nbr_inactive_student':                 nbr_inactive_student,
                             'nbr_cleared_student':                  nbr_cleared_student,
                             'nbr_episode_related_student':          nbr_episode_related_student,
                             'nbr_seasonal_episode_student': nbr_seasonal_episode_related_student})

        elif mosque_category_id:
            mosques = self.env['mk.mosque'].search([('categ_id', '=', mosque_category_id)])
            for mosque in mosques :
                students = self.env['mk.student.register'].search([('mosq_id', '=', mosque.id)])
                nbr_draft_students, nbr_rejected_student, nbr_accepted_student, nbr_inactive_student, nbr_done_student, nbr_moved_student, nbr_cleared_student, \
                nbr_episode_related_student, nbr_seasonal_episode_related_student = self.report_values_count(students,
                                                                                                             nbr_draft_students,
                                                                                                             nbr_rejected_student,
                                                                                                             nbr_accepted_student,
                                                                                                             nbr_inactive_student,
                                                                                                             nbr_done_student,
                                                                                                             nbr_moved_student,
                                                                                                             nbr_cleared_student,
                                                                                                             nbr_episode_related_student,
                                                                                                             nbr_seasonal_episode_related_student)

                docs.append({'categ_id':                              mosque.categ_id.name,
                              'mosques':                              mosque.name,
                              'nbr_draft_students':                   nbr_draft_students,
                              'nbr_accepted_student':                 nbr_accepted_student,
                              'nbr_rejected_student':                 nbr_rejected_student,
                              'nbr_done_student':                     nbr_done_student,
                              'nbr_moved_student':                    nbr_moved_student,
                              'nbr_inactive_student':                 nbr_inactive_student,
                              'nbr_cleared_student':                  nbr_cleared_student,
                              'nbr_episode_related_student':          nbr_episode_related_student,
                              'nbr_seasonal_episode_related_student': nbr_seasonal_episode_related_student,
                              })

        elif gender_type:
            mosques = self.env['mk.mosque'].search([('categ_id.mosque_type', '=', gender_type)])
            for mosque in mosques:
                students = self.env['mk.student.register'].search([('mosq_id', '=', mosque.id)])
                nbr_draft_students, nbr_rejected_student, nbr_accepted_student, nbr_inactive_student, nbr_done_student, nbr_moved_student, nbr_cleared_student, \
                nbr_episode_related_student, nbr_seasonal_episode_related_student = self.report_values_count(students,
                                                                                                             nbr_draft_students,
                                                                                                             nbr_rejected_student,
                                                                                                             nbr_accepted_student,
                                                                                                             nbr_inactive_student,
                                                                                                             nbr_done_student,
                                                                                                             nbr_moved_student,
                                                                                                             nbr_cleared_student,
                                                                                                             nbr_episode_related_student,
                                                                                                             nbr_seasonal_episode_related_student)

                docs.append({'categ_id':                             mosque.categ_id.name,
                             'mosques':                              mosque.name,
                             'nbr_draft_students':                   nbr_draft_students,
                             'nbr_accepted_student':                 nbr_accepted_student,
                             'nbr_rejected_student':                 nbr_rejected_student,
                             'nbr_done_student':                     nbr_done_student,
                             'nbr_moved_student':                    nbr_moved_student,
                             'nbr_inactive_student':                 nbr_inactive_student,
                             'nbr_cleared_student':                  nbr_cleared_student,
                             'nbr_episode_related_student':          nbr_episode_related_student,
                             'nbr_seasonal_episode_related_student': nbr_seasonal_episode_related_student,
                             })

        elif center_id:
            mosques = self.env['mk.mosque'].search([('center_department_id', '=', center_id)])
            for mosque in mosques:
                students = self.env['mk.student.register'].search([('mosq_id', '=', mosque.id)])
                nbr_draft_students, nbr_rejected_student, nbr_accepted_student, nbr_inactive_student, nbr_done_student, nbr_moved_student, nbr_cleared_student, \
                nbr_episode_related_student, nbr_seasonal_episode_related_student = self.report_values_count(students,
                                                                                                             nbr_draft_students,
                                                                                                             nbr_rejected_student,
                                                                                                             nbr_accepted_student,
                                                                                                             nbr_inactive_student,
                                                                                                             nbr_done_student,
                                                                                                             nbr_moved_student,
                                                                                                             nbr_cleared_student,
                                                                                                             nbr_episode_related_student,
                                                                                                             nbr_seasonal_episode_related_student
                                                                                                             )
                docs.append({'center':                               mosque.center_department_id.name,
                             'mosques':                              mosque.name,
                             'nbr_draft_students':                   nbr_draft_students,
                             'nbr_accepted_student':                 nbr_accepted_student,
                             'nbr_rejected_student':                 nbr_rejected_student,
                             'nbr_done_student':                     nbr_done_student,
                             'nbr_moved_student':                    nbr_moved_student,
                             'nbr_inactive_student':                 nbr_inactive_student,
                             'nbr_cleared_student':                  nbr_cleared_student,
                             'nbr_episode_related_student':          nbr_episode_related_student,
                             'nbr_seasonal_episode_related_student': nbr_seasonal_episode_related_student,
                             })

        elif study_class_id:
            departments = self.env['hr.department'].search([])
            for department in departments:
                students = self.env['mk.student.register'].search([('mosq_id.center_department_id', '=', department.id)])
                nbr_draft_students, nbr_rejected_student, nbr_accepted_student, nbr_inactive_student, nbr_done_student, nbr_moved_student, nbr_cleared_student, \
                nbr_episode_related_student, nbr_seasonal_episode_related_student = self.report_values_count(students,
                                                                                                             nbr_draft_students,
                                                                                                             nbr_rejected_student,
                                                                                                             nbr_accepted_student,
                                                                                                             nbr_inactive_student,
                                                                                                             nbr_done_student,
                                                                                                             nbr_moved_student,
                                                                                                             nbr_cleared_student,
                                                                                                             nbr_episode_related_student,
                                                                                                             nbr_seasonal_episode_related_student
                                                                                                             )

                docs.append({'center':                               department.name,
                             'nbr_draft_students':                   nbr_draft_students,
                             'nbr_accepted_student':                 nbr_accepted_student,
                             'nbr_rejected_student':                 nbr_rejected_student,
                             'nbr_done_student':                     nbr_done_student,
                             'nbr_moved_student':                    nbr_moved_student,
                             'nbr_inactive_student':                 nbr_inactive_student,
                             'nbr_cleared_student':                  nbr_cleared_student,
                             'nbr_episode_related_student':          nbr_episode_related_student,
                             'nbr_seasonal_episode_related_student': nbr_seasonal_episode_related_student,
                             })

        return {'doc_ids':              data['ids'],
                'doc_model':            data['model'],
                'docs':                 docs,
                'type_filter':          data['form']['type_filter'],
                'academic_name':        academic_name,
                'study_class_id':       study_class_id,
                'study_class_name':     study_class_name,
                'center_name':          data['form']['center_name'],
                'supervisor_name':      data['form']['supervisor_name'],
                'mosque_category_name': data['form']['mosque_category_name'],
                'mosque_id_name':       data['form']['mosque_id_name'],
                'supervisor_name':      data['form']['supervisor_name'],
                'teacher_name':         data['form']['teacher_name'],
                'success_students':     success_students,
                'failed_students':      failed_students,
                }