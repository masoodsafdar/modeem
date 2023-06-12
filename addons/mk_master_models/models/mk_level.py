#-*- coding:utf-8 -*-


from odoo import models, fields, api
from datetime import datetime
    
class MkLevel(models.Model):
    _name = 'mk.level'
    _description = 'Student Level'
        
    name = fields.Char('Name')
    

