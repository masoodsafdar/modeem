#-*- coding:utf-8 -*-
import openerp.http as http
from openerp.http import Response
from openerp import SUPERUSER_ID
import sys, json
import logging
from datetime import datetime,timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
_logger = logging.getLogger(__name__)
from openerp.http import request
import operator

class MotivicationController(http.Controller):

	###############################################
	# Get student information with it's points (accept student id and return json data)
	##############################################
	@http.route('/get_student_info/<int:student_id>', type='http',website=True ,auth='public', methods=['GET'] ,csrf=False)
	def get_studentInfo(self,student_id,**args):
		results = []
		periods = []
		jobs_data = []
		grades_data = []

		student_data = request.env['mk.student.register'].sudo().search([('id','=',student_id)])

		for stu in student_data :
		
			results.append({
				'id':stu.id})
		return str(results)

	@http.route('/get_all_prizes', type='http',website=True ,auth='public', methods=['GET'] ,csrf=False)
	def get_all_prizes(self,**args):
		""" To Do: return all data of prizes(products) and display it 
		accept nothing but return json data of prizes
		"""
		return

	@http.route('/store/confirm_puy_prizes/<int:prize_id>', type='json',website=True ,auth='public', methods=['GET'] ,csrf=False)
	def confirm_puy_prize(self,prize_id,**args):
		""" To Do: achieve process of prize selection and points markdown
		"""
		return


	@http.route('/store/initial_selection_prize/<int:prize_id>', type='json',website=True ,auth='public', methods=['GET'] ,csrf=False)
	def initial_selection_prize(self,prize_id,**args):
		""" To Do: achieve process of prize selection without confirmation just add to pasket
		"""
		return

	@http.route('/store/delete_order/<int:order_id>', type='json',website=True ,auth='public', methods=['GET'] ,csrf=False)
	def delete_order(self,order_id,**args):
		""" To Do: achieve process of order deletion but only if order in new state
		"""
		return

	@http.route('/store/cancel_order/<int:order_id>', type='json',website=True ,auth='public', methods=['GET'] ,csrf=False)
	def cancel_order(self,order_id,**args):
		""" To Do: achieve process of order canceling but only if order in new state
		"""
		return








	