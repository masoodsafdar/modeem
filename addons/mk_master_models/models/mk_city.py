# -*- coding: utf-8 -*-

from odoo import models,fields,api,_

class mak_city(models.Model):
    _name = 'mk.city'
    _description = 'cities'

    name = fields.Char(string='Name')

