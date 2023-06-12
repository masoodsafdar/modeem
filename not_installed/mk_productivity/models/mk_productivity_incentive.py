# -*- coding: utf-8 -*-
from openerp import models,fields,api,_
from odoo.exceptions import ValidationError

class MkProductivityIncentive(models.Model):
    _name ='mk.productivity_incentive'
    _description ='productivity incentive'
    _rec_name = 'name'

    @api.one
    @api.depends('incentive_id','type_episode_id')
    def compute_name(self):
        incentive = self.incentive_id.name
        type_episode = self.type_episode_id.name

        if incentive and type_episode:
            self.name = type_episode + '/' + incentive or ''

    type_mark       = fields.Selection(string="Mark", selection=[('perfect', 'Perfect'),
                                                                 ('excellent', 'Excellent'),
                                                                 ('very good', 'Very Good'),
                                                                 ('good', 'Good'),
                                                                 ('low', 'Low'),], required=True)
    min_nbr_part    = fields.Integer(string="Minimum number part")
    max_nbr_part    = fields.Integer(string="Maximum number part")
    name            = fields.Char(compute="compute_name", string="Name", store=True)
    incentive_id    = fields.Many2one("mk.incentive",     string="Incentive",   required=True)
    type_episode_id = fields.Many2one("mk.episode_type",  string="Episode type",required=True)

    @api.constrains('min_nbr_part','max_nbr_part','type_episode_id')
    def check_min_max_incentive_parts(self):
        episode_type_incentives = self.env['mk.productivity_incentive'].search([('type_episode_id','=', self.type_episode_id.id)])
        for incentive in episode_type_incentives:
            incentive_check = self.env['mk.productivity_incentive'].search([('min_nbr_part', '>=', incentive.min_nbr_part),
                                                                            ('max_nbr_part','<=',incentive.max_nbr_part)],limit=1)
            if incentive_check:
                return
                #raise ValidationError(_(' Min/Max parts must be different from others in the same episode type'))

class MkIncentive(models.Model):
    _name ='mk.incentive'
    _description ='Incentive'
    _rec_name='name'

    name = fields.Char(string="Incentive", required=True, )
