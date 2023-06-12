# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models
from odoo.http import request

def get_state_translation_value(model_name=None, field_name=None, field_value=None):
    translated_state = dict(request.env[model_name].sudo().fields_get(allfields=[field_name])[field_name]['selection'])[field_value]
    return translated_state

class ReportStatusStatment(models.AbstractModel):
    _name = 'report.mk_episode_management.report_status_statement_template'
    _description = 'report status statement'

    # @api.multi
    def totals(self, period):
        student_ids = period.mapped('link_ids').sudo().mapped('student_id')
        grades = student_ids.mapped('grade_id')
        total_saudi         = len(student_ids.filtered(lambda x: x.nationality == 'سعودي'))
        total_not_saudi     = len(student_ids.filtered(lambda x: x.nationality != 'سعودي'))
        total_preliminary   = len(grades.filtered(lambda x: x.type_level == 'preliminary'))
        total_primary       = len(grades.filtered(lambda x: x.type_level == 'primary'))
        total_medium        = len(grades.filtered(lambda x: x.type_level == 'medium'))
        total_secondary     = len(grades.filtered(lambda x: x.type_level == 'secondary'))
        total_academic      = len(grades.filtered(lambda x: x.type_level == 'academic'))
        total_other         = len(grades.filtered(lambda x: x.type_level == 'other'))
        total               = len(period.mapped('link_ids'))

        return total_saudi, total_not_saudi,total_preliminary,total_primary,total_secondary,total_medium,total_academic,total_other,total

    # @api.multi
    def get_report_values(self, docids, data=None):
        mosque = self.env['mk.mosque'].browse(docids)
        docs = []
        episodes = self.env['mk.episode'].search([('mosque_id', '=', mosque.id), ('active', '=', True),('study_class_id.is_default', '=', True)])

        periode_subh = episodes.filtered(lambda e:  e.selected_period == 'subh')
        periode_zuhr = episodes.filtered(lambda e:  e.selected_period == 'zuhr')
        periode_aasr = episodes.filtered(lambda e:  e.selected_period == 'aasr')
        periode_magrib = episodes.filtered(lambda e: e.selected_period == 'magrib')
        periode_esha = episodes.filtered(lambda e:   e.selected_period == 'esha')

        total_student_subh_saudi, total_student_subh_not_saudi, total_student_subh_preliminary, total_student_subh_primary, total_student_subh_secondary, total_student_subh_medium, total_student_subh_academic, total_student_subh_other, total_student_subh = self.totals(
            periode_subh)
        total_student_zuhr_saudi, total_student_zuhr_not_saudi, total_student_zuhr_preliminary, total_student_zuhr_primary, total_student_zuhr_secondary, total_student_zuhr_medium, total_student_zuhr_academic, total_student_zuhr_other, total_student_zuhr = self.totals(
            periode_zuhr)
        total_student_aasr_saudi, total_student_aasr_not_saudi, total_student_aasr_preliminary, total_student_aasr_primary, total_student_aasr_secondary, total_student_aasr_medium, total_student_aasr_academic, total_student_aasr_other, total_student_aasr = self.totals(
            periode_aasr)
        total_student_magrib_saudi, total_student_magrib_not_saudi, total_student_magrib_preliminary, total_student_magrib_primary, total_student_magrib_secondary, total_student_magrib_medium, total_student_magrib_academic, total_student_magrib_other, total_student_magrib = self.totals(
            periode_magrib)
        total_student_esha_saudi, total_student_esha_not_saudi, total_student_esha_preliminary, total_student_esha_primary, total_student_esha_secondary, total_student_esha_medium, total_student_esha_academic, total_student_esha_other, total_student_esha = self.totals(
            periode_esha)

        total_episodes = len(episodes)
        total_student_saudi = total_student_subh_saudi + total_student_zuhr_saudi + total_student_aasr_saudi + total_student_magrib_saudi + total_student_esha_saudi
        total_student_not_saudi = total_student_subh_not_saudi + total_student_zuhr_not_saudi + total_student_aasr_not_saudi + total_student_magrib_not_saudi + total_student_esha_not_saudi
        total_student_preliminary = total_student_subh_preliminary + total_student_zuhr_preliminary + total_student_aasr_preliminary + total_student_magrib_preliminary + total_student_esha_preliminary
        total_student_primary = total_student_subh_primary + total_student_zuhr_primary + total_student_aasr_primary + total_student_magrib_primary + total_student_esha_primary
        total_student_medium = total_student_subh_medium + total_student_zuhr_medium + total_student_aasr_medium + total_student_magrib_medium + total_student_esha_medium
        total_student_secondary = total_student_subh_secondary + total_student_zuhr_secondary + total_student_aasr_secondary + total_student_magrib_secondary + total_student_esha_secondary
        total_student_academic = total_student_subh_academic + total_student_zuhr_academic + total_student_aasr_academic + total_student_magrib_academic + total_student_esha_academic
        total_student_other = total_student_subh_other + total_student_zuhr_other + total_student_aasr_other + total_student_magrib_other + total_student_esha_other
        total_all_student = total_student_subh + total_student_zuhr + total_student_aasr + total_student_magrib + total_student_esha

        vals = {}
        for episode in episodes:
            teacher = episode.teacher_id
            if not teacher:
                continue
            teacher_id = teacher.id
            emp = vals.get(str(teacher_id), False)

            link_ids = episode.link_ids.ids
            if emp:

                nbr_student= len(link_ids)
                nbr_episode = emp.get('nbr_episode') + 1

                nbr_parts = emp.get('nbr_parts') + self.env['student.test.session'].search_count([('student_id', 'in', link_ids),
                                                                                                  ('test_name.type_test', '=', 'parts'),
                                                                                                  ('state','!=','cancel')])
                nbr_test_final = emp.get('nbr_test_final') + self.env['student.test.session'].search_count([('student_id', 'in', link_ids),
                                                                                                            ('test_name.type_test', '=', 'final'),
                                                                                                            ('state','!=','cancel') ])
                emp.update({'nbr_student':      nbr_student,
                            'nbr_episode':      nbr_episode,
                            'nbr_parts':        nbr_parts,
                            'nbr_test_final':   nbr_test_final,
                            })
                vals.update({str(teacher_id): emp})
            else:
                vals.update({str(teacher_id): {'nbr_student':       len(link_ids),
                                               'nbr_episode':       1,
                                               'name': teacher.name,
                                               'nationality': teacher.country_id.nationality,
                                               'mobile': teacher.mobile_phone,
                                               'job': get_state_translation_value('hr.employee', 'category2',teacher.category2),
                                               'nbr_parts': self.env['student.test.session'].search_count([('student_id', 'in', link_ids),
                                                                                                           ('test_name.type_test', '=', 'parts'),
                                                                                                           ('state', '!=', 'cancel')]),
                                               'nbr_test_final': self.env['student.test.session'].search_count([('student_id', 'in', link_ids),
                                                                                                                ('test_name.type_test', '=', 'final'),
                                                                                                                ('state', '!=', 'cancel')]),
                                               }})

        mosque_employees = self.env['hr.employee'].search([('mosqtech_ids', 'in', mosque.id),
                                                           ('category2', '!=', 'teacher')])
        for mosque_employee in mosque_employees:
            vals.update({str(mosque_employee.id): {'nbr_student':   0,
                                                   'nbr_episode':   0,
                                                   'name':          mosque_employee.name,
                                                   'nationality':   mosque_employee.country_id.nationality,
                                                   'job':           get_state_translation_value('hr.employee', 'category2',mosque_employee.category2),
                                                   'nbr_parts':     0,
                                                   'nbr_test_final':0,
                                                   'mobile':        mosque_employee.mobile_phone}})

        study_class = episodes[0].study_class_id
        list_emp = []

        for key, dict_emp in vals.items():
            list_emp += [dict_emp]

        docs.append({'mosque': mosque,
                     'periode_subh': periode_subh,
                     'periode_zuhr': periode_zuhr,
                     'periode_aasr': periode_aasr,
                     'periode_magrib': periode_magrib,
                     'periode_esha': periode_esha,
                     'total_student_subh': total_student_subh,
                     'total_student_zuhr': total_student_zuhr,
                     'total_student_aasr': total_student_aasr,
                     'total_student_magrib': total_student_magrib,
                     'total_student_esha': total_student_esha,
                     'total_student_subh_saudi': total_student_subh_saudi,
                     'total_student_subh_not_saudi': total_student_subh_not_saudi,
                     'total_student_zuhr_saudi': total_student_zuhr_saudi,
                     'total_student_zuhr_not_saudi': total_student_zuhr_not_saudi,
                     'total_student_aasr_saudi': total_student_aasr_saudi,
                     'total_student_aasr_not_saudi': total_student_aasr_not_saudi,
                     'total_student_magrib_saudi': total_student_magrib_saudi,
                     'total_student_magrib_not_saudi': total_student_magrib_not_saudi,
                     'total_student_esha_saudi': total_student_esha_saudi,
                     'total_student_esha_not_saudi': total_student_esha_not_saudi,

                     'total_student_subh_preliminary': total_student_subh_preliminary,
                     'total_student_zuhr_preliminary': total_student_zuhr_preliminary,
                     'total_student_aasr_preliminary': total_student_aasr_preliminary,
                     'total_student_magrib_preliminary': total_student_magrib_preliminary,
                     'total_student_esha_preliminary': total_student_esha_preliminary,

                     'total_student_subh_primary': total_student_subh_primary,
                     'total_student_zuhr_primary': total_student_zuhr_primary,
                     'total_student_aasr_primary': total_student_aasr_primary,
                     'total_student_magrib_primary': total_student_magrib_primary,
                     'total_student_esha_primary': total_student_esha_primary,

                     'total_student_subh_medium': total_student_subh_medium,
                     'total_student_zuhr_medium': total_student_zuhr_medium,
                     'total_student_aasr_medium': total_student_aasr_medium,
                     'total_student_magrib_medium': total_student_magrib_medium,
                     'total_student_esha_medium': total_student_esha_medium,

                     'total_student_subh_secondary': total_student_subh_secondary,
                     'total_student_zuhr_secondary': total_student_zuhr_secondary,
                     'total_student_aasr_secondary': total_student_aasr_secondary,
                     'total_student_magrib_secondary': total_student_magrib_secondary,
                     'total_student_esha_secondary': total_student_esha_secondary,

                     'total_student_subh_academic': total_student_subh_academic,
                     'total_student_zuhr_academic': total_student_zuhr_academic,
                     'total_student_aasr_academic': total_student_aasr_academic,
                     'total_student_magrib_academic': total_student_magrib_academic,
                     'total_student_esha_academic': total_student_esha_academic,

                     'total_student_subh_other': total_student_subh_other,
                     'total_student_zuhr_other': total_student_zuhr_other,
                     'total_student_aasr_other': total_student_aasr_other,
                     'total_student_magrib_other': total_student_aasr_other,
                     'total_student_esha_other': total_student_aasr_other,

                     'total_episodes': total_episodes,
                     'total_student_saudi': total_student_saudi,
                     'total_student_not_saudi': total_student_not_saudi,
                     'total_student_preliminary': total_student_preliminary,
                     'total_student_primary': total_student_primary,
                     'total_student_medium': total_student_medium,
                     'total_student_secondary': total_student_secondary,
                     'total_student_academic': total_student_academic,
                     'total_student_other': total_student_other,
                     'total_all_student': total_all_student,
                     'episodes': episodes,
                     'study_class': study_class.name,
                     })
        return {
            'doc_model': 'mk.mosque',
            'docs': docs,
            'employee': list_emp,
        }
