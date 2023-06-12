from odoo import models, fields, api, _
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class vehicle_management_line(models.Model):
    _name = 'vehicle.emanagement.line'

    def get_maximum_capacity(self):
        return self.vehicle_ide.vehicle_id.no_of_seats
   
    #vehicle_ide= fields.Many2one ('vehicle.management')
    vehicle_ide = fields.Many2one(string='ids',comodel_name='vehicle.management',ondelete='cascade')
    avilable_seats = fields.Integer(default=get_maximum_capacity)
    work_days= fields.Many2one('mk.work.days', string='vehicle work Days')
    work_periods=fields.Selection([('subh', 'subh'),('zuhr', 'zuhr'),('aasr','aasr'),('magrib','magrib'),('esha','esha')])
    #work_period_subh=fields.Boolean()
    #work_period_zuhr=fields.Boolean()
    #work_period_aasr=fields.Boolean()
    #work_period_magrib=fields.Boolean()
    #work_period_esha=fields.Boolean()
    go_return = fields.Selection(
        string='Go return',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False,
        selection=[('go', 'go'), ('return', 'return')]
    )

    @api.constrains('avilable_seats')
    def avilable_seats_constrain(self):
        for r in self:            
            if r.avilable_seats> r.vehicle_ide.max_capcity:
                raise models.ValidationError('لا يوجد مقاعد شاقرة بهذة المركبة')


 
class vehicle_management(models.Model):
    _name = 'vehicle.management'
    
    # _inherit = 'vehicle.emanagement.line'
    # _columns = {
    # 'vehicle_line':fields.One2many (comodel_name='vehicle.management.line',inverse_name='vehicle_ide')
    #vehicle_line=fields.One2many (comodel_name='vehicle.management.line',inverse_name='vehicle_ide')
    vehicle_id= fields.Many2one(comodel_name='vehicle.records')
    
    max_capcity = fields.Integer( string='capacity', related='vehicle_id.no_of_seats')
    v_lines = fields.One2many( string='lines', comodel_name='vehicle.emanagement.line',inverse_name='vehicle_ide')
    
    


    


