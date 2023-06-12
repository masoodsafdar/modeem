#-*- coding:utf-8 -*-
import re

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class mk_contral_condition(models.Model):
    _name = 'mk.contral.condition'
    _inherit = ['mail.thread']
    _description = 'Contral Condition'
    _rec_name = 'type_id'

    type_id         = fields.Many2one('mk.type.contral', string='Type', track_visibility='onchange')
    address_contral = fields.Char('Address Contral', track_visibility='onchange')
    order           = fields.Char('Order',           track_visibility='onchange')
    note            = fields.Html('Text/Contral',    track_visibility='onchange')
    active          = fields.Boolean('Active',       track_visibility='onchange')
    check_episode   = fields.Boolean('Episodes',     track_visibility='onchange')
    check_courses   = fields.Boolean('Intensive Courses', track_visibility='onchange')
    check_summer    = fields.Boolean('Summer Courses',    track_visibility='onchange')
    check_test      = fields.Boolean('Tests',        track_visibility='onchange')
    check_compet    = fields.Boolean('Competitions', track_visibility='onchange')
    categ_type      = fields.Selection([('male', 'رجالية'),
                                        ('female', 'نسائية')], string="رجالية/نسائية", track_visibility='onchange')
    course_request_type      = fields.Selection(string="نوع الدورة", selection=[('quran_day', 'Quran day'),
                                                                                ('intensive_course', 'Intensive course'),
                                                                                ('ramadan_course', 'Ramadan course')], default='intensive_course', track_visibility='onchange')

    @api.model
    def get_condition_control(self):
        contral_condition = self.env['mk.contral.condition'].search([('check_episode', '=', True)], limit=1)
        condition = []
        if contral_condition:
            note = re.sub('<.*?>', '', contral_condition.note)
            condition.append({'id':   contral_condition.id,
                              'note': note})
        return condition

    @api.model
    def conditions_episode(self):
        query_string = ''' 
                  SELECT note
                  FROM mk_contral_condition
                  WHERE active=True AND check_episode=True
                  '''
        self.env.cr.execute(query_string)
        conditions_episode = self.env.cr.dictfetchall()
        return conditions_episode

