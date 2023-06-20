# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import Warning, ValidationError

import logging
_logger = logging.getLogger(__name__)


class mak_grade(models.Model):
    _name = 'mk.grade'
    _inherit=['mail.thread','mail.activity.mixin']
    _description = 'Educational episodes'

    name           = fields.Char('Grade',     required=True, tracking=True)
    order_grade    = fields.Integer("Order", tracking=True)
    active         = fields.Boolean('Active', default=True,  tracking=True)
    age_categories = fields.Many2many("mk.age.category",string="Age Gategories")
    is_parent      = fields.Boolean('مؤهل خاص بولي الأمر', default=False, tracking=True)
    is_episode     = fields.Boolean('مؤهل خاص بالحلقات',  default=False, tracking=True)
    type_level     = fields.Selection([('preliminary', 'تمهيدي'), 
                                        ('primary', 'ابتدائي'), 
                                        ('medium', 'متوسط'),
                                        ('secondary', 'ثانوي'),
                                        ('academic', 'جامعي'), 
                                        ('other', 'أخرى/أمهات')], string='المستوى الدراسي', tracking=True)

    # _sql_constraints = [('order_grade_uniq', 'unique (order_grade)', "Ordre must be unique please"),]
    
    # @api.multi
    def unlink(self):
        try:
            super(mak_grade, self).unlink()
        except:
            raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))

    @api.model
    def get_parent_grade(self):
        grades = self.env['mk.grade'].search([('active', '=', True),
                                              ('is_parent', '=', True)], order="order_grade")
        grade_list = []
        if grades:
            for grade in grades:
                grade_list.append({'id': grade.id,
                                   'name': grade.name})
        return grade_list

    @api.model
    def get_grade(self, is_parent):
        grades = self.env['mk.grade'].search([('active', '=', True),
                                              ('order_grade', '>', 0),
                                              ('is_parent', '=', is_parent)], order="order_grade, id")
        grade_list = []
        if grades:
            for grade in grades:
                grade_list.append({'id': grade.id,
                                   'name': grade.name})
        return grade_list
