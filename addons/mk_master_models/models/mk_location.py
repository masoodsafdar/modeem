# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
import logging
import xlrd
import xlsxwriter

_logger = logging.getLogger(__name__)

class mak_country_state(models.Model):
	_name = 'res.country.state'
	_inherit = ['res.country.state','mail.thread']

	def default_country(self):
		return 179

	def defult_area(self):
		return 600

	area_id              = fields.Many2one('res.country.state', string="area",    domain=[('type_location','=','area'),
                                                                                          ('enable', '=', True)], default=defult_area, tracking=True)#!=false =>city
	district_id          = fields.Many2one('res.country.state', string="City",    domain=[('type_location','=','city'),
																						  ('enable', '=', True),], tracking=True)
	country_id           = fields.Many2one('res.country',       string='Country', default=default_country, tracking=True)
	latitude             = fields.Char('Latitude',  digits=(12,8), tracking=True)
	longitude            = fields.Char('Longitude', digits=(12,8), tracking=True)
	code                 = fields.Char('code',      required=False, size=2, tracking=True)
	active               = fields.Boolean('Active', default=True, tracking=True)
	center_department_id = fields.Many2one('hr.department', string='Center', tracking=True)
	department_ids       = fields.Many2many('hr.department',string='Additional departments')
	enable               = fields.Boolean("Enable for Educational", default=False, tracking=True)
	type_location        = fields.Selection([('country',  'Country'),											
											 ('city',     'City'),
											 ('area',     'Area'),
											 ('district', 'District'),], default='country')
	district_code        = fields.Char(string="District Code", tracking=True, copy=False)
	flag                 = fields.Boolean(string="Is Defaut center", default=False)


	# @api.one
	@api.constrains('code', 'center_department_id', 'type_location')
	def check_district(self):
		type_location = self.type_location
		msg = ''
		if type_location == 'district':
			code = self.code
			department = self.center_department_id
			
			if code and len(code) > 2:
				msg = ' يجب أن لا يتجاوز كود الحي رقمين'
			
			else:

				district = self.search([('type_location','=','district'),
										('id','!=',self.id),
									    ('code','=',code),
									    ('center_department_id','=',department.id)], limit=1)
				if district:
					msg = 'يوجد حي آخر بنفس الكود يتبع ل'
					msg += department.name
					msg += ' ' + '!'
			
			if msg:
				msg += '!'
				raise ValidationError(msg)				

	# @api.one
	def write(self, vals):
		if 'center_department_id' in vals:
			mosques = self.env['mk.mosque'].search([('district_id','=',self.id)])

			for mosque in mosques:
				mosque.write({'center_department_id': vals['center_department_id']})
				
				mosque.responsible_id.write({'department_id': vals['center_department_id']})
				
				for teacher in mosque.teacher_ids:
					teacher.write({'department_id': vals['center_department_id']})
				
				for supervisor in mosque.supervisors:
					supervisor.write({'department_id': vals['center_department_id']})
				
				#for bus_sup in mosque.bus_supervisors:
					#bus_sup.write({'department_id': vals['center_department_id']})
				
				for manage in mosque.managment_id:
					manage.write({'department_id': vals['center_department_id']})

		return super(mak_country_state, self).write(vals)	
	
	# @api.one
	def unlink(self):
		try:
			super(mak_country_state, self).unlink()
		except:
			raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))

	@api.model
	def get_city(self, area_id):
		try:
			area_id = int(area_id)
		except:
			pass
		city = self.env['res.country.state'].search([('active', '=', True),
													   ('enable', '=', True),
													   ('type_location', '=', 'city'),
													   ('area_id', '=', area_id)], limit=1)
		city_list = []
		if city:
			city_list.append({'id': city.id,
						 'name': city.name})
		return city_list

	@api.model
	def get_area(self):
		area = self.env['res.country.state'].search([('active', '=', True),
													  ('enable', '=', True),
													  ('type_location', '=', 'area')], limit=1)
		area_list = []
		if area:
			area_list.append({'id': area.id,
						   'name':  area.name})
		return area_list

	@api.model
	def get_district(self, area_id):
		try:
			area_id = int(area_id)
		except:
			pass
		districts = self.env['res.country.state'].search([('active', '=', True),
														('enable', '=', True),
														('area_id', '=', area_id)])
		district_list = []
		if districts:
			for district in districts:
				district_list.append({'id':   district.id,
									  'name': district.name})
		return district_list

	@api.model
	def get_department(self, district_id):
		try:
			district_id = int(district_id)
		except:
			pass

		district = self.env['res.country.state'].search([('id', '=', district_id),
													     '|',('active', '=', True),
													         ('active', '=', False)], limit=1)
		district_list = []
		if district:
			district_list.append({'center_department_id': district.center_department_id.id})
		return district_list

	@api.model
	def get_district_details(self):
		file_path = "/opt/odoo/workspace/districts_eduactional.xlsx"

		workbook = xlrd.open_workbook(file_path)
		sheet = workbook.sheets()[0]
		values = []
		if sheet.ncols != 0:
			for rowx in range(1, sheet.nrows):
				cols = sheet.row_values(rowx)
				district_name = cols[0].strip()
				similar_district = self.env['res.country.state'].search([('name', 'like', district_name)])
				if similar_district:
					if len(similar_district) == 1:
						values.append({'external_id': list(similar_district.get_external_id().items())[0][
							1] if similar_district and list(similar_district.get_external_id().items())[0] else False,
									   'id': similar_district.id,
									   'name': similar_district.name,
									   'district_name': district_name,
									   'code': similar_district.code,
									   'many': False})
					else:
						for rec in similar_district:
							values.append({'external_id': list(rec.get_external_id().items())[0][
								1] if similar_district and list(rec.get_external_id().items())[0] else False,
										   'id': rec.id,
										   'name': rec.name,
										   'district_name': district_name,
										   'code': rec.code,
										   'many': True})
				else:
					values.append({'external_id': False,
								   'id': False,
								   'name': district_name,
								   'district_name': district_name,
								   'code': False,
								   'many': False})
		wb = xlsxwriter.Workbook('/opt/odoo/workspace/districts_eduactional.xlsx')

		worksheet = wb.add_worksheet()
		worksheet.set_column('A:D', 20)
		worksheet.write('A1', 'المعرف الخارجي')
		worksheet.write('B1', 'المعرف')
		worksheet.write('C1', 'اسم الحي')
		worksheet.write('D1', 'اسم الحي المعتمد')
		worksheet.write('E1', 'كود')
		worksheet.write('F1', 'Many')
		row = 0
		for val in values:
			row += 1
			worksheet.write(row, 2, val['name'])
			worksheet.write(row, 3, val['district_name'])
			if val['id']:
				worksheet.write(row, 0, val['external_id'])
				worksheet.write(row, 1, val['id'])
				worksheet.write(row, 2, val['name'])
				worksheet.write(row, 4, val['code'])
				worksheet.write(row, 5, val['many'])

		wb.close()


class inherit_hr_department(models.Model):
	_inherit = 'hr.department'

	department_code = fields.Char('Department code')

