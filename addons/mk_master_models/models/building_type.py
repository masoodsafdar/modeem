# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.osv import osv
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
from random import randint
import logging
_logger = logging.getLogger(__name__)

class mk_building_type(models.Model):
    _name="mk.building.type"
    _inherit=['mail.thread','mail.activity.mixin']

    name   = fields.Char("Name", required=True,     tracking=True)
    active = fields.Boolean("Active" ,default=True, tracking=True)
    code   = fields.Char(string="Code", tracking=True, copy=False)

    _sql_constraints = [('code_uniq', 'unique(code)', 'The building type code must be unique !')]

    @api.model
    def create(self, values):
        sequence = self.env['ir.sequence'].get('mk.building.type.serial')
        values['code'] = sequence
        return super(mk_building_type, self).create(values)

    @api.model
    def get_building_type(self):
        building_types = self.env['mk.building.type'].search(['|', ('active', '=', True),
                                                                   ('active', '=', False)])
        item_list = []
        if building_types:
            for type in building_types:
                item_list.append({'id': type.id,
                                  'name': type.name})
        return item_list
