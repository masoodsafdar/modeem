#-*- coding:utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
    
class MkLeave(models.Model):
    _name = 'mk.leave'
        
    name = fields.Char('Name')
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "already exists !"),
    ]