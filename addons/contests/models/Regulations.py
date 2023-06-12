#-*- coding:utf-8 -*-


from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError

class Regulations(models.Model):
    _name = 'regulations'

    name = fields.Char(string='regulation name' ,  required=True,)
    no   = fields.Integer(string='regulation no' , required=True,)
