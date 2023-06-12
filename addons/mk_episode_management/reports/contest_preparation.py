#-*- coding:utf-8 -*-

##############################################################################
#
#    Copyright (C) Appness Co. LTD **hosam@app-ness.com**. All Rights Reserved
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
from lxml import etree
from lxml.builder import E
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from odoo import api, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)

class contestPreparation(models.Model):
    _name = 'contest.preparation'


    contest_type=fields.Many2one("contest.type",string="contest type")
    is_quran=fields.Boolean(string="is qran")
    '''
    # @api.multi
    def write(self, vals):
        for rec in self:
            if self.create_uid.id != self.env.user.id:
                raise ValidationError(_('عذرا ! لايمكنك تعديل هذه المسابقة '))

        return super(contestPreparation, self).write(vals)
    '''
    @api.onchange('contest_type.method', 'contest_type')
    def on_contest_type(self):
        if self.contest_type.method=='quran':
            self.is_quran=True
        elif self.contest_type.method=='program':
            self.is_quran=False
    name = fields.Char(
        string=' contest name',
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=False
    )

    target_grade = fields.Many2many(
        string='Target grade categorys',
        required=True,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='mk.grade',
        relation='',
        column1='',
        column2='',
        domain=[],
        context={},
        limit=None
    )

    contest_fields = fields.Many2many(
        string='contenst fields',
        required=True,
        comodel_name='mk.contenst.fields',
        domain=[],
        context={},
        limit=None
    )

    diff_items=fields.One2many('contest.diff.items','contest_id',string='contenst differentiation items')

    brochure = fields.Binary("برشور  المسابقة")
    brochure_active = fields.Boolean(string='تفعيل البرشور على البورتال')

    
    StartD = fields.Date(
        string='Start Date',
        required=True,
        readonly=False,
        index=False,
        default=fields.Date.today()
    )
    endD = fields.Date(
        string='End Date',
        required=True,
        readonly=False,
        index=False,
    )
    @api.model
    def create(self,vals):
        
        if vals['StartD'] < fields.Date.today():
                raise models.ValidationError('التواريخ المسموح بها ابتداءا من اليوم فمافوق')
        if (vals['endD'] <= fields.Date.today() ):
            raise models.ValidationError('التواريخ المسموح بها ابتداءا من اليوم فمافوق')
        return super(contestPreparation, self).create(vals)

    @api.depends('place','center_id')
    def get_center_emp(self):
        if self.place:
            emps=self.env['hr.employee'].sudo().search([('department_id','=',self.center_id.id),('category2','in',['admin','supervisor','center_admin'])]).ids
            self.center_emp= emps
    
    @api.constrains('endD')
    def _check_end_date(self):
    	for r in self:
            
            if r.endD< r.StartD:
                raise models.ValidationError('تاريخ نهاية المسابقة يجب أن يكون بعد تاريخ بداية المسابقة')

    center_emp = fields.Many2many(
        string='Center emp',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='hr.employee',
        compute=get_center_emp,
        domain=[],
        context={},
        limit=None
    )
    
    
    Target_age_cat = fields.Many2many(
        string='Target age categorys',
        required=True,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='mk.age.category',
        relation='',
        column1='',
        column2='',
        domain=[],
        context={},
        limit=None
    )
    branches = fields.Many2many(
        string='Branches',
        required=False,
        comodel_name='mk.branches.master',
        domain=[('contsets','=',True)],

    )
    

    gender_type = fields.Selection([('male','Male'),
        ('female','Female'),('male,female','All')],
        string="Allowed gender",default="male,female")

    attachment= fields.Many2many(
        string='attachment',
        required=False,
        comodel_name='ir.attachment',
    )
    gools = fields.Text(
        string='contest gools',
        required=True,
        readonly=False,
        index=False,
        default=None,
        help=False,
        translate=False
    )
    conditions = fields.Text(
        string='Conditions',
        required=True,
        readonly=False,
        index=False,
        default=None,
        help=False,
        translate=False
    )

    place = fields.Selection(
        string='Place',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False,
        selection=[('mosque_level', 'mosque_level'), ('center_level', 'center_level'),
        ('organization_level','على مستوى الجمعية')]
    )

    test_id = fields.Many2one(
        string='اسم المسابقة',
        comodel_name='mk.test.names',
        domain=[('is_contest','=', True)],
    )

    center_id = fields.Many2one(
        string='Center',
        required=False,
        readonly=False,
        index=False,
        comodel_name='hr.department',
        domain=[],
        context={},
        auto_join=False
    )

    mosque_id = fields.Many2one(
        string='Mosque',
        required=False,
        readonly=False,
        index=False,
        default=None,
        comodel_name='mk.mosque',
        domain=[],
        context={},
        auto_join=False
    )

    @api.onchange('test_id')
    def on_change_test_id(self):
        if self.test_id:
            self.branches=self.test_id.branches.ids
            self.name=self.test_id.name

class contestType(models.Model):
    _name="contest.type"

    name=fields.Char(string="Name",required="1")
    method=fields.Selection([('quran','quran field'),('program','program field')],string="contest field")