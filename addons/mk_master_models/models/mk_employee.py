# -*- coding: utf-8 -*-
import json

import requests
from odoo import models, fields, api, _, tools
from odoo import SUPERUSER_ID
from odoo.tools import pycompat
import xmlrpc.client as xmlrpclib
from odoo.exceptions import ValidationError, UserError
from random import randint
import re

import os.path
import sys
# Add the directory containing the configuration file to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..', 'conf_files')))
# from conf import ERP_DB, ERP_HOST, ERP_USER, ERP_PASSWORD

import logging
_logger = logging.getLogger(__name__)

class Employee(models.Model):
	_inherit = "hr.employee"

	found_employee = 0
	mosque_new = 0
	
	@api.depends('identification_id')
	def get_employee(self):
		for rec in self:
			employee = self.sudo().search([('identification_id','=', rec.identification_id),
										   ('id','!=', rec.id)], limit=1)
			if employee:
				rec.found_employee = employee[0].id
			
	gender                = fields.Selection([('male', 'Male'),
							                  ('female', 'Female')], groups="hr.group_hr_user", default="male", track_visibility='onchange')
	center_admin_category = fields.Selection([('female', 'Female school'),
							 			      ('male',   'Male school'),
										      ('both',   'male and female school')], string='type of schools', required=False, readonly=False, default='both', track_visibility='onchange')
	mosque_sup            = fields.Many2many('mk.mosque', string='Mosque eduactional supervisor', required=False, readonly=False, index=False, default=None, help=False, domain=[], context={}, auto_join=False, limit=None)
	mosque_new            = fields.Many2one('mk.mosque',  string='new mosque')
	found_employee        = fields.Integer('Found employee', compute=get_employee)
	flag                  = fields.Boolean('Flag')
	employee_name         = fields.Char('employee name',     size=50, translate=False)
	category_name         = fields.Char('category name',     size=50, translate=False)
	mosque_name           = fields.Char('Mosque name',       size=50, translate=False)
	center_name           = fields.Char('Center name',       size=50, translate=False)
	flag2                 = fields.Boolean('Flag 2')
	start_date            = fields.Date('release date')
	expire_date           = fields.Date('Expiration date')
	category2             = fields.Selection("_get_priority_list","category", store=True)
	work_phone            = fields.Char(required=False, size=9, track_visibility='onchange')
	work_email            = fields.Char(required=False, track_visibility='onchange')
	passwd                = fields.Char(string='Passwd',)
	issue_identity        = fields.Date(string='Issue identity',)
	identity_expire       = fields.Date(string='Identity expire', required=False,)
	recruit_ids           = fields.Many2many('hr.recruitment.degree', string='Recruit')
	part_ids              = fields.Many2many('mk.parts',              string='Part id')
	kin_phone             = fields.Char('Kin phone', size=9)
	salary                = fields.Integer('Salary', track_visibility='onchange')
	salary_donor          = fields.Selection([('society', 'Society'),
									    ('masjed',  'Masjed'),
									    ('center',  'Center')], string='Salary donor', track_visibility='onchange')
	contract_type         = fields.Selection([('contractor',   'contractor'),
					 				    ('volunteer',    'volunteer'), 
									    ('collaborator', 'Collaborator')], string='Contract type', track_visibility='onchange')
	department_ids        = fields.Many2many('hr.department', string='مراكز إضافية')
	mosque_id             = fields.Many2one('mk.mosque',      string='Masjed')
	mosqtech_ids          = fields.Many2many('mk.mosque', 'mosque_relation', 'mosq_id','emp_id', string='Masjed')
	registeration_code    = fields.Char(size=12, string="registeration code", track_visibility='onchange')
	job_id                = fields.Many2one(domain=[('educational_job','=','True')], track_visibility='onchange')
	category              = fields.Selection([('teacher',        'المعلمين'),
						                   ('center_admin',   'مدراء / مساعدي مدراء المركز'),
						                   ('bus_sup',        'مشرف الباص'),
						                   ('supervisor',     'مشرفين وإداريين المسجد / المدرسة'), 
						                   ('admin',          'المشرف العام للمسجد /المدرسة'),
						                   ('edu_supervisor', 'مشرف تربوي'),
						                   ('managment',      'إداري\إداريين'),
						                   ('others',         'خدمات مساعدة')], string='Cateqory', default='admin', track_visibility='onchange')
	mobile_phone          = fields.Char("Mobile Phone", required=True, size=12, track_visibility='onchange')
	state                 = fields.Selection([('draft',  'Draft'),
				  			               ('accept', 'Accepted'), 
							               ('reject', 'Rejected')], string='State', default='draft', track_visibility='onchange')
	identification_id     = fields.Char(size=10, groups="base.group_user,group_read_employee", track_visibility='onchange')
	gender                = fields.Selection(groups="base.group_user,group_read_employee",     track_visibility='onchange')
	birthday              = fields.Date(groups="base.group_user,group_read_employee",          track_visibility='onchange')
	marital               = fields.Selection(groups="base.group_user,group_read_employee",     track_visibility='onchange')
	episode_ids           = fields.One2many('mk.episode','teacher_id')
	episode_unactv_ids    = fields.One2many('mk.episode','teacher_id',domain=[('active','=',False)])
	masajed_ids           = fields.One2many('mk.mosque','responsible_id')
	data_clean            = fields.Selection([('merge',         'merge'),
										   ('merge_episode', 'merge_episode'),
										   ('check_id',      'check_id'),])
	tajweed_level         = fields.Selection([('junior', ' مبتدئ/ة'),
											 ('practitioner', 'ممارس/ة'),
											 ('skilled', ' متمكن/ة'),
											 ('distinct', 'متميز/ة'),
											 ('perfect', 'متقن/ة'),
											 ('expert', 'خبير/ة')], string='المستوى التجويدي', track_visibility='onchange')
	years_of_experience   = fields.Integer('سنوات الخبرة', track_visibility='onchange')
	work_location         = fields.Char('Work Location',required=False)
	last_log_from_app = fields.Datetime(related='user_id.last_app_login',string='Last login from the APP')

	@api.model
	def fields_get(self, fields=None):
		res = super(Employee, self).fields_get()
		res['mosque_id']['exportable'] = False
		return res
	@api.model
	def check_num_mobile(self, num_mobile, employee_id):
		# to trim and is digits
		if not num_mobile or not num_mobile.isdigit():
			return 'فضلا رقم الجوال المدخل لابد ان يتكون من ارقام فقط'

		if len(num_mobile) != 9:
			return 'فضلا رقم الجوال لابد ان بتكون من 9 ارقام'

		# if the id starts what other than 1 or 2
		if num_mobile[0] != '5':
			return 'عذرا !! رقم الجوال المدخل غير صحيح يجب أن يبدأ برقم 5'
		return 1

	# @api.one
	@api.constrains('mobile_phone')
	def check_num_mobiles(self):
		res = self.check_num_mobile(self.mobile_phone, self.id)

		if isinstance(res, pycompat.string_types):
			raise ValidationError(res)  # TO DO create from Portal

	@api.onchange('mobile_phone')
	def onchange_mobile(self):
		mobile_phone = self.mobile_phone
		if mobile_phone:
			res = self.check_num_mobile(mobile_phone, self.id)
			if isinstance(res, pycompat.string_types):
				raise ValidationError(res)

	@api.onchange('mosqtech_ids')
	def onchange_mosqtech_ids(self):
		user = self.resource_id.user_id
		if user:
			user.mosque_id = [(6, 0, self.mosqtech_ids.ids)]
	
	@api.model
	def _get_priority_list(self):
		# get logged user group
		categories=[]
		# for security update 
		employee_id = self.env['hr.employee'].sudo().search([('user_id','=',self.env.user.id)], limit=1)
		if employee_id.category == 'center_admin':
			categories = [('center_admin','مدراء / مساعدي مدراء المركز'),
						  ('supervisor', 'مشرفين وإداريين المسجد / المدرسة'),
					      ('admin', 'المشرف العام للمسجد /المدرسة'), 
					      ('edu_supervisor', 'مشرف تربوي'),
					      ('teacher', 'المعلمين'),
					      ('managment','إداري\إداريين'),
					      ('others','خدمات مساعدة'),
					      ('bus_sup','مشرف الباص')]
		elif employee_id.category == 'edu_supervisor':
			categories = [('supervisor', 'مشرفين وإداريين المسجد / المدرسة'),
					      ('admin', 'المشرف العام للمسجد /المدرسة'), 
					      ('teacher', 'المعلمين'),
					      ('managment','إداري\إداريين'),
					      ('others','خدمات مساعدة'),
					      ('bus_sup','مشرف الباص')]
		elif employee_id.category == 'admin':
			categories = [('supervisor', 'مشرفين وإداريين المسجد / المدرسة'),
					      ('teacher', 'المعلمين'),
					      ('managment','إداري\إداريين'),
					      ('others','خدمات مساعدة'),
					      ('bus_sup','مشرف الباص')]
		elif employee_id.category == 'supervisor':
			categories = [('teacher', 'المعلمين'),
					      ('managment','إداري\إداريين'),
					      ('others','خدمات مساعدة'),
					      ('bus_sup','مشرف الباص')]
		else:
			categories = [('teacher', 'المعلمين'),
					      ('center_admin','مدراء / مساعدي مدراء المركز'),
					      ('bus_sup','مشرف الباص'),
					      ('supervisor', 'مشرفين وإداريين المسجد / المدرسة'), 
					      ('admin', 'المشرف العام للمسجد /المدرسة'),
					      ('edu_supervisor', 'مشرف تربوي'),
					      ('managment','إداري\إداريين'),
					      ('others','خدمات مساعدة')]
		return categories

	@api.onchange('department_id')
	def onchange_department_id(self):
		self.mosqtech_ids=False

	@api.onchange('category2')
	def onchange_cateqory(self):
		if self.category2:
			self.category = self.category2
			self.department_id=False
			self.mosqtech_ids=False
			
	@api.model
	def check_id_validity(self, identification_id, employee_id):
		# to trim and is digits
		if not identification_id.isdigit():
			return 'فضلا رقم الهوية المدخل لابد ان يتكون من ارقام فقط'
		
		if len(identification_id) != 10:		
			return 'فضلا رقم الهوية لابد ان بتكون من 10 ارقام'
				
		# if the id starts what other than 1 or 2
		if identification_id[0] != '1' and identification_id[0] != '2':
			return 'عذرا !! رقم الهوية المدخل غير صحيح'
	
		total = 0
		i = 0
		while i < len(identification_id):
			temp = int(identification_id[i]) * 2
			temp = str(temp).ljust(2, '0')
			# adding a "0" digit to the number in case the number is less than 10
			# to prevent index error in the next line
			# example: 3 * 2 = 6 => 60  ,  8 * 2 = 16 => 16
			total += int(temp[0]) + int(temp[1])
			i += 1
			total += int(identification_id[i])
			i += 1
	
		# check if the validation is correct
		if total % 10 != 0:
			return 'عذرا !! رقم الهوية المدخل غير صحيح'
		
		domain = [('identification_id','=',identification_id)]
		if employee_id:
			domain += [('id','!=',employee_id)]

		employee = self.sudo().search(domain, limit=1)
		if employee:
			return 'عذرا! رقم الهوية موجود مسبقا'
		else:
			domain += [('active','=',False)]
			employee = self.sudo().search(domain, limit=1)
			if employee:
				return 'عذرا! رقم الهوية موجود في الأرشيف'
	
		# return the first digit of the input id
		return 1

	# @api.one
	@api.constrains('identification_id')
	def _check_identification_id(self):
		res = self.check_id_validity(self.identification_id, self.id)
		if isinstance(res, pycompat.string_types):
			raise ValidationError(res)#TO DO create from Portal

	# @api.one
	@api.constrains('user_id')
	def _check_related_user(self):
		duplicated_user = self.search([('user_id', '=', self.user_id.id), 
									   ('id', '!=', self.id),
									   ('user_id','!=', False)])
		if duplicated_user:
			return
			#raise ValidationError("عذرا! الرجاء  إختيار إسم مستخدم غير محجوز لموظف اخر")

	@api.onchange('identification_id')
	def invistigate_identity(self):
		identification_id = self.identification_id
		employee_id = self.id
		flag = False
		if identification_id:
			res = self.check_id_validity(identification_id, employee_id)
			if isinstance(res, pycompat.string_types):
				raise ValidationError(res)
			
			if not self.create_date:
				global found_employee
			
			flag = True
			
		self.flag = flag

	# @api.multi
	def add_mosq(self):
		if self.mosque_new and self.found_employee:
			employee = self.sudo().search([('id','=',found_employee)])
			employee.sudo().write({'mosqtech_ids':[(4,self.mosque_new.id)]})
			employees = self.sudo().search([('identification_id','=', self.identification_id),
						 				    ('id','=', self.id)], limit=1)
			employees.sudo().unlink()
			return {'type':      'ir.actions.act_window',
				    'name':      'view_employee1_form_inherit',
				    'res_model': 'hr.employee',
				    'res_id':    self.found_employee,
				    'view_type': 'form',
				    'view_mode': 'form',
				    'target':    'current',}

	# @api.multi
	def unlink(self):
		user_id = self.env.user
		if user_id.id != self.env.ref('base.user_root').id:
			raise ValidationError(_('لا يمكنك حذف الموظف'))
		else:
			try:
				user = self.user_id
				super(Employee, self).unlink()
				if user:
					user.unlink()
			except:
				raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))

	@api.onchange('work_email')
	def change_password(self):
		if self.user_id and self.work_email:
			self.user_id.partner_id.write({'email': self.work_email})

	# @api.one
	def send_passwd(self):
		prms = {}

		headers = {
			'content-type': 'application/json',
		}
		user_system_id = self.env.user.id
		self = self.sudo()		
		
		work_email = self.work_email
		user = self.user_id
		
		if not user:
			raise ValidationError('! هذا الموظف لا يمتلك مستخدم')
		
		if not user.partner_id.email:
			if work_email:
				user.partner_id.write({'email':     work_email,
									
									   'write_uid': user_system_id})
			else:
				raise ValidationError('! حدد إيميل العمل ')
		if user.id == 24329 or user.id == 25530:
			pass
		else:
			n = 4
			range_start = 10 ** (n - 1)
			range_end = (10 ** n) - 1
			passwd = str(randint(range_start, range_end))

			self.write({'passwd':    passwd,

						'write_uid': user_system_id})

			user.write({'password':  passwd,

						'write_uid': user_system_id})

			self.env['mk.general_sending'].send_by_template('mk_send_pass_employee', str(self.id))

			message = self.env['mk.sms_template'].search([('code', '=', 'mk_send_pass')],limit=1)
			message = message[0].sms_text

			mobile_phone = self.mobile_phone

			if mobile_phone:
				message = re.sub(r'val1', self.passwd, message).strip()

				department_id = self.env['hr.department'].search([('id', '=', 42)])

				if department_id.send_time:
					hr_time = int(department_id.send_time)
					prms[department_id.gateway_config.time_send] = str(hr_time) + ":" + str(int((department_id.send_time - hr_time) * 60)) + ":" + '00'
				prms[department_id.gateway_config.user] = department_id.gateway_user
				prms[department_id.gateway_config.password] = department_id.gateway_password
				prms[department_id.gateway_config.sender] = department_id.gateway_sender
				prms[department_id.gateway_config.to] = '966' + mobile_phone
				prms[department_id.gateway_config.message] = message

				url = department_id.gateway_config.url

				if prms:
					try:
						response = requests.post(url, data=json.dumps(prms), headers=headers)
					except:
						pass
		
	@api.model
	def reset_password(self, registeration_code):
		user_id = self.env.ref('mk_student_register.portal_user_id')
		prms = {}
		headers = {
			'content-type': 'application/json',
		}

		n = 4
		range_start = 10 ** (n - 1)
		range_end = (10 ** n) - 1
		passwd = randint(range_start, range_end)

		teacher = self.sudo().search([('registeration_code','=',registeration_code)], limit=1)

		if not teacher:
			teacher = self.sudo().search([('identification_id','=',registeration_code)], limit=1)
		if teacher:
			user = teacher.user_id

			if user.id == SUPERUSER_ID:
				return {'result': 'لا يمكنك تغيير كلمة مرور الأدمين'}

			if not user:
				return {'result': '! هذا الموظف لا يمتلك مستخدم'}

			email = teacher.work_email

			if not email:
				return {'result': '! يجب إضافة إيميل التواصل للموظف'}
			if user.id == 24329 or user.id == 25530:
				pass
			else:
				teacher.sudo(user_id.id).passwd = passwd
				user.sudo(user_id.id).write({'password': passwd,})
				self.env['mk.general_sending'].sudo(user_id.id).send_by_template('mk_send_pass_employee', str(teacher.id))

				mobile_phone = teacher.mobile_phone

				if mobile_phone:
					try:
						message = self.env['mk.sms_template'].search([('code', '=', 'mk_send_pass')], limit=1)
						message = message[0].sms_text
						message = re.sub(r'val1', str(passwd), message).strip()

						department_id = self.env['hr.department'].search([('id', '=', 42)])


						if department_id.send_time:
							hr_time = int(department_id.send_time)
							prms[department_id.gateway_config.time_send] = str(hr_time) + ":" + str(int((department_id.send_time - hr_time) * 60)) + ":" + '00'
						prms[department_id.gateway_config.user] = department_id.gateway_user
						prms[department_id.gateway_config.password] = department_id.gateway_password
						prms[department_id.gateway_config.sender] = department_id.gateway_sender
						prms[department_id.gateway_config.to] = '966' + mobile_phone
						prms[department_id.gateway_config.message] = message


						url = department_id.gateway_config.url

						if prms:
							response = requests.post(url, data=json.dumps(prms), headers=headers)
							if response.json().get('code') != "1":
								msg = 'البيانات الخاصة ببوابة ارسال الرسائل القصيرة ب مركز ' + ' "' + department_id.name + '" ' + ' ' + 'خاطئة' + '!'
								raise ValidationError(msg)
					except:
						pass

			return {'result': 3}

		return {'result': 'رقم التسجيل أو الهوية غير مسجل'}
	
	def accept(self):
		gender = 'male,female'
		
		user_system_id = self.env.user.id
		self = self.sudo()		
		
		category2 = self.category2
		user = self.user_id
		identification_id = self.identification_id
		department_id = self.department_id.id
		
		new_user = False
		
		if not user:
			n = 4
			range_start = 10 ** (n - 1)
			range_end = (10 ** n) - 1
			gpass = randint(range_start, range_end)
			existing_user = self.env['res.users'].search([('login', '=', identification_id),
														  '|', ('active', '=', True),
														       ('active', '=', False)], limit=1)
			if existing_user:
				user = existing_user
				existing_user.write({'active': True})
				user.write({'name': self.name,
						    'password': gpass,
						    'department_id': department_id,
						    'department_ids': [(6, 0, [])],
						    'write_uid': user_system_id, })
			else:
				user = self.env['res.users'].create({'name': self.name,
													 'login': identification_id,
													 'password': gpass,
													 'department_id': department_id,

													 'create_uid': user_system_id,
													 'write_uid': user_system_id, })
				new_user = True

			self.write({'passwd':  gpass,
					    'user_id': user.id,
					    'write_uid':     user_system_id,})

			if category2 == 'center_admin':
				if self.center_admin_category == 'both':
					gender = 'male,female'

				elif self.center_admin_category == 'female':
					gender = 'female'

				elif self.center_admin_category == 'male':
					gender = 'male'

				department_ids = [department_id] + [dep.id for dep in self.department_ids]
				user.write({'department_ids': [(4, dep_id) for dep_id in department_ids],
							'gender':         gender,

							'write_uid':      user_system_id,})

			elif category2 == 'edu_supervisor':
				genders = set([])
				for mosq in self.mosque_sup:
					genders.add(mosq.categ_id.mosque_type)

				if len(genders) > 1:
					gender = 'male,female'
				elif genders:
					gender = list(genders)[0]

				user.write({'mosque_ids': [(4, mosque_sup_id) for mosque_sup_id in self.mosque_sup.ids],
						    'gender':     gender,

						    'write_uid':     user_system_id,})

			else:
				genders = set([])
				for mosq in self.mosqtech_ids:
					genders.add(mosq.categ_id.mosque_type)

				if len(genders) > 1:
					gender = 'male,female'
				elif genders:
					gender = list(genders)[0]

				user.write({'mosque_ids': [(6,0,self.mosqtech_ids.ids)],
					        'gender':     gender,

					        'write_uid':  user_system_id,})

		elif user.login == identification_id:
			n = 4
			range_start = 10**(n-1)
			range_end = (10**n)-1
			gpass = randint(range_start, range_end)
			self.write({'passwd':    gpass,
					
					    'write_uid': user_system_id,})

			user.write({'password': gpass,
					    
					    'write_uid':     user_system_id})

		elif user and user.login != identification_id:
			n = 4
			range_start = 10**(n-1)
			range_end = (10**n)-1
			gpass = randint(range_start, range_end)

			users_replaced = self.env['res.users'].sudo().search([('login','=',identification_id)], limit=1)
			
			if users_replaced:
				user = users_replaced
				self.write({'passwd':    gpass,
						    'user_id':   user.id,
						    
						    'write_uid': user_system_id,})
				
				user.write({'password':  gpass,
								
							'write_uid': user_system_id,})

			else:
				self.write({'passwd':    gpass,
						
						    'write_uid': user_system_id,})

				user.write({'password':  gpass,
							'login':     identification_id,
								   
						    'write_uid': user_system_id,})

		if category2 == 'admin':
			if self.mosqtech_ids:
				self.mosqtech_ids.write({'responsible_id':  self.id,
										 'write_uid':       user_system_id,})
		if category2 == 'supervisor':
			if self.mosqtech_ids:
				for mosque in self.mosqtech_ids:
					has_permission =self.env['mosque.supervisor.request'].search([('mosque_id', '=',mosque.id ),
																				  ('mosque_admin_id', '=',self.id ),
																				  ('state', '=', 'accept')], limit=1)
					if has_permission:
						mosque.write({'mosque_admin_id': self.id, 'write_uid':      user_system_id, })
				
		elif category2 == 'center_admin':						
			department_object = self.env['hr.department'].sudo().search([('id','=',department_id)])
			if department_object.manager_id:
				department_object[0].write({'manager_id': self.id,
										
										    'write_uid':     user_system_id,})

			elif department_object:
				department_object[0].write({'manager_id': self.id,
												   
										    'write_uid':  user_system_id,})               
		
		user.partner_id.write({'email':        self.work_email,
							   'identity_no':  identification_id,
							   'mobile':       self.work_phone,
							   
							   'write_uid':     user_system_id,})
		
		user.write({'lang':      'ar_SY',
				
				    'write_uid': user_system_id,})

		self.write({'state':        'accept',
			        'user_id':      user.id,
			        'salary_donor': 'society',
			        
			        'write_uid': user_system_id,})

		if self.job_id.is_role and self.job_id.role_id:
			self.env['res.users.role.line'].create({'department_id': department_id,
													'user_id':       user.id,
													'role_id':       self.job_id.role_id.id,

													'create_uid':    user_system_id,
													'write_uid':     user_system_id,})
			
			groups = self.job_id.role_id.group_id.implied_ids.ids + [self.job_id.role_id.group_id.id]
			
			if groups:
				user.write({'groups_id': [(6,0,groups)],
	
							'write_uid': user_system_id})

		if category2 == 'admin_center':
			self.write({'salary_donor': 'center',

					    'write_uid':     user_system_id,})
			
		elif category2 == 'admin' or category2 == 'supervisor':
			self.write({'salary_donor': 'masjed',

					    'write_uid':     user_system_id})
		
		else:
			self.write({'salary_donor': 'society',

					    'write_uid':     user_system_id})
		
		if new_user :
				self.send_passwd()

	def synchronize_mosque_to_user(self):
		self = self.sudo()
		department_id = self.department_id.id
		category2= self.category2
		user=self.user_id
		gender=''
		genders = set([])

		if category2 == 'center_admin':
			department_ids = [department_id] + [dep.id for dep in self.department_ids]
			center_admin_category = self.center_admin_category
			if center_admin_category == 'both':
				gender = 'male,female'

			elif center_admin_category == 'female':
				gender = 'female'

			elif center_admin_category == 'male':
				gender = 'male'
			user.write({'department_ids': [(4, dep_id) for dep_id in department_ids],
						'department_id':  department_id,
						'gender'	: gender})

		elif category2 == 'edu_supervisor':
			for mosq in self.mosque_sup:
				genders.add(mosq.categ_id.mosque_type)
				if len(genders) > 1:
					gender = 'male,female'
				else:
					gender = list(genders)[0]
			user.write({'mosque_ids': [(6, 0, self.mosque_sup.ids)],
						'gender'	: gender})

		else:
			for mosq in self.mosqtech_ids:
				genders.add(mosq.categ_id.sudo().mosque_type)

				if len(genders) > 1:
					gender = 'male,female'
				else:
					gender = list(genders)[0]
			user.write({'mosque_ids': [(6, 0, self.mosqtech_ids.ids)],
						'gender'	: gender})

	# @api.one
	def draft(self):
		if self.category == 'admin':
			mosque_object = self.env['mk.mosque'].sudo().search([('id','=',self.mosque_id.id)])
			if mosque_object:
				mosque_object[0].sudo().write({'responsible_id': False})
		self.write({'state':'draft',})

	# @api.one
	def write(self, vals):
		user_id = self.env.user
		if user_id.id != self.env.ref('base.user_root').id:
			if 'active' in vals and vals.get('active') == False and not user_id.has_group('mk_master_models.archive_employee_group'):
				raise ValidationError('عذرا ليس لديك صلاحية أرشفة الموظفين')
		if self.registeration_code == False :
			if self.category == 'supervisor':
				sequence = self.env['ir.sequence'].get('mk.mosque.supervisor.serial')

			elif self.category == 'teacher':
				sequence = self.env['ir.sequence'].get('mk.ep.teacher.serial')

			elif self.category == 'admin':
				sequence = self.env['ir.sequence'].get('mk.mosque.responsiable.serial')

			elif self.category == 'center_admin':
				sequence = self.env['ir.sequence'].get('mk.center.manager.serial')
			else:
				sequence = self.env['ir.sequence'].get('mk.managment.serial')
			vals['registeration_code'] = sequence
		rec = super(Employee, self).write(vals)

		vals_user = {}
		new_mosque_ids = []
		genders = set([])
		gender = ''		
		
		category2 = self.category2
		
		if category2 == 'edu_supervisor' and (('category2' in vals) or ('mosque_sup' in vals)):
			for mosq in self.mosque_sup:
				new_mosque_ids += [mosq.id]
				genders.add(mosq.categ_id.mosque_type)
				
				if len(genders) > 1:
					gender='male,female'					
				else:
					gender = list(genders)[0]
					
		elif category2 == 'center_admin' and (('category2' in vals) or ('center_admin_category' in vals)):
			center_admin_category = self.center_admin_category
			if center_admin_category == 'both':
				gender = 'male,female'

			elif center_admin_category == 'female':
				gender = 'female'

			elif center_admin_category == 'male':
				gender = 'male'
				
			vals_user = {'mosque_ids': []}
				
		elif 'mosqtech_ids' in vals:

			for mosq in self.mosqtech_ids:
				new_mosque_ids += [mosq.id]				
				genders.add(mosq.categ_id.sudo().mosque_type)
				
				if len(genders) > 1:
					gender = 'male,female'
				else:
					gender = list(genders)[0]
					
			if self.category == 'admin' and self.state == 'accept':
				self.mosqtech_ids.write({'responsible_id': self.id}) 
				old_mosques = self.env['mk.mosque'].sudo().search([('responsible_id','=',self.id),
															 	   ('id','not in',new_mosque_ids)])  
				if old_mosques:
					old_mosques.sudo().write({'responsible_id':False})

			if self.category == 'supervisor' and self.state == 'accept':
				for mosque in self.mosqtech_ids:
					has_permission =self.env['mosque.supervisor.request'].search([('mosque_id', '=',mosque.id ),
																				  ('mosque_admin_id', '=',self.id ),
																				  ('state', '=', 'accept')], limit=1)
					if has_permission:
						mosque.write({'mosque_admin_id': self.id})
				old_mosques = self.env['mk.mosque'].sudo().search([('mosque_admin_id','=',self.id),
															 	   ('id','not in',new_mosque_ids)])
				if old_mosques:
					old_mosques.sudo().write({'mosque_admin_id':False})
					
		if gender:
			vals_user.update({'gender': gender})
			
		if new_mosque_ids:
			vals_user.update({'mosque_ids': [(6, 0, new_mosque_ids)]})
			
		department_id = self.department_id.id
		if 'department_id' in vals:			
			vals_user.update({'department_id':  department_id})
			
		if category2 == 'center_admin' and (('category2' in vals) or ('department_id' in vals) or ('department_ids' in vals)):
			department_ids = [department_id] + [dep.id for dep in self.department_ids]
			vals_user.update({'department_ids': [(6, 0,  department_ids)]})
		elif category2 != 'center_admin':
			vals_user.update({'department_ids': [(6, 0,  [])]})
		
		if 'name' in vals:
			vals_user.update({'name': self.name})
			
		if 'identification_id' in vals:
			vals_user.update({'login': self.identification_id})

		if 'active' in vals:
			vals_user.update({'active': self.active})

		if 'work_email' in vals:
			vals_user.update({'email': self.work_email})

		if self.user_id:
			self.user_id.sudo().write(vals_user)
		return rec

	@api.model
	def cron_check_emails(self):
		users = self.env['res.users'].search([])
		users_with_wrong_emails = []
		total = len(users)
		i = 0
		for user in users:
			i += 1
			try:
				tools.formataddr((user.name, user.email))
			except Exception as e:
				emp = self.env['hr.employee'].search([('identification_id', '=', user.login)], limit=1)
				if emp.work_email:
					users_with_wrong_emails.append(user.id)

	# @api.multi
	def toggle_active(self):
		nbr_mosq = len(self.mosqtech_ids.ids)
		if self.active and nbr_mosq > 1:
			raise ValidationError(_('لا يمكنك أرشفة هذا الموظف لارتباطه بمدرسة أخرى'))
		else:
			super(Employee, self).toggle_active()
	
	@api.model
	def _create_user(self, cron_mode=True):
		for record in self:
			if record.user_id == False:
				self.env['res.users'].create({'login':    record.registeration_code,
											  'password': '111'})
		return True
				
	# @api.one
	def reject(self):
		self.write({'state':'reject'})

	@api.model
	def relate_employee_to_mosque(self, vals):
		if vals['mobile_phone'] == False:
			del vals['mobile_phone']
		rec = self.env['hr.employee'].search([('identification_id', '=', vals['identification_id']),
											  '|', ('active', '=', True),
											  	   ('active', '=', False)])

		mosque = self.env['mk.mosque'].search([('code', '=', vals['code']),
											   '|', ('active', '=', True),
											   ('active', '=', False)], limit=1)

		if mosque:
			mosque_id = mosque.id
		else:
			raise ValidationError (('المسجد غير موجود '))
		if rec:
			employee_id=rec.id
			department = self.env['hr.department'].search([('department_code', '=', vals['department_code'])])
			vals['department_id'] = department.id
			department_id=vals['department_id']
			if not rec.category2:
				job = self.env.ref('__export__.hr_job_1210')
				vals.update({'job_id': job and job.id or False,
							 'category': 'admin',
							 'category2': 'admin',
							 'flag': True,
							 'flag2': False,
							 'department_id': department_id,
							 'mosqtech_ids': [(4, mosque_id)]})
				create_taklif_and_send_sms=self.create_supervisor_request_and_send_sms(employee_id,rec,mosque_id, department_id,mosque, vals)

			else:
				if  (rec.category2 == 'admin') and (rec.department_id.id == vals['department_id']):
					job = self.env.ref('__export__.hr_job_1210')
					vals.update({'job_id': job and job.id or False,
								 'flag': True,
								 'flag2': False,
								 'mosqtech_ids': [(4, mosque_id)]})
					rec.write(vals)
					create_taklif_and_send_sms = self.create_supervisor_request_and_send_sms(employee_id, rec, mosque_id,department_id, mosque, vals)
				else:
					pass

		else:
			vals["mosque_id"]=mosque_id
			vals['create_admin_mosq'] = True
			vals['category']=None
			department= self.env['hr.department'].search([('department_code','=',vals['department_code'])])
			vals['department_id']= department.id
			del vals['code']
			del vals['department_code']
			rec = self.env['hr.employee'].create(vals)
		mobile_phone = rec.mobile_phone
		if mobile_phone and mosque.responsible_id.id == rec.id :
			suprv_department_id = rec.department_id
			if suprv_department_id.gateway_user and suprv_department_id.gateway_sender and suprv_department_id.gateway_password:
				pass
			else:
				suprv_department_id = self.env['hr.department'].search([('id', '=', 42)])
			values = {
			  "userName": suprv_department_id.gateway_user,
			  "numbers": '966'+rec.mobile_phone,
			  "userSender": suprv_department_id.gateway_sender,
			  "apiKey": suprv_department_id.gateway_password,
			  "msg": str( " نفيدك بقبول طلب فتح الحلقة"+ mosque.name + "مرحبا عزيزي مشرف حلقة "),
			}

			headers = {
				'Content-Type': 'application/json'
			}
			try:
				response = requests.post('https://www.msegat.com/gw/sendsms.php', data=values, headers=headers)
			except:
				pass
		return rec.id


	@api.model
	def create_supervisor_request_and_send_sms(self,employee_id,rec,mosque_id, department_id,mosque, vals):
		supervisor_request=self.env['mosque.supervisor.request'].create({'date_request': fields.Datetime.now(),
													  'permision_type': 'te',
													  'employee_id': employee_id,
													  'identification_id': rec.identification_id,
													  'mosque_id': mosque_id,
													  'center_id': department_id,
													  'categ_type': mosque.categ_id.mosque_type,
													  'is_valid': True})
		supervisor_request.action_accept()
		rec_write = self.env['hr.employee'].search([('id', '=', employee_id)]).write(vals)
		# send email
		template = self.env.ref('mk_master_models.new_employee_send_doc', raise_if_not_found=False)
		if template:
			b = template.send_mail(rec.id, force_send=True)

		# send sms
		headers = {
			'Content-Type': 'application/json'
		}
		prms = {}
		mobile_phone = rec.mobile_phone
		suprv_department_id = rec.department_id
		department_phone_number = suprv_department_id.phone_number
		if mobile_phone:
			message = "نشكر لكم فتح الحلقة ونأمل منكم تعبئة نموذج موافقة جماعة المسجد(https://bit.ly/MosqueConsent )وإرسالة للمركز. رقم المركز:"
			if department_phone_number:
				message += str(department_phone_number)
			prms[suprv_department_id.gateway_config.user] = suprv_department_id.gateway_user
			prms[suprv_department_id.gateway_config.password] = suprv_department_id.gateway_password
			prms[suprv_department_id.gateway_config.sender] = suprv_department_id.gateway_sender

			if not (prms[suprv_department_id.gateway_config.user] or prms[
				suprv_department_id.gateway_config.password] or prms[suprv_department_id.gateway_config.sender]):
				suprv_department_id = self.env['hr.department'].search([('id', '=', 42)])
				prms[suprv_department_id.gateway_config.user] = suprv_department_id.gateway_user
				prms[suprv_department_id.gateway_config.password] = suprv_department_id.gateway_password
				prms[suprv_department_id.gateway_config.sender] = suprv_department_id.gateway_sender

			prms[suprv_department_id.gateway_config.to] = '966' + mobile_phone
			prms[suprv_department_id.gateway_config.message] = message
			url = suprv_department_id.gateway_config.url
			try:
				response = requests.post(url, data=json.dumps(prms), headers=headers)
			except Exception as Argument:
				pass

	# @api.model
	# def create_from_portal(self, values):
	# 	# values = values['params']
	# 	db = ERP_DB
	# 	user = ERP_USER
	# 	password = ERP_PASSWORD
	# 	common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(ERP_HOST))
	# 	models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(ERP_HOST))
	# 	uid = common.authenticate(db, user, password, {})
	# 	registeration_code = self.env['ir.sequence'].get('mk.mosque.responsiable.serial')
	# 	country_id = self.env['res.country'].search([('id', '=', values.get('country_id'))], limit=1)
	# 	applicant_vals = {
	# 		"mosque_id":          values.get('mosque_id'),
	# 		"identification_id":  values.get('identification_id'),
	# 		"registeration_code": registeration_code,
	# 		"name":               values.get('name'),
	# 		"mobile_phone":       values.get('mobile_phone'),
	# 		"work_email":         values.get('work_email'),
	# 		"country_id":         country_id.code,
	# 		"gender":             values.get('gender'),
	# 		"marital":            values.get('marital'),
	# 	}
	#
	# 	applicant_details = {}
	# 	res = models.execute_kw(db, uid, password, 'hr.applicant', 'create_applicant', [applicant_vals])
	# 	if res:
	# 		applicant_details.update({'admin_mosque_id': res,
	# 								  'registeration_code': registeration_code})
	# 		employee=self.env['hr.employee'].search([('identification_id','=', applicant_vals['identification_id']),
	# 												 '|',('active','=',True),
	# 												     ('active','!=',True)], limit=1)
	# 		if employee:
	# 			employee.write({'active': True})
	# 		else:
	# 			applicant_vals["mosque_id"] = False
	# 			applicant_vals['category'] = False
	# 			applicant_vals['department_id'] = False
	# 			applicant_vals['country_id'] = country_id.id
	#
	# 			new_employee = self.env['hr.employee'].sudo().create(applicant_vals)
	# 	return applicant_details

	@api.model
	def create(self, vals):
		mosque_id = vals.get('mosque_id', False)
		mosque = self.env['mk.mosque'].browse(mosque_id)
		department_id = mosque.center_department_id.id

		if vals.get('create_admin_mosq', False):
			job = self.env.ref('__export__.hr_job_1210')
			vals.update({'job_id':        job and job.id or False,
						 'category':      'admin',
						 'category2':     'admin',
						 'flag':          True,
						 'flag2':         False,
						 'department_id': department_id,
						 'mosqtech_ids':  [(4, mosque_id)]})

		if vals['category'] == 'others':
			vals['state'] = 'accept'

		if vals.get('flag2', False) == True:
		# if vals['flag2'] == True:
			employee = self.sudo().search([('identification_id','=', vals['identification_id'])], limit=1)
			user = self.sudo().search([('user_id','=',self.env.user.id)])

			if vals['mosque_new'] and employee:
				global mosque_new
				mosque_new = vals['mosque_new']
				vals['department_id'] = user.department_id.id
				vals['mosqtech_ids'] = [(4, mosq_id) for mosq_id in user.mosqtech_ids.ids]
				vals['name'] = "."
				vals['flag2'] = False

		vals['flag'] = True

		rec = super(Employee, self).create(vals)

		if rec['category'] == 'supervisor':
			rec['registeration_code'] = self.env['ir.sequence'].get('mk.mosque.supervisor.serial')

		elif rec['category'] == 'teacher':
			rec['registeration_code'] = self.env['ir.sequence'].get('mk.ep.teacher.serial')

		elif rec['category'] == 'admin':
			rec['registeration_code'] = self.env['ir.sequence'].get('mk.mosque.responsiable.serial')

		elif rec['category'] == 'center_admin':
			rec['registeration_code'] = self.env['ir.sequence'].get('mk.center.manager.serial')
		else:
			rec['registeration_code'] = self.env['ir.sequence'].get('mk.managment.serial')

		if vals.get('create_admin_mosq', False):
			employee_id = rec.id
			mosque.responsible_id = employee_id
			mosque.check_parking_mosque
			# self.env['mosque.permision'].create({'type_process': 'new',
			# 													  'date_request': fields.Datetime.now(),
			# 													  'responsible_id': employee_id,
			# 													  'center_id': department_id,
			# 													  'categ_id': mosque.categ_id.id,
			# 													  'categ_type': mosque.categ_id.mosque_type,
			# 													  'perm_type': 'school_perm' if mosque.categ_id.mosque_type == 'male' else 'mosque_perm',
			# 													  'build_type': mosque.build_type.id,
			# 													  'masjed_id': mosque_id,
			# 													  'register_code': mosque.register_code,
			# 													  'episodes': mosque.episodes,
			# 													  'episode_value': mosque.episode_value,
			# 													  'check_maneg_mosque': mosque.check_maneg_mosque,
			# 													  'check_parking_mosque': mosque.check_parking_mosque,
			# 													  'permision_type': 'te',
			# 													  'city_id': mosque.city_id.id,
			# 													  'area_id': mosque.area_id.id,
			# 													  'district_id': mosque.district_id.id})

			self.env['mosque.supervisor.request'].create({'date_request': fields.Datetime.now(),
																		   'permision_type': 'te',
																		   'employee_id': employee_id,
																		   'identification_id': rec.identification_id,
																		   'mosque_id': mosque_id,
																		   'center_id': department_id,
																		   'categ_type': mosque.categ_id.mosque_type, })

			#send email
			template = self.env.ref('mk_master_models.new_employee_send_doc', raise_if_not_found=False)
			if template:
				b = template.send_mail(rec.id, force_send=True)

			#send sms
			headers = {
				'Content-Type': 'application/json'
			}
			prms = {}
			mobile_phone = rec.mobile_phone
			suprv_department_id = rec.department_id
			department_phone_number = suprv_department_id.phone_number
			if mobile_phone:
				message = "نشكر لكم فتح الحلقة ونأمل منكم تعبئة نموذج موافقة جماعة المسجد(https://bit.ly/MosqueConsent )وإرسالة للمركز. رقم المركز:"
				if department_phone_number:
					message += str(department_phone_number)
				prms[suprv_department_id.gateway_config.user] = suprv_department_id.gateway_user
				prms[suprv_department_id.gateway_config.password] = suprv_department_id.gateway_password
				prms[suprv_department_id.gateway_config.sender] = suprv_department_id.gateway_sender

				if not (prms[suprv_department_id.gateway_config.user] or prms[suprv_department_id.gateway_config.password] or prms[suprv_department_id.gateway_config.sender]):
					suprv_department_id = self.env['hr.department'].search([('id', '=', 42)])
					prms[suprv_department_id.gateway_config.user] = suprv_department_id.gateway_user
					prms[suprv_department_id.gateway_config.password] = suprv_department_id.gateway_password
					prms[suprv_department_id.gateway_config.sender] = suprv_department_id.gateway_sender

				prms[suprv_department_id.gateway_config.to] = '966' + mobile_phone
				prms[suprv_department_id.gateway_config.message] = message
				url = suprv_department_id.gateway_config.url
				try:
					response = requests.post(url, data=json.dumps(prms), headers=headers)
				except Exception as Argument:
					pass
		return rec
	
	@api.model
	def cron_check_id_valid0(self, id_emp, pack):
		employees = self.search([('id','>',id_emp),'|',('active','=',True), ('active','!=',True)], order="id", limit=pack)
		i = 0
		j = 0
		d = 0
		y = 0
		for employee in employees:
			identification_id = employee.identification_id
			if not identification_id:
				continue
			emp_id = employee.id

			res = self.check_id_validity(identification_id, emp_id)
			if isinstance(res, pycompat.string_types):
				employee.data_clean = 'merge'
				d += 1
			else:
				employee.data_clean = 'check_id'
				i += 1
						
			y += 1
			j += 1

	@api.model
	def cron_check_id_valid(self, id_emp):
		employees = self.search([('id','>',id_emp),'|',('active','=',True), ('active','!=',True)], order="id", limit=3000)
		i = 0
		j = 0
		d = 0
		y = 0
		for employee in employees:
			identification_id = employee.identification_id
			if not identification_id:
				continue
			emp_id = employee.id
			res = self.check_id_validity(identification_id, emp_id)
			if isinstance(res, pycompat.string_types):
