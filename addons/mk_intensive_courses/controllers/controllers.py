# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo import models, fields, api

from odoo import http
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)


class mk_intensive_courses(http.Controller):

    def get_courses_request(self,department_id,course_id):
        dect = []
        l_days = []
        l_branch = []
        mosq = ' '
        rec_request=request.env['mk.course.request'].sudo().browse([SUPERUSER_ID]).search([('department_id','=',int(department_id)),('course','=',course_id)])
        for rec in rec_request:
            if rec:
                if rec.location == 'internal':
                    mosq = rec.mosque_id.name
                for d in rec.day_ids:
                    n = 0
                    l_days.append(d[n].name)
                    n+=1
                for br in rec.branch_ids:
                    n = 0
                    l_branch.append(br[n].name)
                    n+=1
                dect = {
                    'department_id':rec.department_id.name,
                    'mosque_id':mosq,
                    'subh': rec.subh,
                    'zaher':rec.zaher,
                    'asor':rec.asor,
                    'mogreb':rec.mogreb,
                    'esha':rec.esha,
                    'start_date':rec.start_date,
                    'end_date':rec.end_date,
                    'days_ids':l_days,
                    'branch_ids':l_branch,
                    'seats':rec.no_seats,
                    'hours':rec.no_hours,
                    'cost':rec.cost,
                    'latitute':rec.partner_latitude,
                    'longitude':rec.partner_longitude,
                    'note':rec.note,
                    'course_id':rec.id,
                }
        return dect

    def update_student_course(self,course_id,student_id):
        rec_request=request.env['mk.course.request'].sudo().browse([SUPERUSER_ID]).search([('course','=',int(course_id))])
        l_stud = []
        for rec in rec_request:
            l_stud.append((0,0,{'student_id':student_id}))
            rec.student_ids = l_stud
        return True
            
    @http.route('/register/intensive/course_request/<string:department_id>/<string:course_id>', type='http', auth='public',  csrf=False,)
    def course_request(self,department_id,course_id,**args):
        result=self.get_courses_request(int(department_id),int(course_id))
        return str(result)

    @http.route('/register/update_student/update_student_course/<string:course_id>/<string:student_id>', type='http', auth='public',  csrf=False,)
    def update_student(self,course_id,student_id,**args):
        result=self.update_student_course(int(course_id),int(student_id))
        return str(result)


