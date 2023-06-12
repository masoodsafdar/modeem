import json

import requests

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
from lxml import etree
import urllib.request
import logging
_logger = logging.getLogger(__name__)

def listToString(s):
    # initialize an empty string
    str1 = ","
    # return string
    return (str1.join(s))

class Mk_sms_students(models.TransientModel):
    _name = 'mk.employee.sms'

    department_id      = fields.Many2one('hr.department', string='Department', ondelete='cascade', required=1)
    mosque_ids         = fields.Many2many('mk.mosque',   string='Mosques',    ondelete='cascade')
    job_ids            = fields.Many2many('hr.job',       string='Jobs')
    employee_ids       = fields.Many2many('hr.employee',  string='Employees')
    message            = fields.Text(string='Message', translate=True)
    is_user_department = fields.Boolean(string="is user department", compute='_compute_user_categ')

    @api.onchange('department_id')
    def _compute_user_categ(self):
        user = self.env.user.id
        employee_id = self.env['hr.employee'].search([('user_id', '=', user)])
        employee_categ = employee_id.category2
        if employee_categ == 'center_admin':
            self.is_user_department= True
        else:
            self.is_user_department = False

    @api.onchange('department_id', 'mosque_ids', 'job_ids')
    def onchange_employees(self):
        employees_domain = []
        mosq_domain = []
        is_user_department = self.is_user_department
        department_id = self.department_id

        if is_user_department:
            mosq_domain += [('center_department_id', '=', department_id.id)]
            employees_domain += [('state', '=', 'accept'),
                                 ('department_id', '=', department_id.id)]
        else:
            mosq_domain += ['&', '&', '&', ('center_department_id', '=', department_id.id),
                           ('gateway_user', '!=', False), ('gateway_password', '!=', False),
                           ('gateway_sender', '!=', False), ]


            employees_domain += ['&','&','&','&',('state', '=', 'accept'),
                                 ('department_id', '=', self.department_id.id),
                                 ('mosqtech_ids.gateway_user', '!=', False),
                                 ('mosqtech_ids.gateway_password', '!=', False),
                                 ('mosqtech_ids.gateway_sender', '!=', False)]

        if self.job_ids:
            employees_domain += [('job_id', 'in', self.job_ids.ids)]

        if self.mosque_ids:
            employees_domain += ['|',('mosqtech_ids','in', self.mosque_ids.ids),
                                    '&',('mosque_sup','in', self.mosque_ids.ids),
                                        ('category2', '=', 'edu_supervisor')]

        return {'domain': {'employee_ids': employees_domain,
                           'mosque_ids': mosq_domain,}}

    def send_by_gateway_spec(self, message, mobile, employee_id, mosque_id):
        prms={}
        other=''
        url=''
        
        if mosque_id.gateway_config and mosque_id.gateway_password and mosque_id.gateway_user and mosque_id.gateway_sender:
            if mosque_id.send_time:
                hr_time=int(mosque_id.send_time)
                prms[mosque_id.gateway_config.time_send] = str(hr_time)+":"+str(int((mosque_id.send_time-hr_time)*60))+":"+'00'
            prms[mosque_id.gateway_config.user] = mosque_id.gateway_user
            prms[mosque_id.gateway_config.password] = mosque_id.gateway_password
            prms[mosque_id.gateway_config.sender] = mosque_id.gateway_sender
            prms[mosque_id.gateway_config.to] = "966"+mobile
            prms[mosque_id.gateway_config.message] = message
            if mosque_id.gateway_config.other:
                other=mosque_id.gateway_config.other

            
            url=mosque_id.gateway_config.url


            if prms and other:
                params = urllib.parse.urlencode(prms)+"&"+other
                url=url+"?"+params
                urllib.request.urlopen(url)
            elif prms and not other:
                params=urllib.parse.urlencode(prms)
                url=url+"?"+params
                urllib.request.urlopen(url)
            elif not prms:
                obj_general_sending = self.env['mk.general_sending']
                a=obj_general_sending.send_sms(mobile,str(message))
                return a


    def send_gateway_employee_quta(self, message, numbers, employee_ids, employee_id, mosque_ids, department_id):
        if not employee_ids:
            raise ValidationError('الرجاء تحديد قائمة الموظفين')
        else:
            prms={}
            other=''
            url=''

            headers = {
                'content-type': 'application/json',
            }

            employee_category = employee_id.category

            if employee_category == 'center_admin':
                if department_id.send_time:
                    hr_time = int(department_id.send_time)
                    prms[department_id.gateway_config.time_send] = str(hr_time) + ":" + str(int((department_id.send_time - hr_time) * 60)) + ":" + '00'

                numbers_list = numbers.split(",")
                numbers_list_len = len(numbers_list)
                max_receiver = department_id.gateway_config.max_receiver
                i = 0

                while i < numbers_list_len:
                    numbers_list_sub = numbers_list[i:i + max_receiver]
                    numbers_substring = listToString(numbers_list_sub)
                    i = i + max_receiver

                    prms[department_id.gateway_config.user] = department_id.gateway_user
                    prms[department_id.gateway_config.password] = department_id.gateway_password
                    prms[department_id.gateway_config.sender] = department_id.gateway_sender
                    prms[department_id.gateway_config.to] = numbers_substring
                    prms[department_id.gateway_config.message] = message

                    url = department_id.gateway_config.url

                    if prms:
                        response = requests.post(url, data=json.dumps(prms), headers=headers)
                        if response.json().get('code') != "1":
                            msg = 'البيانات الخاصة ببوابة ارسال الرسائل القصيرة ب مركز ' + ' "' + department_id.name + '" ' + ' ' + 'خاطئة' + '!'
                            raise ValidationError(msg)

            else:
                employees = {}
                mosqs = {}
                for employee in employee_ids:
                    if employee.category2 == 'edu_supervisor':
                        mosquess = employee.mosque_sup
                    else :
                        mosquess = employee.mosqtech_ids
                    for mosq in mosquess:
                        if mosq in mosque_ids:
                            mosque_id = mosq.id
                            employees_mosque = employees.get(mosque_id, '')
                            employees.update({mosque_id: employee.mobile_phone + "," + employees_mosque})

                            if not mosqs.get(mosque_id, False):
                                mosque = mosq
                                mosqs.update({mosque_id: {'gateway_user': mosque.gateway_user,
                                                          'gateway_password': mosque.gateway_password,
                                                          'gateway_sender': mosque.gateway_sender,
                                                          'time_send': str(int(mosque.send_time)) + ":" + str(int((mosque.send_time - int(mosque.send_time)) * 60)) + ":" + '00',
                                                          'message': message}})

                for mosq_id in mosqs:
                    employees_mosque = employees.get(mosq_id)
                    mosque_id = self.env['mk.mosque'].search([('id', '=', mosq_id)])
                    if mosque_id.send_time:
                        hr_time = int(mosque_id.send_time)
                        prms[mosque_id.gateway_config.time_send] = str(hr_time) + ":" + str(int((mosque_id.send_time - hr_time) * 60)) + ":" + '00'
                    employees_mosque_list = employees_mosque.split(",")
                    employees_mosque_list_len = len(employees_mosque_list)-1
                    max_receiver = mosque_id.gateway_config.max_receiver
                    i = 0

                    while i < employees_mosque_list_len:
                        employees_mosque_list_sub = employees_mosque_list[i:i+max_receiver]
                        employees_mosque_substring = listToString(employees_mosque_list_sub)
                        i = i+max_receiver

                        prms[mosque_id.gateway_config.user] = mosqs[mosq_id]['gateway_user']
                        prms[mosque_id.gateway_config.password] = mosqs[mosq_id]['gateway_password']
                        prms[mosque_id.gateway_config.sender] = mosqs[mosq_id]['gateway_sender']
                        prms[mosque_id.gateway_config.time_send] = mosqs[mosq_id]['time_send']
                        prms[mosque_id.gateway_config.to] = employees_mosque_substring
                        prms[mosque_id.gateway_config.message] = mosqs[mosq_id]['message']

                        url = mosque_id.gateway_config.url

                        if prms:
                            response = requests.post(url, data=json.dumps(prms), headers=headers)
                            if response.json().get('code') != "1":
                                msg = 'البيانات الخاصة ببوابة ارسال الرسائل القصيرة ب مسجد ' + ' "' + mosque_id.name + '" ' + ' ' + 'خاطئة' + '!'
                                raise ValidationError(msg)

    def ok(self):
        resource = self.env['resource.resource'].search([('user_id', '=', self.env.user.id)])
        employee_id = self.env['hr.employee'].search([('resource_id', 'in', resource.ids)])
        numbers = ''

        employee_ids =[]
        employees_domain = [('state', '=', 'accept')]

        if not self.employee_ids:
            if not self.mosque_ids:
                if employee_id.category == 'center_admin':
                    employees_domain += [('department_id', '=', self.department_id.id)]
                elif employee_id.category == 'edu_supervisor':
                    employees_domain += ['|', ('mosqtech_ids', 'in', employee_id.mosque_sup.ids),
                                         '&', ('mosque_sup', 'in', employee_id.mosque_sup.ids),
                                              ('category2', '=', 'edu_supervisor')]
                else:
                    employees_domain += ['|', ('mosqtech_ids', 'in', employee_id.mosqtech_ids.ids),
                                         '&', ('mosque_sup', 'in', employee_id.mosqtech_ids.ids),
                                               ('category2', '=', 'edu_supervisor')]

            if self.mosque_ids:
                employees_domain += ['|', ('mosqtech_ids', 'in', self.mosque_ids.ids),
                                     '&', ('mosque_sup', 'in', self.mosque_ids.ids),
                                     ('category2', '=', 'edu_supervisor')]
            if self.job_ids:
                employees_domain += [('job_id', 'in', self.job_ids.ids)]

            employee_ids = self.env['hr.employee'].search(employees_domain + [])

        else:
            employee_ids = self.employee_ids

        for rec in employee_ids:
            if len(rec.mobile_phone) == 12:
                numbers+=rec.mobile_phone+","
            elif len(rec.mobile_phone) == 9:
                numbers += "966"+rec.mobile_phone+","

        numbers = numbers[:-1]

        self.send_gateway_employee_quta(self.message, numbers, employee_ids, employee_id, self.mosque_ids, employee_id.department_id)