# 				user_emp = employee.user_id
# 				if user_emp:
# 					user_emp.active = False
# 				employee.write({'active':     False,
# 							    'data_clean': 'check_id'})
				
				masajeds = self.env['mk.mosque'].search([('responsible_id','=',emp_id),'|',('active','=',True),('active','!=',True)])
				prepas = self.env['mk.student.prepare'].search([('name','=',emp_id)])
				perms = self.env['mosque.permision'].search([('responsible_id','=',emp_id)])
				
				is_del = True
				for ep in employee.episode_ids:
					if ep.academic_id.id == 19:
						is_del = False
						break
					
					links = []
					for link in ep.link_ids:
						if link.state == 'accept':
							is_del = False
							break						
						links += [link.id]
					
					test_sessions = self.env['student.test.session'].search([('student_id','in',links)])
					if test_sessions:
						is_del = False
						break
					
				if is_del:
					for ep in employee.episode_unactv_ids:
						if ep.academic_id.id == 19:
							is_del = False
							break

						links = []
						for link in ep.link_ids:
							if link.state == 'accept':
								is_del = False
								break
							
							links += [link.id]
						
						test_sessions = self.env['student.test.session'].search([('student_id','in',links)])
						if test_sessions:
							is_del = False
							break

				if is_del:
					for m in masajeds:
						is_del = False
						break

				if is_del:
					for ep in employee.episode_ids:
						ep.unlink()
					
					for ep in employee.episode_unactv_ids:
						ep.unlink()
					
					for m in masajeds:
						m.unlink()
					
					for p in prepas:
						p.unlink()
					
					for p in perms:
						p.unlink()
					
					employee.unlink()
					d += 1
					
																
				i += 1
			
			if y == 20:
				y = 0
			
			y += 1				
			j += 1			 

	@api.model
	def cron_del_same_id(self):		
		self = self.sudo()
		sql_query = """select identification_id, count(*)
						from hr_employee
						
						group by identification_id
						having count(*) > 1
						order by identification_id;
				"""	
		self.env.cr.execute(sql_query)
		results = self.env.cr.dictfetchall()
				
		i = 0
		j = 0
		
		sql_query = ''
		t = len(results)
		for line in results:
			i += 1				

			identification_id = line.get('identification_id')
			if not identification_id:
				continue
			
			j += 1

			emps = self.search([('identification_id','=',identification_id),
										  '|',('active','=',True),
										      ('active','!=',True)
										      ], limit=2)
			emp1 = emps[0]
			emp2 = emps[1]
			
			resource_emp = emp1.resource_id
			
			is_res = False
			if resource_emp.id == emp2.resource_id.id:
				is_res = True
				
			emp_unactive = 0
			if not emp1.active:
				emp_unactive += 1
				
			if not emp2.active:
				emp_unactive += 2
			
			del_emp = False
			if emp_unactive == 1:
				del_emp = emp1
			elif emp_unactive == 2:
				del_emp = emp2
			
			masajeds1 = self.env['mk.mosque'].search([('responsible_id','=',emp1.id),'|',('active','=',True),('active','!=',True)])
			masajeds2 = self.env['mk.mosque'].search([('responsible_id','=',emp2.id),'|',('active','=',True),('active','!=',True)])

			if not del_emp:
				emp_unresp = 0
				if not masajeds1:
					emp_unresp += 1
				if not masajeds2:
					emp_unresp += 2
													
				if emp_unresp == 1:
					del_emp = emp1
				elif emp_unresp == 2:
					del_emp = emp2					
			
			emp_unepisode = 0
			if not del_emp:				
				if not emp1.episode_ids and not emp1.episode_unactv_ids:
					emp_unepisode += 1
				if not emp2.episode_ids and not emp2.episode_unactv_ids:
					emp_unepisode += 2
					
				if emp_unepisode == 0:
					emp_unepisode = 0
					if not emp1.episode_ids and emp1.episode_unactv_ids:
						emp_unepisode += 1
					if not emp2.episode_ids and emp2.episode_unactv_ids:
						emp_unepisode += 2
						
					if emp_unepisode == 0:
						emp_unepisode = 0
						if emp1.episode_ids and not emp1.episode_unactv_ids:
							emp_unepisode += 1							
						if emp2.episode_ids and not emp2.episode_unactv_ids:
							emp_unepisode += 2

						if emp_unepisode == 3:
							emp_unepisode = 0
							links1 = []
							for ep in emp1.episode_ids:
								for link in ep.link_ids:
									links1 += [link]
									
							links2 = []
							for ep in emp2.episode_ids:
								for link in ep.link_ids:
									links2 += [link]
																	
							if not links1:
								emp_unepisode += 1
							if not links2:
								emp_unepisode += 2							
							
					elif emp_unepisode == 3:
						emp_unepisode = 0
						links1 = []
						for ep in emp1.episode_unactv_ids:
							for link in ep.link_ids:
								links1 += [link]
								
						links2 = []
						for ep in emp2.episode_unactv_ids:
							for link in ep.link_ids:
								links2 += [link]
																
						if not links1:
							emp_unepisode += 1
						if not links2:
							emp_unepisode += 2
													
				if emp_unepisode == 1:
					del_emp = emp1
				elif emp_unepisode == 2:
					del_emp = emp2
					
			emp1_preps = self.env['mk.student.prepare'].search([('name','=',emp1.id)])
			emp2_preps = self.env['mk.student.prepare'].search([('name','=',emp2.id)])
			
			if not del_emp:
				if not emp1_preps:
					del_emp = emp1
				elif not emp2_preps:
					del_emp = emp2
				
			user_emp1 = emp1.user_id
			user_emp2 = emp2.user_id
			
			if not del_emp and (user_emp1 or user_emp2):
				if not user_emp1:
					del_emp = emp1
				if not user_emp2:
					del_emp = emp2
			
			user_emp = user_emp1
			user1_login = False
			try:
				user1_login = user_emp1.login					
			except:
				user_emp1 = False
				user_emp = user_emp2
				if not del_emp:
					del_emp = emp1
			
			user2_login = False
			try:
				user2_login = user_emp2.login								
			except:
				user_emp2 = False
				if not del_emp:
					del_emp = emp2
					
			if not user1_login and not user2_login:
				user_emp = False

			if user_emp1 and user_emp2 and (user_emp1.id != user_emp2.id) and (user_emp2.login == emp2.identification_id):
				user_emp = user_emp2
				if not del_emp:
					del_emp = emp1
				
			if not del_emp:
				del_emp = emp2
			
			resource_emp = False
			if is_res:
				resource_emp = self.env['resource.resource'].create({'name': 'name_resource'+identification_id})
				del_emp.resource_id = resource_emp.id
				
			emp_pers = emp1
			if del_emp.id == emp1.id:
				emp_pers = emp2
				if emp1_preps:
					emp1_preps.write({'name': emp_pers.id})
					
				if masajeds1:
					masajeds1.write({'responsible_id': emp_pers.id})
					
				perms1 = self.env['mosque.permision'].search([('responsible_id','=',emp1.id)])
				if perms1:
					try:
						perms1.write({'responsible_id': emp_pers.id})
					except:
						for perm in perms1:
							mosq_state = perm.masjed_id.active
							if not mosq_state: 
								perm.masjed_id.active = True
							
							perm.write({'responsible_id': emp_pers.id})
							
							if not mosq_state: 
								perm.masjed_id.active = False							
					
			else:
				if emp2_preps:
					emp2_preps.write({'name': emp_pers.id})
				
				if masajeds2:
					masajeds2.write({'responsible_id': emp_pers.id})
					
				perms2 = self.env['mosque.permision'].search([('responsible_id','=',emp2.id)])
				if perms2:
					try:
						perms2.write({'responsible_id': emp_pers.id})
					except:
						for perm in perms2:
							mosq_state = perm.masjed_id.active
							if not mosq_state: 
								perm.masjed_id.active = True
							
							perm.write({'responsible_id': emp_pers.id})
							
							if not mosq_state: 
								perm.masjed_id.active = False						
						
			for ep in del_emp.episode_ids:
				try:
					ep.write({'teacher_id': emp_pers.id})
				except:
					ep.write({'teacher_id': False})

			for ep in del_emp.episode_unactv_ids:
				try:
					ep.write({'teacher_id': emp_pers.id})
				except:
					ep.write({'teacher_id': False})
					
			if not del_emp.active:
				del_emp.active = True
					
			del_emp.unlink()
			
			if (user1_login or user2_login) and user_emp.login != identification_id:
				other_emp = self.env['hr.employee'].search([('identification_id','=',user_emp.login)], limit=1)
				if other_emp:
					user_emp = False
					emp_pers.user_id = False			
			
			if user_emp and ((not emp_pers.user_id) or emp_pers.user_id.id != user_emp.id):				
				emp_pers.user_id = user_emp.id
			
			if resource_emp:
				resource_emp.unlink()
			
			_logger.info('\n  end  %s \n', j)
		
		_logger.info('\nEND \n')
		
	@api.model
	def cron_merge_emp_same_id(self):		
		#employees = self.search([], order='identification_id, id')
		sql_query = """select identification_id, count(*)
						from hr_employee
						group by identification_id
						having count(*) > 1
						order by identification_id;
				"""	
		self.env.cr.execute(sql_query)
		results = self.env.cr.dictfetchall()
		
		unlink_emps = []
		unlink_user_ids = []
		mk_episode_bug = []
		
		i = 0
		sql_query = ''
		_logger.info('\nSTART\n')
		for line in results:
			i += 1				

			identification_id = line.get('identification_id')
			if not identification_id:
				continue
			emps_to_merge = self.search([('identification_id','=',identification_id),'|',('active','=',True),('active','!=',True)], order="id")
			nbr_emp = len(emps_to_merge)
			#_logger.info("\n%s   %s\n", nbr_emp, employee.identification_id)
			#if nbr_emp > 1:
			_logger.info("\n%s   %s\n", nbr_emp, identification_id)
			emp_still = emps_to_merge[0]
			emp_still_id = emp_still.id
			
			name = emp_still.name
			work_location = emp_still.work_location
			work_email = emp_still.work_email
			mobile_phone = emp_still.mobile_phone
			kin_phone = emp_still.kin_phone
			work_phone = emp_still.work_phone
			recruit_ids = [recruit.id for recruit in emp_still.recruit_ids]#m2m
			job_id = emp_still.job_id#m2o
			category2 = emp_still.category2
			center_admin_category = emp_still.center_admin_category
			department_id = emp_still.department_id#m2o
			country_id = emp_still.country_id#m2o
			issue_identity = emp_still.issue_identity
			identity_expire = emp_still.identity_expire
			birthday = emp_still.birthday
			gender = emp_still.gender
			marital = emp_still.marital
			salary = emp_still.salary
			salary_donor = emp_still.salary_donor#m2o
			contract_type = emp_still.contract_type
			part_ids = [part.id for part in emp_still.part_ids]#m2m
			user = emp_still.user_id#m2o
			user_ids = []
			
			try:
				user.active
			except:			
				_logger.info("\n%s   %s\n", nbr_emp, identification_id)			
				_logger.info("\n %s \n", user)
				user = False
				_logger.info("\n %s \n", user)
			
			for emp_to_merge in emps_to_merge:
				#_logger.info("\n %s \n", user)
				if emp_to_merge.id != emp_still.id:
					#unlink_emps += [emp_to_merge]
					name_new = emp_to_merge.name
					if not name or (name_new and len(name_new) > len(name)):
						name = name_new
						
					work_location_new = emp_to_merge.work_location
					if not work_location or (work_location_new and len(work_location_new) > len(work_location)):
						work_location = work_location_new

					work_email_new = emp_to_merge.work_email
					if not work_email or (work_email_new and len(work_email_new) > len(work_email)):
						work_email = work_email_new
					
					
					mobile_phone_new = emp_to_merge.mobile_phone
					if not mobile_phone or (mobile_phone_new and len(mobile_phone_new) > len(mobile_phone)):
						mobile_phone = mobile_phone_new
												
					kin_phone_new = emp_to_merge.kin_phone
					if not kin_phone or (kin_phone_new and len(kin_phone_new) > len(kin_phone)):
						kin_phone = kin_phone_new
												
					work_phone_new = emp_to_merge.work_phone
					if not work_phone or (work_phone_new and len(work_phone_new) > len(work_phone)):
						work_phone = work_phone_new
												
					recruit_ids += [recruit.id for recruit in emp_to_merge.recruit_ids]#m2m
					
					job_id_new = emp_to_merge.job_id#m2o
					if not job_id:
						job_id = job_id_new
												
					category2_new = emp_to_merge.category2
					if not category2:
						category2 = category2_new
												
					center_admin_category_new = emp_to_merge.center_admin_category
					if not center_admin_category:
						center_admin_category = center_admin_category_new
												
					department_id_new = emp_to_merge.department_id#m2o
					if not department_id:
						department_id = department_id_new
												
					country_id_new = emp_to_merge.country_id#m2o
					if not country_id:
						country_id = country_id_new
												
					issue_identity_new = emp_to_merge.issue_identity
					if not issue_identity:
						issue_identity = issue_identity_new
												
					identity_expire_new = emp_to_merge.identity_expire
					if not identity_expire:
						identity_expire = identity_expire_new
												
					birthday_new = emp_to_merge.birthday
					if not birthday:
						birthday = birthday_new
												
					gender_new = emp_to_merge.gender
					if not gender:
						gender = gender_new
												
					marital_new = emp_to_merge.marital
					if not marital:
						marital = marital_new
												
					salary_new = emp_to_merge.salary
					if not salary or salary_new > salary:
						salary = salary_new
												
					salary_donor_new = emp_to_merge.salary_donor#m2o
					if not salary_donor:
						salary_donor = salary_donor_new
												
					contract_type_new = emp_to_merge.contract_type
					if not contract_type:
						contract_type = contract_type_new
												
					part_ids += [part.id for part in emp_to_merge.part_ids]#m2m
					
					user_id_new = emp_to_merge.user_id#m2o
					#_logger.info("\nn %s \n", user_id_new)
					if not user:
						user = user_id_new
					elif user_id_new:
						try:
							user_id_new.active
							user_ids += [user_id_new]
						except:			
							_logger.info("\n2%s   %s\n", nbr_emp, identification_id)			
							_logger.info("\n %s \n", user_id_new)
							user = False
							_logger.info("\n %s \n", user_id_new)						
					
					emp_to_merge_id = emp_to_merge.id
					unlink_emps += [emp_to_merge_id]
					class1_objs = self.env['employee.test.session'].search([('emp_id','=',emp_to_merge_id)])
					if class1_objs:
						class1_objs.write({'emp_id': emp_still_id})
						
					class2_objs = self.env['employee.test.session'].search([('teacher','=',emp_to_merge_id)])
					if class2_objs:
						class2_objs.write({'teacher': emp_still_id})
						
					class3_objs = self.env['committee.tests'].search([('examiner_employee_id','=',emp_to_merge_id),'|',('active','=',True),('active','!=',True)])
					if class3_objs:
						class3_objs.write({'examiner_employee_id': emp_still_id})
						
					class4_objs = self.env['committe.member'].search([('member_id','=',emp_to_merge_id)])
					if class4_objs:
						class4_objs.write({'member_id': emp_still_id})
						
					class5_objs = self.env['question.error'].search([('member','=',emp_to_merge_id)])
					if class5_objs:
						class5_objs.write({'member': emp_still_id})	
						
					class6_objs = self.env['student.test.session'].search([('teacher','=',emp_to_merge_id),'|',('active','=',True),('active','!=',True)])
					if class6_objs:
						class6_objs.write({'teacher': emp_still_id})
						
					class7_objs = self.env['mosque.permision'].search([('supervision_id','=',emp_to_merge_id)])
					if class7_objs:
						class7_objs.write({'supervision_id': emp_still_id})
						
					class71_objs = self.env['mosque.permision'].search([('responsible_id','=',emp_to_merge_id)])
					if class71_objs:
						class71_objs.write({'responsible_id': emp_still_id})							
						
					class8_objs = self.env['teacher.test'].search([('teacher_id','=',emp_to_merge_id)])
					if class8_objs:
						class8_objs.write({'teacher_id': emp_still_id})	
						
					class9_objs = self.env['mosque.supervisor.line'].search([('employee_id','=',emp_to_merge_id)])
					if class9_objs:
						class9_objs.write({'employee_id': emp_still_id})
						
					class10_objs = self.env['mosque.supervisor.request'].search([('employee_id','=',emp_to_merge_id)])
					if class10_objs:
						class10_objs.write({'employee_id': emp_still_id})
						
					class11_objs = self.env['mk.productivity.teach'].search([('teacher_id','=',emp_to_merge_id)])
					if class11_objs:
						class11_objs.write({'teacher_id': emp_still_id})
						
					class12_objs = self.env['mk.course.request'].search([('employee_id','=',emp_to_merge_id)])
					if class12_objs:
						class12_objs.write({'employee_id': emp_still_id})	
						
					class14_objs = self.env['mk.course.emp'].search([('emp_id','=',emp_to_merge_id)])
					if class14_objs:
						class14_objs.write({'emp_id': emp_still_id})
						
					class15_objs = self.env['mk.mosque'].search([('teacher_ids','in',[emp_to_merge_id]),'|',('active','=',True),('active','!=',True)])
					for class15_obj in class15_objs:
						teacher15_ids = [teacher15.id for teacher15 in class15_obj.teacher_ids if teacher15.id != emp_to_merge_id] + [emp_still_id]
						class15_obj.write({'teacher_ids': [(6, 0, teacher15_ids)]})	
						
					class16_objs = self.env['mk.mosque'].search([('mosq_other_emp_ids','in',[emp_to_merge_id]),'|',('active','=',True),('active','!=',True)])
					for class16_obj in class16_objs:
						mosq_other_emp_ids = [mosq_other_emp.id for mosq_other_emp in class16_obj.mosq_other_emp_ids if mosq_other_emp.id != emp_to_merge_id] + [emp_still_id]
						class16_obj.write({'mosq_other_emp_ids': [(6, 0, mosq_other_emp_ids)]})		
						
					class17_objs = self.env['mk.mosque'].search([('supervisors','in',[emp_to_merge_id]),'|',('active','=',True),('active','!=',True)])
					for class17_obj in class17_objs:
						supervisors = [supervisor.id for supervisor in class17_obj.supervisors if supervisor.id != emp_to_merge_id] + [emp_still_id]
						class17_obj.write({'supervisors': [(6, 0, supervisors)]})
						
					class18_objs = self.env['committee.test'].search([('examiner_employee_id','=',emp_to_merge_id),'|',('active','=',True),('active','!=',True)])
					if class18_objs:
						class18_objs.write({'examiner_employee_id': emp_still_id})
						
					class19_objs = self.env['mk.test.class.committee'].search([('examiner_employee_id','=',emp_to_merge_id),'|',('active','=',True),('active','!=',True)])
					if class19_objs:
						class19_objs.write({'examiner_employee_id': emp_still_id})	
						
					class20_objs = self.env['mk.attendance.students'].search([('supervisor_id','=',emp_to_merge_id)])
					if class20_objs:
						class20_objs.write({'supervisor_id': emp_still_id})
						
					class21_objs = self.env['mk.transport.management'].search([('supervisor_id','=',emp_to_merge_id)])
					if class21_objs:
						class21_objs.write({'supervisor_id': emp_still_id})
						
					class22_objs = self.env['vehicle.records'].search([('responsible','=',emp_to_merge_id)])
					if class22_objs:
						class22_objs.write({'responsible': emp_still_id})
						
					class23_objs = self.env['vehicle.records'].search([('superviser_id','=',emp_to_merge_id)])
					if class23_objs:
						class23_objs.write({'superviser_id': emp_still_id})		
						
					class24_objs = self.env['event.registrations'].search([('invited','=',emp_to_merge_id)])
					if class24_objs:
						class24_objs.write({'invited': emp_still_id})	
						
					class25_objs = self.env['event.invite'].search([('employee_id','=',emp_to_merge_id)])
					if class25_objs:
						class25_objs.write({'employee_id': emp_still_id})	
						
					class26_objs = self.env['event.attendee'].search([('employee_id','=',emp_to_merge_id)])
					if class26_objs:
						class26_objs.write({'employee_id': emp_still_id})
						
					class27_objs = self.env['mk.episode'].search([('teacher_id','=',emp_to_merge_id),'|',('active','=',True),('active','!=',True)])
					if class27_objs:
						
						try:
							class27_objs.write({'teacher_id': emp_still_id})
						except:
							_logger.info("\n ** %s\n", class27_objs)
							mk_episode_bug += [identification_id]
						
					class28_objs = self.env['mk.mosque'].search([('edu_supervisor','in',[emp_to_merge_id]),'|',('active','=',True),('active','!=',True)])
					for class28_obj in class28_objs:
						edu_supervisors = [edu_supervisor.id for edu_supervisor in class28_obj.edu_supervisor if edu_supervisor.id != emp_to_merge_id] + [emp_still_id]
						class28_obj.write({'edu_supervisor': [(6, 0, edu_supervisors)]})	

					class29_objs = self.env['mk.mosque'].search([('responsible_id','=',emp_to_merge_id),'|',('active','=',True),('active','!=',True)])
					if class29_objs:
						class29_objs.write({'responsible_id': emp_still_id})
						
					class30_objs = self.env['mk.episode.attendace'].search([('teacher','=',emp_to_merge_id)])
					if class30_objs:
						class30_objs.write({'teacher': emp_still_id})	
						
					class31_objs = self.env['mk.comments.behavior.students'].search([('teacher','=',emp_to_merge_id)])
					if class31_objs:
						class31_objs.write({'teacher': emp_still_id})	
						
					class32_objs = self.env['mk.student.prepare'].search([('name','=',emp_to_merge_id)])
					if class32_objs:
						class32_objs.write({'name': emp_still_id})
						
