#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class contenst_test_names(models.Model):
    _inherit = 'mk.test.names'
    
    is_contest = fields.Boolean(string='contests')
