from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class AddERror(models.TransientModel):    
	_name="add.error"

	item            = fields.Many2one("mk.discount.item",   string="Item")
	evaluation_item = fields.Many2one("mk.evaluation.items",string="evaluation item")
	question_id     = fields.Many2one("test.questions",string="question")
	value           = fields.Integer(string="Error value")
	surah           = fields.Many2one("mk.surah",       string="Surah")
	aya             = fields.Many2one("mk.surah.verses",string="verses")
	lines           = fields.One2many("add.error.line","wi","lines")
	member          = fields.Many2one("hr.employee",string="عضو اللجنة")
	mode            = fields.Selection([('edit','edit'),('read','read')],string="mode",default='edit')
	session_id      = fields.Many2one("student.test.session",            string="session")

	@api.onchange('session_id')
	def change_session(self):
		return {'domain':{'question_id':[('id', 'in',self.session_id.test_question.ids)]}}

	@api.onchange('question_id')
	def change_quas(self):
		#members domain
		member_ids=[]
		if self.question_id.session_id.sudo().center_id.center_group == 'student':
			#if self.question_id.session_id.state=='done':
				#self.mode='read'
			member_ids=self.env['committe.member'].sudo().search([('committe_id','=',self.session_id.committe_id.id)])

		else:
			member_ids=self.env['committe.member'].sudo().search([('committe_id','=',self.question_id.emp_session_id.committe_id.id)])

		if member_ids:
			user_id = self.env.user
			employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])
			members=[]
			for me in member_ids:
				members.append(me.member_id.id)
			if members:
				if employee_id.id in members:
					self.member = employee_id.id
					self.member_error_items(self.member)
				return {'domain': {'member': [('id', 'in', members)]}}

	@api.onchange('member')
	def change_qua(self):
		self.member_error_items(self.member)

	def member_error_items(self,member):
		self.lines = False
		if member:
			items = []
			items = self.env['mk.evaluation.items'].search([('id', 'in', self.question_id.session_id.branch.evaluation_items.ids)])
			if not items:
				items=self.env['mk.evaluation.items'].search([('id','in',self.question_id.emp_session_id.branch.evaluation_items.ids)])
			if items:
				itemss = []
				for ev_item in items:
					first_time = True
					cr = self.env.cr
					for item in ev_item.discount_items:
						# get item sum(value) for this q and this member
						query = ('''SELECT sum(value) FROM question_error where item=%d and question_id=%d and member=%d;'''%(item.id,self.question_id.id,member.id))
						cr.execute(query)
						sum_value = self.env.cr.fetchone()
						if None not in sum_value:
							value = sum_value[0]
						else:
							value = 0

						member_rows = self.env['question.error'].search([('item', '=', item.id),
																		 ('question_id', '=', self.question_id.id),
																		 ('member', '=', member.id)])
						# check if there is multiple rows
						if member_rows:
							if len(member_rows) > 1:
	
								query = ('''Delete FROM question_error where item=%d and question_id=%d and member=%d;'''%(item.id,self.question_id.id,member.id))
								cr.execute(query)

								self.env['question.error'].create({'value'            : value,
																	'item'            : item.id,
																	'evaluation_item' : ev_item.id,
																	'question_id'     : self.question_id.id,
																	'member'          : member.id})
						dis_all = False
						if value!= 0 :
							if item.allowed_discount/value == item.amount:
								dis_all = True
						if first_time:
							itemss.append((0, 0, {'dis_all'          : dis_all,
												  'value'            : value,
												  'item'             : item.id,
												  'item_id'          : item.id,
												  'evaluation_item'  : ev_item.id,
								                 "evaluation_item_id": ev_item.id,
												  'amount'           : item.amount,
												  'maximum'          : item.allowed_discount}))
						else:
							itemss.append((0, 0, {'dis_all'            : dis_all,
												  'value'              : value,
												  'item'               : item.id,
												  'item_id'            : item.id,
												  "evaluation_item_id" : ev_item.id,
												  'amount'             : item.amount,
												  'maximum'            : item.allowed_discount}))
						first_time = False
				self.lines = itemss


	@api.multi
	def ok(self):
		current_date = datetime.now().date()
		exam_end_date = datetime.strptime(self.session_id.center_id.exam_end_date, '%Y-%m-%d').date()
		study_class_id = self.session_id.study_class_id
		if study_class_id and study_class_id.is_default and current_date > exam_end_date:
			raise ValidationError(_('عذرا لايمكنك تحديث خصم لإختبار بعد تاريخ نهاية الاختبار'))
		else:
			for rec in self.lines:
				member_rows = self.env['question.error'].search([('item','=',rec.item_id),
															   ('question_id','=',self.question_id.id),
															   ('member','=',self.member.id)])

				if member_rows:
					member_rows[0].write({'value' : rec.value,
										  'user_id' : self.member.sudo().user_id.id})
				else:
					self.env['question.error'].create({'item':rec.item_id,
													   'question_id':self.question_id.id,
													   'value':rec.value,
													   'member':self.member.id,
													   'user_id':self.member.sudo().user_id.id})
			self.change_qua()
			self.member = False
			self.lines = False
			return {"type": "ir.actions.do_nothing",}



class adding_view(models.TransientModel):
	_name="add.error.line"

	item               = fields.Many2one("mk.discount.item",   string="Item")
	evaluation_item    = fields.Many2one("mk.evaluation.items",string="evaluation item")
	evaluation_item_id = fields.Integer(string="ev id")
	item_id            = fields.Integer(string="item id")
	question_id        = fields.Many2one("test.questions",string="question")
	value              = fields.Integer(string="Error value")
	wi                 = fields.Many2one("add.error",     string="lines")
	maximum            = fields.Float(string="maximum discount amount")
	amount             = fields.Float(string="discount amount")
	dis_all            = fields.Boolean(string="disc all")

	@api.onchange('dis_all')
	def dis_all_ch(self):
		if self.dis_all:
			if self.amount:
				self.value=self.maximum/self.amount