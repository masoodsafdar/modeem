#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class contestStages(models.Model):
    _name = 'contest.stages'

    no       = fields.Integer('Stage number', required=True)
    name     = fields.Char('Name', required=True)
    Start_D  = fields.Date('Stage Start Date', required=True)
    end_D    = fields.Date('Stage End Date', required=True)
    place    = fields.Selection(string='Place',required=True, selection=[('department', 'department'), 
                                                                         ('episode', 'episode')])
    relation = fields.Many2one(string='Relation between stage & contest', comodel_name='contest.preparation', ondelete='cascade')
    stages   = fields.Many2one(string='Relation between stage & calender',  comodel_name='contest.calendar', ondelete='cascade')