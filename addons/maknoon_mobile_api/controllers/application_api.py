import re
from random import randint

import requests
from odoo import http, _
from odoo import models, fields, api, tools, SUPERUSER_ID
from odoo.http import Controller, request
from odoo.addons.web.controllers.main import Session
import json
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.http import request, Response
from odoo.fields import Datetime



import logging
_logger = logging.getLogger(__name__)

def get_state_translation_value(model_name=None, field_name=None, field_value=None):
    translated_state = dict(request.env[model_name].sudo().fields_get(allfields=[field_name])[field_name]['selection'])[field_value]
    return translated_state

def deserialise_request_data(data):
    return json.loads(data.decode("utf-8"))


class SessionAuth(Session):
    @http.route('/web/session/authenticate', type='json', auth="none")
    def authenticate(self, db, login, password, base_location=None):
        _logger.info('\n\n\n __________ authenticate')
        responseData = {'success': False}
        try:
            authenticate = super(SessionAuth, self).authenticate(db, login, password, base_location)

            teacher = request.env['hr.employee'].sudo().search([('user_id.partner_id', '=', authenticate.get('partner_id'))])
            responseData['success'] = True
            responseData['data'] =  {'gender': teacher.gender,
                                     'id': teacher.id,
                                     'name': teacher.name,
                                     'user_id': teacher.user_id.id,
                                     }
            responseData['db'] = authenticate.get('db')
            responseData['session_id'] = authenticate.get('session_id')
            responseData['uid'] = authenticate.get('uid')
            responseData['user_context'] = authenticate.get('user_context')
            responseData['username'] = authenticate.get('username')
            responseData['name'] = authenticate.get('name')
            responseData['partner_id'] = authenticate.get('partner_id')
            responseData['web.base.url'] = authenticate.get('web.base.url')
        except Exception as e:
            responseData['success'] = False
            responseData['error'] = e
        return responseData


