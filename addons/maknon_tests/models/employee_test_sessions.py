#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree
import random

import logging
_logger = logging.getLogger(__name__)


class TestEmployeeSession(models.Model):
	_name = 'employee.test.session'
	_rec_name='emp_id'

	@api.depends('center_id')
	def cheack_user_logged_in(self):
		for rec in self:
			if rec.sudo().center_id.center_id.center_id.id in [self.env.user.department_id.id] or rec.sudo().center_id.center_id.center_id.id in self.env.user.department_ids.ids: 
				rec.editable=True
			else:
				rec.editable=False
				
	@api.depends('center_id')    
	def _get_avilable_techer(self):
		for rec in self:
			rec.avalible_teacher=False
			
	@api.one
	@api.depends('center_id.is_auto_assign_committee','center_id.committee_test_ids','center_id.committee_test_ids.members_ids')
	def get_users(self):
		center = self.center_id
		user_ids = []
		if center and center.is_auto_assign_committee:
			for committee in center.committee_test_ids:
				for member in committee.members_ids:
					if not member.main_member:
						continue
					
					user_employee = member.member_id.user_id
					if user_employee:
						user_ids += [user_employee.id]
						break
					
		self.user_ids = user_ids
				
	editable         = fields.Boolean(string="show", default=True)#,compute='cheack_user_logged_in')
	state            = fields.Selection([('draft',  'Draft'),
					 				     ('absent', 'absent'),
									     ('start',  'start'),
									     ('done',   'Done test'),
									     ('cancel', 'cancel')],default="draft",string="status")
	#test_time=fields.Many2one("center.time.table",string="Test Time")
	date             = fields.Date(string="Date")
	degree           = fields.Integer(string="Deserved degree")
	maximum_degree   = fields.Integer(related='branch.maximum_degree',string="Maximum degree")
	duration         = fields.Integer(related='branch.duration',string="exam duration")
	appreciation     = fields.Selection([('excellent',   'Excellent'),
										 ('v_good',      'Very good'),
										 ('good',        'Good'),
										 ('acceptable', 'Acceptable'),
										 ('fail',       'Fail')], string="appreciation")
	avalible_teacher = fields.Many2many("hr.employee",     string="available",compute='_get_avilable_techer')
	teacher          = fields.Many2one("hr.employee",               string="Teacher")
	committe_id    	 = fields.Many2one("committee.tests",           string="committe")
	user_id        	 = fields.Many2one("res.users",                 string="user_id")
	user_ids      	 = fields.Many2many("res.users",                string="user_id", compute=get_users, store=True)	
	center_id        = fields.Many2one("mk.test.center.prepration", string="Test center")
	test_name        = fields.Many2one("mk.test.names",             string="Test Name")
	branch           = fields.Many2one("mk.branches.master",        string="Branch")
	emp_id           = fields.Many2one("hr.employee",               string="Examiner Name")
	test_session_id  = fields.Many2one("center.time.table",         string="TestCenterTimetable")
	test_question    = fields.One2many("test.questions",         "emp_session_id", string="session questions")
	items_question   = fields.One2many("employee.item.quastion", "session_id",     string="Employee Item")
	
	
	@api.onchange('branch')
	def onc_branch(self):
		return {'domain':{'emp_id':[('job_id', 'in',self.branch.job_id.ids),
								    ('category','=','teacher')]}}
	
	@api.onchange('center_id')
	def on_center(self):
		return {'domain':{'test_name':[('id', 'in',self.center_id.test_names.ids)]}}		

	def cancel_exam(self):
		self.write({'state':'cancel'})
		
	##CONSTRIANT
	@api.constrains('test_name', 'branch')
	def _check_test(self):
		if self.test_name.parent_test:
			if not self.is_pass_parent_test():
				raise ValidationError(_('الطالب لم يجلس لاخنبار'+'  '+self.test_name.parent_test.name))             

			if self.branch.parent_branch and not self.is_pass_parent_branch():
				raise ValidationError(_('الطالب لم يجلس في الفرع'+'  '+self.branch.parent_branch.name))

		if self.branch.parent_branch and not self.is_pass_parent_branch():
			raise ValidationError(_('الطالب لم يجلس في الفرع'+'  '+self.branch.parent_branch.name))                     

	def is_pass_parent_test(self):
		tests = self.env['employee.test.session'].search([('id','!=',self.id),
														  ('emp_id','=',self.emp_id.id),
														  ('test_name','=',self.test_name.parent_test.id)])
		if tests:
			st_branches=[]
			for session in tests:
				if session.branch.id not in st_branches and session.degree > session.branch.minumim_degree:
					st_branches.append(session.branch.id)
					
			if len(st_branches) == len(self.test_name.parent_test.branches.ids):
				return True
		
		return False

	def is_pass_parent_branch(self):
		test_branch = self.env['employee.test.session'].search([('emp_id','=',self.emp_id.id),
																('branch','=',self.branch.parent_branch.id),
																('degree','>',self.branch.parent_branch.minumim_degree)], limit=1)
		if test_branch:
			return True
		
		return False

	@api.multi
	def start_exam(self):
		q_ids = []
		
		user_id = self.env.user.id
		center = self.center_id
		committee_member = False
		
		if center.is_auto_assign_committee:
			committee_member = self.env['committe.member'].search([('member_id.user_id','=',user_id),
														           ('center_id','=',self.center_id.id)], limit=1)
		vals_start = {'state': 'start'}
		if committee_member:
			vals_start.update({'user_id':     user_id,
					           'committe_id': committee_member.committe_id.id})
						
		if self.branch.quations_method == 'subject':
			if self.branch.employee_items:
				for item in self.branch.employee_items:
					self.env['employee.item.quastion'].create({'session_id': self.id,
															   'item':       item.id})
			
			for part in self.branch.parts_ids:    			
				quations_ids = self.env['mk.subject.page'].search([('subject_page_id','=',self.branch.subject_id.id),
							  									   ('part_id','=',part.id)])
				selected_ids = random.sample(quations_ids,self.branch.qu_number_per_part)
				q_ids.extend(selected_ids)
			
			if len(q_ids) != 0:
				for subject in q_ids:
					self.env['test.questions'].create({'emp_session_id': self.id,
													   'from_surah':     subject.from_surah.id,
													   'from_aya':       subject.from_verse.id,
													   'to_surah':       subject.to_surah.id,
													   'to_aya':         subject.to_verse.id})
					
				self.write(vals_start)

		elif self.branch.quations_method == 'lines':   		
			for part in self.branch.parts_ids:    			
				quations_ids=self.env['mk.surah.verses'].search([('line_no','=',2),
																 ('part_id','=',part.id)])
				selected_ids=random.sample(quations_ids,self.branch.qu_number_per_part)
				q_ids.extend(selected_ids)

			if len(q_ids)!=0:
				for subject in q_ids:
					self.env['test.questions'].create({'emp_session_id': self.id,
													   'from_surah':     subject.surah_id.id,
													   'from_aya':       subject.id,
													   'to_surah':       subject.surah_id.id,
													   'to_aya':         subject.id})
					
				self.write(vals_start)

	@api.multi
	def end_exam(self):
		degree = 0
		for q in self.test_question:
			for error in q.error_details:
				degree += (error.value*error.item.amount)
		self.degree = self.branch.maximum_degree-degree
		self.state = 'done'

		appreciation_ids=self.env['mk.passing.items'].search([('branches','in',self.branch.id),
															  ('from_degree','>=',self.branch.maximum_degree-degree),
															  ('to_degree','<=',self.branch.maximum_degree-degree)])
		if appreciation_ids:
			self.appreciation = appreciation_ids[0].appreciation


class TestEmployeeItems(models.Model):
	_name = 'employee.item.quastion'

	session_id      = fields.Many2one("employee.test.session",string="session")
	item            = fields.Many2one("employee.items",string="employee item")
	deserved_degree = fields.Integer(string="Deserved Degree")
