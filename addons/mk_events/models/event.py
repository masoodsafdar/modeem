# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import re
from odoo.exceptions import UserError, ValidationError
import math
import urllib.request
import logging
_logger = logging.getLogger(__name__)


class mk_events(models.Model):
    _inherit = 'event.event'

#     name = fields.Char()




    @api.depends('agenda','recommendations')
    def get_recommondaion_objects(self):
        if self.agenda and self.recommendations:
            self.obj_recommendation="اﻷهداف"+'\n'+"<br>"+self.agenda+'\n'+"<br>"+"التوصيات"+'<br>'+'\n'+self.recommendations
    event_date = fields.Date(
        string='Event date',
        required=False,
        readonly=False,
        index=False,
        help=False
    )
    event_status = fields.Many2one(
        string='Event status',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='event.status',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )
    event_start = fields.Float(
        string='Event start',
        required=False,
        readonly=False,
        index=False,
        default=0.0,
        digits=(16, 2),
        help=False
    )
    event_end = fields.Float(
        string='Event end',
        required=False,
        readonly=False,
        index=False,
        default=0.0,
        digits=(16, 2),
        help=False
    )
    agenda = fields.Text(
        string='Agenda',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        translate=False
    )
    attachments = fields.Many2many(
        string='Attachments',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='ir.attachment',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )
    
    employee_ids = fields.One2many(
        string='Employee',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='event.invite',
        inverse_name='event_id',
        context={},
        auto_join=False,
        limit=None
    )
    
    attendee_ids = fields.One2many(
        string='attendee',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='event.attendee',
        inverse_name='event_id',
        domain=[],
        context={},
        auto_join=False,
        limit=None
    )
    
    guest_ids = fields.One2many(
        string='guests',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='event.guest',
        inverse_name='event_id',
        domain=[],
        context={},
        auto_join=False,
        limit=None
    )
    
    place = fields.Selection(
        string='Place',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False,
        selection=[('inside', 'inside'), ('outside', 'outside'),('company','في مقر الجمعية')]
    )
    maknoon_street = fields.Char(string='maknoon street',)

    center_id = fields.Many2one(
        string='Center',
        required=False,
        readonly=False,
        index=False,
        comodel_name='hr.department',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    mosque_id = fields.Many2one(
        string='Mosque',
        required=False,
        readonly=False,
        index=False,
        default=None,
        comodel_name='mk.mosque',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )
    latitude = fields.Char(
        string='Latitude',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=False
    )
    longitude = fields.Char(
        string='Longitude',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=False
    )
    describe_place = fields.Char(
        string='Describe place',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=False
    )
    remind_sms = fields.Boolean(
        string='Remind with sms',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )
    recommendations = fields.Text(
        string='Recommendations',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        translate=False
    )
    obj_recommendation = fields.Text(
        string='objects and recommendation',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        compute=get_recommondaion_objects
    )
    other_attachements = fields.Many2many(
        string='Other attachements',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='ir.attachment',
        relation='event_attachment_rel',
        column1='event_id',
        column2='attach_id',
        domain=[],
        context={},
        limit=None
    )
    date_tz = fields.Selection(
        required=False
    )
    date_begin = fields.Datetime(
        required=False
    )
    date_end = fields.Datetime(
        required=False
    )
    period = fields.Selection(
        string='Period',
        required=True,
        readonly=False,
        index=False,
        default=False,
        help=False,
        selection=[('صباحا', 'صباحا'), ('مساء', 'مساء')]
    )
    @api.constrains('event_start')
    def event_time(self):
        if self.event_start>=13 or self.event_start<0:
            raise UserError(_('الرجاء ادخال التوقيت الصحيح'))

    @api.constrains('event_end')
    def event_time(self):
        if self.event_end>=13 or self.event_end<0:
            raise UserError(_('الرجاء ادخال التوقيت الصحيح'))


    @api.onchange('center_id')
    def get_mosques(self):
        mosque_ids=self.env['mk.mosque'].search([('center_department_id','=',self.center_id.id)]).ids
        return {'domain':{'mosque_id':[('id','in',mosque_ids)]}}


    @api.multi
    def button_done(self):
        self.write({'state':'done','remind_sms':False})
        return True

    @api.multi
    def button_confirm(self):
        self.write({'state':'confirm','remind_sms':False})
        return True

    @api.multi
    def button_cancel(self):
        self.write({'state':'cancel','remind_sms':False})
        return True


    @api.onchange('place')
    def get_place(self):
        if self.place == 'inside':
            self.latitude=False
            self.longitude=False
            self.describe_place=False
            self.maknoon_street=False
        elif self.place == 'company':
            self.latitude=False
            self.longitude=False
            self.describe_place=False
            self.center_id=False
            self.mosque_id=False
            maknoon=self.env['res.company'].search([('name','=','جمعية تحفيظ القران الكريم بالرياض')])
            if maknoon:
                self.maknoon_street=maknoon.street + " "+ maknoon.street2 + " "+ maknoon.city
        elif self.place == 'outside':
            self.center_id=False
            self.mosque_id=False
            self.maknoon_street=False

            #self.update({'mosque_ids':[(4,id) for id in self.employee_id.mosqtech_ids.ids]})

    '''
    @api.one
    def send_reminder(self):
        mail=self.env['mail.message']
        link="https://www.google.com/maps/@"+self.latitude+","+self.longitude+",15z"
        message="سيكون إجتماع val1 في يوم val2 عند الساعة val3 المكان : val4"
        hour=str(int(self.event_start))+":"+str(int((self.event_start-int(self.event_start))*60))
        message=message[0].sms_text
        message=re.sub(r'val1', self.name, message).strip()
        message=re.sub(r'val2', self.event_date, message).strip()
        message=re.sub(r'val3', str(hour), message).strip()
        if self.place == 'inside':
            #event_place=self.center_id.name + "بمسجد" + self.mosque_id.name 
            message=re.sub(r'val4', str(self.mosque_id.name), message).strip()
        elif self.place == 'outside':
            event_place=self.describe_place+"رابط الموقع"+link
            message=re.sub(r'val4', event_place, message).strip()
        vals={
                    'message_type': 'notification',
                    'subject': 'تذكير ',
                    'body': message,
                    'partner_ids':[(6, 0, [employee.user_id.partner_id.id for employee in self.employee_ids])] }

        mail.create(vals)
    '''

    @api.one
    def send_reminder_for_users(self):
        latitude=0
        longitude=0
        link="https://www.google.com/maps/@"+str(latitude)+","+str(longitude)+",15z"
        if self.latitude and self.longitude:
            link="https://www.google.com/maps/@"+self.latitude+","+self.longitude+",15z"
        phones=[]
        emails=""
        for rec in self.employee_ids:
            if rec.employee_id.mobile_phone:
                phones.append("966"+rec.employee_id.mobile_phone)
            if rec.email:
                emails+=rec.email
                emails+=","
        for rec in self.attendee_ids:
            if rec.employee_id.mobile_phone:
                phones.append("966"+rec.employee_id.mobile_phone)
            if rec.email:
                emails+=rec.email
                emails+=","

        message=self.env['mk.sms_template'].search([('code', '=', 'mk_send_reminder')],limit=1)
        hour=str(int(self.event_start))+":"+str(int((self.event_start-int(self.event_start))*60))
        if message:
            message=message[0].sms_text
            message=re.sub(r'val1', self.name, message).strip()
            message=re.sub(r'val2', self.event_date, message).strip()
            message=re.sub(r'val3', str(hour), message).strip()
            message=message+" "+self.period
            if self.remind_sms:
                obj_general_sending = self.env['mk.general_sending']
                if self.place == 'inside':
                    if not self.mosque_id and self.center_id:
                        message=message+" المكان : مركز "+self.center_id.name
                        if self.center_id.latitude and self.center_id.longitude:
                            link="https://www.google.com/maps/@"+self.center_id.latitude+","+self.center_id.longitude+",15z"
                            message=message+" رابط الموقع "+link
                            for item in phones:
                                obj_general_sending.send_sms(item,str(message))

                    #event_place=self.center_id.name + "بمسجد" + self.mosque_id.name 
                    if self.mosque_id and self.center_id:
                        message= message+str(" المكان : مسجد "+self.mosque_id.name)
                        if self.mosque_id.latitude and self.mosque_id.longitude:
                            link="https://www.google.com/maps/@"+self.mosque_id.latitude+","+self.mosque_id.longitude+",15z"
                            message= message+" رابط الموقع "+link
                            if self.mosque_id.gateway_config and self.mosque_id.gateway_password and self.mosque_id.gateway_user and self.mosque_id.gateway_sender:
                                prms={}
                                other=''
                                url=''
                                for item in phones:
                                    if self.mosque_id.send_time:
                                        hr_time=int(self.mosque_id.send_time)
                                        prms[self.mosque_id.gateway_config.time_send] = str(hr_time)+":"+str(int((self.mosque_id.send_time-hr_time)*60))+":"+'00'
                                        prms[self.mosque_id.gateway_config.user] = self.mosque_id.gateway_user
                                        prms[self.mosque_id.gateway_config.password] = self.mosque_id.gateway_password
                                        prms[self.mosque_id.gateway_config.sender] = self.mosque_id.gateway_sender
                                        prms[self.mosque_id.gateway_config.to] = "966"+item
                                        prms[self.mosque_id.gateway_config.message] = message
                                        if self.mosque_id.gateway_config.other:
                                            other=self.mosque_id.gateway_config.other
                                       

                                    
                                        url=self.mosque_id.gateway_config.url


                                        if prms and other:
                                            params = urllib.parse.urlencode(prms)+"&"+other
                                            url=url+"?"+params
                                            urllib.request.urlopen(url)
                                        elif prms and not other:
                                            params=urllib.parse.urlencode(prms)
                                            url=url+"?"+params
                                            urllib.request.urlopen(url)



                        
                    
                elif self.place == 'outside':
                    if self.describe_place:
                        event_place=" المكان "+self.describe_place+" رابط الموقع "+link
                    elif  not self.describe_place:
                        event_place=" رابط الموقع "+link
                    message= message+event_place
                    for item in phones:
                        obj_general_sending.send_sms(item,str(message))
                elif self.place=="company":
                    maknoon=self.env['res.company'].search([('name','=','جمعية مكنون')])
                    message+=" المكان : "+ maknoon.name+" , "+self.maknoon_street
                    if maknoon.latitude and maknoon.longitude:
                            link="https://www.google.com/maps/@"+maknoon.latitude+","+maknoon.longitude+",15z"
                            message= message+" رابط الموقع "+link
                            for item in phones:
                                obj_general_sending.send_sms(item,str(message))
        # if self.remind_sms:
        #     obj_general_sending = self.env['mk.general_sending']

            # for item in phones:
            #     obj_general_sending.send_sms(item,str(message))
        mail=self.env['mail.message']
        employees=[]
        attedees=[]
        for employee in self.employee_ids:
            partner=employee.employee_id.sudo().user_id.partner_id.id 
            if partner:

                employees.append(partner)

        for employee in self.attendee_ids:
            attendee=employee.employee_id.sudo().user_id.partner_id.id 
            if attendee:
                attedees.append(attendee)

        vals={
                    'message_type': 'notification',
                    'subject': 'تذكير ',
                    'body': message,
                    'partner_ids':[(6, 0, employees)] }

        vals2={
                    'message_type': 'notification',
                    'subject': 'تذكير ',
                    'body': message,
                    'partner_ids':[(6, 0, attedees)] }
        mail.create(vals)
        mail.create(vals2)
        
        mail_obj = self.env['mail.mail']

        msg_id = mail_obj.create({'body_html':message,'email_to':emails,'subject':"تذكير"})
        msg_id.send()
        
    @api.one
    def send_sms(self):
        latitude=0
        longitude=0
        link="https://www.google.com/maps/@"+str(latitude)+","+str(longitude)+",15z"
        if self.latitude and self.longitude:
            link="https://www.google.com/maps/@"+self.latitude+","+self.longitude+",15z"
        phones=[]
        emails=""
        for rec in self.guest_ids:
            if rec.phone:
                phones.append("966"+rec.phone)

        message=self.env['mk.sms_template'].search([('code', '=', 'mk_send_reminder')],limit=1)
        hour=str(int(self.event_start))+":"+str(int((self.event_start-int(self.event_start))*60))
        if message:
            message=message[0].sms_text
            message=re.sub(r'val1', self.name, message).strip()
            message=re.sub(r'val2', self.event_date, message).strip()
            message=re.sub(r'val3', str(hour), message).strip()
            message=message+" "+self.period
            
            if self.place == 'inside' :
                #event_place=self.center_id.name + "بمسجد" + self.mosque_id.name 

                if self.center_id and self.mosque_id:
                    message= message+str(" المكان : مسجد "+self.mosque_id.name)
                    if self.mosque_id.latitude and self.mosque_id.longitude:
                        link="https://www.google.com/maps/@"+self.mosque_id.latitude+","+self.mosque_id.longitude+",15z"
                        message=message+" رابط الموقع "+link
                elif self.center_id and not self.mosque_id:

                    message=message+" المكان : مركز "+self.center_id.name
                    if self.center_id.latitude and self.center_id.longitude:
                        link="https://www.google.com/maps/@"+self.center_id.latitude+","+self.center_id.longitude+",15z"
                
                
                        message=message+" رابط الموقع "+link
            elif self.place == 'outside':
                if self.describe_place:
                    message=message+" المكان : "+self.describe_place+" رابط الموقع "+link
            

            elif self.place=="company":
                maknoon=self.env['res.company'].search([('name','=','جمعية تحفيظ القران الكريم بالرياض')])
                message+=" المكان : "+ maknoon.name+" , "+self.maknoon_street
                if maknoon.latitude and maknoon.longitude:
                        link="https://www.google.com/maps/@"+maknoon.latitude+","+maknoon.longitude+",15z"
                        message= message+" رابط الموقع "+link

            message=message+" الرجاء تأكيد الحضور"
        if self.remind_sms:
            obj_general_sending = self.env['mk.general_sending']
            
            for item in phones:
                obj_general_sending.send_sms(item,str(message))
            emails=""
        self.ensure_one()

        for rec in self.guest_ids:
            if rec.email:
                emails+=rec.email
                emails+=","
        mail_obj = self.env['mail.mail']
        

        msg_id = mail_obj.create({'body_html':message,'email_to':emails,'subject':"تذكير"})
        msg_id.send()        
    @api.one
    def action_email(self):
        link=""

        emails=""
        self.ensure_one()
        template = self.env.ref('event.event_registration_mail_template_badge')
        compose_form = self.env.ref('mk_events.email_compose_message_event_wizard_form')
        for rec in self.employee_ids:
            if rec.email:
                emails+=rec.email
                emails+=","
        for rec in self.attendee_ids:
            if rec.email:
                emails+=rec.email
                emails+=","
        for rec in self.guest_ids:
            if rec.email:
                emails+=rec.email
                emails+=","
        mail_obj = self.env['mail.mail']
        message="سيكون إجتماع val1 في يوم val2 عند الساعة val3 "

        msg_id = mail_obj.create({'body_html':message,'email_to':emails,'subject':"تذكير"})
        msg_id.send()

    @api.multi
    def action_send_badge_email(self):
        """ Open a window to compose an email, with the template - 'event_badge'
            message loaded by default
        """

        message=self.obj_recommendation+"</br>"
        emails=""
        self.ensure_one()
        template = self.env.ref('event.event_registration_mail_template_badge')
        compose_form = self.env.ref('mk_events.email_compose_message_event_wizard_form')
        for rec in self.employee_ids:
            if rec.email:
                emails+=rec.email
                emails+=","
        for rec in self.attendee_ids:
            if rec.email:
                emails+=rec.email
                emails+=","
        for rec in self.guest_ids:
            if rec.email:
                emails+=rec.email
                emails+=","
        attach=self.attachments.ids+self.other_attachements.ids

        ctx = dict(
            default_model='event.event',
            default_res_id=self.id,
            #default_use_template=bool(template),
            #default_template_id=template.id,
            default_composition_mode='comment',
            default_emails=emails,
            default_body=message,
            default_attachment_ids=[(4,id) for id in attach]
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message.event',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }



class Eventinvite(models.Model):
    _name = 'event.invite'
    #_inherit=['mail.thread','mail.activity.mixin']

    @api.model
    def create(self, vals):
        values={'event_id':vals['event_id'],'invited':vals['employee_id']}
        register=self.env['event.registrations'].sudo().create(values)
        return super(Eventinvite, self).create(vals)
    

    
    event_id = fields.Many2one(
        'event.event', string='Event', required=True,)
    employee_id = fields.Many2one(
        'hr.employee', string='employee',
        domain=[('category2','not in',['teacher','others'])],
    )
    center_id = fields.Many2one(
        string='Center id',
        required=False,
        readonly=False,
        index=False,
        related='employee_id.department_id',
        comodel_name='hr.department',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )
    email = fields.Char(
        string='Email',
        required=False,
        readonly=False,
        index=False,
        related='employee_id.work_email',
        help=False,
        size=50,
        translate=False
    )
    mosque_ids = fields.Many2many(
        string='Mosque id',
        required=False,
        readonly=False,
        index=False,
        default=None,
        comodel_name='mk.mosque',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )
    job_id = fields.Many2one(
        string='job id',
        required=False,
        readonly=False,
        index=False,
        default=None,
        related='employee_id.job_id',
        comodel_name='hr.job',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )
    attendance_confirm = fields.Boolean(
        string='Attendance confirm',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )
    attendance_state = fields.Boolean(
        string='Attendance state',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )

    agenda_sent = fields.Boolean(
        string='agenda sent',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )

    agenda_reply = fields.Boolean(
        string='agenda reply',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )

    recommendation_acceptance = fields.Boolean(
        string='Recommendation acceptance',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )
    @api.onchange('employee_id')
    def get_mosque(self):
        if self.employee_id:
            self.mosque_ids=self.employee_id.mosqtech_ids.ids
            #self.update({'mosque_ids':[(4,id) for id in self.employee_id.mosqtech_ids.ids]})

class EventGuest(models.Model):
    _name = 'event.guest'
    #_inherit=['mail.thread','mail.activity.mixin']
    _order = 'name, create_date desc'

    
    event_id = fields.Many2one(
        'event.event', string='Event', required=True,)
    name = fields.Char(
        string='Name',
        required=True,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=False

    )

    partner = fields.Char(
        string='partner',
        required=False,
        readonly=False,
        index=False,
        help=False,
        translate=False
    )
    
    email = fields.Char(
        string='Email',
        required=False,
        readonly=False,
        index=False,
        help=False,
        translate=False
    )
    phone = fields.Char(
        string='Phone',
        required=False,
        readonly=False,
        index=False,
        help=False,
        size=9,
        translate=False
    )

    attendance_confirm = fields.Boolean(
        string='Attendance confirm',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )
    attendance_state = fields.Boolean(
        string='Attendance state',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )

    agenda_sent = fields.Boolean(
        string='agenda sent',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )

    agenda_reply = fields.Boolean(
        string='agenda reply',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )
    recommendation_acceptance = fields.Boolean(
        string='Recommendation acceptance',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )

class EventRegistration(models.Model):
    _name = 'event.attendee'
    _description = 'Attendee'
    #_inherit=['mail.thread','mail.activity.mixin']


    @api.model
    def create(self, vals):
        register=self.env['event.registrations'].sudo().create({'event_id':vals['event_id'],'invited':vals['employee_id']})
        return super(EventRegistration, self).create(vals)

    event_id = fields.Many2one(
        'event.event', string='Event', required=True,)
    employee_id = fields.Many2one(
        'hr.employee', string='employee',
        domain=[('category2','not in',['teacher','others'])],
    )
    center_id = fields.Many2one(
        string='Center id',
        required=False,
        readonly=False,
        index=False,
        related='employee_id.department_id',
        comodel_name='hr.department',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )
    email = fields.Char(
        string='Email',
        required=False,
        readonly=False,
        index=False,
        related='employee_id.work_email',
        help=False,
        size=50,
        translate=False
    )
    mosque_ids = fields.Many2many(
        string='Mosque id',
        required=False,
        readonly=False,
        index=False,
        default=None,
        related='employee_id.mosqtech_ids',
        comodel_name='mk.mosque',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )
    job_id = fields.Many2one(
        string='job',
        required=False,
        readonly=False,
        index=False,
        default=None,
        related='employee_id.job_id',
        comodel_name='hr.job',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )
    attendance_confirm = fields.Boolean(
        string='Attendance confirm',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )
    attendance_state = fields.Boolean(
        string='Attendance state',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )

    agenda_sent = fields.Boolean(
        string='agenda sent',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )

    agenda_reply = fields.Boolean(
        string='agenda reply',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )

    recommendation_acceptance = fields.Boolean(
        string='Recommendation acceptance',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )


