#-*- coding:utf-8 -*-
import odoo.http as http
from odoo.http import Response, request
from odoo import SUPERUSER_ID
import json

import logging

_logger = logging.getLogger('_______logger ____________')


class WebFormController(http.Controller):

	@http.route('/register/get/areas', type='json', auth='public',  csrf=False)
	def get_areas(self, **args):
		res = []
		for area in request.env['res.country.state'].sudo().search([('type_location','=','area'), ('enable','=',True)]):
			res += [{'id':   area.id,
					 'name': area.name}]
		return res
	
	@http.route('/register/get/cities/<int:area_id>', type='json', auth='public',  csrf=False)
	def get_cities(self, **args):
		#data = json.loads(request.httprequest._cached_data)
		#request.httprequest._cached_data
		res = []		
		area_id = args.get('area_id', 0)
		for city in request.env['res.country.state'].sudo().search([('type_location','=','city'), ('enable','=',True), ('area_id','=',area_id)]):
			res += [{'id':   city.id,
					 'name': city.name}]
		return res
	
	@http.route('/register/get/districts/<int:city_id>', type='json', auth='public',  csrf=False)
	def get_districts(self, **args):
		res = []		
		city_id = args.get('city_id', 0)
		for district in request.env['res.country.state'].sudo().search([('type_location','=','district'), ('enable','=',True), ('district_id','=',city_id)]):
			res += [{'id':   district.id,
					 'name': district.name}]
		return res
	
	@http.route('/register/get/building_types', type='json', auth='public',  csrf=False)
	def get_building_types(self, **args):
		res = []
		for building_type in request.env['mk.building.type'].sudo().search([]):
			res += [{'id':   building_type.id,
					 'name': building_type.name}]
		return res
	
	@http.route('/register/get/nationalities', type='json', auth='public',  csrf=False)
	def get_nationalities(self, **args):				
		res = []
		sa_nationality = request.env.ref('base.pm')
		if not sa_nationality:
			return res
		
		sa_nationality_id = sa_nationality.id
		sa_arabic = request.env['ir.translation'].sudo().search([('res_id','=',sa_nationality_id),
															   ('name','=','res.country,name'),
															   ('lang','=','ar_SY')], limit=1)
		
		if not sa_arabic:
			return res
		
		res = [{'id':   sa_nationality.id,
			    'name': sa_arabic.value}]
		return res
	
	@http.route('/register/get_episodes_data/<int:episode_id>', type='json', auth='public',  csrf=False)
	def get_episodes(self,episode_id,**args):
		results=[]
		periods=[]
		jobs_data=[]
		grades_data=[]
		episode_data=request.env['mk.episode'].sudo().browse(SUPERUSER_ID).search([('id','=',episode_id)])
		for epi in episode_data:
			if epi.subh:
				periods.append('s')
			if epi.zuhr:
				periods.append('z')
			if epi.aasr:
				periods.append('a')
			if epi.magrib:
				periods.append('m')
			if epi.esha:
				periods.append('e')
			if epi.teacher_id:
				teacher=epi.teacher_id.name
			else:
				teacher=''
			if epi.episode_work:
				episode_work=epi.episode_work.name
			else:
				episode_work=''
			if epi.episode_type:
				episode_type=epi.episode_type.name
			else:
				episode_type=''
			if epi.teacher_id:
				teacher_id=epi.teacher_id.id
			else:
				teacher_id=''
			for job in epi.job_ids:
				jobs_data.append([job.id,job.name])
			for grade in epi.grade_ids:
				grades_data.append([grade.id,grade.name])
			results.append({
				'id':epi.id,'episode_name':epi.name,
				'mosque_id':epi.mosque_id.id,'mosque_name':epi.mosque_id.name,
				'study_year_id':epi.academic_id.id,'study_year_name':epi.academic_id.name,
				'study_class_id':epi.study_class_id.id,'study_class_name':epi.study_class_id.name,
				'start_date':epi.start_date,'women_or_men':epi.women_or_men,'end_date':epi.end_date,
				'episode_work_id':epi.episode_work.id,'episode_work_name':episode_work,
				'episode_type_id':epi.episode_type.id,'episode_type_name':episode_type,
				'job_ids':jobs_data,'grade_ids':grades_data,
				'teacher_id':teacher_id,'teacher_name':teacher,
				'period_ids':periods})
		return str(results)

	@http.route('/register/get/mosque/info/<int:mosque_id>', type='json', auth='public',  csrf=False)	
	def get_mosque_inf(self, mosque_id, **args):

		if mosque_id == 0:
			episode_ids=request.env['mk.episode'].sudo().search([('state', '=', 'accept')])
			teacher_ids=request.env['hr.employee'].sudo().search([('state', '=', 'accept'),('category','=','teacher')])
			supervisor_ids=request.env['hr.employee'].sudo().search([('state', '=', 'accept'),('category','=','supervisor')])
			#student_ids=request.env['mk.student.register'].sudo().search([])
			mosques=request.env['mk.mosque'].sudo().search([])
			#rec.teacher_ids=teacher_ids
			#courses=request.env['mk.course.request'].sudo().search([('state','=','accept')])

			return  str({'mosques':len(mosques),
                         'teachers_number':len(teacher_ids),
                         'episodes_number':len(episode_ids),
                         'student_number': [],#len(student_ids),
                         'supervisor':len(supervisor_ids)})


		else:
			episode_ids=request.env['mk.episode'].sudo().search([('mosque_id', '=', mosque_id), ('state', '=', 'accept')])
			teacher_ids=request.env['hr.employee'].sudo().search([('state', '=', 'accept'), ('mosqtech_ids', '=', mosque_id), ('category','=','teacher')])
			#student_ids=request.env['mk.student.register'].sudo().search([('mosque_id', '=', mosque_id)])
			mosques=request.env['mk.mosque'].sudo().search([('id','=',mosque_id)])
			#rec.teacher_ids=teacher_ids
			#courses=request.env['mk.course.request'].sudo().search([('state','=','accept'),('mosque_id','=',mosque_id)])
			return  str({'teachers_number':len(teacher_ids),
                         'episodes_number':len(episode_ids),
                         'student_number': [], #len(student_ids),
                         'supervisor':len(mosques.supervisors)})
			
	@http.route('/register/study_class_data', type='json', auth='public',  csrf=False)
	def get_study_class(self,**args):
		result={}
		
		leaves=[]
		study_class_ids=request.env['mk.study.class'].sudo().search([('is_default','=', True)])
		formal_leave_ids=request.env['mk.formal.leave'].sudo().search([('start_date','>=', study_class_ids[0].start_date),('end_date','<=', study_class_ids[0].end_date),('study_year_id', '=', study_class_ids[0].study_year_id.id)])
		for leave in formal_leave_ids:
			leaves.append({
				'name':leave.leave_id.name,
				'start_date':leave.start_date,
				'islamic_start_date':leave.islamic_start_date,
				'islamic_end_date':leave.islamic_end_date,
				'end_date':leave.end_date
				})
		leaves = sorted(leaves, key=lambda k: k['start_date'])
		if study_class_ids:
			result={'name': study_class_ids[0].name,'islamic_start_date':study_class_ids[0].islamic_start_date,'islamic_end_date':study_class_ids[0].islamic_end_date,
				'start_date':study_class_ids[0].start_date,'end_date':study_class_ids[0].end_date, 'holidays':leaves}
		return result

	@http.route('/register/episode',type='json',auth='public',csrf=False)
	def register_episode(self,**args):
		res = []
		mosq=args.get('mosque_id',{})
		emp=args.get('employee_id',{})
		emp_recs = request.env['hr.employee'].sudo().search([('id','=',emp),('category','in',['admin']),('category2','in',['admin'])])
		
		for emp in emp_recs:
			emp.update({'mosqtech_ids':(4,mosq)})

	@http.route('/register/get/aya/<int:surah_id>',type='json', auth='public',  csrf=False)	
	def get_aya_surah(self, surah_id, **args):
		result=[]
		surah_verses_model=request.env['mk.surah.verses']
		verses=surah_verses_model.sudo().search([('surah_id','=',surah_id)])
		for rec in verses:
			result.append(rec.verse)
		return str(result)

	@http.route('/motivate/mosque/<int:center_id>/<string:type_categ>/<int:supervisor_id>/<int:mosque_id>/<int:teacher_id>',type='json',auth='public',csrf=False)
	def motivate_mosque_id(self,mosque_id,center_id,teacher_id,supervisor_id,type_categ,**args):
		episode_domain=[('state','=','accept')]
		categ_ids=request.env['mk.mosque.category'].sudo().search([('mosque_type','=',type_categ)]).ids
		msq_ids=request.env['mk.mosque'].sudo().search([('categ_id','in',categ_ids)]).ids

		if center_id!=0:
			if type_categ!='all':
				msq_ids=request.env['mk.mosque'].sudo().search([('categ_id','in',categ_ids),('center_department_id','=',center_id),('state', '=', 'accept')]).ids
				episode_domain=[('state', '=', 'accept'),('mosque_id','in',msq_ids)]
			else:
				episode_domain=episode_domain

		if mosque_id!=0:
			

				episode_domain=[('state', '=', 'accept'),('mosque_id','=',mosque_id)]
		if  teacher_id!=0:
			
				episode_domain=[('state', '=', 'accept'),('mosque_id','=',mosque_id),('teacher_id','=',teacher_id)]
		if  supervisor_id!=0:
			sup_rec=request.env['hr.employee'].search([('id','=',supervisor_id)]).mosque_sup.ids
			episode_domain=[('state', '=', 'accept'),('mosque_id','in',sup_rec)]

		episode_links=request.env['mk.episode'].sudo().search(episode_domain)

		result=[]
		episode_types=[]
		epi_dic={}
		ep_parts=0
		for episode in episode_links:
			if episode.mosque_id.center_department_id.id==center_id:
				episode_productivity=0
				test_student_model=request.env['mk.test.result.student']
				test_recs=test_student_model.sudo().search([('student_id','in',episode.students_list.ids)])


				for  test_rec in test_recs:

						if test_rec.total_dgrees>test_rec.min_score:
							student_test=request.env['mk.test.internal.registerations'].sudo().search([('student_id','=',test_rec.student_id.id)])
							#ep_parts+=len(test_rec.test_type_id.test_branch_ids.part_ids.ids)
							if student_test:
								ep_parts+=len(student_test.test_branch_id.part_ids.ids)


		return str(ep_parts)

	@http.route('/register/update_mosque/<int:target_id>/<int:mosque_id>/<int:is_student>/',type='json',auth='public',csrf=False)
	def register_update_mosque_id(self,target_id,mosque_id,is_student,**args):
		res = []
		#mosq=args.get('mosque_id',{})
		#emp=args.get('employee_id',{})
		if is_student==0:
			emp_recs = request.env['hr.employee'].sudo().search([('id','=',target_id),('category','in',['admin'])])
			for emp in emp_recs:
				emp.update({'mosqtech_ids':[(4,mosque_id)]})
		else:
			st_recs = request.env['mk.student.register'].sudo().search([('id','=',target_id)])
			for st in st_recs:
				st.update({'mosque_id':[(4,mosque_id)]})
		
		return "done"


