# -*- coding: utf-8 -*-

from odoo import models,fields,api,_

class mak_area(models.Model):
    _name = 'mk.area'
    _description = 'Areas'

    name = fields.Char(string='Name')
    city_id = fields.Many2one(
        'mk.city',string='City'
    )