# 					class33_objs = self.env['mk.employee.sms'].search([('employee','in',[emp_to_merge_id])])
# 					for class33_obj in class33_objs:
# 						employees33 = [employee33.id for employee33 in class33_obj.employee if employee33.id != emp_to_merge_id] + [emp_still_id]
# 						class33_obj.write({'employee': [(6, 0, employees33)]})
								
			unlink_user_ids += [u.id for u in user_ids]
			user_id = user and user.id or False

			for user_id_new in user_ids:		
				user_new_id = user_id_new.id
									
				class1_user_objs = self.env['res.users.role.line'].search([('user_id','=',user_new_id)])	
				if class1_user_objs:
					class1_user_objs.write({'user_id': user_id})

				class2_user_objs = self.env['employee.test.session'].search([('user_id','=',user_new_id)])	
				if class2_user_objs:
					class2_user_objs.write({'user_id': user_id})

				class3_user_objs = self.env['question.error'].search([('user_id','=',user_new_id)])	
				if class3_user_objs:
					class3_user_objs.write({'user_id': user_id})
					
				class4_user_objs = self.env['student.test.session'].search([('user_id','=',user_new_id),'|',('active','=',True),('active','!=',True)])	
				if class4_user_objs:
					class4_user_objs.write({'user_id': user_id})
					
				class5_user_objs = self.env['mk.supervisor.mosque'].search([('user_id','=',user_new_id)])	
				if class5_user_objs:
					class5_user_objs.write({'user_id': user_id})
					
				class6_user_objs = self.env['mk.course.request'].search([('user_id','=',user_new_id)])	
				if class6_user_objs:
					class6_user_objs.write({'user_id': user_id})
					
				class7_user_objs = self.env['mk.course.request'].search([('employee_id2','=',user_new_id)])	
				if class7_user_objs:
					class7_user_objs.write({'employee_id2': user_id})	
					
