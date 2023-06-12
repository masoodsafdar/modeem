# -*- coding: utf-8 -*-
from odoo.tools import odoo,image,image_colorize, image_resize_image_big
#from odoo import models, api, fields
#from wand.image import Image
from odoo import tools
from odoo import models,fields,api,_
from odoo.osv import osv
from datetime import datetime
from odoo.exceptions import Warning, ValidationError


class mk_news_events(models.Model):
    _inherit = 'mk.news'
    
    contest = fields.Many2one("contest.preparation",string="contest")