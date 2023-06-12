# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.tools import pycompat

from odoo.tools.translate import _
from odoo.exceptions import UserError


class ScheduleTest(models.Model):
    _name = 'mk.schedule.test'
    _description = 'Schedule test'

    @api.model
    def get_default_mosque(self):
        mosque_id = self._context.get('mosque_id', False)
        return mosque_id

    # @api.one
    @api.depends('mosque_id','study_class_id','state')
    def _get_episodes(self):
        mosque = self.mosque_id
        mosque_id = mosque.id
        if (not mosque_id) or (mosque_id and not isinstance(mosque_id, pycompat.integer_types)):
            mosque_id = self.mosque_ctx_id.id
        study_class = self.study_class_id
        if study_class:
            self.episod_ids = ()
        if mosque_id and study_class and self.state == 'confirm':
            episodes = self.env['mk.episode'].search([('study_class_id', '=', study_class.id),
                                                      ('mosque_id','=',mosque_id),])
            self.episode_mosq_ids = episodes
        else:
            self.episode_mosq_ids = []

    # @api.one
    @api.depends('episod_ids')
    def _get_day_episode_ids(self):
        days_episode = []
        list_days_ep = []
        days = self.env['mk.work.days'].search([])
        episodes_count = len(self.episod_ids)
        for episode in self.episod_ids:
            for day_episode in episode.episode_days:
                list_days_ep.append(day_episode.id)
        if list_days_ep:
            for day in days:
                count_occ = list_days_ep.count(day.id)
                if count_occ == episodes_count:
                    days_episode.append(day.id)
            self.day_episod_ids = [(6, 0, days_episode)]

    mosque_ctx_id         = fields.Many2one('mk.mosque', default=get_default_mosque)
    mosque_id             = fields.Many2one('mk.mosque',      string='Mosque',   invisible="1", )
    approache_id          = fields.Many2one('mk.approaches',  string='Approach', invisible="1", )
    study_year_id         = fields.Many2one('mk.study.year',  string='Study Year',    required=True)
    study_class_id        = fields.Many2one('mk.study.class', string='Study class',   required=True)
    type_schedule         = fields.Selection([('program', 'Program'),
                                              ('period', 'Period')], string='Schedule type', required=True,    default='program')
    type_org              = fields.Selection([('general', 'General'),
                                              ('mosque', 'Mosque')], string='Organism type', invisible='1')
    period_schedule       = fields.Selection([('week', 'Week'),
                                              ('month', 'Month')],   string='Schedule Periode',             default='month')
    nbr_period            = fields.Integer( string='Number',                                                   default=1)
    episode_mosq_ids      = fields.Many2many('mk.episode','episode_mosque_schedule_test_rel', 'episode_id', 'schedule_test_id',    string='Mosque episodes', compute=_get_episodes, store=True)
    episod_ids            = fields.Many2many('mk.episode', 'episode_schedule_test_rel', 'episode_id', 'schedule_test_id',          string='Episodes')
    day_episod_ids        = fields.Many2many('mk.work.days', string='Episode days', compute=_get_day_episode_ids)
    day_exam_id           = fields.Many2one('mk.work.days',  string='Exam day')
    state                 = fields.Selection([('draft', 'Draft'),
                                            ('confirm', 'Confirm'),
                                            ('done', 'Done')],     string='State',           default='draft')
    day_schedule_test_ids = fields.One2many('mk.schedule.test.day', 'schedule_test_id', string='Schedule tests')


    @api.onchange('study_year_id')
    def change_study_year_id(self):
        self.study_class_id = False

        study_year_id = self.study_year_id.id
        if study_year_id:
            return {'domain': {'study_class_id': [('study_year_id', '=', study_year_id)]}}

    # @api.multi
    def action_confirm(self):
        self.write({'state': 'confirm'})

    # @api.multi
    def action_done(self):
        start_date = self.study_class_id.start_date
        end_date = self.study_class_id.end_date
        type_org = self.env.context.get('type_org', False)
        
        period_schedule = self.period_schedule
        type_schedule = self.type_schedule
        nbr_period = self.nbr_period
        if period_schedule == 'month':
            nbr_period = nbr_period * 4
        day_exam = self.day_exam_id.order
        if day_exam != 0:
            day_exam = day_exam - 1
        else:
            day_exam = 6

        generation_date = []
        generation_date_periode = []
        tests = []
        if type_schedule == 'period':
            if type_org == 'mosque':
                if self.episod_ids and self.day_exam_id:
                    for episode in self.episod_ids:
                        if episode.day_schedule_test_ids:
                            raise UserError(_("لقد تم برمجة اختبارات لهذه الحلقة"))
                        date_start = episode.start_date
                        date_end = episode.end_date
                        the_start_date = datetime.strptime(date_start, '%Y-%m-%d').date()
                        the_end_date = datetime.strptime(date_end, '%Y-%m-%d').date()
                        date_delta = (the_end_date - the_start_date)
                        for x in range((date_delta).days):
                            dd = the_start_date + timedelta(days=x)
                            the_day_f = dd.weekday()
                            if the_day_f == day_exam:
                                generation_date.append(dd)

                        for i in range(1, len(generation_date), nbr_period):
                            generation_date_periode.append(generation_date[i])

                        for date_exam in generation_date_periode:
                            vals = {'schedule_test_id': self.id,
                                    'episode_id': episode.id,
                                    'date_test': date_exam,
                                    'type_schedule': 'period',
                                    'type_org': 'mosque'}
                        tests.append((0, 0, vals))
                        episode.day_schedule_test_ids = tests
                else :
                    raise UserError(_("الرجاء التأكد من وجود الحلقات و يوم الاختبار"))
            elif type_org == 'general':
                the_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                the_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                date_delta = (the_end_date - the_start_date)
                for x in range((date_delta).days):
                    dd = the_start_date + timedelta(days=x)
                    the_day_f = dd.weekday()
                    if the_day_f == 6:
                        generation_date.append(dd)

                for i in range(1, len(generation_date), nbr_period):
                    generation_date_periode.append(generation_date[i])

                for date_exam in generation_date_periode:
                    vals = {'schedule_test_id': self.id,
                            'date_test': date_exam,
                            'date_end': min(date_exam + timedelta(days=6), the_end_date),
                            'type_schedule': 'period',
                            'type_org': 'general'
                            }
                    tests.append((0, 0, vals))
                self.day_schedule_test_ids = tests

        elif type_schedule == 'program':
            if type_org == 'mosque':
                for episode in self.episod_ids:
                    if episode.day_schedule_test_ids:
                        raise UserError(_("لقد تم برمجة اختبارات لهذه الحلقة"))
                    vals = {'schedule_test_id': self.id,
                            'episode_id': episode.id,
                            'date_test': episode.start_date,
                            'type_schedule': 'program',
                            'type_org': 'mosque'
                            }
                    tests.append((0,0,vals))
                    episode.day_schedule_test_ids = tests
            elif type_org == 'general':
                vals = {'schedule_test_id': self.id,
                        'type_schedule': 'program',
                        'type_org': 'general'
                        }
                tests.append((0, 0, vals))
                self.day_schedule_test_ids = tests

        self.write({'state': 'done'})


class ScheduleTestDay(models.Model):
    _name = 'mk.schedule.test.day'
    _description = 'Schedule test day'

    # @api.one
    @api.depends('schedule_test_id')
    def _get_period_schedule(self):
        self.period_schedule = self.schedule_test_id.period_schedule

    # @api.one
    @api.depends('schedule_test_id')
    def _get_number_period(self):
        self.nbr_period = self.schedule_test_id.nbr_period


    schedule_test_id = fields.Many2one('mk.schedule.test',      string='Schedule test')
    episode_id       = fields.Many2one('mk.episode',            string='Episode')
    date_test        = fields.Date(                             string='Date test')
    date_end         = fields.Date(                             string='Date end')
    type_schedule    = fields.Selection([('program', 'Program'),
                                         ('period', 'Period')], string='Schedule type', default='program')
    period_schedule  = fields.Selection([('week', 'Week'),
                                        ('month', 'Month')],    string='Schedule Periode', compute=_get_period_schedule, store=True)
    nbr_period       = fields.Integer(string='Number', compute=_get_number_period, store=True)