# 				class8_user_objs = self.env['smsclient'].search([('users_id','in',[user_new_id])])
# 				for class8_user_obj in class8_user_objs:
# 					user8_ids = [user8_id.id for user8_id in class8_user_obj.users_id if user8_id.id != user_new_id] + [user_id]
# 					class8_user_obj.write({'users_id': [(6, 0, user8_ids)]})						
					
				class9_user_objs = self.env['sms.smsclient.history'].search([('user_id','=',user_new_id)])	
				if class9_user_objs:
					class9_user_objs.write({'user_id': user_id})
					
				class10_user_objs = self.env['audit.log'].search([('user_id','=',user_new_id)])	
				if class10_user_objs:
					class10_user_objs.write({'user_id': user_id})
					
				class11_user_objs = self.env['website.support.department.contact'].search([('user_id','=',user_new_id)])	
				if class11_user_objs:
					class11_user_objs.write({'user_id': user_id})	
					
				class12_user_objs = self.env['website.support.ticket'].search([('create_user_id','=',user_new_id)])	
				if class12_user_objs:
					class12_user_objs.write({'create_user_id': user_id})
					
				class13_user_objs = self.env['website.support.ticket'].search([('user_id','=',user_new_id)])	
				if class13_user_objs:
					class13_user_objs.write({'user_id': user_id})
					
				class14_user_objs = self.env['website.support.ticket'].search([('closed_by_id','=',user_new_id)])	
				if class14_user_objs:
					class14_user_objs.write({'closed_by_id': user_id})	
					
				class15_user_objs = self.env['website.support.ticket.categories'].search([('cat_user_ids','in',[user_new_id])])
				for class15_user_obj in class15_user_objs:
					user5_ids = [cat_user.id for cat_user in class15_user_obj.cat_user_ids if cat_user.id != user_new_id] + [user_id]
					class15_user_obj.write({'cat_user_ids': [(6, 0, user5_ids)]})	

			if gender not in ['male', 'female', 'other']:
				gender = 'other'	
				
			emp_still.write({'name':                  name,
							 'work_location':         work_location,
							 'work_email':            work_email,
							 'mobile_phone':          mobile_phone,
							 'kin_phone':             kin_phone,
							 'work_phone':            work_phone,
							 'recruit_ids':           recruit_ids and [(6, 0, recruit_ids)] or [],
					         'job_id':                job_id and job_id.id or False,
					         'category2':             category2,
					         'center_admin_category': center_admin_category,
					         'department_id':         department_id and department_id.id or False,
					         'country_id':            country_id and country_id.id or False,
					         'issue_identity':        issue_identity,
					         'identity_expire':       identity_expire,
					         'birthday':              birthday,
					         'gender':                gender,
					         'marital':               marital,
					         'salary':                salary,
					         'salary_donor':          salary_donor,
					         'contract_type':         contract_type,
					         'part_ids':              part_ids and [(6, 0, part_ids)] or [],
					         'user_id':               user_id})					

		x = 0
		resource_issue = []
		for unlink_emp_id in unlink_emps:
			x += 1
			unlink_emp = self.browse(unlink_emp_id)
			_logger.info('\nD %s \n', x)
			
			try:
				if unlink_emp.identification_id in mk_episode_bug:
					unlink_emp.write({'data_clean': 'merge_episode',})
					continue
					
				if unlink_emp_id in (25160,26744,26617,28041,28040,29374,28384):
					continue
							
				unlink_emp.sudo().unlink()
			except:
				resource_issue += [unlink_emp.id]
