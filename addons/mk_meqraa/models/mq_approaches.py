#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from num2words import num2words
from odoo.tools.translate import _


class MkApproaches(models.Model):
    _inherit = 'mk.approaches'
    
    is_approache_meqraa = fields.Boolean(string='Is approache Meqraa', default=False)