#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class contenst_fields(models.Model):
    _name = 'mk.contenst.fields'
    
    name           = fields.Char(required="1")
    field_item_ids = fields.One2many("mk.fields.items","field_id","field items")


class contenst_fields_items(models.Model):
    _name = 'mk.fields.items'
    
    name       = fields.Char(required="1")
    field_id   = fields.Many2one("mk.contenst.fields",string="fields")
