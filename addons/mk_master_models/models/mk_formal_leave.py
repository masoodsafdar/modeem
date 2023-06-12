#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _


class MkFormalLeave(models.Model):
    _name = 'mk.formal.leave'
    _inherit = ['mail.thread']
    _rec_name = 'name'

    # @api.multi
    def get_year_default(self):
        academic_year = self.env['mk.study.year'].search([('is_default', '=', True)], limit=1)
        return academic_year and academic_year.id or False 
        
    name          = fields.Char('الإجازة', track_visibility='onchange')
    company_id    = fields.Many2one('res.company',   string='Company',    default=lambda self:self.env.user.company_id.id, track_visibility='onchange')
    study_year_id = fields.Many2one('mk.study.year', string='Study Year',  default=get_year_default, track_visibility='onchange')
    leave_id      = fields.Many2one('hr.holidays.status', 'Leave', track_visibility='onchange')
    start_date    = fields.Date('Start Date', track_visibility='onchange')
    end_date      = fields.Date('End Date', track_visibility='onchange')
    active        = fields.Boolean('Active', default=True, track_visibility='onchange')
    
    # @api.one
    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        if (self.start_date < self.study_year_id.start_date):
                raise ValidationError(_('تاريخ البداية اقل من تاريخ بداية السنة الدراسية'))
        if (self.end_date > self.study_year_id.end_date):
                raise ValidationError(_('تاريخ النهاية اكبر من تاريخ نهاية السنة الدراسية'))