class CreateMosqueCategory(http.Controller):

	@http.route('/public/mosque_category', type="http", methods=['GET', 'POST'], auth="public", csrf=False)
	def CreateMosqueCategory(self, **kw):
		try:
			obj_mosq_categ = request.env['mk.mosque.category']
			vals = {}
			if 'name' in kw.keys():
				vals.update({'name': kw.get('name')})
			if 'mosque_type' in kw.keys():
				vals.update({'mosque_type': kw.get('mosque_type')})
			if 'order_categ' in kw.keys():
				vals.update({'order_categ': kw.get('order_categ')})
			if 'is_complexe' in kw.keys():
				is_complexe = kw.get('is_complexe')
				if is_complexe == 'False':
					vals.update({'is_complexe': False})
				else:
					vals.update({'is_complexe': True})
			if 'code' in kw.keys():
				code = kw.get('code')
				vals.update({'code': kw.get('code')})
			if 'active' in kw.keys():
				active = kw.get('active')
				if active == 'False':
					vals.update({'active': False})
				else:
					vals.update({'active': True})


			mosque_categ = obj_mosq_categ.sudo().search([('code', '=', code),
														 '|', ('active', '=', True),
														 	  ('active', '=', False)], limit=1)

			if not mosque_categ:
				mosque_categ = obj_mosq_categ.sudo().create(vals)
			else:
				mosque_categ.write(vals)

			return json.dumps({'status': 'OK', 'id': mosque_categ.id})
		except Exception as e:
			return json.dumps({'status': 'Failed', 'error': str(e)})


	@http.route('/public/delete_mosque_category', type="http", methods=['GET', 'POST'], auth="public", csrf=False)
	def DeleteMosqueCategory(self, **kw):
		try:
			if 'code' in kw.keys():
				code = kw.get('code')
			if code:
				mosque_categ = request.env['mk.mosque.category'].sudo().search([('code', '=', code),
															 '|', ('active', '=', True),
																  ('active', '=', False)], limit=1)
				if mosque_categ:
					mosque_categ.write({'active': False})
					return json.dumps({'status': 'OK', 'id': mosque_categ.id})
		except Exception as e:
			return json.dumps({'status': 'Failed', 'error': str(e)})