# 				sql_insert = "update hr_employee set data_clean='merge' where id=%s;"%(unlink_emp.id)
# 				self.env.cr.execute(sql_insert)				

		_logger.info("\n END\n")
		
		nbr_users = len(user_ids)
		
		users_issue = []
		j = 0
		for unlink_user in user_ids:
			try:
				unlink_user.sudo().unlink()
			except:
				users_issue += [unlink_user.id]
				
			j += 1
		
		_logger.info("\n nbr_users%s    j%s\n", nbr_users, j)		
		_logger.info('\nmk_episode_bug\n%s\n',mk_episode_bug)
		_logger.info('\nresource_issue\n%s\n',len(resource_issue))
		_logger.info('\nusers_issue\n%s\n',users_issue)
		
		_logger.info("\n END2\n")

	@api.model
	def get_id_valid(self):		
		i = 1000000198
		nbr = 0
		num_ids = []
		while nbr < 100:
			res = self.check_id_validity(str(i), False)
			if not isinstance(res, pycompat.string_types) and res == 1:
				num_ids += [i]
				_logger.info('\n *********** \n %s \n *********** \n', nbr)
				nbr += 1

			i += 1
			_logger.info('\n\n %s %s \n\n', i, nbr)

		_logger.info('\n\n %s \n\n', num_ids)

