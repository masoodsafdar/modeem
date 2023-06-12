from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class AddERror(models.TransientModel):    
	_name="add.teacher"

	session_id  = fields.Integer("Session id")
	teacher     = fields.Many2one("hr.employee", string="Teacher")
	s_type      = fields.Selection([('emp','emp'),
				  				    ('st','st')], default="st", string="type")
	committe_id = fields.Many2one("committee.tests", string="committe")

	@api.onchange('session_id')
	def onchange_session(self):
		session_id = self.session_id
		if self.s_type == 'st':
			session_id = self.env['student.test.session'].sudo().search([('id','=',session_id)])
			
		elif self.s_type == 'emp':
			session_id = self.env['employee.test.session'].sudo().search([('id','=',session_id)])
		
		if session_id:
			committee_obj = self.env['committee.tests'].search([('commitee_id','=',session_id[0].center_id.id)])
			if committee_obj:
				return {'domain':{'committe_id':[('id', 'in',committee_obj.ids)]}}
	
	@api.multi
	def ok(self):
		session_obj = []
		if self.s_type == 'st':
			session_obj = self.env['student.test.session'].sudo().search([('id','=',self.session_id)])

			if session_obj[0].sudo().student_id.episode_id.teacher_id.id in [member.member_id.id  for member in self.committe_id.sudo().members_ids]:
				raise ValidationError(_('المعلم'+' << '+session_obj[0].sudo().student_id.episode_id.teacher_id.name+' >> '+ 'هو معلم للطالب وهو احد اعضاء اللجنة '))
		else:
			session_obj = self.env['employee.test.session'].sudo().search([('id','=',self.session_id)])

		if session_obj:
			current_date = datetime.now().date()
			exam_end_date = datetime.strptime(session_obj.center_id.exam_end_date, '%Y-%m-%d').date()
			if session_obj.study_class_id and session_obj.study_class_id.is_default and current_date > exam_end_date:
				raise ValidationError(_('عذرا لايمكنك إسناد لجنة إختبار بعد تاريخ نهاية الاختبارات'))
			else:
				main_member = self.env['committe.member'].sudo().search([('committe_id','=',self.committe_id.id),
																		 ('main_member','=',True)])
				if main_member:
					session_obj[0].sudo(self.env.user.id).write({'committe_id': self.committe_id.id,
																 'user_id':     main_member[0].member_id.user_id.id})
				else:
					raise ValidationError(_('عذرا , يجب تحديد العضو الرئيسي للجنة اولا من اعدادات المركز'))