class DepartmentCategory(http.Controller):

	@http.route('/public/department_category', type="http", methods=['GET', 'POST'], auth="public", csrf=False)
	def CreateDepartmentCategory(self, **kw):
		try:
			obj_mosq_categ = request.env['hr.department.category']
			vals = {}
			if 'name' in kw.keys():
				vals.update({'name': kw.get('name')})
			if 'code' in kw.keys():
				code = kw.get('code')
				vals.update({'code': kw.get('code')})
			if 'active' in kw.keys():
				active = kw.get('active')
				if active == 'False':
					vals.update({'active': False})
				else:
					vals.update({'active': True})

			mosque_categ = obj_mosq_categ.sudo().search([('code', '=', code),
														 '|', ('active', '=', True),
														 	  ('active', '=', False)], limit=1)

			if not mosque_categ:
				mosque_categ = obj_mosq_categ.sudo().create(vals)
			else:
				mosque_categ.write(vals)

			return json.dumps({'status': 'OK', 'id': mosque_categ.id})
		except Exception as e:
			return json.dumps({'status': 'Failed', 'error': str(e)})


	@http.route('/public/delete_department_category', type="http", methods=['GET', 'POST'], auth="public", csrf=False)
	def DeleteDepartmentCategory(self, **kw):
		try:
			if 'code' in kw.keys():
				code = kw.get('code')
			if code:
				mosque_categ = request.env['hr.department.category'].sudo().search([('code', '=', code),
																				 '|', ('active', '=', True),
																					  ('active', '=', False)], limit=1)
				if mosque_categ:
					mosque_categ.write({'active': False})

			return json.dumps({'status': 'OK', 'id': mosque_categ.id})
		except Exception as e:
			return json.dumps({'status': 'Failed', 'error': str(e)})