# 		vals = {
# 		 'create_admin_mosq': True,
#  		
# 		 'mosque_id':         2,
# 		 'identification_id': '1000000024',
# 		 'work_email':        'tesst@yahoo.fr',
# 		 'name':              'Test1stname' + ' 2ndname' + ' 3rdname' + '4thname',
# 		 'mobile_phone':      '512345678',
# 		 'country_id':        173,
# 		 'gender':            'male',
# 		 'marital':           'married',}
				
# 		vals = {"name":"testdddddd",
# 				"episodes":"ddddddsss",
# 				"episode_value":"ev",
# 				"categ_id":6,
# 				"build_type":6,
# 				"check_maneg_mosque":1,
# 				"check_parking_mosque":1,
# 				"area_id":600,
# 				"city_id":401,
# 				"district_id":2,
# 				"latitude":"24.7375218976305",
# 				"longitude":"46.84370270368792",
# 				"state":"permision"}
		
# 	    emp = self.env['mk.mosque'].create(vals)
# 		emp = self.env['hr.employee'].create(vals)
# 		_logger.info('\n *********** \n %s \n *********** \n', emp)
		
		_logger.info('\n\n %s \n\n', num_ids)

	@api.model
	def get_responsible_count(self):
		_logger.info('***************************   get_responsible_count function is loading  ')
		count= 0
		accepted_responsibles = self.env['hr.employee'].search([('state', '=', 'accept'),
																('category', '=', 'admin'),
																'|', ('active', '=', True),
																     ('active', '=', False)])
		if accepted_responsibles:
			count = len(accepted_responsibles)

		_logger.info('count    :    : %s', count)
		return count

	@api.model
	def get_teacher_count(self):
		_logger.info('***************************   get_teacher_count function is loading  ')
		count = 0
		accepted_teachers = self.env['hr.employee'].search([('category', '=', 'teacher'),
															('state', '=', 'accept'),
															'|', ('active', '=', True),
															('active', '=', False)])
		if accepted_teachers:
			count = len(accepted_teachers)

		_logger.info('count       : %s: ', count)
		return count

	@api.model
	def get_educ_supervisors(self, department_id, type_mosque):
		try:
			department_id = int(department_id)
		except:
			pass
		type_mosque = type_mosque

		if type_mosque != "male" and type_mosque != "female":
			type_mosque = False

		sub_query_mosque = " "

		if type_mosque:
			sub_query_mosque = " AND m.center_department_id=%s AND m.gender_mosque='%s' " % (department_id, type_mosque)

		elif department_id:
			sub_query_mosque = " AND m.center_department_id=%s " % (department_id)

		query_string = """SELECT distinct(e.id) id, e.name
		                       FROM hr_employee e 
		                            LEFT JOIN hr_employee_mk_mosque_rel mr ON e.id=mr.hr_employee_id
		                            LEFT JOIN mk_mosque m ON m.id=mr.mk_mosque_id  
		                       WHERE e.category='edu_supervisor' AND
		                             e.active=True AND
		                             m.active=True %s """ % (sub_query_mosque)

		self.env.cr.execute(query_string)
		educ_supervisors = self.env.cr.dictfetchall()
		return educ_supervisors

	@api.constrains('work_email')
	def _check_employee_email(self):
		email = self.work_email
		regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
		if email:
			if not (re.fullmatch(regex, email)):
				raise ValidationError(_('Invalid Email!'))

	@api.model
	def set_employee_user_mosques(self):
		_logger.info('\n\n  __________ START')
		employees = self.env['hr.employee'].search([('category2', 'not in', ['edu_supervisor', 'center_admin'])])
		total = len(employees)
		_logger.info('\n\n  __________ total   :    %s', total)
		i= 0
		for employee_id in employees:
			i+= 1
			employee_mosqtechs = employee_id.mosqtech_ids
			_logger.info('\n\n  __________ employee_mosqtechs   :    %s', employee_mosqtechs)
			user = employee_id.user_id
			if not user:
				continue
			_logger.info('\n\n  __________ user   :    %s', user)
			genders = set([])
			for mosq in employee_mosqtechs:
				genders.add(mosq.categ_id.sudo().mosque_type)
				if len(genders) > 1:
					gender = 'male,female'
				else:
					gender = list(genders)[0]
			user.write({'mosque_ids': [(6, 0, employee_mosqtechs.ids)],
						'gender': gender})
			_logger.info('\n\n  __________      %s|%s  ', i,total)

		# query1 = """  select emp_id from mosque_relation
        #               where emp_id in
        #               ( select id from hr_employee where identification_id in (select login from res_users) )
        #               group by emp_id
        #               HAVING count(mosq_id) > 1; """
		# self.env.cr.execute(query1)
		# employees = self.env.cr.dictfetchall()
		# _logger.info('\n\n  __________ employees   :    %s', employees)
		# total = len(employees)
		# i1 =0
		# _logger.info('\n\n  __________ total   :    %s', total)
		# for employee_id in employees:
		# 	i1 +=1
		# 	employee = self.env['hr.employee'].browse(employee_id['emp_id'])
		# 	_logger.info('\n\n  __________ employee   :    %s', employee)
		# 	employee_mosqtechs = employee.mosqtech_ids
		# 	_logger.info('\n\n  __________ employee_mosqtechs   :    %s', employee_mosqtechs)
		# 	if not employee_mosqtechs:
		# 		continue
		# 	user = employee.user_id
		# 	if not user:
		# 		continue
		# 	_logger.info('\n\n  __________ user   :    %s', user)
		# 	genders = set([])
		# 	for mosq in employee_mosqtechs:
		# 		genders.add(mosq.categ_id.sudo().mosque_type)
		# 		if len(genders) > 1:
		# 			gender = 'male,female'
		# 		else:
		# 			gender = list(genders)[0]
		# 	user.write({'mosque_ids': [(6, 0, employee_mosqtechs.ids)],
		# 				'gender': gender})
		# 	_logger.info('\n\n  __________ first     %s|%s  ', i1,total)
		# query2 = """  select hr_employee_id from hr_employee_mk_mosque_rel
		#                       where hr_employee_id in
		#                       ( select id from hr_employee where identification_id in (select login from res_users) )
		#                       group by hr_employee_id
		#                       HAVING count(mk_mosque_id) > 1; """
		# self.env.cr.execute(query2)
		# employees2 = self.env.cr.dictfetchall()
		# _logger.info('\n\n  __________ employees2   :    %s', employees2)
		# total2 = len(employees2)
		# i2 = 0
		# _logger.info('\n\n  __________ total2   :    %s', total2)
		# for employee_id in employees2:
		# 	i2+=1
		# 	employee = self.env['hr.employee'].browse(employee_id['hr_employee_id'])
		# 	_logger.info('\n\n  __________ employee   :    %s', employee)
		# 	employee_mosque_sup = employee.mosque_sup
		# 	_logger.info('\n\n  __________ employee_mosque_sup   :    %s', employee_mosque_sup)
		# 	if not employee_mosque_sup:
		# 		continue
		# 	user = employee.user_id
		# 	if not user:
		# 		continue
		# 	_logger.info('\n\n  __________ user   :    %s', user)
		# 	genders = set([])
		# 	for mosq in employee_mosque_sup:
		# 		genders.add(mosq.categ_id.sudo().mosque_type)
		# 		if len(genders) > 1:
		# 			gender = 'male,female'
		# 		else:
		# 			gender = list(genders)[0]
		# 	user.write({'mosque_ids': [(6, 0, employee_mosque_sup.ids)],
		# 				'gender': gender})
		# 	_logger.info('\n\n  __________ Second     %s|%s  ', i2, total2)
		_logger.info('\n\n  __________ END')