class MobileAppApi(http.Controller):

    @http.route('/main/reset_pwd', methods=['GET'], auth='public', csrf=False, website=True)
    def reset_pwd(self, **args):
        _logger.info('\n\n\n ________ /main/reset_pwd ')
        responseData = {'success': 1}
        if request.httprequest.method == 'GET':
            try:
                register_code = args.get('register_code')
                _logger.info('\n\n\n ________ register_code : %s   login_as  : %s', register_code, args.get('login_as'))
                if register_code:
                    teacher = request.env['hr.employee'].sudo().search([('registeration_code', '=', register_code)], limit=1)

                    if not teacher:
                        teacher = request.env['hr.employee'].sudo().search([('identification_id', '=', register_code)], limit=1)

                    if not teacher:
                        responseData['success'] = 0
                        responseData['data'] = {'result': 'رقم التسجيل أو الهوية غير مسجل'}

                    else:
                        user = teacher.user_id

                        if user.id == SUPERUSER_ID:
                            result = {'result': 'لا يمكنك تغيير كلمة مرور الأدمين'}

                        if not user:
                            result = {'result': '! هذا الموظف لا يمتلك مستخدم'}
                        prms = {}
                        headers = {
                            'content-type': 'application/json',
                        }

                        n = 4
                        range_start = 10 ** (n - 1)
                        range_end = (10 ** n) - 1
                        passwd = randint(range_start, range_end)


                        email = teacher.work_email

                        if not email:
                            result = {'result': '! يجب إضافة إيميل التواصل للموظف'}
                        if user.id == 24329 or user.id == 25530:
                            pass
                        else:
                            teacher.sudo().passwd = passwd
                            user.sudo().write({'password': passwd, })
                            request.env['mk.general_sending'].sudo().send_by_template('mk_send_pass_employee',str(teacher.id))

                            mobile_phone = teacher.mobile_phone

                            if mobile_phone:
                                try:
                                    message = request.env['mk.sms_template'].search([('code', '=', 'mk_send_pass')],limit=1)
                                    message = message[0].sms_text
                                    message = re.sub(r'val1', str(passwd), message).strip()

                                    department_id = request.env['hr.department'].sudo().search([('id', '=', 42)])

                                    if department_id.send_time:
                                        hr_time = int(department_id.send_time)
                                        prms[department_id.gateway_config.time_send] = str(hr_time) + ":" + str(
                                            int((department_id.send_time - hr_time) * 60)) + ":" + '00'
                                    prms[department_id.gateway_config.user] = department_id.gateway_user
                                    prms[department_id.gateway_config.password] = department_id.gateway_password
                                    prms[department_id.gateway_config.sender] = department_id.gateway_sender
                                    prms[department_id.gateway_config.to] = '966' + mobile_phone
                                    prms[department_id.gateway_config.message] = message

                                    url = department_id.gateway_config.url

                                    if prms:
                                        requests.post(url, data=json.dumps(prms), headers=headers)
                                except:
                                    pass

                            result = {'result': 3}

                        responseData['success'] = 0
                        responseData['data'] = result
            except Exception as e:
                responseData['success'] = 1
                responseData['error'] = (e)
        return json.dumps(responseData)

    def check_line_state(self, line):
        to_aya = line.to_aya.original_surah_order
        next_aya = request.env['mk.surah.verses'].sudo().search([('surah_id', '=', line.to_surah.id),
                                                       ('original_surah_order', '=', to_aya+1)], limit=1)

        if next_aya:
            from_surah = line.to_surah.name
            from_aya = next_aya.original_surah_order
        else:
            order_surah = line.to_surah.order + 1

            surah_id = request.env['mk.surah'].sudo().search([('order', '=', order_surah)], limit=1)

            aya_id = request.env['mk.surah.verses'].sudo().search([('surah_id', '=', surah_id.id),
                                                        ('original_surah_order', '=', 1)], limit=1)

            from_surah = surah_id.name if surah_id.name else None
            from_aya = aya_id.original_surah_order
        vals = {'degree': line.degree or None,
                'from_aya': from_aya or 1,
                'from_sura_name': from_surah or None,
                'mistake': line.mistake or 0,
                'prep_id': line.preparation_id.id or None,
                'to_aya': None,
                'to_sura_name': None}
        return vals

    @http.route('/main/teacher/episodes', auth="user",  method='GET', csrf=False)
    def teacher_episodes(self, **args):
        user_id = request.env.user.id
        responseData = {'success': False}
        episodes = []
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    episode_ids = request.env['mk.episode'].sudo().search([('teacher_id', '=', int(args.get('teacher_id'))),
                                                                           ('study_class_id.is_default', '=', True),
                                                                           ('state', '=', 'accept')])

                    for episode in episode_ids:
                        episodes.append({'display_name': episode.display_name,
                                         'epsd_type':    episode.episode_type and episode.episode_type.name or False,
                                         'epsd_work':    episode.episode_work and episode.episode_work.name or False,
                                         'id':           episode.id,
                                         'name':         episode.name})
                    responseData['success'] = True
                    responseData['result'] = episodes
            except Exception as e:
                responseData['success'] = False
                responseData['error'] = e
        return  Response(json.dumps(responseData['result']), content_type="application/json", status=200)

    @http.route('/main/teacher/order_students', auth="user",  method='GET', csrf=False)
    def teacher_order_students(self, **args):
        user_id = request.env.user.id
        responseData = {'success': False}
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    episode_id = int(args.get('episode_id'))
                    filter = args.get('filter')
                    students = []
                    actual_date = datetime.strptime(fields.Date.today(), '%Y-%m-%d').date()
                    links = request.env['mk.link'].sudo().search([('episode_id', '=', episode_id),
                                                        ('state', '=', 'accept')])
                    presences = request.env['mk.student.prepare.presence'].sudo().search([('episode_id', '=', episode_id),
                                                                                       ('presence_date', '=', actual_date)])
                    # test_sessions = request.env['student.test.session'].sudo().search([('episode_id', '=', episode_id),
                    #                                                                    ('state', '!=', 'cancel')])
                    for link in links:
                        link_id = link.id

                        presence = presences.filtered(lambda p: p.link_id == link)
                        state = 'تحضير الطالب'
                        if presence:
                            presence = presence[0]
                            state = get_state_translation_value('mk.student.prepare.presence', 'status',presence.status)

                        age = 0
                        # dob = link.student_id.birthdate
                        # if dob:
                        #     d1 = datetime.strptime(dob, "%Y-%m-%d").date()
                        #     d2 = date.today()
                        #     age = relativedelta(d2, d1).years
                        preparation = link.preparation_id
                        general_behavior = preparation.general_behavior_type
                        general_behavior_type = False
                        if general_behavior:
                            general_behavior_type = get_state_translation_value('mk.student.prepare','general_behavior_type',general_behavior)

                        vals = {'id': link_id,
                                'student_id': link.student_id.id,
                                'plan_id': preparation.id,
                                'general_behavior_type': general_behavior_type,
                                'name': link.student_id.display_name,
                                'rate': 0,
                                'age': age,
                                'state': state}

                        # test_session = test_sessions.filtered(lambda t: t.student_id == link)
                        # if test_session:
                        #     vals.update({'test_register': True,
                        #                  'session_id': test_session.id,
                        #                  'type_exam_id': test_session.test_name.id,
                        #                  'track': test_session.branch.trackk,
                        #                  'branch_id': test_session.branch.id,
                        #                  'period_id': test_session.test_time.id})
                        # else:
                        vals.update({'test_register': False,
                                     'session_id': False,
                                     'type_exam_id': False,
                                     'track': False,
                                     'branch_id': False,
                                     'period_id': False})
                        students += [vals]
                    responseData['success'] = True
                    responseData['result'] = students
            except Exception as e:
                responseData['success'] = False
                responseData['error'] = str(e)
        return  Response(json.dumps(responseData['result']), content_type="application/json", status=200)

    @http.route('/main/teacher/educational_plan', auth="user",  method='GET', csrf=False)
    def educational_plan(self, **args):
        user_id = request.env.user.id
        responseData = {'success': False}
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    episode_id = int(args.get('episode_id'))
                    student_id = int(args.get('student_id'))

                    line_link = request.env['mk.link'].sudo().search([('episode_id', '=', episode_id),
                                                               ('student_id', '=', student_id)], limit=1)
                    lines = request.env['mk.listen.line'].sudo().search([('student_id', '=', line_link.id)], order='order')

                    memorize_lines = []
                    s_review_lines = []
                    big_review_lines = []
                    tlawa_lines = []

                    if line_link.is_memorize:
                        for line in lines.filtered(lambda l: l.type_follow == 'listen'):
                            memorize_lines.append({"prep_id": line.id or None,
                                                   "actual_date": line.actual_date or None,
                                                   "from_sura_name": line.from_surah.name or None,
                                                   "from_aya": line.from_aya.original_surah_order or None,
                                                   "to_sura_name": line.to_surah.name or None,
                                                   "to_aya": line.to_aya.original_surah_order or None,
                                                   "total_mstk_qty": line.total_mstk_qty,
                                                   "total_mstk_read": line.total_mstk_read})

                    if line_link.is_min_review:
                        for line in lines.filtered(lambda l: l.type_follow == 'review_small'):
                            s_review_lines.append({"prep_id": line.id or None,
                                                   "actual_date": line.actual_date or None,
                                                   "from_sura_name": line.from_surah.name or None,
                                                   "from_aya": line.from_aya.original_surah_order,
                                                   "to_sura_name": line.to_surah.name or None,
                                                   "to_aya": line.to_aya.original_surah_order,
                                                   "total_mstk_qty": line.total_mstk_qty,
                                                   "total_mstk_read": line.total_mstk_read})

                    if line_link.is_big_review:
                        for line in lines.filtered(lambda l: l.type_follow == 'review_big'):
                            big_review_lines.append({"prep_id": line.id,
                                                     "actual_date": line.actual_date,
                                                     "from_sura_name": line.from_surah.name or None,
                                                     "from_aya": line.from_aya.original_surah_order,
                                                     "to_sura_name": line.to_surah.name or None,
                                                     "to_aya": line.to_aya.original_surah_order,
                                                     "total_mstk_qty": line.total_mstk_qty,
                                                     "total_mstk_read": line.total_mstk_read})

                    if line_link.is_tlawa:
                        for line in lines.filtered(lambda l: l.type_follow == 'tlawa'):
                            tlawa_lines.append({"prep_id": line.id,
                                                "actual_date": line.actual_date,
                                                "from_sura_name": line.from_surah.name or None,
                                                "from_aya": line.from_aya.original_surah_order,
                                                "to_sura_name": line.to_surah.name or None,
                                                "to_aya": line.to_aya.original_surah_order,
                                                "total_mstk_qty": line.total_mstk_qty,
                                                "total_mstk_read": line.total_mstk_read})

                    educational_plan = {'plan_listen': memorize_lines,
                                        'plan_review_small': s_review_lines,
                                        'plan_review_big': big_review_lines,
                                        'plan_tlawa': tlawa_lines}

                    responseData['success'] = True
                    responseData['result'] = educational_plan

            except Exception as e:
                responseData['success'] = False
                responseData['error'] = e
        return  Response(json.dumps(responseData['result']), content_type="application/json", status=200)

    @http.route('/main/teacher/plan_lines', auth="user",  method='GET', csrf=False)
    def teacher_plain_lines(self, **args):
        user_id = request.env.user.id
        responseData = {'success': False}
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    episode_id = int(args.get('episode_id'))
                    student_id = int(args.get('student_id'))
                    tlawa = {}
                    listen = {}
                    reviewsmall = {}
                    reviewbig = {}

                    link = request.env['mk.link'].search([('episode_id', '=', episode_id),
                                                       ('student_id', '=', student_id),
                                                       ('state', '=', 'accept')], limit=1)
                    preparation_id = link.preparation_id.id
                    default_vals = {'degree': None,
                                    'from_aya': 1,
                                    'from_sura_name': "الفاتحة",
                                    'mistake': 0,
                                    'prep_id': preparation_id or None,
                                    'to_aya': None,
                                    'to_sura_name': None}
                    done_listen_lines = request.env['mk.listen.line'].search([('preparation_id', '=', preparation_id)],order='id desc')

                    if link.is_memorize:
                        done_listen_line = done_listen_lines.filtered(lambda l: l.type_follow == 'listen')
                        listen = done_listen_line and self.check_line_state(done_listen_line[0]) or default_vals

                    if link.is_min_review:
                        done_review_small_line = done_listen_lines.filtered(lambda l: l.type_follow == 'review_small')
                        reviewsmall = done_review_small_line and self.check_line_state(done_review_small_line[0]) or default_vals

                    if link.is_big_review:
                        done_review_big_line = done_listen_lines.filtered(lambda l: l.type_follow == 'review_big')
                        reviewbig = done_review_big_line and self.check_line_state(done_review_big_line[0]) or default_vals

                    if link.is_tlawa:
                        done_tlawa_line = done_listen_lines.filtered(lambda l: l.type_follow == 'tlawa')
                        tlawa = done_tlawa_line and self.check_line_state(done_tlawa_line[0]) or default_vals

                    data = {'tlawa': tlawa,
                            'listen': listen,
                            'reviewsmall': reviewsmall,
                            'reviewbig': reviewbig}
                    responseData['success'] = True
                    responseData['result'] = data

            except Exception as e:
                responseData['success'] = False
                responseData['error'] = e
        return Response(json.dumps(responseData['result']), content_type="application/json", status=200)

    # @http.route('/main/teacher/set_attendance', auth="user", method='POST', csrf=False)
    # def teacher_set_attendance(self, **args):
    #     responseData = {'success': 1}
    #     if request.httprequest.method == 'POST':
    #         try:
    #             if request.env.user._is_public():
    #                 responseData['success'] = False
    #                 responseData['error'] = _('No user is registred with this login')
    #             else:
    #                 preparation_id = int(args.get('plan_id'))
    #                 state = args.get('filter')
    #                 preparation = request.env['mk.student.prepare'].sudo().search([('id', '=', preparation_id)], limit=1)
    #
    #                 episode = preparation.stage_pre_id
    #                 if episode.state == 'done':
    #                     prepare = request.env['mk.student.prepare'].sudo().search([('link_id.student_id', '=', preparation.student_register_id.id),
    #                                                                      ('link_id.state', '=', 'accept'),
    #                                                                      ('study_class_id.is_default', '=', True)], limit=1)
    #                     if prepare:
    #                         preparation = prepare
    #                 actual_date = datetime.strptime(fields.Date.today(), '%Y-%m-%d').date()
    #                 existing_presence = request.env['mk.student.prepare.presence'].sudo().search([('preparation_id', '=', preparation.id),
    #                                                                                               ('presence_date', '=', actual_date)], limit=1)
    #                 if existing_presence:
    #                     existing_presence.sudo().write({'status': state})
    #                 else:
    #                     link = preparation.link_id
    #                     request.env['mk.student.prepare.presence'].sudo().create({'preparation_id': preparation.id,
    #                                                                                          'presence_date': actual_date,
    #                                                                                          'status': state,
    #                                                                                          'link_id': link.id,
    #                                                                                          'episode_id': link.episode_id.id,
    #                                                                                          'mosque_id': link.mosq_id.id,
    #                                                                                          'center_department_id': link.mosq_id.center_department_id.id,
    #                                                                                          'student_register_id': link.student_id.id,
    #                                                                                          'study_year_id': link.academic_id.id,
    #                                                                                          'study_class_id': link.study_class_id.id,
    #                                                                                          'is_from_mobile': True})
    #                 responseData['success'] = 0
    #         except Exception as e:
    #             responseData['success'] = 1
    #             responseData['error'] = e
    #     return Response(json.dumps(responseData), content_type="application/json", status=200)

    @http.route('/main/teacher/mushaf_subject_surahs', auth="user", method='GET', csrf=False)
    def get_mushaf_subject_surahs(self, **args):
        subject_page_id = int(args.get('subject_page_id'))
        responseData = {'success': 1}
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    query_string = '''
                                select id, name, mk_surah.order as surah_order 
                                from mk_surah  where id in (
                                    select distinct from_surah
                                    from mk_subject_page
                                    WHERE active = true and 
                                    subject_page_id = {})
                    			    order by surah_order;'''.format(subject_page_id)

                    request.env.cr.execute(query_string)
                    mushaf_subject_surahs = request.env.cr.dictfetchall()
                    responseData['success'] = 0
                    responseData['data'] = mushaf_subject_surahs

            except Exception as e:
                responseData['success'] = 1
                responseData['error'] = e

        return Response(json.dumps(responseData['data']), content_type="application/json", status=200)

    @http.route('/main/teacher/memorize_method_surah_lines', auth="user", method='GET', csrf=False)
    def get_memorize_method_surah_lines(self, **args):
        subject_page_id = int(args.get('subject_page_id'))
        surah_id = int(args.get('surah_id'))
        responseData = {'success': 1}
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    query_string = '''
                                   select m.id, 
                                   m.order, 
                                   m.from_surah, 
                                   m.to_surah, 
                                   m.from_verse, 
                                   v.original_surah_order as order_verse_from, 
                                    m.to_verse, 
                                    m.is_test 
                                    from mk_subject_page m, 
                                    mk_surah_verses v
                                    WHERE active = true and
                            		m.from_verse = v.id and
                                    subject_page_id = {} and 
                                    from_surah = {} '''.format(subject_page_id, surah_id)
                    request.env.cr.execute(query_string)
                    memorize_method_surah_lines = request.env.cr.dictfetchall()
                    responseData['success'] = 0
                    responseData['data'] = memorize_method_surah_lines

            except Exception as e:
                responseData['success'] = 1
                responseData['error'] = e
        return Response(json.dumps(responseData['data']), content_type="application/json", status=200)

    # @http.route('/main/teacher/add_listen_line', auth="user", type="json", method='POST', csrf=False)
    # def teacher_add_listen_line(self, **args):
    #     args = deserialise_request_data(request.httprequest._cached_data)
    #     responseData = {'success': False}
    #     if request.httprequest.method == 'POST':
    #         try:
    #             if request.env.user._is_public():
    #                 responseData['success'] = False
    #                 responseData['error'] = _('No user is registred with this login')
    #             else:
    #                 link_id = int(args['link_id'])
    #                 type_follow = args['type_follow']
    #                 from_surah_id = args['from_surah']
    #                 from_aya_id = args['from_aya']
    #                 to_surah_id = args['to_surah']
    #                 to_aya_id = args['to_aya']
    #                 listen_lines = {}
    #                 actual_date = datetime.strptime(fields.Date.today(), '%Y-%m-%d').date()
    #                 student_link = request.env['mk.link'].sudo().search([('id', '=', link_id)], limit=1)
    #                 student_register = student_link.student_id
    #                 episode = student_link.episode_id
    #                 if episode.state == 'done':
    #                     stdnt_link = request.env['mk.link'].sudo().search([('student_id', '=', student_register.id),
    #                                                              ('state', '=', 'accept'),
    #                                                              ('study_class_id.is_default', '=', True)], limit=1)
    #                     if stdnt_link:
    #                         student_link = stdnt_link
    #                 preparation = student_link.preparation_id
    #
    #                 from_aya = request.env['mk.surah.verses'].sudo().search([('surah_id', '=', int(from_surah_id)),
    #                                                                ('original_surah_order', '=', int(from_aya_id))],
    #                                                               limit=1)
    #
    #                 to_aya = request.env['mk.surah.verses'].sudo().search([('surah_id', '=', int(to_surah_id)),
    #                                                              ('original_surah_order', '=', int(to_aya_id))],
    #                                                             limit=1)
    #
    #                 vals = {'preparation_id': preparation.id,
    #                         'type_follow': type_follow,
    #                         'student_id': student_link.id,
    #                         'student_register_id': student_link.student_id.id,
    #                         'mosque_id': student_link.mosq_id.id,
    #                         'episode': student_link.episode_id.id,
    #                         'center_department_id': student_link.mosq_id.center_department_id.id,
    #                         'approache_id': student_link.approache.id,
    #                         'study_year_id': student_link.academic_id.id,
    #                         'study_class_id': student_link.study_class_id.id,
    #                         'actual_date': actual_date,
    #                         'from_surah': int(from_surah_id),
    #                         'from_aya': from_aya.id,
    #                         'to_surah': int(to_surah_id),
    #                         'to_aya': to_aya.id,
    #                         'is_from_mobile': True,
    #                         'total_mstk_qty': int(args['total_mstk_qty']),
    #                         'total_mstk_read': int(args['total_mstk_read']),
    #                         'state': 'done'}
    #
    #                 line_id = request.env['mk.listen.line'].sudo().create(vals)
    #
    #                 if line_id:
    #                     listen_lines.update({'line_id': line_id.id})
    #                     existing_presence = request.env['mk.student.prepare.presence'].sudo().search([('preparation_id', '=', preparation.id),
    #                                                                                                 ('presence_date', '=', actual_date)], limit=1)
    #                     if existing_presence:
    #                         existing_presence.write({'status': 'present'})
    #                     else:
    #                         request.env['mk.student.prepare.presence'].sudo().create({'preparation_id': preparation.id,
    #                                                                         'presence_date': actual_date,
    #                                                                         'status': 'present',
    #                                                                         'link_id': student_link.id,
    #                                                                         'episode_id': student_link.episode_id.id,
    #                                                                         'mosque_id': student_link.mosq_id.id,
    #                                                                         'center_department_id': student_link.mosq_id.center_department_id.id,
    #                                                                         'student_register_id': student_link.student_id.id,
    #                                                                         'study_year_id': student_link.academic_id.id,
    #                                                                         'study_class_id': student_link.study_class_id.id,
    #                                                                         'is_from_mobile': True})
    #
    #                     new_start_point = self.check_line_state(line_id)
    #                     if new_start_point:
    #                         listen_lines.update({'new_start_point': new_start_point})
    #                 responseData['success'] = True
    #                 responseData['result'] = listen_lines
    #
    #         except Exception as e:
    #             responseData['success'] = False
    #             responseData['error'] = str(e)
    #     return responseData['result']

    #region Offline Api
    @http.route('/main/teacher/offline/check_episodes', type="json", auth="user", method='POST', csrf=False)
    def teacher_offline_check_episodes(self, **args):
        user_id = request.env.user.id
        user = request.env['res.users'].sudo().browse(user_id)
        user.sudo().write({'last_app_login': Datetime.now()})
        args = deserialise_request_data(request.httprequest._cached_data)
        data = args.get('data')
        responseData = {'success': False}
        if request.httprequest.method == 'POST':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    teacher_id = data['teacher_id']
                    app_episode_ids = data['episodes']
                    current_episode_ids = request.env['mk.episode'].sudo().search([('teacher_id', '=', teacher_id),
                                                                                   ('study_class_id.is_default', '=', True),
                                                                                   ('state', '=', 'accept')]).ids
                    deleted_episodes = []
                    new_episodes = []
                    update = False

                    set_app_episode_ids = set(app_episode_ids)
                    set_current_episode_ids = set(current_episode_ids)

                    if set_app_episode_ids != set_current_episode_ids:
                        update = True
                        items = set_app_episode_ids.intersection(set_current_episode_ids)
                        deleted_episodes = list(set_app_episode_ids - items)
                        new_episode_ids = list(set_current_episode_ids - items)
                        if new_episode_ids:
                            new_links = request.env['mk.link'].sudo().search([('episode_id', 'in', new_episode_ids),
                                                                               ('state', '=', 'accept')])
                            listen_lines = request.env['mk.listen.line'].sudo().search([('student_id', 'in', new_links.ids)])
                            today_presences = request.env['mk.student.prepare.presence'].sudo().search([('link_id', 'in', new_links.ids),
                                                                                                        ('presence_date', '=', date.today())], limit=1)
                            for new_episode in new_episode_ids:
                                students = []

                                links = new_links.filtered(lambda l: l.episode_id.id == new_episode)
                                if links:
                                    episode = False
                                    for link in links:
                                        print("****************link", link)
                                        student = link.student_id
                                        if not episode:
                                            episode = link.episode_id

                                        age = 0
                                        # dob = link.student_id.birthdate
                                        # if dob:
                                        #     d1 = datetime.strptime(dob, "%Y-%m-%d").date()
                                        #     d2 = date.today()
                                        #     age = relativedelta(d2, d1).years

                                        # test_session = request.env['student.test.session'].sudo().search([('student_id', '=', link_id),
                                        #                                                         ('state', '!=', 'cancel')], limit=1)
                                        new_lines = []

                                        for line in listen_lines.filtered(lambda l: l.student_id == link):
                                            new_lines.append({"prep_id": line.id or None,
                                                              "actual_date": line.actual_date or None,
                                                              "type_follow": line.type_follow or None,
                                                              "from_sura_name": line.from_surah.name or None,
                                                              "from_aya": line.from_aya.original_surah_order,
                                                              "to_sura_name": line.to_surah.name or None,
                                                              "to_aya": line.to_aya.original_surah_order,
                                                              "total_mstk_qty": line.total_mstk_qty,
                                                              "total_mstk_read": line.total_mstk_read})

                                        presence = today_presences.sudo().filtered(lambda w: w.link_id == link)
                                        state = 'تحضير الطالب'
                                        if presence:
                                            presence = presence[0]
                                            state = get_state_translation_value('mk.student.prepare.presence', 'status', presence.status)

                                        students += [{'id': link.id,
                                                      'student_id': student.id,
                                                      'plan_id': link.preparation_id.id,
                                                      'general_behavior_type': False,
                                                      'name': student.display_name,
                                                      'new_lines': new_lines,
                                                      'rate': 0,
                                                      'age': age,
                                                      'test_register': False,
                                                      'session_id': False,
                                                      'type_exam_id': False,
                                                      'track': False,
                                                      'branch_id': False,
                                                      'period_id': False,
                                                      'state': state}]
                                else:
                                    episode = request.env['mk.episode'].sudo().browse(new_episode)

                                new_episodes += [{'id': new_episode,
                                                  'display_name': episode.display_name,
                                                  'name': episode.name,
                                                  'epsd_type': episode.program_id.name,
                                                  'epsd_work': episode.approache_id.name,
                                                  'students': students}]

                    result = {'update': update,
                              'deleted_episodes': deleted_episodes,
                              'new_episodes': new_episodes}
                    responseData['success'] = True
                    responseData['result'] = result
            except Exception as e:
                responseData['success'] = False
                responseData['error'] = str(e)
        return responseData['result']

    @http.route('/main/teacher/offline/check_students', type="json", auth="user", method='POST', csrf=False)
    def teacher_offline_check_students(self, **args):
        user_id = request.env.user.id
        args = deserialise_request_data(request.httprequest._cached_data)
        data = args.get('data')
        responseData = {'success': False}
        if request.httprequest.method == 'POST':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    episode_id = data['episode_id']
                    app_link_ids = data['links']
                    actual_date = date.today()
                    current_link_ids = request.env['mk.link'].sudo().search([('episode_id', '=', episode_id),
                                                                   ('state', '=', 'accept')]).ids
                    deleted_links = []
                    new_links = []
                    update = False
                    set_app_link_ids = set(app_link_ids)
                    set_current_link_ids = set(current_link_ids)

                    if set_app_link_ids != set_current_link_ids:
                        update = True
                        items = set_app_link_ids.intersection(set_current_link_ids)
                        deleted_links = list(set_app_link_ids - items)
                        new_link_ids = list(set_current_link_ids - items)
                        i_new_links = request.env['mk.link'].browse(new_link_ids)
                        listen_lines = request.env['mk.listen.line'].sudo().search([('student_id', 'in', new_link_ids)], order='order')
                        today_presences = request.env['mk.student.prepare.presence'].sudo().search([('link_id', 'in', new_link_ids),
                                                                                                   ('presence_date', '=', actual_date)], limit=1)
                        for link in i_new_links:
                            student = link.student_id
                            age = 0
                            # dob = link.student_id.birthdate
                            # if dob:
                            #     d1 = datetime.strptime(dob, "%Y-%m-%d").date()
                            #     d2 = date.today()
                            #     age = relativedelta(d2, d1).years
                            # test_session = request.env['student.test.session'].sudo().search([('student_id', '=', link_id),
                            #                                                                ('state', '!=', 'cancel')],limit=1)
                            new_lines = []

                            for line in listen_lines.filtered(lambda l: l.student_id == link):
                                new_lines.append({"prep_id": line.id,
                                                   "actual_date": line.actual_date,
                                                   "type_follow": line.type_follow,
                                                   "from_sura_name": line.from_surah.name or None,
                                                   "from_aya": line.from_aya.original_surah_order,
                                                   "to_sura_name": line.to_surah.name or None,
                                                   "to_aya": line.to_aya.original_surah_order,
                                                   "total_mstk_qty": line.total_mstk_qty,
                                                   "total_mstk_read": line.total_mstk_read})
                            presence = today_presences.sudo().filtered(lambda p: p.link_id == link)
                            state = 'تحضير الطالب'
                            if presence:
                                presence = presence[0]
                                state = get_state_translation_value('mk.student.prepare.presence', 'status', presence.status)
                            new_links.append({'id': link.id,
                                              'student_id': student.id,
                                              'plan_id': link.preparation_id.id,
                                              'general_behavior_type': False,
                                              'name': student.display_name,
                                              'new_lines': new_lines,
                                              'rate': 0,
                                              'age': age,
                                              'test_register': False,
                                              'session_id': False,
                                              'type_exam_id': False,
                                              'track': False,
                                              'branch_id': False,
                                              'period_id': False,
                                              'state': state})
                            sorted(new_links, key=lambda k: k['age'])
                    results = {'update': update,
                              'deleted_links': deleted_links,
                              'new_links': new_links}
                    responseData['success'] = True
                    responseData['result'] = results

            except Exception as e:
                responseData['success'] = False
                responseData['error'] = str(e)
        return responseData['result']

    @http.route('/main/teacher/offline/add_listen_line', type="json", auth="user", method='POST', csrf=False)
    def teacher_offline_add_listen_line(self, **args):
        args = deserialise_request_data(request.httprequest._cached_data)
        data = args.get('data')
        responseData = {'success': False}
        if request.httprequest.method == 'POST':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    all_listen_lines = []
                    link_objs = {}
                    aya_objs = {}
                    for item in data:
                        link_id = int(item['link_id'])
                        type_follow = item['type_follow']
                        from_surah_id = int(item['from_surah'])
                        from_aya_order = int(item['from_aya'])
                        to_surah_id = int(item['to_surah'])
                        to_aya_order = int(item['to_aya'])
                        listen_date = item['actual_date']
                        listen_lines = {}

                        student_link = link_objs.get(link_id, False)
                        if not student_link:
                            student_link = request.env['mk.link'].sudo().search([('id', '=', link_id)], limit=1)
                            episode = student_link.episode_id
                            if episode.state == 'done':
                                stdnt_link = request.env['mk.link'].sudo().search(
                                    [('student_id', '=', student_link.student_id.id),
                                     ('state', '=', 'accept'),
                                     ('study_class_id.is_default', '=', True)], limit=1)
                                if stdnt_link:
                                    student_link = stdnt_link

                            link_objs.update({link_id: student_link})

                        preparation = student_link.preparation_id

                        from_aya = aya_objs.get((from_surah_id, from_aya_order), False)
                        if not from_aya:
                            from_aya = request.env['mk.surah.verses'].sudo().search([('surah_id', '=', from_surah_id),
                                                                           ('original_surah_order', '=',
                                                                            from_aya_order)], limit=1)
                            aya_objs.update({(from_surah_id, from_aya_order): from_aya})

                        to_aya = aya_objs.get((to_surah_id, to_aya_order), False)
                        if not to_aya:
                            to_aya = request.env['mk.surah.verses'].sudo().search([('surah_id', '=', to_surah_id),
                                                                         ('original_surah_order', '=', to_aya_order)],
                                                                        limit=1)
                            aya_objs.update({(to_surah_id, to_aya_order): to_aya})
                        preparation_id = preparation.id
                        student_id = student_link.student_id.id
                        mosq_id = student_link.mosq_id.id
                        episode_id = student_link.episode_id.id
                        academic_id = student_link.academic_id.id
                        study_class_id = student_link.study_class_id.id
                        center_department_id = student_link.mosq_id.center_department_id.id

                        vals = {'preparation_id': preparation_id,
                                'type_follow': type_follow,
                                'student_id': student_link.id,
                                'student_register_id': student_id,
                                'mosque_id': mosq_id,
                                'center_department_id': center_department_id,
                                'episode': episode_id,
                                'approache_id': student_link.approache.id,
                                'study_year_id': academic_id,
                                'study_class_id': study_class_id,
                                'actual_date': listen_date,
                                'from_surah': from_surah_id,
                                'from_aya': from_aya.id,
                                'to_surah': to_surah_id,
                                'to_aya': to_aya.id,
                                'is_from_mobile': True,
                                'total_mstk_qty': int(item['total_mstk_qty']),
                                'total_mstk_read': int(item['total_mstk_read']),
                                'state': 'done'}

                        listen_line = request.env['mk.listen.line'].sudo().create(vals)

                        listen_lines.update({'line_id': listen_line.id})
                        existing_presence = request.env['mk.student.prepare.presence'].sudo().search([('preparation_id', '=', preparation_id),
                                                                                                      ('presence_date', '=', listen_date)], limit=1)
                        if not existing_presence:
                            request.env['mk.student.prepare.presence'].sudo().create({'preparation_id': preparation_id,
                                                                                        'presence_date': listen_date,
                                                                                        'status': 'present',
                                                                                        'link_id': student_link.id,
                                                                                        'episode_id': episode_id,
                                                                                        'mosque_id': mosq_id,
                                                                                        'center_department_id': center_department_id,
                                                                                        'student_register_id': student_id,
                                                                                        'study_year_id': academic_id,
                                                                                        'study_class_id': study_class_id,
                                                                                        'is_from_mobile': True})
                        else:
                            existing_presence.sudo().write({'status': 'present'})
                        # new_start_point = self.check_line_state(listen_line)
                        # if new_start_point:
                        listen_lines.update({'new_start_point': {'degree': listen_line.degree,
                                                                 'from_aya': to_aya_order,
                                                                 'from_sura_name': to_aya.surah_id.name or None,
                                                                 'mistake': listen_line.mistake,
                                                                 'prep_id': listen_line.preparation_id.id,
                                                                 'to_aya': None,
                                                                 'to_sura_name': None}})

                        all_listen_lines.append(listen_lines)
                    responseData['success'] = True
                    responseData['result'] = all_listen_lines

            except Exception as e:
                responseData['success'] = False
                responseData['error'] = e
        return responseData['result']

    @http.route('/main/teacher/offline/set_attendance', type="json", auth="user", method='POST', csrf=False)
    def teacher_offline_set_attendance(self, **args):
        args = deserialise_request_data(request.httprequest._cached_data)
        data = args.get('data')
        responseData = {'success': False}
        if request.httprequest.method == 'POST':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    prep_objs = {}
                    for item in data:
                        preparation_id = item['plan_id']
                        state = item['state']
                        date = item['date']
                        preparation = prep_objs.get(preparation_id, False)
                        if not preparation:
                            preparation = request.env['mk.student.prepare'].sudo().search([('id', '=', preparation_id),
                                                                                 ('stage_pre_id.state', '=', 'accept'),
                                                                                 '|', ('active', '=', True),
                                                                                 ('active', '=', False)], limit=1)

                            if not preparation:
                                prepare = request.env['mk.student.prepare'].sudo().search([('link_id.student_id', '=', preparation.student_register_id.id),
                                                                                     ('link_id.state', '=', 'accept'),
                                                                                     ('study_class_id.is_default', '=', True),
                                                                                     '|', ('active', '=', True),
                                                                                          ('active', '=', False)], limit=1)
                                preparation = prepare
                            if not preparation:
                                continue
                            prep_objs.update({preparation_id: preparation})

                        existing_presence = request.env['mk.student.prepare.presence'].sudo().search([('preparation_id', '=', preparation.id),
                                                                                                      ('presence_date', '=', date)], limit=1)
                        if existing_presence:
                            existing_presence.sudo().write({'status': state})
                        else:
                            link = preparation.link_id
                            presence = request.env['mk.student.prepare.presence'].sudo().create({'preparation_id': preparation.id,
                                                                                                 'presence_date': date,
                                                                                                 'status': state,
                                                                                                 'link_id': link.id,
                                                                                                 'episode_id': link.episode_id.id,
                                                                                                 'mosque_id': link.mosq_id.id,
                                                                                                 'center_department_id': link.mosq_id.center_department_id.id,
                                                                                                 'student_register_id': link.student_id.id,
                                                                                                 'study_year_id': link.academic_id.id,
                                                                                                 'study_class_id': link.study_class_id.id,
                                                                                                 'is_from_mobile': True})
                    responseData['success'] = True
                    responseData['result'] = True

            except Exception as e:
                responseData['success'] = False
                responseData['error'] = e
        return json.dumps(responseData)
    #endregion

    #region Student Behaviors
    @http.route('/main/teacher/mk_student_behaviors', auth="user", method='GET', csrf=False)
    def mk_student_behaviors(self, **args):
        responseData = {'success': False}
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    student_behaviors = request.env['mk.student.behaviors'].sudo().search_read([], ['id', 'name'])
                    responseData['success'] = True
                    responseData['result'] = student_behaviors

            except Exception as e:
                responseData['success'] = False
                responseData['error'] = e
        return  Response(json.dumps(responseData['result']), content_type="application/json", status=200)

    @http.route('/main/teacher/add_behavior', auth="user", type="http", method='GET', csrf=False)
    def add_behavior(self, **args):
        plan_id = int(args.get('plan_id'))
        behavior_id = int(args.get('behavior_id'))
        responseData = {'success': 1}
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    student_bahavior = request.env['mk.student.prepare.behavior'].sudo().create({'preparation_id': plan_id,
                                                                                                 'behavior_id': behavior_id,
                                                                                                 'date_behavior': datetime.strptime(fields.Date.today(), '%Y-%m-%d') })
                    responseData['success'] = 0
                    responseData['id'] = student_bahavior and student_bahavior.id or False
            except Exception as e:
                responseData['success'] = 1
                responseData['error'] = str(e)
        return Response(json.dumps(responseData), content_type="application/json", status=200)

    @http.route('/main/student/behaviors', auth="user",  method='GET', csrf=False)
    def student_behaviors(self, **args):
        link_id = int(args.get('link_id'))
        responseData = {'success': 1}
        student_behaviors = []
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    preparation_id = request.env['mk.student.prepare'].sudo().search([('link_id', '=', link_id)], limit=1)
                    behaviors = request.env['mk.student.prepare.behavior'].sudo().search([('preparation_id', '=', preparation_id.id)])
                    if behaviors:
                        teacher = preparation_id.name
                        teacher_name = teacher.name

                        episode = preparation_id.stage_pre_id
                        episode_id = episode.id
                        episode_name = episode.name

                        period_id = episode.period_id.id

                        mosque = episode.mosque_id
                        mosque_name = mosque.name

                        student = preparation_id.link_id.student_id
                        student_id = student.id
                        student_name = student.display_name


                        for behavior in behaviors:
                            student_behaviors +=   [{'id': behavior.id,
                                                     'date': behavior.date_behavior,
                                                     'period': period_id,

                                                     'teacher_name': teacher_name,
                                                     'masjed_name': mosque_name,

                                                     'episode_id': episode_id,
                                                     'episode_name': episode_name,

                                                     'student_id': student_id,
                                                     'student_name': student_name,

                                                     'comment_name': behavior.behavior_id.name,

                                                     'punishment_name': '',
                                                     'punish_date': False, }]

                    responseData['success'] = 0
                    responseData['data'] = student_behaviors

            except Exception as e:
                responseData['success'] = 1
                responseData['error'] = e
        return  Response(json.dumps(responseData), content_type="application/json", status=200)

    @http.route('/main/teacher/set_student_general_behavior', auth="user",  method='POST', csrf=False)
    def set_general_behaviors_type(self, **args):
        general_behavior_type = args.get('general_behavior user_id : %s', request.env.user.id)
        link_id = int(args.get('link_id'))
        responseData = {'success': 0}
        if request.httprequest.method == 'POST':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    preparation_id = request.env['mk.student.prepare'].sudo().search([('link_id', '=', link_id)], limit=1)
                    if preparation_id:
                        try:
                            preparation_id.sudo().write({'general_behavior_type': general_behavior_type})
                            msg = 'success'
                        except:
                            msg = 'failed, Please verify behavior'

                    responseData['success'] = 1
                    responseData['msg'] = msg
            except Exception as e:
                responseData['success'] = 0
                responseData['error'] = str(e)
        return Response(json.dumps(responseData), content_type="application/json", status=200)
    #endregion

    #region Notifications
    @http.route('/main/teacher_mobile/notifications', auth="user",  method='GET', csrf=False)
    def teacher_mobile_noitifications(self, **args):
        teacher_id = args.get('teacher_id')
        responseData = {'success': False}
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    responseData['result'] = request.env['mk.notification.line'].teacher_mobile_noitifications(teacher_id)
                    responseData['success'] = True

            except Exception as e:
                responseData['success'] = False
                responseData['error'] = e
        return  Response(json.dumps(responseData['result']), content_type="application/json", status=200)

    @http.route('/main/teacher_mobile/consult_notif', auth="user",  method='GET', csrf=False)
    def consult_notification(self, **args):
        notif_id = args.get('notif_id')
        responseData = {'success': 1}
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    msg = request.env['mk.notification.line'].sudo().consult_notification(notif_id)
                    responseData['success'] = 0
                    responseData['consult_notif'] = msg

            except Exception as e:
                responseData['success'] = 1
                responseData['error'] = str(e)
        return  Response(json.dumps(responseData), content_type="application/json", status=200)
    #endregion

    #region Complaints
    @http.route('/main/teacher_mobile/add_complaints', auth="user", method='POST', csrf=False)
    def add_complaints(self, **args):
        user_id = args.get('user_id')
        subject = args.get('subject')
        description = args.get('description')

        responseData = {'success': 1}
        if request.httprequest.method == 'POST':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    user = request.env['res.users'].search([('id', '=', user_id)], limit=1)
                    category_id = request.env.ref('website_support.website_support_complaints').id
                    complaints_ticket = request.env['website.support.ticket'].with_context(from_mobile=True).sudo().create({'create_user_id': user_id,
                                                                                                                            'center_id': user.department_id.id,
                                                                                                                            'email': user.partner_id.email,
                                                                                                                            'category': category_id,
                                                                                                                            'subject': subject,
                                                                                                                            'description': str(description)})
                    responseData['success'] = 0
                    responseData['complaints_ticket'] = complaints_ticket and complaints_ticket.id or False

            except Exception as e:
                responseData['success'] = 1
                responseData['error'] = str(e)
        return  Response(json.dumps(responseData), content_type="application/json", status=200)
    #endregion

    #region Tests
    @http.route('/main/test/periods', auth="user", method='GET', csrf=False)
    def test_periods(self, **args):
        responseData = {'success': False}
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    query_string = ''' select id, name 
                                       from test_period
                                       where active=True
                                       order by id;'''
                    request.env.cr.execute(query_string)
                    test_periods = request.env.cr.dictfetchall()
                    responseData['success'] = True
                    responseData['result'] = test_periods

            except Exception as e:
                responseData['success'] = False
                responseData['error'] = str(e)
        return Response(json.dumps(responseData['result']), content_type="application/json", status=200)

    @http.route('/main/test/centers', auth="user", method='GET', csrf=False)
    def test_centers(self, **args):
        gender = args.get('gender')
        episode_id = int(args.get('episode_id'))
        user_id = args.get('user_id')

        responseData = {'success': False}
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    query = '''
                            SELECT test_center.id,
                            test_center.name

                            FROM
                            (SELECT distinct mk_test_center_prepration.id,
                            mk_test_center_prepration.name

                            FROM mk_test_center_prepration
                            LEFT JOIN center_time_table ON center_time_table.center_id=mk_test_center_prepration.id
                            LEFT JOIN mak_test_center ON mk_test_center_prepration.center_id=mak_test_center.id
                            LEFT JOIN hr_department ON mak_test_center.center_id=hr_department.id '''

                    if episode_id and episode_id > 0:
                        query += ''' left join mk_mosque on mk_mosque.center_department_id=hr_department.id
                                            left join mk_episode on mk_episode.mosque_id=mk_mosque.id'''

                    query += ''' WHERE center_time_table.active = True AND
                            center_time_table.type_center='student' AND
                            center_time_table.date >= current_date AND
                            mak_test_center.gender = '{}'  AND'''.format(gender)

                    if episode_id and episode_id > 0:
                        query += ''' mk_episode.id={}) test_center order by test_center.name;'''.format(episode_id)
                    else:
                        query += ''' 
                                hr_department.id IN (SELECT res_users.department_id 
                                FROM res_users 
                                WHERE res_users.id={}

                                UNION

                                SELECT hr_department_res_users_rel.hr_department_id 
                                FROM hr_department_res_users_rel 
                                WHERE res_users_id={}
                                UNION

                                SELECT hr_department.id
                                FROM hr_department
                                LEFT JOIN mk_mosque ON mk_mosque.center_department_id=hr_department.id
                                LEFT JOIN mk_mosque_res_users_rel ON mk_mosque_res_users_rel.mk_mosque_id=mk_mosque.id
                                WHERE mk_mosque_res_users_rel.res_users_id={})

                                UNION

                                SELECT distinct mk_test_center_prepration.id,
                                mk_test_center_prepration.name

                                FROM mk_test_center_prepration
                                LEFT JOIN center_time_table ON center_time_table.center_id=mk_test_center_prepration.id
                                LEFT JOIN mak_test_center ON mk_test_center_prepration.center_id=mak_test_center.id
                                LEFT JOIN hr_department ON mak_test_center.center_id=hr_department.id 

                                WHERE center_time_table.active = True AND
                                center_time_table.type_center='student' AND
                                center_time_table.date >= current_date AND
                                mak_test_center.gender = '{}'  AND
                                mak_test_center.main_company=True) test_center

                                order by test_center.name;'''.format(user_id, user_id, user_id, gender)

                    request.env.cr.execute(query)
                    test_centers = request.env.cr.dictfetchall()
                    responseData['success'] = True
                    responseData['result'] = test_centers

            except Exception as e:
                responseData['success'] = False
                responseData['error'] = str(e)
        return Response(json.dumps(responseData['result']), content_type="application/json", status=200)

    @http.route('/main/test/center_prepar_type_tests', auth="user", method='GET', csrf=False)
    def center_prepar_type_tests(self, **args):
        center_prepration_id = args.get('center_prepration_id')

        responseData = {'success': False}
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    center_prepar_type_tests = request.env['mk.test.names'].center_prepar_type_tests(
                        center_prepration_id)
                    responseData['success'] = True
                    responseData['result'] = center_prepar_type_tests

            except Exception as e:
                responseData['success'] = False
                responseData['error'] = e
        return Response(json.dumps(responseData['result']), content_type="application/json", status=200)

    @http.route('/main/test/test_branches', auth="user", method='GET', csrf=False)
    def test_branches(self, **args):
        test_id = args.get('test_id')
        trackk = args.get('trackk')

        responseData = {'success': 1}
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    msg = request.env['mk.branches.master'].get_test_branches(test_id, trackk)
                    responseData['success'] = 0
                    responseData['data'] = msg

            except Exception as e:
                responseData['success'] = 1
                responseData['error'] = e

        return Response(json.dumps(responseData['data']), content_type="application/json", status=200)

    @http.route('/main/test/calendar_center', auth="user", method='GET', csrf=False)
    def calendar_center(self, **args):
        gender = args.get('gender')
        center_id = args.get('center_id')
        episode_id = args.get('episode_id', False)
        period_id = args.get('period_id', False)
        user_id = args.get('user_id')

        responseData = {'success': False}
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    responseData['result'] = request.env['center.time.table'].sudo().calendar_center(gender, center_id,episode_id, period_id,user_id)
                    responseData['success'] = True

            except Exception as e:
                responseData['success'] = False
                responseData['error'] = e
        return Response(json.dumps(responseData['result']), content_type="application/json", status=200)

    @http.route('/main/test/add_student_test_session', auth="user", method='GET', csrf=False)
    def add_student_test_session(self, **args):
        student_id = args.get('student_id')
        test_name_id = args.get('test_name_id')
        test_time_id = args.get('test_time_id')
        branch_id = args.get('branch_id')
        trackk = args.get('trackk')
        responseData = {'success': 1}
        if request.httprequest.method == 'GET':
            try:
                if request.env.user._is_public():
                    responseData['success'] = False
                    responseData['error'] = _('No user is registred with this login')
                else:
                    link = request.env['mk.link'].sudo().search([('id', '=', student_id)], limit=1)
                    mosque = link.student_id.mosq_id

                    test_name = request.env['mk.test.names'].sudo().search([('id', '=', test_name_id)], limit=1)

                    test_time = request.env['center.time.table'].sudo().search([('id', '=', test_time_id)], limit=1)
                    avalible_minutes = test_time.avalible_minutes
                    test_center_preparation = test_time.center_id
                    academic_id = test_center_preparation.academic_id.id
                    study_class_id = test_center_preparation.study_class_id.id

                    branch = request.env['mk.branches.master'].sudo().search([('id', '=', branch_id)], limit=1)
                    flag, msg = request.env['select.students'].action_student_validate(branch, trackk, academic_id,
                                                                                    study_class_id, student_id, test_name,
                                                                                    avalible_minutes, 1, test_time)
                    session_id = False
                    if flag:
                        session = request.env['student.test.session'].sudo().create({'student_id': student_id,
                                                                                  'test_name': test_name_id,
                                                                                  'test_time': test_time_id,
                                                                                  'branch': branch_id,
                                                                                  'center_name': test_time.center_id.center_id.display_name,
                                                                                  'center_id': test_time.center_id.id,
                                                                                  'masjed_name': mosque.name,
                                                                                  'mosque_id': mosque.id, })
                        session_id = session.id
                        msg = False
                    responseData['success'] = 0
                    responseData['result'] = {'session_id': session_id,
                                              'msg': msg}

            except Exception as e:
                responseData['success'] = 1
                responseData['error'] = str(e)
        return Response(json.dumps(responseData['result']), content_type="application/json", status=200)
    #endregion