class ResCountryStateControllers(http.Controller):

	@http.route('/public/country_state', type="http", methods=['GET', 'POST'], auth="public", csrf=False)
	def CountryStateController(self, **kw):
		try:
			obj_country_state = request.env['res.country.state']
			vals = {'type_location':'district'}
			if 'name' in kw.keys():
				vals.update({'name': kw.get('name')})
			if 'district_code' in kw.keys():
				code = kw.get('district_code')

				vals.update({'district_code': kw.get('district_code')})
				country_state = obj_country_state.sudo().search([('district_code', '=', code),
																 ('type_location', '=', 'district'),
																 '|', ('active', '=', True),
																 	  ('active', '=', False)], limit=1)

			## In case of creating new country state we make public administration as default center department and flag is Flase

			department_id = request.env['hr.department'].sudo().search([('id', '=', 42)])
			code = kw.get('district_code')
			vals.update({'code': code[len(code)-2:]})

			if not country_state:

				district = obj_country_state.sudo().search([('type_location', '=', 'city')], limit=1)
				vals.update({'center_department_id': department_id.id,
							 'flag': True,
							 'district_id': district.id})
				country_state = obj_country_state.sudo().create(vals)
			else:

				country_state.write(vals)
			return json.dumps({'status': 'OK', 'id': country_state.id})
		except Exception as e:
			return json.dumps({'status': 'Failed', 'error': str(e)})

	@http.route('/public/delete_country_state', type="http", methods=['GET', 'POST'], auth="public", csrf=False)
	def DeleteCountryStateController(self, **kw):
		try:
			obj_country_state = request.env['res.country.state']
			vals = {'type_location':'district'}
			if 'name' in kw.keys():
				vals.update({'name': kw.get('name')})
			if 'district_code' in kw.keys():
				code = kw.get('district_code')

				vals.update({'district_code': kw.get('district_code')})
				country_state = obj_country_state.sudo().search([('district_code', '=', code),
																 ('type_location', '=', 'district'),
																 '|', ('active', '=', True),
																 	  ('active', '=', False)], limit=1)

				if country_state:
					country_state.write({'active': False})
			return json.dumps({'status': 'OK', 'id': country_state.id})
		except Exception as e:
			return json.dumps({'status': 'Failed', 'error': str(e)})


