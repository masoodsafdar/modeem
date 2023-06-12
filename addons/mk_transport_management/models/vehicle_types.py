from odoo import models, fields, api
from odoo.tools.translate import _

class vehicle_types(models.Model):
    _name = 'vehicle.types'
    
    #vehicle_ide= field_name = fields.Many2one(comodel_name='vehicle.records')
    name =fields.Char()
    code =fields.Char()
    