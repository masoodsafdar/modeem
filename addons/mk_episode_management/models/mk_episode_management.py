# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from datetime import datetime, date
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class episode_programs(models.Model):
    _inherit = 'mk.episode'

    @api.model
    def archive_seasonal_episode(self):
        episodes = self.env['mk.episode'].search([('study_class_id.is_default', '=', True),
                                                  ('episode_season_id', '!=', False),
                                                  ('is_episode_meqraa', '=', False)], limit=50)
        total = len(episodes)
        i = 0
        list_mk_link = []

        for episode in episodes:
            link_ids = episode.link_ids
            i += 1
            for link_id in link_ids:
                try:
                    link_id.sudo().action_cancel()
                except:
                    list_mk_link.append(link_id.id)
                    continue
            episode.sudo().write({'active': False})

    @api.onchange('women_or_men')
    def initialise_program_id(self):
        self.program_id=False
        self.approache_id=False
        self.episode_path_id=False

    @api.onchange('program_id')
    def initialise_approach_id(self):
        self.approache_id=False
        self.episode_path_id=False

    @api.onchange('approache_id')
    def initialise_path_id(self):
        self.episode_path_id = False

    @api.depends('mosque_id', 'mosque_id.center_department_id')
    def get_department(self):
        for rec in self:
            mosque_id = rec.mosque_id
            rec.department_id = mosque_id.center_department_id.id

    @api.depends('selected_period')
    def get_episode_period(self):
        selected_period = self.selected_period

        if selected_period in ['subh', 'zuhr']:
            self.episode_period = 'morning'

        elif selected_period in ['aasr', 'magrib', 'esha']:
            self.episode_period = 'evening'


    program_id            = fields.Many2one('mk.programs',   string='نوع البرنامج', track_visibility='onchange')
    approache_id          = fields.Many2one('mk.approaches', string='البرنامج' , track_visibility='onchange')
    episode_path_id       = fields.Many2one('mk.path',       string='المسار' ,   track_visibility='onchange')
    department_id         = fields.Many2one('hr.department', string="Department", compute=get_department, store=True , track_visibility='onchange')
    day_schedule_test_ids = fields.One2many('mk.schedule.test.day', 'episode_id', string='Schedule test day')
    is_online             = fields.Boolean('Online', track_visibility='onchange')
    episode_period        = fields.Selection([('morning', 'Morning'),
                                              ('evening', 'Evening')], string='Episode Period', compute='get_episode_period',store=True, track_visibility='onchange')


    # @api.multi
    def draft_validate(self):
        self.write({'state':'draft'})

    # @api.multi
    def reject_validate(self):
        self.write({'state':'reject'})

    # @api.multi
    def accept_validate(self):
        if not self.teacher_id:
            msg = 'لا يمكنك تفعيل الحلقة الرجاء تحديد المعلم'
            raise ValidationError(msg)
        else:
            self.write({'state':'accept'})

    active          = fields.Boolean("Active",default=True)
    # program_archive = fields.One2many("mk.episode.program.archive","episode_id","Episode Program Archive")

    @api.onchange('episode_type')
    def _onchange_episode_type(self):
        self.episode_work = False

    # @api.multi
    def write(self,vals):
        if 'teacher_id' in vals:
            filtered_links = self.link_ids.filtered(lambda r: r.state == 'accept')
            if filtered_links:
                for link in filtered_links:
                    link.preparation_id.write({'name': vals.get('teacher_id')})
            return super(episode_programs, self).write(vals)
        if 'name' in vals and self.is_episode_meqraa == False:
            fmt = '%Y-%m-%d'
            current_date = date.today()
            end_date = (datetime.strptime(self.study_class_id.end_date, fmt)).date()

            if current_date > end_date:
                raise ValidationError(_('لا يمكنك تعديل إسم الحلقة بعد انتهاء الفصل الدراسي'))
            else:
                return super(episode_programs, self).write(vals)
        # else:
        #     if 'program_id' in vals:
        #         archive_obj=self.env['mk.episode.program.archive']
        #         archive_obj.create({'episode_id':self.id,
        #                             'academic_id':self.academic_id.id,
        #                             'study_class_id':self.study_class_id.id,
        #                             'program_id':vals['program_id']})
        return super(episode_programs, self).write(vals)

    @api.model
    def get_episode_type_by_mosque(self,mosque_id):
        types =[]
        episode_types = []
        try:
            mosque_id = int(mosque_id)
        except:
            pass
        mosque_episodes = self.env['mk.episode'].sudo().search([('mosque_id', '=', mosque_id),
                                                                ('state', 'in', ['accept','draft']),
                                                                ('active', '=', True),
                                                                ('program_id', '!=', False)])
        for episode in mosque_episodes:
            episode_type = episode.program_id
            if episode_type.id not in types:
                types += [episode_type.id]
                episode_types += [{'id': episode_type.id,
                                   'name': episode_type.name }]
        return str(episode_types)

    def update_episode_name(self):
        episode_form = self.env.ref('mk_episode_management.wizard_update_episode_name_form')
        return {
            'name': _('Update episode name'),
            'type': 'ir.actions.act_window',
            'binding_view_types': 'form',
            'view_mode': 'form',
            'res_model': 'mk.update.episode.name',
            'views': [(episode_form.id, 'form')],
            'view_id': episode_form.id,
            'target': 'new',
            'context': {'default_episode_id': self.id, 'default_name': self.name}
        }

    # @api.multi
    def update_period_wizard_action(self):
        update_form = self.env.ref('mk_episode_management.period_form_wizard')

        vals = {
            'name': _(' تغيير فترة الحلقة '),
            'type': 'ir.actions.act_window',
            'binding_view_types': 'form',
            'view_mode': 'form',
            'res_model': 'episode.update.periode.wizard',
            'views': [(update_form.id, 'form')],
            'view_id': update_form.id,
            'context': {'default_updated_period': self.selected_period,
                        'default_episode_id': self.id},
            'target': 'new',
        }
        return vals


class Wizard_update_episode_name(models.TransientModel):
    _name = 'mk.update.episode.name'
    _description = 'Update episode name'

    name = fields.Char(string='الاسم', required=True)

    def action_update_episode_name(self):
        episode = self.env['mk.episode'].search([('id', '=', self.env.context.get('default_episode_id'))], limit=1)
        episode.parent_episode.write({'name': self.name})
