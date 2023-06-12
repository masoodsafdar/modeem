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

class MkTestInternalRegisterations(models.Model):
    _name = 'mk.test.internal.registerations'
    _rec_name = 'student_id'

    @api.onchange('period_id')
    def period_onchange(self):
        if self.period_id.subh_period:
        	self.period_subh = 's'
        if self.period_id.zuhr_period:
        	self.period_zuhr = 'z'
        if self.period_id.aasr_period:
        	self.period_aasr = 'a' 
        if self.period_id.magrib_period:
        	self.period_magrib = 'm'
        if self.period_id.esha_period:
        	self.period_esha = 'e'  
        	
    @api.depends('period_id','subh','zuhr','aasr','magrib','esha')
    def _test_time(self):
        time = None
        if self.period_id:
            if self.subh:
            	time = 'from ' +  str(self.period_id.subh_period_from) +' ' +'to ' + str(self.period_id.subh_period_to)  
            elif self.zuhr:
            	time = 'from ' +  str(self.period_id.zuhr_period_from) +' ' +'to ' + str(self.period_id.zuhr_period_to)  
            elif self.subh:
            	time = 'from ' +  str(self.period_id.aasr_period_from) +' ' +'to ' + str(self.period_id.aasr_period_to)  
            elif self.magrib:
            	time = 'from ' +  str(self.period_id.magrib_period_from) +' ' +'to ' + str(self.period_id.magrib_period_to)  
            elif self.esha:
            	time = 'from ' +  str(self.period_id.esha_period_from) +' ' +'to ' + str(self.period_id.esha_period_to)  
            self.test_time = time	
        else:
            self.test_time = time

    @api.onchange('company_id')
    def onchange_p(self):
        if self.company_id:
        	p_ids= self.env['mk.periods'].search([('company_id','=',self.company_id.id)])
        	if p_ids:
        		self.period_id= p_ids[0].id
        else:
        	self.period_id = False

    @api.multi
    def get_study_class(self):
        study_class_ids=self.env['mk.study.class'].search([('study_year_id', '=', self.get_year_default()),('is_default', '=', True)])
        if study_class_ids:
            return study_class_ids[0]
    
    @api.multi
    def get_year_default(self):
        academic_year = self.env['mk.study.year'].search([('is_default','=',True)], limit=1)
        return academic_year and academic_year.id or False 

    company_id = fields.Many2one('res.company', string='Company',ondelete='restrict', default=lambda self: self.env['res.company']._company_default_get('mk.test.internal.registerations'))
    test_type_id = fields.Many2one('mk.test.type', string='Test Type',ondelete='restrict')
    study_year_id = fields.Many2one('mk.study.year', string='Study Year',ondelete='restrict', default=get_year_default)
    study_class_id = fields.Many2one('mk.study.class', string='Study Class Year',ondelete='restrict', readonly=True , default=get_study_class )
    test_center_config_id = fields.Many2one('mk.test.center.config', string='Test Center',ondelete='restrict')
    center_department_id = fields.Many2one('hr.department', string='Center',ondelete='restrict')
    mosque_department_id = fields.Many2one('hr.department', string='Mosque',ondelete='restrict')
    student_id = fields.Many2one('mk.link', string='Student')
    mosque_id = fields.Many2one('mk.mosque', string='Mosque',)




    test_date = fields.Date('Test Date')
    period_id = fields.Many2one('mk.periods', string='Period',)
    test_time = fields.Char(compute='_test_time', string='Test Time', store=True)
    
    subh = fields.Boolean('Subh')
    zuhr = fields.Boolean('Zuhr')
    aasr = fields.Boolean('Aasr')
    magrib = fields.Boolean('Magrib')
    esha = fields.Boolean('Esha')
    
    period_subh = fields.Char('Subh')
    period_zuhr = fields.Char('Zuhr')
    period_aasr = fields.Char('Aasr')
    period_magrib = fields.Char('Magrib')
    period_esha = fields.Char('Esha')

    time_id = fields.Many2one('mk.test.time', string="Time")
    time_backup_id = fields.Many2one('mk.test.time', string="Time Backup")


    @api.onchange('time_id')
    def onchange_time_id(self):
        if self.time_id.id != self.time_backup_id.id:
        	if self.time_backup_id:
        		self.time_backup_id.write({'chec':False})
        	if self.time_id:
        		self.time_id.write({'chec':True})
        		self.time_backup_id = self.time_id.id
        	else:
        		self.time_backup_id = False

    

    @api.constrains('test_date')
    def _check_test_date(self):
        if (self.test_date < self.test_center_config_id.exam_start_date or self.test_date > self.test_center_config_id.exam_end_date):
            raise ValidationError(_('Invalid Start Date'))
    """
    @api.model    
    def fields_view_get(self, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(MkTestInternalRegisterations, self).fields_view_get(view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
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

    @api.one
    def update_test_time(self):
        time_obj= self.env['mk.test.time']
        time_ids= time_obj.search([('test_center_config_id','=',self.test_center_config_id.id),('test_date','=',self.test_date),('test_type_id','=',self.test_type_id.id),('study_year_id','=',self.study_year_id.id),('study_class_id','=',self.study_class_id.id)])
        counter = 0
        for t in time_ids:
        	counter +=1
        if counter == 0:
            duration= self.test_type_id.duration
            from_period = False
            to_period = False
            if self.subh:
                from_period = self.period_id.subh_period_from
                to_period = self.period_id.subh_period_to
            elif self.zuhr:
                from_period = self.period_id.zuhr_period_from
                to_period = self.period_id.zuhr_period_to
            elif self.aasr:
                from_period = self.period_id.aasr_period_from
                to_period = self.period_id.aasr_period_to
            elif self.magrib:
                from_period = self.period_id.magrib_period_from
                to_period = self.period_id.magrib_period_to
            elif self.esha:
                from_period = self.period_id.esha_period_from
                to_period = self.period_id.esha_period_to

            if (not from_period) or (not to_period):
                raise ValidationError(_('Please, Check periods...'))
            else:
                rate= 0.00
                rate = float(duration)/60
                f_period= from_period
                t_period= from_period
                while ((t_period+rate) <= to_period+.1):
                	if rate == 0 :
                		break
                	t_period= t_period+rate

                	fr = 0
                	fr = int(60*(f_period - int(f_period)))

                	to = 0
                	to = int(60*(t_period - int(t_period)))
                	time_obj.create({

                		'subh':self.subh,
                		'zuhr':self.zuhr,
                		'aasr':self.aasr,
                		'magrib':self.magrib,
                		'esha':self.esha,
                		'from_period': f_period,
                		'to_period': t_period,
                		'company_id':self.company_id.id,
                		'test_type_id':self.test_type_id.id,
                		'study_year_id':self.study_year_id.id,
                		'study_class_id':self.study_class_id.id,
                		'test_center_config_id':self.test_center_config_id.id,
                		'test_date':self.test_date,
                		'name': _(' From ').encode('utf-8','ignore') + (str(int(f_period)).encode('utf-8','ignore'))+':'.encode('utf-8','ignore')+(str(fr).encode('utf-8','ignore'))+ _(' To ').encode('utf-8','ignore')+ (str(int(t_period)).encode('utf-8','ignore'))+':'.encode('utf-8','ignore')+(str(to).encode('utf-8','ignore')),
                		#'name': _(' From ').encode('utf-8','ignore') + (str(f_period).encode('utf-8','ignore'))+ _(' To ').encode('utf-8','ignore')+ (str(t_period).encode('utf-8','ignore')),
                	})
                	f_period= f_period+rate
        	

        else:
        	raise ValidationError(_('Already Exist Periods'))
	
    
class MkTestTime(models.Model):
    _name = 'mk.test.time'

    @api.depends('test_id')
    def get_checked(self):
        register_obj= self.env['mk.test.internal.registerations']
        check= True
        for rec in self:
        	for r in register_obj.search([('time_id','=',rec.id)]):
        		rec.checked = True
        		check= False
        		break
        	if check:
        		rec.checked = False

    @api.multi
    def get_test(self):
        register_obj= self.env['mk.test.internal.registerations']
        check= True
        for rec in self:
        	for r in register_obj.search([('time_id','=',rec.id)]):
        		rec.test_id = r.id
        		check= False
        		break
        	if check:
        		rec.test_id = False


    test_id = fields.Many2one('mk.test.internal.registerations',compute="get_test", string="Test")
    name = fields.Char("Time")
    test_date = fields.Date("Date")
    checked = fields.Boolean(compute="get_checked", string="Checked",)
    chec = fields.Boolean("Check")
    company_id = fields.Many2one('res.company', string='Company')
    test_type_id = fields.Many2one('mk.test.type', string='Test Type')
    study_year_id = fields.Many2one('mk.study.year', string='Study Year',)
    study_class_id = fields.Many2one('mk.study.class', string='Study Class Year',)
    test_center_config_id = fields.Many2one('mk.test.center.config', string="Test Center")
    from_period = fields.Float("From Period")
    to_period = fields.Float("To Period")
    subh = fields.Boolean('Subh')
    zuhr = fields.Boolean('Zuhr')
    aasr = fields.Boolean('Aasr')
    magrib = fields.Boolean('Magrib')
    esha = fields.Boolean('Esha')
