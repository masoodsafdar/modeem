# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
from odoo.exceptions import ValidationError

class MkProductivity(models.Model):
    _name ='mk.productivity'
    _description ='productivity Management'
    _rec_name= 'name'

    @api.one
    @api.depends('teacher_id','study_year_id')
    def compute_name(self):
        teacher = self.teacher_id.name
        study_year = self.study_year_id.name
        if teacher and study_year:
            self.name = 'انتاجية المعلم/ المعلمة ' + teacher + ' ل ' + study_year

    @api.one
    @api.depends('study_year_id','teacher_id')
    def get_episodes(self):
        study_year_id = self.study_year_id
        teacher_id = self.teacher_id
        if study_year_id and teacher_id:
            self.episode_ids = self.env['mk.episode'].search([('academic_id', '=', study_year_id.id),
                                                             ('teacher_id','=',self.teacher_id.id),])

    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirmed'})

    @api.multi
    def action_done(self):
        productivity = []
        episode_types = []
        episodes_list =[]
        for episode in self.episode_ids:
            for episode_type in episode.episode_type:
                if episode_type.id not in episode_types:
                    episode_types.append(episode_type.id)
        for type in episode_types:
            for episode in self.episode_ids:
                if episode.episode_type.id == type:
                    episodes_list.append(episode.id)
            vals = {'productivity_id': self.id,
                    'episode_ids': episodes_list,
                    'type_episode_id': type}
            productivity.append((0, 0, vals))
        self.episode_productivity_ids = productivity
        self.write({'state': 'prod_count_done'})

    teacher_id               = fields.Many2one("hr.employee",   string="Teacher",    required=True, domain=[('category','=','teacher')])
    study_year_id            = fields.Many2one("mk.study.year", string="Study year", required=True)
    name                     = fields.Char(string="Name",                        compute="compute_name", store=True)
    episode_ids              = fields.Many2many('mk.episode', string='Episodes', compute="get_episodes", store=True, )
    episode_productivity_ids = fields.One2many("mk.episode_productivity", inverse_name="productivity_id", string="Episode productivities", ondelete='cascade')
    state                    = fields.Selection(string="State", selection=[('draft', 'Draft'),
                                                                           ('confirmed', 'Confirmed'),
                                                                           ('prod_count_done', 'productivity count done')], default='draft', required=True )

    # @api.constrains('teacher_id','study_year_id')
    # def check_existance(self):
    #     productivity = self.env['mk.productivity'].search([('teacher_id', '=', self.teacher_id.id),
    #                                                         ('study_year_id','=',self.study_year_id.id)],limit=1)
    #     if productivity:
    #         raise ValidationError(_(' Productivity for the same teacher and study year already exist'))







