#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class NominationTypes(models.Model):
    _name = 'nomination.types'
    
    name = fields.Char('nomination type name' , required=True,)
    code = fields.Integer('nomination code' ,   required=True,)
