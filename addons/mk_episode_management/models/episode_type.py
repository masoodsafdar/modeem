# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.osv import osv
from odoo.exceptions import Warning
from odoo.exceptions import UserError


class mk_episode_type(models.Model):
    _inherit = 'mk.episode_type'
    
    type_task_ids  = fields.One2many("mk.epsoide.works", inverse_name="type_episode_id", string="Episode task type")
    type_categ_ids = fields.Many2many('mk.grade',string='Type categories', domain=[('is_episode','=',True)])
    minimum        = fields.Integer(string='Minimum',              tracking=True)
    parts_no       = fields.Integer(string='Parts no for student', tracking=True)
    performance    = fields.One2many('mk.performance', inverse_name='episode_type', string='Performance')
    

class performance(models.Model):
    _name = 'mk.performance'
    # _inherit=['mail.thread','mail.activity.mixin']
    # _description = u'performance'
    _inherit=['mail.thread','mail.activity.mixin']
    _description = 'Performance'
    _rec_name = 'name'
    _order = 'name ASC'

    name       = fields.Char('Name', required=True, translate=True, tracking=True)
    min_degree = fields.Integer('Minimum degree', tracking=True)
    max_degree = fields.Integer('Maximum degree', tracking=True)
    rate       = fields.Selection([('best',      'best'),
                                   ('excellent', 'excellent'), 
                                   ('verygood',  'very good'),
                                   ('good',      'good'),
                                   ('low',       'low')], string='rate', tracking=True)
    episode_type = fields.Many2one('mk.episode_type', string='Episode type', tracking=True)
    