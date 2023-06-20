from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from odoo.tools.translate import _

class MkTestEmployee(models.Model):
    _name = 'employee.items'
    _inherit=['mail.thread','mail.activity.mixin']

    name     = fields.Char(string="Name", required=True, tracking=True)
    total    = fields.Integer(string="total degree",     tracking=True)
    branches = fields.Many2many("mk.branches.master",    tracking=True, string="branches")