class MosqueContollers(http.Controller):

	@http.route('/public/mosque', type="http", methods=['GET', 'POST'], auth="public", csrf=False)
	def CreateMosque(self, **kw):
		try:
			obj_country_state = request.env['res.country.state']
			vals = {}
			if 'name' in kw.keys():
				vals.update({'name': kw.get('name')})
			if 'mosque_type' in kw.keys():
				vals.update({'mosque_type': kw.get('mosque_type')})
			if 'district_id' in kw.keys():
				code = kw.get('district_id')
				country_state = obj_country_state.sudo().search([('district_code', '=', code),
																 ('type_location', '=', 'district'),
																 '|', ('active', '=', True),
																      ('active', '=', False)], limit=1)
				if country_state:
					vals.update({'district_id': country_state.id})
			if 'category_id' in kw.keys():
				category_code = kw.get('category_id')
				dept_categ = request.env['hr.department.category'].sudo().search([('code', '=', category_code),
																					'|', ('active', '=', True),
																						 ('active', '=', False)], limit=1)
				vals.update({'mosq_type': dept_categ.id})
			if 'build_type_id' in kw.keys():
				build_type_id = kw.get('build_type_id')
				build_typ = request.env['mk.building.type'].sudo().search([('code', '=', build_type_id),
																			'|', ('active', '=', True),
																				('active', '=', False)], limit=1)
				vals.update({'build_type': build_typ.id})
			if 'mosque_category_id' in kw.keys():
				mosque_categ_code = kw.get('mosque_category_id')
				mosque_categ = request.env['mk.mosque.category'].sudo().search([('code', '=', mosque_categ_code),
																				'|', ('active', '=', True),
																					 ('active', '=', False)], limit=1)
				vals.update({'categ_id': mosque_categ.id})
			# if 'manager_id' in kw.keys():
			# 	manager_identification_id = kw.get('manager_id')
			# 	manager = request.env['hr.employee'].sudo().search([('identification_id', '=', manager_identification_id),
			# 													 '|', ('active', '=', True),
			# 													       ('active', '=', False)], limit=1)
			#
			# 	if manager:
			# 		vals.update({'mosque_admin_id': manager.id})

			if 'active' in kw.keys():
				active = kw.get('active')
				if active == 'False':
					vals.update({'active': False})
				else:
					vals.update({'active': True})
			if 'complex_name' in kw.keys():
				vals.update({'complex_name': kw.get('complex_name')})
			if 'episodes' in kw.keys():
				vals.update({'episodes': kw.get('episodes')})
			if 'latitude' in kw.keys():
				vals.update({'latitude': kw.get('latitude')})
			if 'longitude' in kw.keys():
				vals.update({'longitude': kw.get('longitude')})
			if 'is_maneg_mosque' in kw.keys():
				vals.update({'check_maneg_mosque': kw.get('is_maneg_mosque')})
			if 'is_parking_mosque' in kw.keys():
				vals.update({'check_parking_mosque': kw.get('is_parking_mosque')})
			if 'register_code' in kw.keys():
				vals.update({'register_code': kw.get('register_code')})
			if 'episode_value' in kw.keys():
				vals.update({'episode_value': kw.get('episode_value')})
			if 'code' in kw.keys():
				code = kw.get('code')
				vals.update({'code': code})
				mosque = request.env['mk.mosque'].sudo().search([('code', '=', code),
														    	  '|', ('active', '=', True),
																	   ('active', '=', False)], limit=1)
			if 'responsible_department' in kw.keys():
				code_admin_dept = kw.get('responsible_department')
				center_department = request.env['hr.department'].sudo().search([('department_code','=',code_admin_dept)])
				vals.update({'center_department_id': center_department.id})
			if not mosque:
				city = obj_country_state.sudo().search([('type_location', '=', 'city')], limit=1)
				area = obj_country_state.sudo().search([('type_location', '=', 'area')], limit=1)
				vals.update({'city_id': city.id,
							 'area_id': area.id})
				mosque = request.env['mk.mosque'].sudo().create(vals)
			else:
				mosque.write(vals)
			if mosque:
				mosque.sudo().write({'is_synchro_edu_admin': True})
				return json.dumps({'status': 'OK', 'id': mosque.id, 'mosque_id': mosque.id, 'register_code':  mosque.register_code})
			return json.dumps({'status': 'Failed', 'error': 'No data'})
		except Exception as e:
			return json.dumps({'status': 'Failed', 'error': str(e)})


	@http.route('/public/delete_mosque', type="http", methods=['GET', 'POST'], auth="public", csrf=False)
	def DeleteMosque(self, **kw):
		try:
			if 'code' in kw.keys():
				code = kw.get('code')
				if code:
					mosque = request.env['mk.mosque'].sudo().search([('code', '=', code),
																	  '|', ('active', '=', True),
																		   ('active', '=', False)], limit=1)
					if mosque:
						mosque.sudo().write({'active': False,
											 'is_synchro_edu_admin': False})

				return json.dumps({'status': 'OK', 'id': mosque.id})
		except Exception as e:
			return json.dumps({'status': 'Failed', 'error': str(e)})

