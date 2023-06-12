import json

from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError
from datetime import date

import requests

import logging
_logger = logging.getLogger(__name__)


def listToString(s):
    # initialize an empty string
    str1 = ","
    # return string
    return (str1.join(s))

class Mk_sms_students(models.TransientModel):
    _name = 'mk.student.sms'

    department_id      = fields.Many2one('hr.department', string='Department', ondelete='cascade', required=1)
    mosque_ids         = fields.Many2many('mk.mosque',   string='Mosques',    ondelete='cascade')
    episode_id         = fields.Many2one('mk.episode',    string='Episode',    ondelete='cascade')
    student_ids        = fields.Many2many('mk.student.register',      string='Students')
    parents_ids        = fields.Many2many('res.partner',  string='Parents')
    message            = fields.Text('Message', translate=True)
    is_user_department = fields.Boolean(string='is user department', compute='_compute_user_categ')
    type_message       = fields.Selection([('absance_notif', 'اعلام غياب'),
                                           ('stop_ep_notif', 'تعليق دوام'),
                                           ('stop_student_notif', 'اعلام انقطاع'),
                                           ('start_registration_notif', 'التسجيل في حلقات'),
                                           ('reprise_ep_notif', 'استئناف حلقات'),
                                           ('quran_day', 'اليوم القراني'),
                                           ('free_notif', 'رسالة'),], default='free_notif', string='النوع')
    @api.depends('department_id')
    def _compute_user_categ(self):
        user = self.env.user.id
        employee_id = self.env['hr.employee'].search([('user_id', '=', user)])
        employee_categ = employee_id.category2
        if employee_categ == 'center_admin':
            self.is_user_department= True
        else:
            self.is_user_department = False

    @api.onchange('department_id')
    def onchange_department_id(self):
        self.student_ids = False
        self.mosque_ids = False

    @api.onchange('mosque_ids')
    def onchange_mosque_ids(self):
        self.student_ids = False

    @api.onchange('department_id', 'mosque_ids')
    def onchange_students_parents(self):
        department_id = self.department_id
        mosq_domain = [('center_department_id', '=', department_id.id),
                       ('active', '=', True)]
        students_domain = [('request_state', '=', 'accept'),
                           ('active', '=', True),
                           ('department_id', '=', department_id.id)]
        if self.mosque_ids :
            students_domain += [('mosq_id', 'in', self.mosque_ids.ids)]

        return {'domain': {'student_ids': students_domain,
                           'mosque_ids' : mosq_domain}}
    

    def send_gateway_student_quta(self, message, type_message, numbers, department_id, student_ids):
        prms = {}

        headers = {
            'content-type': 'application/json',
        }
        if message == False or '':
            msg = 'الرجاء تحديد الرسالة'
            raise ValidationError(msg)
        if numbers == '':
            msg = 'الرجاء تحديد الطلاب'
            raise ValidationError(msg)
        gateway_user = department_id.gateway_user
        gateway_password = department_id.gateway_password
        gateway_sender = department_id.gateway_sender
        url = department_id.gateway_config.url

        send_time = department_id.send_time
        if send_time:
            hr_time = int(department_id.send_time)
            department_time_send = str(hr_time) + ":" + str(int((send_time - hr_time) * 60)) + ":" + '00'
        if type_message == 'free_notif':
            if send_time:
                prms[department_id.gateway_config.time_send] = department_time_send

            numbers_list = numbers.split(",")
            numbers_list_len = len(numbers_list)
            max_receiver = department_id.gateway_config.max_receiver
            i = 0

            while i < numbers_list_len:
                numbers_list_sub = numbers_list[i:i + max_receiver]
                numbers_substring = listToString(numbers_list_sub)
                i = i + max_receiver

                prms[department_id.gateway_config.user] = gateway_user
                prms[department_id.gateway_config.password] = gateway_password
                prms[department_id.gateway_config.sender] = gateway_sender
                prms[department_id.gateway_config.to] = numbers_substring
                prms[department_id.gateway_config.message] = message

                if prms:
                    response = requests.post(url, data=json.dumps(prms), headers=headers)
                    if response.json().get('code') != "1":
                        msg = 'البيانات الخاصة ببوابة ارسال الرسائل القصيرة خاطئة !'
                        raise ValidationError(msg)
        elif type_message == 'absance_notif' or type_message == 'stop_student_notif':
            for student in student_ids:
                prms[department_id.gateway_config.user] = gateway_user
                prms[department_id.gateway_config.password] = gateway_password
                prms[department_id.gateway_config.sender] = gateway_sender

                mosque = student.mosq_id
                prms[department_id.gateway_config.to] = student.mobile

                if mosque.gender_mosque == 'female':
                    if type_message == 'absance_notif':
                        message = 'نفيدكم بتغيب ابنتكم student عن الحلقة مدرسة mosque'
                    elif type_message == 'stop_student_notif':
                        message = 'نفيدكم بانقطاع ابنتكم student عن الحلقة مدرسة mosque'

                message = message.replace("mosque", mosque.display_name)
                prms[department_id.gateway_config.message] = message.replace("student", student.name)

                if mosque.sent_sms_count < 0:
                    raise ValidationError("مسجد "+ mosque.display_name + "إستوفى الحد المسموح به للرسائل القصيرة")
                response = requests.post(url, data=json.dumps(prms), headers=headers)
                if response.json().get('code') == "1":
                    mosque.sent_sms_count = mosque.sent_sms_count - 1
                    self.env['sms.traceability'].create({'user_id':self.env.user.id,
                                                         'mosque_id':mosque.id,
                                                         'nbr_message_sent': "1",
                                                         'message':message})

                if response.json().get('code') != "1":
                    msg = 'البيانات الخاصة ببوابة ارسال الرسائل القصيرة خاطئة !' +response
                    raise ValidationError(msg)

        else:
            students ={}
            mosqs = {}
            for student in student_ids:
                mosque_id = student.mosq_id.id
                students_mosque = students.get(mosque_id, '')
                students.update({mosque_id:  student.mobile + "," + students_mosque})

                if not mosqs.get(mosque_id, False):
                    mosque = student.mosq_id
                    if mosque.gender_mosque== 'female':
                        if type_message == 'stop_ep_notif':
                            message = ' نفيدكم بتعليق الدوام بالحضور للمدرسة هذا اليوم الموافق:' + str(date.today())+ ' '+ 'مدرسة mosque'
                        elif type_message == 'start_registration_notif':
                            message = 'بدأ التسجيل في حلقات مدرسة mosque أهلا وسهلا بك'
                        elif type_message == 'reprise_ep_notif':
                            message = 'تستأف الحلقات في مدرسة mosque غدا باذن الله فأهلا وسهلا بك'
                        elif type_message == 'quran_day':
                            message = 'بدأ التسجيل في اليوم القراني فرصة لتثبيت حفظك ومراجعته مدرسة mosque'
                    else:
                        message = message
                    mosqs.update({mosque_id: {'message':  message.replace("mosque", mosque.display_name)}})
            mosques_finish_sent_sms = []
            for mosq_id in mosqs:
                students_mosque = students.get(mosq_id)
                if send_time:
                    prms[department_id.gateway_config.time_send] = department_time_send
                mosque = self.env['mk.mosque'].search([('id', '=', (mosq_id))])
                students_mosque_list = students_mosque.split(",")
                if (mosque.sent_sms_count - len(students_mosque_list) + 1) < 0:
                    raise ValidationError(" لقد تم إرسال رسائل عدد" + str(len(mosques_finish_sent_sms))+" المساجد : "+ str(mosques_finish_sent_sms) +" ولكن   عدد الرسائل التي بصدد الإرسال بالنسبة لمسجد" + mosque.display_name + "تتجاوز الحد المسموح به ب "+ str((mosque.sent_sms_count - len(students_mosque_list))) )
                mosques_finish_sent_sms.append(mosque.display_name)
                students_mosque_list_len = len(students_mosque_list) - 1
                max_receiver = department_id.gateway_config.max_receiver
                i = 0
                while i < students_mosque_list_len:
                    students_mosque_list_sub = students_mosque_list[i:i + max_receiver]
                    students_mosque_substring = listToString(students_mosque_list_sub)
                    i = i + max_receiver

                    prms[department_id.gateway_config.user] = gateway_user
                    prms[department_id.gateway_config.password] = gateway_password
                    prms[department_id.gateway_config.sender] = gateway_sender
                    prms[department_id.gateway_config.to] = students_mosque_substring
                    prms[department_id.gateway_config.message] = mosqs[mosq_id]['message']

                    if prms:
                        response = requests.post(url, data=json.dumps(prms), headers=headers)
                        if response.json().get('code') == "1":
                            mosque.sent_sms_count = mosque.sent_sms_count - students_mosque_list_len
                            self.env['sms.traceability'].create({'user_id': self.env.user.id,
                                                                 'mosque_id': mosque.id,
                                                                 'nbr_message_sent': students_mosque_list_len ,
                                                                 'message': message})
                        if response.json().get('code') != "1":
                            msg = 'البيانات الخاصة ببوابة ارسال الرسائل القصيرة خاطئة !'
                            raise ValidationError(msg)




    def ok(self):
        resource = self.env['resource.resource'].search([('user_id', '=', self.env.user.id)])
        employee_id = self.env['hr.employee'].search([('resource_id', 'in', resource.ids)])
        department_id = self.env['hr.department'].sudo().search([('code', '=', '7')])

        numbers = ''
        student_ids = self.student_ids
        mosque_ids = self.mosque_ids
        students_domain = [('request_state', '=', 'accept'),
                           ('active', '=', True)]

        if not student_ids:
            if not mosque_ids:
                if employee_id.category == 'center_admin':
                    students_domain += [('department_id', '=', self.department_id.id)]
                elif employee_id.category =='edu_supervisor':
                    students_domain += [('mosq_id', 'in', employee_id.mosque_sup.ids)]
                else:
                    students_domain += [('mosq_id', 'in', employee_id.mosqtech_ids.ids)]

            else:
                students_domain += [('mosq_id', 'in', mosque_ids.ids)]

            student_ids = self.env['mk.student.register'].search(students_domain+ [])

        for rec in student_ids:
            if rec.mobile:
                if len(rec.mobile) == 12:
                    numbers += rec.mobile + ","
                elif len(rec.mobile) == 9:
                    numbers += "966" + rec.mobile + ","

        numbers = numbers[:-1]

        numbers_no_redendant = list(set(numbers.split(",")))

        numbersToStr = ','.join([str(elem) for elem in numbers_no_redendant])
        type_message = self.type_message

        if type_message == 'absance_notif':
            message = 'نفيدكم بتغيب ابنكم student عن الحلقات حلقات mosque'
        elif type_message == 'stop_ep_notif':
            message = 'نفيدكم بتعليق الدوام بالحلقات لهذا اليوم حلقات mosque'
        elif type_message == 'stop_student_notif':
            message = 'نفيدكم بانقطاع ابنكم student عن الحلقات حلقات جامع mosque'
        elif type_message == 'start_registration_notif':
            message = 'بدأ التسجيل في حلقات mosque فأهلا باهل القران, أهل الله وخاصته'
        elif type_message == 'reprise_ep_notif':
            message = 'تستأف الحلقات في mosque يوم الاحد فأهلا باهل القران, أهل الله وخاصته'
        elif type_message == 'quran_day':
            message = 'بدأ التسجيل في اليوم القراني فرصة لتثبيت حفظك ومراجعته حلقات mosque'
        else:
            message = self.message
        self.send_gateway_student_quta(message, type_message, numbersToStr, department_id, student_ids)


class mk_gateway_configurationInherit(models.Model):
    _inherit = 'mk.smsclient.config'

    max_receiver = fields.Integer(String='Max receiver')
    response_success = fields.Char(String='Response success')


class SmsTraceability(models.Model):
    _name = 'sms.traceability'
    _description = 'SMS Traceability'

    message = fields.Text(string='Message')
    nbr_message_sent = fields.Char(string='number message sent')
    mosque_id = fields.Many2one('mk.mosque', string='Mosque')
    user_id = fields.Many2one('res.users', string='User')

class mk_mosqueInherit(models.Model):
    _inherit = 'mk.mosque'

    sent_sms_count = fields.Integer(string='Sent Down Counter', default='700', )
    sms_ids = fields.One2many('sms.traceability', 'mosque_id', string="Sent SMS")

    @api.model
    def cron_default_sent_sms_count(self):
        self.env.cr.execute(''' update mk_mosque set sent_sms_count=700 ''')
