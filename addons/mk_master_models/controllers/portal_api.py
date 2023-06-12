#-*- coding:utf-8 -*-
import odoo.http as http
from odoo.http import Response, request
from odoo import SUPERUSER_ID
import json

import logging

_logger = logging.getLogger('_______logger ____________')


class MosqueContollers(http.Controller):

	@http.route('/public/mosque/create', type="json", methods=['POST'], auth="public", csrf=False)
	def public_mosque_create(self, **kw):
		try:
			data = {}
			for field_name, field_value in kw.items():
				data[field_name] = field_value
			mosque = request.env['mk.mosque']
			try:
				mosq_details = mosque.create_from_portal(data)
				msg = {'success': 0, 'mosque_id': mosq_details['mosque_id'],
					   'register_code': mosq_details['register_code']}
				return msg
			except Exception as e:
				error_string = str(e)
				if "\n" in error_string:
					error_string = error_string.split("\n")[0]
				return json.dumps({'status': 'Failed', 'error': error_string})

		except Exception as e:
			return json.dumps({'status': 'Failed', 'error': str(e)})
