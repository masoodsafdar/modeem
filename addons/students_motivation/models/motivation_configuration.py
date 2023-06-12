from odoo import models, fields, api ,_
from odoo.exceptions import ValidationError


class StandardsItems(models.Model):
	_name  = 'standard.items'

	name        = fields.Char("Name")
	points      = fields.Float("High point")
	active_bool = fields.Boolean("Item Active",default=True) 

	@api.constrains('points')
	def points_validation(self):
		if self.points <= 0 :
			raise ValidationError(_('Item Points cannot be zero or less'))