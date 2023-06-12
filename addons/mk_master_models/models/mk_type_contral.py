#-*- coding:utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class mk_type_contral(models.Model):
    _name = 'mk.type.contral'
    _description = 'Type Contral'

    name = fields.Char(
        string='Type Contral',
    )