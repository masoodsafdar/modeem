# -*- coding: utf-8 -*-
from odoo import models, fields, api

class episode_programs(models.Model):
    _name = 'mk.episode'
    
    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """

    @api.one
    def draft_validate(self):
        self.write({'state':'draft'})
        
    @api.one
    def reject_validate(self):
        self.write({'state':'reject'})
        
    @api.one
    def accept_validate(self):
        self.write({'state':'accept'})
