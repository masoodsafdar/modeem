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

class MkTestStudentPreparation(models.Model):
    _name = 'mk.test.student.preparation'

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == "start":
                raise ValidationError(_('لا يمكنك حذف سجل تم تأكيده'))
            else:
                try:
                    super(MkTestStudentPreparation, rec).unlink()
                except:
                    raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))




    @api.onchange('test_registeration_id')
    def test_registeration_onchange(self):
    	self.test_type_id = self.test_registeration_id.test_type_id.id
    	self.study_year_id = self.test_registeration_id.study_year_id.id
    	self.study_class_id = self.test_registeration_id.study_class_id.id
    	self.link_id = self.test_registeration_id.student_id.id
    	self.test_center_config_id = self.test_registeration_id.test_center_config_id.id
    	self.test_date = self.test_registeration_id.test_date
    	self.test_time = self.test_registeration_id.test_time
    	self.period_id = self.test_registeration_id.period_id.id
    	
    @api.onchange('test_registeration_id')
    def period_onchange(self):
        if self.test_registeration_id.subh:
        	self.period_t = _('Subh')
        if self.test_registeration_id.zuhr:
        	self.period_t = _('Zuhr')
        if self.test_registeration_id.aasr:
        	self.period_t = _('Aasr')
        if self.test_registeration_id.magrib:
        	self.period_t = _('Magrib')
        if self.test_registeration_id.esha:
        	self.period_t = _('Esha')	
    
    @api.one
    def do_draft(self):
    	self.state = 'draft'
    	
    @api.one
    def do_start(self):
    	self.state = 'start'
    
    @api.one
    def do_cancel(self):
    	self.state = 'cancelled'

    @api.multi
    def get_year_default(self):
        academic_year = self.env['mk.study.year'].search([('is_default','=',True)], limit=1)
        return academic_year and academic_year.id or False 
    
    @api.multi
    def get_study_class(self):
        study_class_ids=self.env['mk.study.class'].search([('study_year_id', '=', self.get_year_default()),('is_default', '=', True)])
        if study_class_ids:
            return study_class_ids[0]

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mk.test.student.preparation'), ondelete='restrict')
    test_type_id = fields.Many2one('mk.test.type', string='Test Type', ondelete='restrict')
    study_year_id = fields.Many2one('mk.study.year', string='Study Year',ondelete='restrict', default=get_year_default)
    study_class_id = fields.Many2one('mk.study.class', string='Study Class Year', ondelete='restrict', readonly=True,default=get_study_class )
    test_center_config_id = fields.Many2one('mk.test.center.config', string='Test Center', ondelete='restrict')
    test_registeration_id = fields.Many2one('mk.test.internal.registerations', string='Test Registeration', ondelete='restrict')
    link_id = fields.Many2one('mk.link', string='Student')


    test_date = fields.Date('Test Date')
    period_id = fields.Many2one('mk.periods', string='Period')
    test_time = fields.Char(string='Test Time')
    period_t = fields.Char(string='Test period')
    state = fields.Selection([
	('draft', 'Draft'),
	('start', 'Start'),
	('cancelled', 'Cancelled'),
	], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
    comment = fields.Text('Comment')
    
    """
    
    @api.model    
    def fields_view_get(self, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(MkTestStudentPreparation, self).fields_view_get(view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
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
    

