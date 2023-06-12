# -*- encoding: utf-8 -*-

from odoo import api, fields, models , _
from datetime import datetime


class refactoreWizard(models.TransientModel):
	_name = 'update.wizard'
	_description = 'Move Data Wizard'

	def iden_less_than_ten(self):
		res_users = self.env['res.users']
		employee_ids = self.env['hr.employee'].search([])

		for employee in employee_ids:
			if len(employee.identification_id) < 10:
				users = res_users.search([('login','=',employee.identification_id)])
				users.unlink()
			episode_ids = self.env['mk.episode'].search([('teacher_id','=',employee.id)])
			for episode in episode_ids:
				episode.teacher_id = False
			employee.unlink()

	def get_employee_data(self):
		self.iden_less_than_ten()
		res_users = self.env['res.users']
		visited = []
		visited_with_ids = {}
		Output = [] 
		dup = []
		dup_ids =[]
		employee_ids = self.env['hr.employee'].search([])
		for employee in employee_ids:
			if employee.identification_id not in visited:
				visited.append(employee.identification_id)
				visited_with_ids[employee.identification_id] = employee
				Output.append((employee.identification_id , employee.id))
			else :
				dup.append(employee.identification_id)
				dup_ids.append(employee)
		print('............................ dup_ids ',len(dup_ids))
		for employee in dup_ids:
			stay_id = visited_with_ids[employee.identification_id]
			if not stay_id.registeration_code:
				stay_id.registeration_code = employee.registeration_code
			if not stay_id.work_email:
				stay_id.work_email = employee.work_email
			if not stay_id.mobile_phone:
				stay_id.mobile_phone = employee.mobile_phone
			if not stay_id.job_id:
				stay_id.job_id = employee.job_id
			if not stay_id.category2:
				stay_id.category2 = employee.category2
			if not stay_id.department_id:
				stay_id.department_id = employee.department_id.id
			for mosq_id in employee.mosqtech_ids:
				stay_id.mosqtech_ids = [(4, mosq_id.id)]
			episode_ids = self.env['mk.episode'].search([('teacher_id','=',employee.id)])
			for episode in episode_ids:
				episode.teacher_id = stay_id.id
			prepare_ids = self.env['mk.student.prepare'].search([('name','=',employee.id)])
			for prepare in prepare_ids:
				prepare.name = stay_id.id
			mosque_ids = self.env['mk.mosque'].search([('responsible_id','=',employee.id)])
			for mosque in mosque_ids:
				mosque.responsible_id = stay_id.id
			users = res_users.search([('login','=',employee.identification_id)])
			users.unlink()
			employee.unlink()
	def get_student_data(self):
		visited = set() 
		Output = [] 
		dup = []
		dup_ids = []
		student_ids = self.env['mk.student.register'].search([])
		for student in student_ids:
			if student.identity_no not in visited:
				visited.add(student.identity_no)
				Output.append((student.identity_no , student.id))
			else :
				dup.append(student.identity_no)
				dup_ids.append(student.id)
		
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'mk.student.register',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'domain': [('id', 'in', dup_ids)],
		}

class deleterec(models.TransientModel):
	_name = 'courses.wizard'

	couser_type_id = fields.Integer('Course Type ID')
	def process_add(self,data):

		query = ('''
				update refactor_courses set course_type = %s
					
				''')
		params = (self.couser_type_id,)
		self.env.cr.execute(query, params)


class course_rec(models.TransientModel):
	_name = 'courses.refactor.wizard'       

	def process_del(self , data):
		
		query = ('''
				delete from refactor_courses where status != 1 and status != 2
					
				''')
		self.env.cr.execute(query)


	def process_merge(self,data):

		courses_ids = self.env['refactor.courses'].search([('status','=',2)])

		for course in courses_ids:
			course_root = self.env['refactor.courses'].search([('status','=',1),('course_id','=',course.course_id)])
			course_root.write({
				'to_surah_order': course.surah_order,
				'to_part_order':course.part_order,
				'to_verse_original_order':course.verse_original_order,
				'to_course_type':course.course_type,
				'to_test':course.test,
				})

			course.unlink()

	def process_del_courses(self,data):
		course_no = 0
		course_id = self.env['refactor.courses'].search([])
		for c_id in course_id:
			course_type = c_id.course_type

			break

		query = ('''
				delete from mk_subject_page where subject_page_id = %s
					
				''')

		params = (course_type,)
		self.env.cr.execute(query,params)

	def process_create(self):

		course_refactor_ids = self.env['refactor.courses'].search([])

		for line in course_refactor_ids:
			test_is = False
			surah_id = self.env['mk.surah'].search([('order','=',line.surah_order)])
			part_id = self.env['mk.parts'].search([('order','=',line.part_order)])
			verse_id = self.env['mk.surah.verses'].search([('surah_id','=',surah_id.id),('original_surah_order','=',line.verse_original_order)])
			
			to_surah_id = self.env['mk.surah'].search([('order','=',line.to_surah_order)])
			to_part_id = self.env['mk.parts'].search([('order','=',line.to_part_order)])
			to_verse_id = self.env['mk.surah.verses'].search([('surah_id','=',to_surah_id.id),('original_surah_order','=',line.to_verse_original_order)])
			if line.to_test == 1:
				test_is = True

			if part_id.id == to_part_id.id:
				part_id = part_id

			else:
				part_id = self.env['mk.parts'].search(['|',('order','=',line.part_order),('order','=',line.to_part_order)])

			self.env['mk.subject.page'].create({
				'subject_page_id':line.course_type,
				'from_surah':surah_id.id,
				'from_verse':verse_id.id,
				'to_surah':to_surah_id.id,
				'to_verse':to_verse_id.id,
				'part_id':[(6, 0, part_id.ids)],
				'is_test':test_is,
				'order':line.course_id,
				})
			#line.unlink()
	def process_clear(self):

		query = ('''
				delete from refactor_courses
					
				''')
		self.env.cr.execute(query)





		


class partassign(models.TransientModel):
	_name = 'part.part'

	part_id = fields.Many2one('mk.parts' , string="Part")

	@api.multi
	def process_add(self, data):
		ids = data.get('active_ids', [])
		query = ('''
				update mk_surah_verses set part_id = %s
				where id in %s
					
				''')
		params = (self.part_id.id , tuple(ids))
		self.env.cr.execute(query, params)

