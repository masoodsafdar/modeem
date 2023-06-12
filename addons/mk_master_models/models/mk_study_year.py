#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError

import logging
_logger = logging.getLogger(__name__)


class MkStudyYear(models.Model):
    _name = 'mk.study.year'
    _inherit = ['mail.thread']
    _order = 'order'
       
    name               = fields.Char('Name', track_visibility='onchange')
    company_id         = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mk.study.year'))
    order              = fields.Integer('Order',   track_visibility='onchange')
    fiscal_year        = fields.Char('Fiscal Year',track_visibility='onchange')
    start_date         = fields.Date('Start Date', track_visibility='onchange')
    end_date           = fields.Date('End Date',   track_visibility='onchange')
    islamic_start_date = fields.Date('Islamic Start Date', track_visibility='onchange')
    islamic_end_date   = fields.Date('Islamic End Date',   track_visibility='onchange')
    active             = fields.Boolean('Active', default=True, track_visibility='onchange')
    class_ids          = fields.One2many('mk.study.class', 'study_year_id',  string='Classes')
    formal_leave_ids   = fields.One2many('mk.formal.leave', 'study_year_id', string='Formal Leaves')
    urgent_leave_ids   = fields.One2many('mk.urgent.leave', 'study_year_id', string='Urgent Leaves')
    is_default         = fields.Boolean(string="is default", default=False, readonly=True, track_visibility='onchange')

    # @api.multi
    def set_as_default(self):
        ids=self.env['mk.study.year'].search(['|',('active','=',False),('active','=',True)])
        for rec in ids:
            rec.write({'is_default':False,})
        self.write({'is_default':True})
        
    # @api.multi
    def unlink(self):
        try:
            super(MkStudyYear, self).unlink()
        except:
            raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))

    @api.model
    def get_years_study(self):
        years_study = self.env['mk.study.year'].search([('active', '=', True),
                                                        ('is_default', '=', True)], limit=1)
        item_list = []
        if years_study:
            item_list.append({'name':       years_study.name,
                              'start_date': years_study.start_date,
                              'end_date':   years_study.end_date})
        return item_list

