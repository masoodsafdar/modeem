# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)
    
class TestEvaluationItems(models.Model):
    _name = 'mk.evaluation.items'
    _inherit = ['mail.thread']

    discount_items = fields.One2many("mk.discount.item","evaluation_item","discount items")
    branches       = fields.Many2many("mk.branches.master", string="branches")
    name           = fields.Char(   string="Name",         required="1", track_visibility='onchange')
    total          = fields.Integer(string="Total degree", required="1", track_visibility='onchange')
    part_discount  = fields.Boolean(string="full discount",              track_visibility='onchange')
    active         = fields.Boolean(string="active", default=True, groups="maknon_tests.group_evaluation_items_archives", track_visibility='onchange')

    @api.model
    def list_evaluation_items(self):
        query_string = ''' 
               SELECT id, name
               From mk_evaluation_items
               WHERE active=True;
               '''
        self.env.cr.execute(query_string)
        list_evaluation_items = self.env.cr.dictfetchall()
        return list_evaluation_items

class TestDiscountItems(models.Model):
    _name='mk.discount.item'

    name             = fields.Char( string="Name")
    amount           = fields.Float(string="Amount")
    evaluation_item  = fields.Many2one("mk.evaluation.items", "evaluation item")
    allowed_discount = fields.Integer(string="allowed discount")