class res_users(models.Model):
	_inherit = 'res.users'

	gender = fields.Selection([('male', 'مساجد رجالية'),
							   ('female', 'مدارس نسائية'),
							   ('male,female', 'مساجد رجالية ومدارس نسائية')], string="Allowed gender",
							  default="male,female")
	data_clean = fields.Selection([('merge', 'merge'),
								   ('check_id', 'check_id')])
	last_app_login = fields.Datetime('Last login from the APP')

	@api.model
	def create(self, vals):
		user = super(res_users, self).create(vals)
		if not user.partner_id.email:
			user.partner_id.email = '.'
		return user


class ChangePasswordUser(models.TransientModel):
	""" A model to configure users in the change password wizard. """
	_inherit = 'change.password.user'

	# @api.multi
	def change_password_button(self):
		_logger.info('******change_password_button******')
		for line in self:
			if line.user_id.id == SUPERUSER_ID:
				raise UserError(_("لا يمكنك تغيير كلمة مرور الأدمين."))
			if not line.new_passwd:
				raise UserError(_("Before clicking on 'Change Password', you have to write a new password."))
			line.user_id.write({'password': line.new_passwd})
			employee_id = self.env['hr.employee'].search([('user_id', '=', line.user_id.id)], limit=1)
			employee_id.write({'passwd': line.new_passwd})
		# don't keep temporary passwords in the database longer than necessary
		self.write({'new_passwd': False})

