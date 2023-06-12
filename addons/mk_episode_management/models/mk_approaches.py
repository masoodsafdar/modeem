# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class mk_approaches(models.Model):
    _inherit = 'mk.approaches'
    
    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """

    test_schedule_ids = fields.One2many('mk.schedule.test', 'mosque_id', string='Schedule test')
