from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class TestRegister(models.TransientModel):    
	_name="test.register"

	@api.multi
	def get_study_class(self):
		study_class = self.env['mk.study.class'].search([('study_year_id', '=', self.get_year_default()),
														 ('is_default', '=', True)], limit=1)
		return study_class and study_class.id or False

	@api.multi
	def get_year_default(self):
		academic_year = self.env['mk.study.year'].search([('is_default', '=', True)], limit=1)
		return academic_year and academic_year.id or False

	academic_id      = fields.Many2one('mk.study.year',     string='Academic Year', default=get_year_default, required=True,                      ondelete='restrict')
	study_class_id   = fields.Many2one('mk.study.class',    string='Study class',   default=get_study_class,  domain=[('is_default', '=', True)], ondelete='restrict')
	test_time        = fields.Many2one("center.time.table", string="Test Time")
	#center_id=fields.Many2one("mk.test.center.prepration",string="Test center")
	test_name        = fields.Many2one("mk.test.names",      string="Test Name")
	branch           = fields.Many2one("mk.branches.master", string="Branch")
	#student_id=fields.Many2one("mk.link",string="student")
	branch_duration  = fields.Integer(related='branch.duration', string="branch duration")
	avalible_minutes = fields.Integer("remaining minutes")
	total_minutes    = fields.Integer("total minutes")
	teacher          = fields.Many2one("hr.employee",  string="Teacher")
	avalible_teacher = fields.Many2many("hr.employee", string="available")
	student_id       = fields.Many2many("mk.link",     string="students")
	
	@api.onchange('test_time')
	def center_id_tests(self):
		return {'domain':{'test_name':[('id', 'in',self.test_time.center_id.test_names.ids)]}}

	@api.multi
	def ok(self):

		if self.test_name.parent_test:
			if self.is_pass_parent_test():
				if self.is_pass_test_before()==False:
					if self.is_it_his_normal_track():
						if self.is_it_pass_next_tests():
							if self.is_there_is_available_seats():
								self.env['student.test.session'].sudo().create({'student_id':self.student_id.id,
																				'test_name':self.test_name.id,
																				'test_time':self.test_time.id,
																				'branch':self.branch.id,
																				'center_name':self.test_time.center_id.center_id.display_name
																				#'center_id':self.center_id.id,
																				#'avalible_teacher':[(4,id) for id in self.avalible_teacher.ids]
																				})

		else:	
				if self.is_pass_test_before()==False:
					if self.is_it_his_normal_track():
						if self.is_it_pass_next_tests():
							if self.is_there_is_available_seats():
								self.env['student.test.session'].sudo().create({'student_id':self.student_id.id,
																				'test_name':self.test_name.id,
																				'test_time':self.test_time.id,
																				'branch':self.branch.id,
																				'center_name':self.test_time.center_id.center_id.display_name
																				#'center_id':self.center_id.id,
																				#'avalible_teacher':[(4,id) for id in self.avalible_teacher.ids]
																				})


	def is_pass_parent_test(self):
		up_branches=self.env['mk.branches.master'].sudo().search([('test_name','=',self.test_name.parent_test.id),
																  ('trackk','=','up')],order='order desc',limit=1)
		if up_branches:
			is_test_up=self.env['student.test.session'].sudo().search([('student_id','=',self.student_id.id),
																	('branch','=',up_branches[0].id),
																	('academic_id','=',self.academic_id.id),
																	('study_class_id','=',self.study_class_id.id),
																	('state','=','done'),
																	('is_pass','=',True)])
			if is_test_up:
				return True
			
			else:
				down_branches=self.env['mk.branches.master'].sudo().search([('test_name','=',self.test_name.parent_test.id),
																		    ('trackk','=','down')], order='order desc', limit=1)
				if down_branches:
					is_test_down=self.env['student.test.session'].sudo().search([('student_id','=',self.student_id.id),
																				 ('branch','=',down_branches[0].id),
																				 ('academic_id','=',self.academic_id.id),
																				 ('study_class_id','=',self.study_class_id.id),
																				 ('state','=','done'),
																				 ('is_pass','=',True)])
					if is_test_down:
						return True
					
					else:			
						raise ValidationError(_('عفوا الطالب لم يكمل اختبار فروع '+str(self.test_name.parent_test.name)+' وهو  متطلب'))
					
		else:
			down_branches=self.env['mk.branches.master'].sudo().search([('test_name','=',self.test_name.parent_test.id),
																	   ('trackk','=','down')], order='order desc', limit=1)
			if down_branches:
				is_test_down=self.env['student.test.session'].sudo().search([('student_id','=',self.student_id.id),
																			 ('branch','=',down_branches[0].id),
																			 ('academic_id','=',self.academic_id.id),
																			 ('study_class_id','=',self.study_class_id.id),
																			 ('state','=','done'),
																			 ('is_pass','=',True)])
				if is_test_down:
					return True
				
				else:			
					raise ValidationError(_('عفوا الطالب لم يكمل اختبار فروع '+str(self.test_name.parent_test.name)+' وهو  متطلب'))

	def is_pass_parent_branch(self):
		is_test_branch=self.env['student.test.session'].search([('student_id','=',self.student_id.id),
															    ('branch','=',self.branch.parent_branch.id),
															    ('degree','>',self.branch.parent_branch.minumim_degree)])
		if is_test_branch:
			return True
		else:
			return False

	def is_there_is_available_seats(self):
		if self.branch_duration>self.avalible_minutes:
			return False
		else:
			return True

	def is_pass_test_before(self):
		is_test=self.env['student.test.session'].search([('student_id','=',self.student_id.id),
														 ('branch','=',self.branch.id),
														 ('academic_id','=',self.academic_id.id),
														 ('study_class_id','=',self.study_class_id.id)], limit=1)
		if is_test:
			if is_test[0].state=='done':
				if is_test[0].degree<self.branch.minumim_degree:
					return False
				else:
					raise ValidationError(_('الطالب نجح في هذا الفرع مسبقا'))
			else:
					raise ValidationError(_('تم تسجيل الطالب في هذا الفرع سابقا'))

		else:
			return False

	def is_it_his_normal_track(self):
		is_test = self.env['student.test.session'].search([('student_id','=',self.student_id.id),
														   ('academic_id','=',self.academic_id.id),
														   ('study_class_id','=',self.study_class_id.id),
														   ('state','=','done'),
														   ('is_pass','=',True)], order="done_date desc", limit=1)
		if is_test:
			if is_test[0].branch.trackk!=self.branch.trackk:
				masar=""
				if is_test[0].branch.trackk=='up':
					masar="من الناس إلى الفاتحة"
				else:
					masar="من الفاتحة إلى الناس"
				raise ValidationError(_('مسار الطالب '+' [ '+masar+' ] '+'غير مسموح له بتغيير المسار'))
			else:
				return True
		else:
			return True

	def is_it_pass_next_tests(self):
		is_test=self.env['student.test.session'].search([('student_id','=',self.student_id.id),
														 ('academic_id','=',self.academic_id.id),
														 ('study_class_id','=',self.study_class_id.id),
														 ('state','=','done'),
														 ('is_pass','=',True),
														 ('test_name','=',self.test_name.id),
														 ('branch_order','>',self.branch.order)])
		if is_test:
			passed_branches=[]
			for test in is_test:
				info=str(is_test[0].branch.name)
				passed_branches.append(info)
			raise ValidationError(_('الطالب نجح في الفروع '+str(passed_branches)+'وهي فروع شاملة لهذا الفرع'))
		else:
			return True