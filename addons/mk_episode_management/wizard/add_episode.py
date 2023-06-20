from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AddEpisodeMasterWizard(models.TransientModel):
    _name = 'add.mk.episode.master'

    @api.model
    def get_year_default(self):
        year = self.env['mk.study.year'].search([('is_default', '=', True)], limit=1)
        return year and year.id or False

    @api.model
    def get_study_class(self):
        study_class = self.env['mk.study.class'].search([('study_year_id', '=', self.get_year_default()),
                                                         ('is_default', '=', True)], limit=1)
        return study_class and study_class.id or False

    @api.onchange('study_class_id')
    def onchange_studey_class(self):
        study_class_id = self.study_class_id
        if study_class_id:
            start_date = study_class_id.start_date
            end_date   = study_class_id.end_date
            self.teacher_subh_id = False
            self.teacher_zuhr_id = False
            self.teacher_aasr_id = False
            self.teacher_magrib_id = False
            self.teacher_esha_id = False

            self.start_date_subh = start_date
            self.start_date_zuhr = start_date
            self.start_date_aasr = start_date
            self.start_date_magrib = start_date
            self.start_date_esha = start_date

            self.end_date_subh = end_date
            self.end_date_zuhr = end_date
            self.end_date_aasr = end_date
            self.end_date_magrib = end_date
            self.end_date_esha = end_date

    @api.onchange('mosque_id')
    def onchange_mosque(self):
        teacher_ids = []
        if self.mosque_id:
            self.teacher_subh_id = False
            self.teacher_zuhr_id = False
            self.teacher_aasr_id = False
            self.teacher_magrib_id = False
            self.teacher_esha_id = False
            teacher_ids = (self.env['hr.employee'].search([('mosqtech_ids', 'in', [self.mosque_id.id]),
                                                           ('category2', '=', 'teacher')])).ids

        return {'domain': {'teacher_subh_id': [('id', 'in', teacher_ids)],
                           'teacher_zuhr_id': [('id', 'in', teacher_ids)],
                           'teacher_aasr_id': [('id', 'in', teacher_ids)],
                           'teacher_magrib_id': [('id', 'in', teacher_ids)],
                           'teacher_esha_id': [('id', 'in', teacher_ids)]}}

    @api.onchange('academic_id')
    def onchange_academic_year(self):
        study_class_ids = []
        for rec in self.academic_id.class_ids:
            study_class_ids.append(rec.id)

        return {'domain': {'study_class_id': [('id', 'in', study_class_ids)]}}

    @api.model
    def get_default_days(self):
        return self.env['mk.work.days'].search([('order', '<', 5)]).ids

    def episode_teacher(self, teacher_id, selected_period):
        domain = [('study_class_id', '=', self.study_class_id.id)]
        if teacher_id:
            episode = self.env['mk.episode'].search(domain + [('teacher_id', '=', teacher_id),
                                                              ('selected_period', '=', selected_period)], limit=1)
            if episode:
                msg = 'المعلم يدرس في نفس الفترة في حلقة' + ' "' + episode.name + '" ' + 'في مسجد' + ' "' + episode.mosque_id.name + '" ' + ' !'
                raise ValidationError(msg)

    @api.onchange('teacher_subh_id','teacher_zuhr_id','teacher_aasr_id','teacher_magrib_id','teacher_esha_id')
    def onchange_teacher(self):
        if self.subh:
            teacher_id = self.teacher_subh_id.id
            selected_period = 'sobh'
            self.episode_teacher(teacher_id,selected_period)
        if self.subh:
            teacher_id = self.teacher_zuhr_id.id
            selected_period = 'zuhr'
            self.episode_teacher(teacher_id,selected_period)
        if self.subh:
            teacher_id = self.teacher_aasr_id.id
            selected_period = 'aasr'
            self.episode_teacher(teacher_id,selected_period)
        if self.subh:
            teacher_id = self.teacher_magrib_id.id
            selected_period = 'magrib'
            self.episode_teacher(teacher_id,selected_period)
        if self.subh:
            teacher_id = self.teacher_esha_id.id
            selected_period = 'esha'
            self.episode_teacher(teacher_id,selected_period)

    @api.onchange('mosque_id')
    def get_gender_mosque(self):
        gender_mosque = self.mosque_id.gender_mosque
        gender = False
        if gender_mosque == 'male':
            gender = 'men'
        else:
            gender = 'women'

        self.gender = gender

    @api.onchange('program_subh_id')
    def onchange_program_subh_id(self):
        self.approache_subh_id = False

    @api.onchange('program_zuhr_id')
    def onchange_program_zuhr_id(self):
        self.approache_zuhr_id = False

    @api.onchange('program_aasr_id')
    def onchange_program_aasr_id(self):
        self.approache_aasr_id = False

    @api.onchange('program_magrib_id')
    def onchange_program_magrib_id(self):
        self.approache_magrib_id = False

    @api.onchange('program_esha_id')
    def onchange_program_esha_id(self):
        self.approache_esha_id = False

    @api.model
    def default_get(self, fields):
        res = super(AddEpisodeMasterWizard, self).default_get(fields)

        mosques_ids = False
        user_id = self.env.user
        employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])
        category = employee_id.category2
        if category == 'edu_supervisor':
            mosques_ids = employee_id.mosque_sup.ids
        elif category in ['admin', 'teacher', 'supervisor', 'center_admin']:
            mosques_ids = employee_id.mosqtech_ids.ids

        if 'mosque_id' in fields:
            res.update({'mosque_id': mosques_ids and mosques_ids[0] or False})
        return res

    name           = fields.Char('Name')
    mosque_id      = fields.Many2one('mk.mosque',      string='Masjed')
    academic_id    = fields.Many2one('mk.study.year',  string='Academic Year', required=True, default=get_year_default, copy=False)
    study_class_id = fields.Many2one('mk.study.class', string='Study class',   default=get_study_class,domain=[('is_default', '=', True)], copy=False)
    gender         = fields.Selection([('men', 'men episode'),
                                       ('women', 'women episode')], string='Gender')

    subh   = fields.Boolean('Subh')
    zuhr   = fields.Boolean('Zuhr')
    aasr   = fields.Boolean('Aasr')
    magrib = fields.Boolean('Magrib')
    esha   = fields.Boolean('Esha')

    teacher_subh_id       = fields.Many2one('hr.employee', string='Teacher Sobh')
    grade_subh_ids        = fields.Many2many('mk.grade', 'mk_episode_grade1_rel', 'episode_id', 'grade_id', string='Grades Sobh', domain=[('is_episode', '=', True)])
    episode_type_subh_id  = fields.Many2one('mk.episode_type', string='Episode Type Sobh')
    episode_work_subh_id  = fields.Many2one('mk.epsoide.works', string='episode work Sobh')
    start_date_subh       = fields.Date('Start date Sobh', copy=False)
    end_date_subh         = fields.Date('End date Sobh', copy=False)
    error_register_subh   = fields.Selection([('total', 'Overall'),
                                             ('detailed', 'Detailed')], string='Error register')
    episode_days_subh_ids = fields.Many2many('mk.work.days', 'mk_episode_days1_rel', 'episode_id', 'day_id', string='work days Sobh', default=get_default_days)
    program_subh_id = fields.Many2one('mk.programs', string='Program', tracking=True)
    approache_subh_id = fields.Many2one('mk.approaches', string='Approach', tracking=True)

    teacher_zuhr_id       = fields.Many2one('hr.employee', string='Teacher Zuhr')
    grade_zuhr_ids        = fields.Many2many('mk.grade',  'mk_episode_grade2_rel', 'episode_id', 'grade_id', string='Grades Zuhr', domain=[('is_episode', '=', True)])
    episode_type_zuhr_id  = fields.Many2one('mk.episode_type', string='Episode Type Zuhr')
    episode_work_zuhr_id  = fields.Many2one('mk.epsoide.works', string='episode work Zuhr')
    start_date_zuhr       = fields.Date('Start date Zuhr', copy=False)
    end_date_zuhr         = fields.Date('End date Zuhr', copy=False)
    error_register_zuhr   = fields.Selection([('total', 'Overall'),
                                              ('detailed', 'Detailed')], string='Error register')
    episode_days_zuhr_ids = fields.Many2many('mk.work.days','mk_episode_days2_rel', 'episode_id', 'day_id', string='work days Sobh', default=get_default_days)
    program_zuhr_id       = fields.Many2one('mk.programs', string='Program', tracking=True)
    approache_zuhr_id     = fields.Many2one('mk.approaches', string='Approach', tracking=True)

    teacher_aasr_id         = fields.Many2one('hr.employee', string='Teacher Aasr')
    grade_aasr_ids          = fields.Many2many('mk.grade', 'mk_episode_grade3_rel', 'episode_id', 'grade_id', string='Grades Aasr', domain=[('is_episode', '=', True)])
    episode_type_aasr_id    = fields.Many2one('mk.episode_type', string='Episode Type Aasr')
    episode_work_aasr_id    = fields.Many2one('mk.epsoide.works', string='episode work Aasr')
    start_date_aasr         = fields.Date('Start date Aasr', copy=False)
    end_date_aasr           = fields.Date('End date Aasr', copy=False)
    error_register_aasr     = fields.Selection([('total', 'Overall'),
                                                ('detailed', 'Detailed')], string='Error register')
    episode_days_aasr_ids   = fields.Many2many('mk.work.days', 'mk_episode_days3_rel', 'episode_id', 'day_id', string='work days Sobh', default=get_default_days)
    program_aasr_id         = fields.Many2one('mk.programs', string='Program', tracking=True)
    approache_aasr_id       = fields.Many2one('mk.approaches', string='Approach', tracking=True)

    teacher_magrib_id       = fields.Many2one('hr.employee', string='Teacher Magrib')
    grade_magrib_ids        = fields.Many2many('mk.grade',  'mk_episode_grade4_rel', 'episode_id', 'grade_id', string='Grades Magrib', domain=[('is_episode', '=', True)])
    episode_type_magrib_id  = fields.Many2one('mk.episode_type', string='Episode Type Magrib')
    episode_work_magrib_id  = fields.Many2one('mk.epsoide.works', string='episode work Magrib')
    start_date_magrib       = fields.Date('Start date Magrib', copy=False)
    end_date_magrib         = fields.Date('End date Magrib', copy=False)
    error_register_magrib   = fields.Selection([('total', 'Overall'),
                                                ('detailed', 'Detailed')], string='Error register')
    episode_days_magrib_ids = fields.Many2many('mk.work.days', 'mk_episode_days4_rel', 'episode_id', 'day_id', string='work days Sobh', default=get_default_days)
    program_magrib_id         = fields.Many2one('mk.programs', string='Program', tracking=True)
    approache_magrib_id       = fields.Many2one('mk.approaches', string='Approach', tracking=True)

    teacher_esha_id        = fields.Many2one('hr.employee', string='Teacher Esha')
    grade_esha_ids         = fields.Many2many('mk.grade',  'mk_episode_grade5_rel', 'episode_id', 'grade_id', string='Grades Esha', domain=[('is_episode', '=', True)])
    episode_type_esha_id   = fields.Many2one('mk.episode_type', string='Episode Type Esha')
    episode_work_esha_id   = fields.Many2one('mk.epsoide.works', string='episode work Esha')
    start_date_esha        = fields.Date('Start date Esha', copy=False)
    end_date_esha          = fields.Date('End date Esha', copy=False)
    error_register_esha    = fields.Selection([('total', 'Overall'),
                                               ('detailed', 'Detailed')], string='Error register')
    episode_days_esha_ids = fields.Many2many('mk.work.days', 'mk_episode_days5_rel', 'episode_id', 'day_id', string='work days Sobh', default=get_default_days)
    program_esha_id = fields.Many2one('mk.programs', string='Program', tracking=True)
    approache_esha_id = fields.Many2one('mk.approaches', string='Approach', tracking=True)

    is_online_subh        = fields.Boolean('Online')
    is_online_zuhr        = fields.Boolean('Online')
    is_online_aasr        = fields.Boolean('Online')
    is_online_magrib        = fields.Boolean('Online')
    is_online_esha        = fields.Boolean('Online')

    # @api.multi
    def create_episode(self):
        episode_master_values = {'name': self.name,
                                 'mosque_id': self.mosque_id.id,
                                 'academic_id': self.academic_id.id,
                                 'study_class_id': self.study_class_id.id}
        parent_episode = self.env['mk.episode.master'].create(episode_master_values)
        if self.subh:
            episode_subh = self.env['mk.episode'].create({'parent_episode': parent_episode.id,
                                                          'selected_period': 'subh',
                                                          'subh': True,
                                                          'name': parent_episode.name,
                                                          'mosque_id': self.mosque_id.id,
                                                          'academic_id': self.academic_id.id,
                                                          'study_class_id': self.study_class_id.id,
                                                          'teacher_id': self.teacher_subh_id.id,
                                                          'state':  'accept' if self.teacher_subh_id else 'draft',
                                                          'grade_ids': [(6,0, self.grade_subh_ids.ids )],
                                                          'start_date': self.start_date_subh,
                                                          'end_date': self.end_date_subh,
                                                          'is_online': self.is_online_subh,
                                                          'program_id': self.program_subh_id.id,
                                                          'approache_id': self.approache_subh_id.id,
                                                          'error_register': self.error_register_subh,
                                                          'women_or_men' : self.gender,
                                                          'episode_days': [(6,0, self.episode_days_subh_ids.ids )], })
            parent_episode.subh = True

        if self.zuhr:
            episode_zuhr = self.env['mk.episode'].create({'parent_episode': parent_episode.id,
                                                          'selected_period': 'zuhr',
                                                          'zuhr': True,
                                                          'name': parent_episode.name,
                                                          'mosque_id': self.mosque_id.id,
                                                          'academic_id': self.academic_id.id,
                                                          'study_class_id': self.study_class_id.id,
                                                          'teacher_id': self.teacher_zuhr_id.id,
                                                          'state': 'accept' if self.teacher_zuhr_id else 'draft',
                                                          'grade_ids': [(6,0, self.grade_zuhr_ids.ids )],
                                                          'start_date': self.start_date_zuhr,
                                                          'end_date': self.end_date_zuhr,
                                                          'is_online': self.is_online_zuhr,
                                                          'program_id': self.program_zuhr_id.id,
                                                          'approache_id': self.approache_zuhr_id.id,
                                                          'error_register': self.error_register_zuhr,
                                                          'women_or_men': self.gender,
                                                          'episode_days': [(6,0, self.episode_days_zuhr_ids.ids )] })
            parent_episode.zuhr = True

        if self.aasr:
            episode_aasr = self.env['mk.episode'].create({'parent_episode': parent_episode.id,
                                                          'selected_period': 'aasr',
                                                          'aasr': True,
                                                          'name': parent_episode.name,
                                                          'mosque_id': self.mosque_id.id,
                                                          'academic_id': self.academic_id.id,
                                                          'study_class_id': self.study_class_id.id,
                                                          'teacher_id': self.teacher_aasr_id.id,
                                                          'state': 'accept' if self.teacher_aasr_id else 'draft',
                                                          'grade_ids': [(6,0, self.grade_aasr_ids.ids )],
                                                          'start_date': self.start_date_aasr,
                                                          'end_date': self.end_date_aasr,
                                                          'is_online': self.is_online_aasr,
                                                          'program_id': self.program_aasr_id.id,
                                                          'approache_id': self.approache_aasr_id.id,
                                                          'error_register': self.error_register_aasr,
                                                          'women_or_men': self.gender,
                                                          'episode_days': [(6,0, self.episode_days_aasr_ids.ids )] })
            parent_episode.aasr = True

        if self.magrib:
            episode_magrib = self.env['mk.episode'].create({'parent_episode': parent_episode.id,
                                                            'selected_period': 'magrib',
                                                            'magrib': True,
                                                            'name': parent_episode.name,
                                                            'mosque_id': self.mosque_id.id,
                                                            'academic_id': self.academic_id.id,
                                                            'study_class_id': self.study_class_id.id,
                                                            'teacher_id': self.teacher_magrib_id.id,
                                                            'state': 'accept' if self.teacher_magrib_id else 'draft',
                                                            'grade_ids': [(6,0, self.grade_magrib_ids.ids )],
                                                            'start_date': self.start_date_magrib,
                                                            'end_date': self.end_date_magrib,
                                                            'is_online': self.is_online_magrib,
                                                            'program_id': self.program_magrib_id.id,
                                                            'approache_id': self.approache_magrib_id.id,
                                                            'error_register': self.error_register_magrib,
                                                            'women_or_men': self.gender,
                                                            'episode_days': [(6,0, self.episode_days_magrib_ids.ids )]})
            parent_episode.magrib = True

        if self.esha:
            episode_esha = self.env['mk.episode'].create({'parent_episode': parent_episode.id,
                                                          'selected_period': 'esha',
                                                          'esha': True,
                                                          'name': parent_episode.name,
                                                          'mosque_id': self.mosque_id.id,
                                                          'academic_id': self.academic_id.id,
                                                          'study_class_id': self.study_class_id.id,
                                                          'teacher_id': self.teacher_esha_id.id,
                                                          'state': 'accept' if self.teacher_esha_id else 'draft',
                                                          'grade_ids': [(6,0, self.grade_esha_ids.ids )],
                                                          'start_date': self.start_date_esha,
                                                          'end_date': self.end_date_esha,
                                                          'is_online': self.is_online_esha,
                                                          'program_id': self.program_esha_id.id,
                                                          'approache_id': self.approache_esha_id.id,
                                                          'error_register': self.error_register_esha,
                                                          'women_or_men': self.gender,
                                                          'episode_days': [(6,0, self.episode_days_esha_ids.ids )] })
            parent_episode.esha = True

        episode_form = self.env.ref('mk_episode_management.mk_episode_master_form_view')

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'binding_view_types': 'form',
            'view_mode': 'form',
            'res_model': 'mk.episode.master',
            'views': [(episode_form.id, 'form')],
            'view_id': episode_form.id,
            'res_id': parent_episode.id,
            'target': 'current',
        }
