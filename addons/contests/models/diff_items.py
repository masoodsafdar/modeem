#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class contenst_diff_items(models.Model):
    _name = 'contest.diff.items'
    
    name       = fields.Char(required="1")
    contest_id = fields.Many2one("contest.preparation",string="contest")
