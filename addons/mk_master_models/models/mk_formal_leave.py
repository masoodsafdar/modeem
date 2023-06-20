#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _


class MkFormalLeave(models.Model):
    _name = 'mk.formal.leave'
    _inherit=['mail.thread','mail.activity.mixin']
    _rec_name = 'name'

    # @api.multi
    def get_year_default(self):
        academic_year = self.env['mk.study.year'].search([('is_default', '=', True)], limit=1)
        return academic_year and academic_year.id or False 
        
    name          = fields.Char('الإجازة', tracking=True)
    company_id    = fields.Many2one('res.company',   string='Company',    default=lambda self:self.env.user.company_id.id, tracking=True)
    study_year_id = fields.Many2one('mk.study.year', string='Study Year',  default=get_year_default, tracking=True)
    leave_id      = fields.Many2one('hr.holidays.status', 'Leave', tracking=True)
    start_date    = fields.Date('Start Date', tracking=True)
    end_date      = fields.Date('End Date', tracking=True)
    active        = fields.Boolean('Active', default=True, tracking=True)
    
    # @api.one
    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        if (self.start_date < self.study_year_id.start_date):
                raise ValidationError(_('تاريخ البداية اقل من تاريخ بداية السنة الدراسية'))
        if (self.end_date > self.study_year_id.end_date):
                raise ValidationError(_('تاريخ النهاية اكبر من تاريخ نهاية السنة الدراسية'))
