# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class UpdateEpisodeTime(models.TransientModel):
    _name = 'update.time'
    _description = 'Update episode time'
    
    episode_id  = fields.Many2one('mk.episode', string="Episode")
    time_id     = fields.Many2one('mq.time',    string="الفترة", required=True)
    update_date = fields.Date('Update Date', required=True)

    def update_episode_time(self):
        episode_id = self.episode_id
        time_id = self.time_id
        update_date = self.update_date
        sessions = self.env['mq.session'].search([('episode_id', '=', episode_id.id),
                                                  ('status', '=', 'planned'),
                                                  ('start_date', '>=', update_date)])
        if sessions:
            episode_id.write({'time_id': time_id.id})
            for session in sessions:
                session.write({'time_session_id': time_id.id})
        return True