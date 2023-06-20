from odoo import models, fields, api
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)
    
class Testperiod(models.Model):
	_name='test.period'
	_inherit=['mail.thread','mail.activity.mixin']

	name        = fields.Char(string="Period name",    tracking=True)
	total_hours = fields.Integer(string="Total Hours", tracking=True)
	active      = fields.Boolean(string="active", default=True, groups="maknon_tests.group_test_period_archives", tracking=True)

	@api.model
	def test_periods(self):
		query_string = ''' 
		     select id, name 
		     from test_period
		     where active=True
		     order by id;
		     '''
		self.env.cr.execute(query_string)
		test_periods = self.env.cr.dictfetchall()
		return test_periods