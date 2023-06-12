from odoo import models, fields, api
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)
    
class Testperiod(models.Model):
	_name='test.period'
	_inherit = ['mail.thread']

	name        = fields.Char(string="Period name",    track_visibility='onchange')
	total_hours = fields.Integer(string="Total Hours", track_visibility='onchange')
	active      = fields.Boolean(string="active", default=True, groups="maknon_tests.group_test_period_archives", track_visibility='onchange')

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