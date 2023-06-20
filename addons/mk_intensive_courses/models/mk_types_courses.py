#-*- coding:utf-8 -*-
from odoo import models, fields, api


class mk_types_courses(models.Model):
    _name = 'mk.types.courses'
    _inherit=['mail.thread','mail.activity.mixin']
    
    @api.model
    def get_year_default(self):
        year = self.env['mk.study.year'].search([('is_default','=',True)], limit=1)
        return year and year.id or False

    @api.model
    def get_study_class(self):
        study_class = self.env['mk.study.class'].search([('study_year_id', '=', self.get_year_default()),
                                                         ('is_default', '=', True)], limit=1)
        return study_class and study_class.id or False           
    
    number         = fields.Char('Number', tracking=True)
    name           = fields.Char('Name', tracking=True)
    start_date     = fields.Date('Start Date', required=True, tracking=True)
    end_date       = fields.Date('End Date', tracking=True)
    # test_str_date  = fields.Date('Test Start Date', required=True, tracking=True)
    # test_end_date  = fields.Date('Test End Date', tracking=True)
    academic_id    = fields.Many2one('mk.study.year',  string='العام الدراسي', default=get_year_default, tracking=True)
    study_class_id = fields.Many2one('mk.study.class', string='الفصل الدراسي', default=get_study_class, tracking=True)
    minimum_no_day = fields.Integer(string="Minimum No Of Days", tracking=True, default=20)
    active         = fields.Boolean('نشط', default=True, tracking=True)

    
    @api.constrains('end_date')
    def _check_start_date(self):
        if self.end_date < self.start_date:
            raise models.ValidationError('تاريخ نهاية الدورة المكثفة غير صحيح')
        
        # if self.test_end_date < self.test_str_date:
        #     raise models.ValidationError('تاريخ نهاية الإختبار غير صحيح')