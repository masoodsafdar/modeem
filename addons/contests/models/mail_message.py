
from odoo import api, fields, models, _
from lxml import etree
from lxml.builder import E
from odoo.addons.base.res import res_users
import re
from odoo.exceptions import ValidationError

import logging


class Message(models.Model):
    _inherit = 'mail.message'

    subtype = fields.Many2one('mail.message', string='Last Seen')