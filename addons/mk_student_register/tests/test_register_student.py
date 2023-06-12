
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.exceptions import Warning

class Mk_RegStudent_TestCase(TransactionCase):


	def setUp(self):

		super(Mk_RegStudent_TestCase, self).setUp()
		student_reg_model = self.env['mk.student.register']

		student_reg_model.create(
			{
			 'name':name,
			}
		)



