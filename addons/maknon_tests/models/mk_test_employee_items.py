from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from odoo.tools.translate import _

class MkTestEmployee(models.Model):
    _name = 'employee.items'
    _inherit = ['mail.thread']

    name     = fields.Char(string="Name", required=True, track_visibility='onchange')
    total    = fields.Integer(string="total degree",     track_visibility='onchange')
    branches = fields.Many2many("mk.branches.master",    track_visibility='onchange', string="branches")