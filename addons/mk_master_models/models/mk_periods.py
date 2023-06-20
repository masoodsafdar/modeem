#-*- coding:utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.tools.translate import _
from odoo.exceptions import Warning, ValidationError

    
class MkPeriods(models.Model):
    _name = 'mk.periods'
    _inherit=['mail.thread','mail.activity.mixin']

        
    # @api.multi
    def unlink(self):
        try:
            super(MkPeriods, self).unlink()
        except:
            raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))

    @api.onchange('company_id')
    def onchange_company_name(self):
        if self.company_id:self.name = ('الفترات' +('-'+self.company_id.name)or '')

    company_id       = fields.Many2one('res.company', string="Company", default=lambda self:self.env.user.company_id.id, tracking=True)
    name             = fields.Char('Name', tracking=True)
    subh_period      = fields.Boolean('Subh Period', tracking=True)
    subh_period_from = fields.Float('From Hour', tracking=True)
    subh_period_to   = fields.Float('To Hour', tracking=True)
    
    zuhr_period      = fields.Boolean('Zuhr Period', tracking=True)
    zuhr_period_from = fields.Float('From Hour', tracking=True)
    zuhr_period_to   = fields.Float('To Hour', tracking=True)
    
    aasr_period      = fields.Boolean('Aasr Period', tracking=True)
    aasr_period_from = fields.Float('From Hour', tracking=True)
    aasr_period_to   = fields.Float('To Hour', tracking=True)
    
    magrib_period      = fields.Boolean('Magrib Period', tracking=True)
    magrib_period_from = fields.Float('From Hour', tracking=True)
    magrib_period_to   = fields.Float('To Hour', tracking=True)
    
    esha_period      = fields.Boolean('Esha Period', tracking=True)
    esha_period_from = fields.Float('From Hour', tracking=True)
    esha_period_to   = fields.Float('To Hour', tracking=True)
     
    

