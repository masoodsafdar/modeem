# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.osv import osv
from odoo.exceptions import Warning
from odoo.exceptions import UserError


class mk_episode_type(models.Model):
    _inherit = 'mk.episode_type'
    
    type_task_ids  = fields.One2many("mk.epsoide.works", inverse_name="type_episode_id", string="Episode task type")
    type_categ_ids = fields.Many2many('mk.grade',string='Type categories', domain=[('is_episode','=',True)])
    minimum        = fields.Integer(string='Minimum',              track_visibility='onchange')
    parts_no       = fields.Integer(string='Parts no for student', track_visibility='onchange')
    performance    = fields.One2many('mk.performance', inverse_name='episode_type', string='Performance')
    

class performance(models.Model):
    _name = 'mk.performance'
    _inherit = ['mail.thread']
    _description = u'performance'

    _rec_name = 'name'
    _order = 'name ASC'

    name       = fields.Char('Name', required=True, index=True, size=50, translate=True, track_visibility='onchange')
    min_degree = fields.Integer('Minimum degree', track_visibility='onchange')
    max_degree = fields.Integer('Maximum degree', track_visibility='onchange')
    rate       = fields.Selection([('best',      'best'),
                                   ('excellent', 'excellent'), 
                                   ('verygood',  'very good'),
                                   ('good',      'good'),
                                   ('low',       'low')], string='rate', track_visibility='onchange')
    episode_type = fields.Many2one('mk.episode_type', string='Episode type', track_visibility='onchange')
    