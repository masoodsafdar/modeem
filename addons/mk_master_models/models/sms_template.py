# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.osv import osv
from datetime import datetime
from odoo.exceptions import Warning
class sms_template(models.Model):
    _name = 'mk.sms_template'
    # _inherit=['mail.thread','mail.activity.mixin']
    # _description = u'sms_template'
    _inherit=['mail.thread','mail.activity.mixin']
    _description = 'SMS Template'  

    name     = fields.Char(string='Name',     required=True, translate=True, tracking=True)
    sms_text = fields.Text(string='Sms text', required=True, translate=True, tracking=True)
    code     = fields.Char(string='Code', required=True, tracking=True)