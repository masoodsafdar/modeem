#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from odoo.tools.translate import _


class MkPrograms(models.Model):
    _inherit = 'mk.programs'
    
    is_program_meqraa = fields.Boolean(string='Is program Meqraa', default=False)