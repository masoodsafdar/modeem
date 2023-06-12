# -*- coding: utf-8 -*-
import odoo.http as http
from odoo.http import Response
from odoo import SUPERUSER_ID
import sys, json
import logging
_logger = logging.getLogger(__name__)
from odoo.http import request
from datetime import datetime,timedelta,date
from dateutil.relativedelta import relativedelta
from odoo import models,fields,api
from openerp import fields
class WebFormController(http.Controller):    
    
    @http.route('/user_guide/user_guide/<string:name>/<string:featurer>/<string:description>/<string:attachment>/<string:video>', type='http', auth='public',  csrf=False)
	def get_feature(self,**args):
		result=[]
		## master:name / details: featuers
		#search (get all modules)
		modules_ids=request.env['mk.user.guide'].sudo().search([])
			#-- list ids (modules_ids)
			for module in modules_ids:
				if module.portal_true=='True':
					featuers_list=[]
					for featuers in module.info:
						featuers_list.append({'feature':featuers.feature,
							                  'description':featuers.description
							                  'attachment' :featuers.attachment
							                  'video':featuers.video})
					result.append({'name':name,'finfo':featuers_list})
			print("#################################",result)
		return str(result)
