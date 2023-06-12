# -*- coding: utf-8 -*-

from odoo import models,fields,api,_

class mak_district(models.Model):
    _name = 'mk.district'
    _description = 'District'

    name = fields.Char(string='Name')
    area_id = fields.Many2one(
        'mk.area',string='Area'
    )

    center_department_id = fields.Many2one('hr.department', string='Center')
