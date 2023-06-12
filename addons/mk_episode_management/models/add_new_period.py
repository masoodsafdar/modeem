#-*- coding:utf-8 -*-
from odoo import models, fields, api


class new_period_wizerd(models.TransientModel):
    _name = 'new.period'
    
    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """
    
    episode_id      = fields.Many2one('mk.episode.master', string='Episode')
    teacher_id      = fields.Many2one('hr.employee',       string='Teacher', domain=[('category2','=','teacher')])
    episode_type    = fields.Many2one('mk.episode_type',   string='Episode Type')
    selected_period = fields.Selection([('subh', 'subh'), 
                                        ('zuhr', 'zuhr'),
                                        ('aasr','aasr'),
                                        ('magrib','magrib'),
                                        ('esha','esha')], string='period')

    # @api.one
    def yes(self):
        master_episode = self.episode_id
        selected_period = self.selected_period 
               
        if master_episode:
            vals = {'name':            master_episode.name,                    
                    'academic_id':     master_episode.academic_id.id,
                    'study_class_id':  master_episode.study_class_id.id,
                    'mosque_id':       master_episode.mosque_id.id,
                    'selected_period': selected_period,
                    'teacher_id':      self.teacher_id.id,
                    'episode_type':    self.episode_type.id}
            
            vals_write = {}
            
            if selected_period == 'subh':
                vals.update({'subh': True})                    
                vals_write.update({'subh': True})
                
            elif self.selected_period == 'zuhr':                
                vals.update({'zuhr': True})                    
                vals_write.update({'zuhr': True})
                                
            elif selected_period == 'aasr':
                vals.update({'aasr': True})                    
                vals_write.update({'aasr': True})
                
            elif selected_period == 'magrib':
                vals.update({'magrib': True})                    
                vals_write.update({'magrib': True})
                
            elif selected_period == 'esha':
                vals.update({'esha': True})                    
                vals_write.update({'esha': True})

            episode = self.env['mk.episode'].create(vals)
            
            if episode:
                vals_write.update({'episode_ids': [(4, episode.id)]})
                master_episode.write(vals_write)
