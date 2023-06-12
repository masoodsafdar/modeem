#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _


class mk_branch_courses(models.Model):
    _name = 'mk.branch.courses'

    name         = fields.Char('Name')
    num_branch   = fields.Char('Branch No')
    part_from_id = fields.Many2one('mk.parts', string='Part From', ondelete='restrict')
    part_to_id   = fields.Many2one('mk.parts', string='Part To',   ondelete='restrict')
    order        = fields.Selection([('as','Ascanding'),
                                     ('ds','Descanding')], string='Order')
    age_range    = fields.Selection([('op','Open'),
                                     ('limt','Limited')], 'Age Range')
    age_id       = fields.Many2many('mk.age.category', string='Age')  
