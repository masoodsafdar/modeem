from odoo import models, fields, api

class PopupUpdateCourseData(models.TransientModel):
    _name = 'course.request.update.wizard'

    @api.multi
    def _get_start_date_class(self):
        course_id = self._context.get('default_course_id')
        course = self.env['mk.course.request'].browse(course_id)
        return course.start_date

    @api.multi
    def get_end_date_class(self):
        course_id = self._context.get('default_course_id')
        course = self.env['mk.course.request'].browse(course_id)
        return course.end_date

    @api.multi
    def get_day_ids(self):
        course_id = self._context.get('default_course_id')
        course = self.env['mk.course.request'].browse(course_id)
        return course.day_ids.ids

    location = fields.Selection(string="Location", selection=[('internal', 'داخل المدرسة'),
                                                              ('external', 'خارج المدرسة'),
                                                              ('female_episodes', 'حلقات نسائية في مسجد/جامع'),
                                                              ('remotly', 'عن بعد')])
    external_mosq_name = fields.Char('اسم المسجد/الجامع')
    academic_id    = fields.Many2one('mk.study.year', string='العام الدراسي')
    study_class_id = fields.Many2one('mk.study.class', string='الفصل الدراسي')
    course_id      = fields.Many2one('mk.course.request', string='Course')
    start_date     = fields.Date(string='Start Date', default=_get_start_date_class)
    end_date       = fields.Date(string='End Date', default=get_end_date_class)
    day_ids        = fields.Many2many('mk.work.days', string="الايام للبرنامج", default=get_day_ids)

    def action_update(self):
        course_id = self.course_id
        academic_id = self.academic_id
        study_class_id = self.study_class_id
        location = self.location
        external_mosq_name = self.external_mosq_name
        day_ids = self.day_ids
        course_id.write({'academic_id': academic_id.id,
                         'study_class_id': study_class_id.id,
                         'location': location,
                         'external_mosq_name': external_mosq_name,
                         'day_ids': [(6,0, day_ids.ids )]})
        start_date = self.start_date
        end_date = self.end_date
        if start_date:
            course_id.write({'start_date': start_date})
        if end_date:
            course_id.write({'end_date': end_date})
        mosque = course_id.mosque_id
        episode_season_ids = set()

        course_requests = mosque and mosque.course_request_ids or []
        for course_request in course_requests:
            if course_request.study_class_id.id != study_class_id.id:
                continue

            episode_season_ids.add(course_request.id)

        episodes = self.env['mk.episode'].search([('study_class_id', '=', study_class_id.id),
                                                  ('mosque_id', '=', mosque.id)])
        for episode in episodes:
            episode.episode_specific_ids = list(episode_season_ids)

