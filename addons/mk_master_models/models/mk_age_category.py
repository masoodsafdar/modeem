#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _

    
class MkAgeCategory(models.Model):
    _name = 'mk.age.category'
    _inherit=['mail.thread','mail.activity.mixin']


    @api.depends('from_age','to_age')
    def compute_name(self):
        for rec in self:
            to_age = rec.to_age
            if to_age < 10:
                name = (str(rec.to_age)) +'-' +(str(rec.from_age))+' '+(_('year'))
            else: 
                name = (str(rec.to_age)) +'-' +(str(rec.from_age))+' '+ 'سنة'
            
            rec.name = name
            
    name     = fields.Char(compute="compute_name", string='Name', store=True, tracking=True)
    from_age = fields.Integer('From', tracking=True)
    to_age   = fields.Integer('To',   tracking=True)