class BuildingTypeControllers(http.Controller):

	@http.route('/public/building_type', type="http", methods=['GET', 'POST'], auth="public", csrf=False)
	def BuildingTypeController(self, **kw):
		try:
			obj_building_type = request.env['mk.building.type']
			vals = {}
			if 'name' in kw.keys():
				vals.update({'name': kw.get('name')})
			if 'active' in kw.keys():
				vals.update({'active': kw.get('active')})
			if 'code' in kw.keys():
				code = kw.get('code')
				vals.update({'code': kw.get('code')})

				building_type = obj_building_type.sudo().search([('code', '=', code),
																 '|', ('active', '=', True),
																 	  ('active', '=', False)], limit=1)
			if not building_type:
				building_type = obj_building_type.sudo().create(vals)
			else:
				building_type.write(vals)
			return json.dumps({'status': 'OK', 'id': building_type.id})
		except Exception as e:
			return json.dumps({'status': 'Failed', 'error': str(e)})

	@http.route('/public/delete_building_type', type="http", methods=['GET', 'POST'], auth="public", csrf=False)
	def DeleteBuildingTypeController(self, **kw):
		try:
			obj_building_type = request.env['mk.building.type']
			vals = {}
			if 'name' in kw.keys():
				vals.update({'name': kw.get('name')})
			if 'active' in kw.keys():
				vals.update({'active': kw.get('active')})
			if 'code' in kw.keys():
				code = kw.get('code')
				vals.update({'code': kw.get('code')})

				building_type = obj_building_type.sudo().search([('code', '=', code),
																 '|', ('active', '=', True),
																 	  ('active', '=', False)], limit=1)
				if building_type:
					building_type.write({'active': False})
			return json.dumps({'status': 'OK', 'id': building_type.id})
		except Exception as e:
			return json.dumps({'status': 'Failed', 'error': str(e)})