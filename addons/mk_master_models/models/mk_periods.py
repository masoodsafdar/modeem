#-*- coding:utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.tools.translate import _
from odoo.exceptions import Warning, ValidationError

    
class MkPeriods(models.Model):
    _name = 'mk.periods'
    _inherit = ['mail.thread']

        
    # @api.multi
    def unlink(self):
        try:
            super(MkPeriods, self).unlink()
        except:
            raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))

    @api.onchange('company_id')
    def onchange_company_name(self):
        if self.company_id:self.name = ('الفترات' +('-'+self.company_id.name)or '')

    company_id       = fields.Many2one('res.company', string="Company", default=lambda self:self.env.user.company_id.id, track_visibility='onchange')
    name             = fields.Char('Name', track_visibility='onchange')
    subh_period      = fields.Boolean('Subh Period', track_visibility='onchange')
    subh_period_from = fields.Float('From Hour', track_visibility='onchange')
    subh_period_to   = fields.Float('To Hour', track_visibility='onchange')
    
    zuhr_period      = fields.Boolean('Zuhr Period', track_visibility='onchange')
    zuhr_period_from = fields.Float('From Hour', track_visibility='onchange')
    zuhr_period_to   = fields.Float('To Hour', track_visibility='onchange')
    
    aasr_period      = fields.Boolean('Aasr Period', track_visibility='onchange')
    aasr_period_from = fields.Float('From Hour', track_visibility='onchange')
    aasr_period_to   = fields.Float('To Hour', track_visibility='onchange')
    
    magrib_period      = fields.Boolean('Magrib Period', track_visibility='onchange')
    magrib_period_from = fields.Float('From Hour', track_visibility='onchange')
    magrib_period_to   = fields.Float('To Hour', track_visibility='onchange')
    
    esha_period      = fields.Boolean('Esha Period', track_visibility='onchange')
    esha_period_from = fields.Float('From Hour', track_visibility='onchange')
    esha_period_to   = fields.Float('To Hour', track_visibility='onchange')
     
    

