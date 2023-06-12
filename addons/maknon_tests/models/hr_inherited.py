#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
import re
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class emp(models.Model):
	_inherit = 'hr.employee'

	outsource            = fields.Boolean(string="معلم مؤقت")
	edu_supervisordomain = fields.Selection([('educational', 'تعليمي'),
											 ('administrative', 'اداري'),
											 ('financial', 'مالي'),
											 ('qualitative', 'نوعي'),
											 ('tests', 'الاختبارات')], string='المجال', track_visibility='onchange')
	training_course_ids = fields.One2many("mk.training.courses", "employee_id", "Courses")

	@api.model
	def get_pass(self, identification_id):
		identification_id = str(identification_id)

		employee = self.env['hr.employee'].search([('identification_id', '=', identification_id),
												   '|',('active', '=', True),
												       ('active', '=', False)], limit=1)
		list_item = []
		if employee:
			list_item.append({'passwd': employee.passwd })
		return list_item

	@api.model
	def tech_login(self, identification_id, password):
		identification_id = str(identification_id)
		password = str(password)

		item_list = []
		employee_id = self.env['hr.employee'].search([('identification_id', '=', identification_id),
											          ('passwd', '=', password),
											          '|', ('active', '=', True),
											               ('active', '=', False),], limit=1)
		if employee_id:
			item_list.append({'gender': employee_id.gender,
						      'name': employee_id.name,
						      'id': employee_id.id,
						      'user_id': employee_id.resource_id.user_id.id if employee_id.resource_id.user_id else False,
						      'category': employee_id.category})
		return item_list

	@api.model
	def get_teacher(self, identification_id):
		identification_id = str(identification_id)

		result_list = []
		employee = self.env['hr.employee'].search([('identification_id', '=', identification_id),
												   '|', ('active', '=', True),
												        ('active', '=', False)], limit=1)
		if employee:
			result_list.append({'id': employee.id,
								'name': employee.name,
								'identification_id': employee.identification_id,
								'passport_id': employee.passport_id,
								'work_phone': employee.work_phone,
								'work_email': employee.work_email,
								'country_id': employee.country_id.id,
								'job_id': employee.job_id.id,
								'gender': employee.gender,
								'marital': employee.marital,
								'birthday': employee.birthday})
		return result_list

	@api.model
	def injaaz_rate_total(self, emp_id, ep_id, follow):
		try:
			emp_id = int(emp_id)
			ep_id = int(ep_id)
			follow = str(follow)
		except:
			pass

		if emp_id > 0 and int(ep_id) > 0:
			query_string = ''' 
	          SELECT 
	          count(*) 
	          FROM 
	            public.hr_employee, 
	            public.mk_episode, 
	            public.mk_link, 
	            public.mk_listen_line
	          WHERE 
	            hr_employee.id = mk_episode.teacher_id AND
	            mk_link.episode_id = mk_episode.id AND
	            mk_link.student_id = mk_listen_line.student_id
	            AND mk_listen_line.type_follow = %s AND hr_employee.id=%s and mk_episode.id=%s;
	            '''
			params = (follow, emp_id, ep_id)
		else:
			query_string = ''' 
	                  SELECT 
	                    count(*)  
	                    FROM 
	                      public.hr_employee, 
	                      public.mk_episode, 
	                      public.mk_link, 
	                      public.mk_listen_line
	                    WHERE 
	                      hr_employee.id = mk_episode.teacher_id AND
	                      mk_link.episode_id = mk_episode.id AND
	                      mk_link.student_id = mk_listen_line.student_id
	                      AND mk_listen_line.type_follow = %s AND hr_employee.id=%s;
	                      '''
			params = (follow, emp_id)
		if query_string:
			self.env.cr.execute(query_string, params)
			item_list = self.env.cr.dictfetchall()
		return item_list

	@api.model
	def injaaz_rate_done(self, emp_id, ep_id, follow):
		try:
			emp_id = int(emp_id)
			ep_id = int(ep_id)
			follow = str(follow)
		except:
			pass

		if emp_id > 0 and int(ep_id) > 0:
			query_string = ''' 
	           SELECT 
	        count(*) 
	        FROM 
	          public.hr_employee, 
	          public.mk_episode, 
	          public.mk_link, 
	          public.mk_listen_line
	        WHERE 
	          hr_employee.id = mk_episode.teacher_id AND
	          mk_link.episode_id = mk_episode.id AND
	          mk_link.student_id = mk_listen_line.student_id AND mk_listen_line.state='done'
	        AND mk_listen_line.type_follow=%s AND hr_employee.id=%s and mk_episode.id=%s And mk_listen_line.state='done';   '''
			params = (follow, emp_id, ep_id)
		else:
			query_string = ''' 
	                   SELECT 
	        count(*)  
	        FROM 
	          public.hr_employee, 
	          public.mk_episode, 
	          public.mk_link, 
	          public.mk_listen_line
	        WHERE 
	          hr_employee.id = mk_episode.teacher_id AND
	          mk_link.episode_id = mk_episode.id AND
	          mk_link.student_id = mk_listen_line.student_id AND mk_listen_line.state='done'
	        AND mk_listen_line.type_follow=%s AND hr_employee.id=%s;
	        '''
			params = (follow, emp_id)
		if query_string:
			self.env.cr.execute(query_string, params)
			item_list = self.env.cr.dictfetchall()
		return item_list

	@api.one
	def write(self, vals):
		identification_id = self.identification_id
		if 'name' in vals :
			name = vals.get('name')
			split_name = name.split(' ')
			len_split_name = len(split_name)
			student_id = self.env['mk.student.register'].search([('category', '!=', False),
																 ('identity_no', '=', identification_id)], limit=1)
			if student_id:
				student_id.write({'name': split_name[0],
					              'second_name': split_name[1] if len_split_name >=2 else False,
                				  'third_name': split_name[2] if len_split_name >=3 else False,
                                  'fourth_name': split_name[3] if len_split_name >=4 else False})
		return super(emp, self).write(vals)

class EmployeeCourses(models.Model):
	_name = 'mk.training.courses'

	employee_id         = fields.Many2one('hr.employee', string='Employee', ondelete='set null')
	course              = fields.Char('Course')
	date                = fields.Date('Date')







