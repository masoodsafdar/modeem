# -*- coding: utf-8 -*-
from openerp import models,fields,api,_

class MkEpisodeType(models.Model):
    _inherit = 'mk.episode_type'
    _rec_name = 'name'

    type_test      = fields.Selection(string="Test type", selection=[('parts',  'Parts'),
                                                                    ('final', 'Final'),
                                                                    ('parts_final', 'Parts and Final'),
                                                                    ('contest', 'Contest'),
                                                                    ('diploma', 'Diploma')])
    episode_ids   = fields.One2many("mk.episode",                inverse_name="episode_type",    string="Episodes",   ondelete='cascade')
    incentive_ids = fields.One2many("mk.productivity_incentive", inverse_name="type_episode_id", string="Incentives", ondelete='cascade')