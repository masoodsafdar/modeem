# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.exceptions import UserError, ValidationError


class MqAnnualVacation(models.Model):
    _name = 'mq.annual.vacation'
    
    name         = fields.Char(string='Name vacation', required=True)
    date_from    = fields.Date('Date From')
    date_to      = fields.Date('Date To')
    

class MqTime(models.Model):
    _name = 'mq.time'
    
    name         = fields.Char(string='Name time', required=True)
    time_from    = fields.Float('From')
    time_to      = fields.Float('To')


class episode_programs(models.Model):
    _inherit = 'mk.episode'
    
    is_episode_meqraa   = fields.Boolean(string='Episode Meqraa', default=False)
    riwaya              = fields.Selection([('riwaya1', u'حفص عن عاصم الكوفي'), 
                                            ('riwaya2', u'قالون عن نافع المدني'),
                                            ('riwaya3', u'ورش عن نافع المدني')], string='Riwaya')
    
    
    days_recitation    = fields.Selection([('recitation1', 'Saturday/Monday/Wednesday'),
                                           ('recitation2', 'Sunday/Tuesday/Thursday')], string='Days of recitation')
    
    time_id   = fields.Many2one('mq.time', string='Times')
    
    @api.onchange('days_recitation')
    def on_change_days_recitation(self):
        list_days = []
        if self.days_recitation:
            if self.days_recitation == 'recitation1':
                list_days = [1,3,5]
                self.episode_days = [(6, 0, [])]
                self.episode_days = [(4, x, None) for x in list_days]
            else:
                list_days = [2,4,6]
                self.episode_days = [(6, 0, [])]
                self.episode_days = [(4, x, None) for x in list_days]
            
    @api.onchange('time_id')
    def on_change_time_id(self):
        if self.time_id:
            self.time_from = self.time_id.time_from
            self.time_to = self.time_id.time_to
        else:
            self.time_from = False
            self.time_to = False

    @api.one
    def write(self, vals):
        if 'active' in vals and self.is_episode_meqraa:
            active = vals.get('active')
            if active == False and not self.env.user._is_superuser():
                msg = ' لا يمكنك أرشفة حلقة المقرأة' + '!'
                raise ValidationError(msg)
            else:
                return super(episode_programs, self).write(vals)
        else:
            return super(episode_programs, self).write(vals)

    @api.multi
    def action_assign_students_course_from_episode_multi(self):
        episode_id = self.env['mk.episode'].browse(self.env.context.get('active_id'))
        meqraa_assign_episode_form = self.env.ref('mk_meqraa.view_meqraa_student_request_multi_form')
        is_meqraa = episode_id.is_episode_meqraa
        if is_meqraa:
            return {
                'name': _('تنسيب لحلقة مقرأة'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mk.student.internal_transfer',
                'views': [(meqraa_assign_episode_form.id, 'form')],
                'view_id': meqraa_assign_episode_form.id,
                'target': 'new',
                'context': {'default_episode_assign_id': episode_id.id,
                            'default_type_order': 'assign_ep'}
            }
        else:
            return super(episode_programs, self).action_assign_students_course_from_episode_multi()
