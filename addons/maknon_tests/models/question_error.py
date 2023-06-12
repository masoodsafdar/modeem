#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class TestCenterTimetable(models.Model):
	_name = 'question.error'

	item            = fields.Many2one("mk.discount.item",    string="Item")
	evaluation_item = fields.Many2one("mk.evaluation.items", string="evaluation item")
	question_id     = fields.Many2one("test.questions",      string="question")
	value           = fields.Integer("Error numbers")
	surah           = fields.Many2one("mk.surah",        string="Surah")
	aya             = fields.Many2one("mk.surah.verses", string="verses")
	member          = fields.Many2one("hr.employee",     string="العضو")
	user_id         = fields.Many2one("res.users",       string="العضو")

	@api.onchange('member')
	def member_user_id(self):
		if self.member:
			self.user_id=self.member.sudo().user_id.id
			
	@api.model
	def add_question_error(self, quest_err_id, value, member_id, item_id, evaluation_item_id, question_id):
		if quest_err_id:
			quest_err = self.search([('id','=',quest_err_id)], limit=1)
			quest_err.value = value
		else:
			member = self.env['hr.employee'].search([('id','=',member_id)], limit=1)
			user_id = member.user_id.id
			
			quest_err = self.create({'item':           item_id,
									'evaluation_item': evaluation_item_id,
									'question_id':     question_id,
									'value':           value,
									'member':          member_id,
									'user_id':         user_id})
			
			quest_err_id = quest_err.id
		
		return quest_err_id
				