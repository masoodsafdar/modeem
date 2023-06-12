# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class get_top_five_student(models.Model):
    _name = 'get.top.five.student'

    name     = fields.Char()
    rate     = fields.Float()
    top_five = fields.Many2one('top.five')

    @api.model
    def get_top_student(self):
        top_students = []
        top_five_students = self.env['get.top.five.student'].search([])
        if top_five_students:
            for student in top_five_students:
                attachment = self.env['ir.attachment'].search([('res_name', '=', student.name),
                                                               ('name', '=', 'image'),
                                                               ('res_model', '=', 'mk.student.register')])
                if attachment:
                    top_students.append({'name':       student.name,
                                         'image_path': attachment.store_fname if attachment else False})
        return top_students


class get_top_five_episode(models.Model):
    _name = 'get.top.five.episode'

    name     = fields.Char()
    rate     = fields.Float()
    top_five = fields.Many2one('top.five')

    @api.model
    def get_top_episode(self):
        top_episodes = []
        top_five_episodes = self.env['get.top.five.episode'].search([])

        if top_five_episodes:
            for episode in top_five_episodes:
                top_episodes.append({'id':   episode.id,
                                     'name': episode.name})

        return top_episodes


class get_top_five_teacher(models.Model):
    _name = 'get.top.five.teacher'

    name     = fields.Char()
    rate     = fields.Float()
    top_five = fields.Many2one('top.five')

    def get_injaz(self,te_id,type_follow,ep_id):
        self._cr.execute("SELECT total , acturaldegree from injaaz_rate(%s,%s,%s);",(te_id,type_follow,ep_id))
        return self._cr.fetchall()

    @api.model
    def get_top_teacher(self):
        _logger.info('')
        query_string = ''' 
                   SELECT get_top_five_teacher.name ,
                   attach.store_fname as image_path
                    FROM  public.get_top_five_teacher ,
                    ir_attachment as attach 
                    WHERE attach.res_name=get_top_five_teacher.name
                    and attach.name='image' and attach.res_model='hr.employee' ; 
                    '''
        self.env.cr.execute(query_string)
        top_techers = self.env.cr.dictfetchall()
        return top_techers

