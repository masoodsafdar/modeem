#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class mk_work_days(models.Model):
    _name = 'mk.work.days'
    _inherit = ['mail.thread']
    _order = 'order asc'
    
    order  = fields.Integer('Order',  track_visibility='onchange')
    name   = fields.Char('Name',      track_visibility='onchange')
    active = fields.Boolean('Active', track_visibility='onchange', default=True)

    # @api.one
    def unlink(self):
        try:
            super(mk_work_days, self).unlink()
        except:
            raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))

    @api.model
    def student_transport_episode_days(self, episode_id):
        try:
            episode_id = int(episode_id)
        except:
            pass

        query_string = ''' 
               select id, name
               from mk_work_days 
               left join mk_episode_mk_work_days_rel 
               on mk_episode_mk_work_days_rel.mk_work_days_id=mk_work_days.id
               where mk_episode_id={} order by id;
               '''.format(episode_id)

        self.env.cr.execute(query_string)
        episode_days = self.env.cr.dictfetchall()
        return episode_days
