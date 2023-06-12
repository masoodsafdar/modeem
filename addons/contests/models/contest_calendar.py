#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class contestCalendar(models.Model):
    _name = 'contest.calendar'

    name           = fields.Many2one(string='contest name',   comodel_name='contest.preparation', ondelete='cascade', required=True)
    stage_relation = fields.One2many(string='Stage relation', comodel_name='contest.stages', inverse_name='stages')
    SD             = fields.Date('start Date', readonly=True, related='name.StartD')
    ED             = fields.Date('end Date',   readonly=True, related='name.endD',)

    # on change function hear
    # @api onchange('SD')
    # def _chane_startD(self):
    #   self.SD = self.env.contest.preparation('StartD')
 
    # @api onchange('ED')
    #def _change_endD(self):
    #    self.ED = self.env['preparation']
