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
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from odoo.tools.translate import _

class MkTestCenterConfig(models.Model):
    _name = 'mk.test.center.config'

    _rec_name = 'center_id'
        

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mk.test.center.config'))
    center_id = fields.Many2one('mk.test.center', string='Test Center')
    study_year_id = fields.Many2one('mk.study.year', 'Study Year', ondelete="cascade", )
    active = fields.Boolean('Active', default=True)
    website_registeration = fields.Boolean('Registeration by Website',)
    department_ids = fields.Many2many('hr.department', 'test_center_department_rel', 'test_center_id', 'department_id', string="Departments")
    registeration_start_date = fields.Date('Registeration Start Date')
    registeration_end_date = fields.Date('Registeration End Date')
    exam_start_date = fields.Date('Exam Start Date')
    exam_end_date = fields.Date('Exam End Date')
    
    subh = fields.Boolean('Subh')
    zuhr = fields.Boolean('Zuhr')
    aasr = fields.Boolean('Aasr')
    magrib = fields.Boolean('Magrib')
    esha = fields.Boolean('Esha')
    
    friday = fields.Boolean('Friday')
    saturday = fields.Boolean('Saturday')
    sunday = fields.Boolean('Sunday')
    monday = fields.Boolean('Monday')
    tuesday = fields.Boolean('Tuesday')
    wednesday = fields.Boolean('Wednesday')
    thursday = fields.Boolean('Thursday')
    
    @api.constrains('registeration_start_date', 'registeration_end_date','exam_start_date','exam_end_date')
    def _check_date(self):
        if (self.registeration_start_date < self.study_year_id.start_date):
                raise ValidationError(_('Invalid Registeration Start Date'))
        if (self.registeration_end_date > self.study_year_id.end_date):
                raise ValidationError(_('Invalid Registeration End Date'))
        if (self.exam_start_date < self.study_year_id.start_date):
                raise ValidationError(_('Invalid Exam Start Date'))
        if (self.exam_end_date > self.study_year_id.end_date):
                raise ValidationError(_('Invalid Exam End Date'))
    """
    @api.model    
    def fields_view_get(self, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(MkTestCenterConfig, self).fields_view_get(view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='company_id']")
        company_ids = []
        company_recs= self.env['mk.study.year'].search([])
        company_ids = [x.company_id.id for x in company_recs]
        domain = "[('id', 'in', " + str(company_ids) + ")]"
	   for node in nodes:
		node.set('domain', domain)
        res['arch'] = etree.tostring(doc)
        return res

    """
    

