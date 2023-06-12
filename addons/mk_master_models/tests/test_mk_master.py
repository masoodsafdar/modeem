
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.exceptions import Warning

class Mk_Master_TestCase(TransactionCase):


	def setUp(self):

		super(Mk_Master_TestCase, self).setUp()
		center_model = self.env['mk.center']
		stage_model = self.env['mk.stage']
		teacher_model = self.env['mk.teacher']
		associate_model = self.env['mk.associate']

		center_model.create(
			{
			 'name':name,
			}
		)

		stage_model.create(
			{
			 'name':name,
			}
		)

		

		teacher_model.create(
			{
			 'name':name,
			}
		)

		associate_model.create(
			{
			 'name':name,
			}
		)


