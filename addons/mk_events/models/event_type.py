# -*- coding: utf-8 -*-

from odoo import models, fields, api

class mk_events_configuration(models.Model):
    _inherit = 'event.type'

#     name = fields.Char()
    no = fields.Integer(string="event number")
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100