# -*- coding: utf-8 -*-

from odoo import models,fields,api,_

class mk_campus(models.Model):
    _name ='mk.campus'
    _description ='Campus'

    name =fields.Char(string='Campus')
    company_id = fields.Many2one('res.company', string='Company')

