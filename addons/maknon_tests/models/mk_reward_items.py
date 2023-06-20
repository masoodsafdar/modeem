# -*- coding: utf-8 -*-
from odoo import models, fields, api

    
class TestPassingItems(models.Model):
    _name = 'mk.reward.items'
    _inherit=['mail.thread','mail.activity.mixin']

    #Relational  fields
    active     = fields.Boolean(string="active", default=True, groups="maknon_test2.group_reward_items_archives", tracking=True)
    age_groups = fields.Many2many("mk.grade",           string="Age gruops")	
    branches   = fields.Many2many("mk.branches.master", string="branches")
    # Primary Fields
    reward_type  = fields.Selection([('certificate',      'Certificate'),
                                     ('certificate_cash', 'Certificate + Cash')], string="Reward Type", default='certificate', tracking=True)
    appreciation = fields.Selection([('excellent','Excellent'),
                                     ('v_good',     'Very good'),
                                     ('good',       'Good'),
                                     ('acceptable', 'Acceptable'),
                                     ('fail',       'Fail')], string="appreciation", tracking=True)

    amount       = fields.Float(string="amount", tracking=True)
    age_fillter  = fields.Selection([('open',  'Open'),
                                     ('close', 'Close')], string="Age Fillter", default="open", tracking=True)
