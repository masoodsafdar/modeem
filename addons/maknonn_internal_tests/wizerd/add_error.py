from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
class AddERror(models.TransientModel):    
	_name="add.error.q"

	item=fields.Many2one("mk.discount.item",string="Item")
	evaluation_item=fields.Many2one("mk.evaluation.items",string="evaluation item")
	question_id=fields.Many2one("test.questions",string="question")
	value=fields.Integer(string="Error value")

	@api.onchange('question_id')
	def change_quasasa(self):
		print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHI")
		items=self.env['mk.discount.item'].search([('evaluation_item','in',self.question_id.internal_session_id.evaluation_items.ids)])
		if items:
			return {'domain':{'item':[('id', 'in', items.ids)]}}
	
	@api.multi
	def ok(self):
	    self.env['question.error'].create({
				'item':self.item.id,
				'question_id':self.question_id.id,
				'value':self.value
				})
