from odoo import models,fields,api
from langdetect import detect
from odoo.tools.translate import _
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)

class mk_gateway_configuration(models.Model):
    _name = 'mk.smsclient.config'
    # vals {'subject','body_html','email_to'}
    
    name         = fields.Char(string='Name')
    url          = fields.Char(string='Url',      required=True, size=50)
    user         = fields.Char(string='User',     required=True, size=50)
    sender       = fields.Char(string='sender',   required=True, size=50)
    password     = fields.Char(string='password', required=True, size=50)
    other        = fields.Char(string='other',                   size=50)
    to           = fields.Char(string='to',       required=True, size=50)
    message      = fields.Char(string='Message',  required=True, size=50)
    msg_url      = fields.Text(string='Message Url')
    time_send    = fields.Char(string='Time send')
