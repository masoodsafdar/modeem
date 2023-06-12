#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class MKUserGuide(models.Model):
    _name = 'mk.user.guide'

    sequence    = fields.Integer()
    name        = fields.Char('module name')
    info        = fields.One2many('mk.user.guide.line','info_id')
    active      = fields.Boolean(string="Active",default=True)
    portal_true = fields.Boolean(string="portal_true",default=False)

    @api.model
    def get_model(self):
        user_guides = self.env['mk.user.guide'].search_read(domain=['|', ('active', '=', True),
                                                                         ('active', '=', False)], fields=['id', 'name'])
        return user_guides


class MKUserGuideLine(models.Model):
    _name = 'mk.user.guide.line'

    sequence    = fields.Integer()
    name        = fields.Char()
    description = fields.Text()
    attachment  = fields.Many2many(comodel_name='ir.attachment')
    video       = fields.Char()
    info_id     = fields.Many2one('mk.user.guide')

    @api.model
    def get_lines(self, model_id):
        user_guide_lines = self.env['mk.user.guide.line'].search_read(domain=[('info_id', '=', int(model_id))], fields=['id', 'name'])
        return user_guide_lines

    @api.model
    def get_line(self, line_id):
        try:
            line_id = int(line_id)
        except:
            pass

        query_string = ''' 
                        select guide.name,
                        guide.description ,
                        guide.video,
                        atach.ir_attachment_id 
                        from mk_user_guide_line as guide, 
                        ir_attachment_mk_user_guide_line_rel as atach
                        where guide.id=atach.mk_user_guide_line_id and id={} ; '''.format(line_id)
        self.env.cr.execute(query_string)
        lines = self.env.cr.dictfetchall()
        return lines

