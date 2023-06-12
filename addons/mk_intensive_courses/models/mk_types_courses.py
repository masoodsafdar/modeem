#-*- coding:utf-8 -*-
from odoo import models, fields, api


class mk_types_courses(models.Model):
    _name = 'mk.types.courses'
    _inherit = ['mail.thread']
    
    @api.model
    def get_year_default(self):
        year = self.env['mk.study.year'].search([('is_default','=',True)], limit=1)
        return year and year.id or False

    @api.model
    def get_study_class(self):
        study_class = self.env['mk.study.class'].search([('study_year_id', '=', self.get_year_default()),
                                                         ('is_default', '=', True)], limit=1)
        return study_class and study_class.id or False           
    
    number         = fields.Char('Number', track_visibility='onchange')
    name           = fields.Char('Name', track_visibility='onchange')
    start_date     = fields.Date('Start Date', required=True, track_visibility='onchange')
    end_date       = fields.Date('End Date', track_visibility='onchange')
    # test_str_date  = fields.Date('Test Start Date', required=True, track_visibility='onchange')
    # test_end_date  = fields.Date('Test End Date', track_visibility='onchange')
    academic_id    = fields.Many2one('mk.study.year',  string='العام الدراسي', default=get_year_default, track_visibility='onchange')
    study_class_id = fields.Many2one('mk.study.class', string='الفصل الدراسي', default=get_study_class, track_visibility='onchange')
    minimum_no_day = fields.Integer(string="Minimum No Of Days", track_visibility='onchange', default=20)
    active         = fields.Boolean('نشط', default=True, track_visibility='onchange')

    
    @api.constrains('end_date')
    def _check_start_date(self):
        if self.end_date < self.start_date:
            raise models.ValidationError('تاريخ نهاية الدورة المكثفة غير صحيح')
        
        # if self.test_end_date < self.test_str_date:
        #     raise models.ValidationError('تاريخ نهاية الإختبار غير صحيح')