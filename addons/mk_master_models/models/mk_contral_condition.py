#-*- coding:utf-8 -*-
import re

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class mk_contral_condition(models.Model):
    _name = 'mk.contral.condition'
    _inherit=['mail.thread','mail.activity.mixin']
    _description = 'Contral Condition'
    _rec_name = 'type_id'

    type_id         = fields.Many2one('mk.type.contral', string='Type', tracking=True)
    address_contral = fields.Char('Address Contral', tracking=True)
    order           = fields.Char('Order',           tracking=True)
    note            = fields.Html('Text/Contral',    tracking=True)
    active          = fields.Boolean('Active',       tracking=True)
    check_episode   = fields.Boolean('Episodes',     tracking=True)
    check_courses   = fields.Boolean('Intensive Courses', tracking=True)
    check_summer    = fields.Boolean('Summer Courses',    tracking=True)
    check_test      = fields.Boolean('Tests',        tracking=True)
    check_compet    = fields.Boolean('Competitions', tracking=True)
    categ_type      = fields.Selection([('male', 'رجالية'),
                                        ('female', 'نسائية')], string="رجالية/نسائية", tracking=True)
    course_request_type      = fields.Selection(string="نوع الدورة", selection=[('quran_day', 'Quran day'),
                                                                                ('intensive_course', 'Intensive course'),
                                                                                ('ramadan_course', 'Ramadan course')], default='intensive_course', tracking=True)

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

