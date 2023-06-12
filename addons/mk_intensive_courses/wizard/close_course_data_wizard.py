from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class CloseCourseDataWizard(models.TransientModel):
    _name = 'close.course.data'

    def _get_default_masjed(self):
        return self.env['mk.mosque'].browse(self.env.context.get('mosque_id'))

    course_episode_nbr       = fields.Integer('Course Episodes', required=True)
    course_students_nbr      = fields.Integer('Course Students', required=True)
    course_teachers_nbr      = fields.Integer('Course Teachers', )
    course_administrators_nbr = fields.Integer('Course Administrators')
    close_total_hours        = fields.Integer('Total hours',     required=True)
    parts_nbr                = fields.Integer('Parts nbr')
    parts_female_total_nbr   = fields.Integer('Parts female total nbr')
    parts_female_total_done_nbr = fields.Integer('Parts female total done nbr')

    students_finals_nbr      = fields.Integer('Students finals')
    students_final_tests_nbr = fields.Integer('Students in final tests', required=True)
    students_parts_tests_nbr = fields.Integer('Students in parts tests', required=True)

    mosque_id          = fields.Many2one('mk.mosque',default=_get_default_masjed, track_visibility='onchange')
    gender_mosque      = fields.Selection(related="mosque_id.gender_mosque", string='Mosque gender', track_visibility='onchange')


    @api.one
    def action_confirm(self, data):
        course_id = data.get('active_id', [])
        current_course_id = self.env['mk.course.request'].sudo().search([('id', '=', course_id)])
        course_episode_nbr = self.course_episode_nbr
        course_students_nbr = self.course_students_nbr
        close_total_hours = self.close_total_hours
        students_final_tests_nbr = self.students_final_tests_nbr
        students_parts_tests_nbr = self.students_parts_tests_nbr

        vals = {'course_episode_nbr': course_episode_nbr,
                'course_students_nbr': course_students_nbr,
                'close_total_hours': close_total_hours,
                'students_final_tests_nbr': students_final_tests_nbr,
                'students_parts_tests_nbr': students_parts_tests_nbr,
                'state': 'closed'
        }
        if self.gender_mosque == 'female':
            course_teachers_nbr = self.course_teachers_nbr
            course_administrators_nbr = self.course_administrators_nbr
            parts_female_total_done_nbr = self.parts_female_total_done_nbr
            parts_female_total_nbr = self.parts_female_total_nbr
            # if course_teachers_nbr <= 0:
            #     raise ValidationError(_("You must fill in number of course teachers."))
            # if course_administrators_nbr <= 0:
            #     raise ValidationError(_("You must fill in number of course administrators."))
            # if parts_female_total_nbr <= 0:
            #     raise ValidationError(_("You must fill in total number of female parts."))
            # if parts_female_total_done_nbr <= 0:
            #     raise ValidationError(_("You must fill in total number of done female parts."))
            vals.update({'course_teachers_nbr': course_teachers_nbr,
                         'course_administrators_nbr': course_administrators_nbr,
                         'parts_female_total_nbr': parts_female_total_nbr,
                         'parts_female_total_done_nbr': parts_female_total_done_nbr,})
        elif self.gender_mosque == 'male':
            parts_nbr = self.parts_nbr
            students_finals_nbr = self.students_finals_nbr
            if course_episode_nbr <= 0:
                raise ValidationError(_("You must fill in number of course episode."))
            if course_students_nbr <= 0:
                raise ValidationError(_("You must fill in number of course students."))
            if close_total_hours <= 0:
                raise ValidationError(_("You must fill in total hours."))
            if students_final_tests_nbr <= 0:
                raise ValidationError(_("You must fill in number of final tests students."))
            if students_parts_tests_nbr <= 0:
                raise ValidationError(_("You must fill in number of parts tests students."))
            if parts_nbr <= 0:
                raise ValidationError(_("You must fill in number of parts."))
            if students_finals_nbr <= 0:
                raise ValidationError(_("You must fill in number of final students."))
            vals.update({'parts_nbr': parts_nbr,
                         'students_finals_nbr': students_finals_nbr,})
        current_course_id.write(vals)

        # methode 1
        return current_course_id.print_close_certificate()

        # #methode 2
        # data={  'id':   current_course_id.id,
        #         'model': current_course_id._name,
        #         'form': current_course_id.read()[0]}
        # return self.env.ref('mk_intensive_courses.close_quran_day_course_data_id').report_action(self, data=data)
        #
        #
        # #methode 3
        # base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # report_url = base_url + '/report/pdf/mk_intensive_courses.close_quran_day_certificate/%s' % (current_course_id.id,)
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': report_url,
        #     'target': 'new',
        # }

        # return res
        # return {'type': 'ir.actions.act_window_close'}
