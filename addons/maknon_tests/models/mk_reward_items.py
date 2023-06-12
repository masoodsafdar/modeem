# -*- coding: utf-8 -*-
from odoo import models, fields, api

    
class TestPassingItems(models.Model):
    _name = 'mk.reward.items'
    _inherit = ['mail.thread']

    #Relational  fields
    active     = fields.Boolean(string="active", default=True, groups="maknon_test2.group_reward_items_archives", track_visibility='onchange')
    age_groups = fields.Many2many("mk.grade",           string="Age gruops")	
    branches   = fields.Many2many("mk.branches.master", string="branches")
    # Primary Fields
    reward_type  = fields.Selection([('certificate',      'Certificate'),
                                     ('certificate_cash', 'Certificate + Cash')], string="Reward Type", default='certificate', track_visibility='onchange')
    appreciation = fields.Selection([('excellent','Excellent'),
                                     ('v_good',     'Very good'),
                                     ('good',       'Good'),
                                     ('acceptable', 'Acceptable'),
                                     ('fail',       'Fail')], string="appreciation", track_visibility='onchange')

    amount       = fields.Float(string="amount", track_visibility='onchange')
    age_fillter  = fields.Selection([('open',  'Open'),
                                     ('close', 'Close')], string="Age Fillter", default="open", track_visibility='onchange')
