# -*- coding: utf-8-
import base64
import json
import requests
from lxml import etree
# from odoo.osv.orm import setup_modifiers

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import pycompat
from datetime import datetime, date

from random import randint

import pytz
from time import gmtime, strftime
import re

import logging
_logger = logging.getLogger(__name__)

class mk_student_register(models.Model):
    _name = 'mk.student.register'
    _description = 'Students  profile'
    _inherit = ['mail.thread']
    _rec_name='display_name'
    _order = 'create_date desc'

    # @api.multi
    def name_get(self):
        result = []
        for record in self:
            first_name = record.name
            second_name = record.second_name
            third_name = record.third_name
            fourth_name = record.fourth_name
            
            name = ''
            if first_name:
                name = first_name
                
            if second_name:
                name += ' ' + second_name
    
            if third_name:
                name += ' ' + third_name
                
            if fourth_name:
                name += ' ' + fourth_name
                
            result.append((record.id, name))
            
        return result
    
    # @api.one
    @api.depends('birthdate')
    def get_student_age(self):
        today = date.today()
        birthdate = self.birthdate
        age = 0
        if birthdate:
            birthdate_cnvrt = datetime.strptime(birthdate, '%Y-%m-%d').date()
            age = today.year - birthdate_cnvrt.year - ((today.month, today.day) < (birthdate_cnvrt.month, birthdate_cnvrt.day))
        self.student_age = age

    # @api.one
    @api.depends('mosq_id')
    def get_department(self):
        mosque = self.mosq_id
        self.department_id = mosque and mosque[0].center_department_id.id or False

    # @api.one
    @api.depends('name','second_name','third_name','fourth_name')
    def _display_name(self):
        first_name = self.name
        second_name = self.second_name
        third_name = self.third_name
        fourth_name = self.fourth_name
        
        name = ''
        if first_name:
            name = first_name
            
        if second_name:
            name += ' ' + second_name

        if third_name:
            name += ' ' + third_name
            
        if fourth_name:
            name += ' ' + fourth_name

        self.display_name = name        
    
    def default_country(self):
        return 179

    def default_area(self):
        return 600

    def default_city(self):
        return 401

    def _generate_passwd(self):
        n=4
        range_start = 10**(n-1)
        range_end = (10**n)-1
        gpass=randint(range_start, range_end)
              
        return gpass
    
    # @api.one
    @api.depends('request_draft_ids','request_accept_ids','request_reject_ids','request_draft_ids.state','request_accept_ids.state','request_reject_ids.state')
    def get_request(self):
        accept_requests = self.sudo().request_accept_ids
        request = False
         
        if len(accept_requests):
            request = accept_requests[0]

        else:
            draft_requests = self.sudo().request_draft_ids 
            if len(draft_requests):
                request = draft_requests[0]
                 
            else:
                reject_requests = self.sudo().request_reject_ids 
                if len(reject_requests):
                    request = reject_requests[0]
                                                 
        self.request_id = request and request.id or False

    @api.model
    def is_current_study_class(self):
        query1 = '''update mk_student_register set is_current_study_class = False ; '''
        self.env.cr.execute(query1)
        query = '''update mk_student_register set is_current_study_class = True 
                           where id in(select link.student_id FROM mk_link link
                                        join mk_episode ep on link.episode_id = ep.id
                                        join mk_study_class class on ep.study_class_id = class.id
                                         where class.is_default = True and link.state='accept'
                                         group by link.student_id ); '''
        self.env.cr.execute(query)

    # @api.multi
    @api.depends('request_draft_ids','request_draft_ids.state','request_accept_ids','request_accept_ids.state', 'link_ids', 'link_ids.state')
    def get_current_request_accept(self):
        for rec in self:
            rec.is_current_study_class = rec.request_accept_ids.filtered(lambda l: l.study_class_id.is_default == True) and True or False

    # @api.one
    @api.depends('request_id.state')
    def get_request_state(self):
        request = self.sudo().request_id
        self.request_state = request and request.state or ''
        
    # @api.one
    @api.depends('country_id', 'country_id.nationality')
    def get_nationality(self):
        country = self.country_id
        self.nationality = country and country.nationality or ''

    # @api.one
    @api.depends('country_id')
    def get_nationality_group(self):
        country_id = self.country_id
        if country_id.id == 179:
            self.nationality_group = 'sa'
        else:
            self.nationality_group = 'non_sa'

    @api.onchange('mosq_id')
    def onchange_mosq_gender(self):
        categ_mosque = self.mosq_id.categ_id
        self.gender = categ_mosque.mosque_type

    # @api.one
    @api.depends('mosq_id')
    def get_categ_gender(self):
        categ_mosque = self.mosq_id.categ_id
        self.categ_mosque_id = categ_mosque.id
        self.gender_mosque   = categ_mosque.mosque_type

    @api.model
    def default_get(self, fields):
        res = super(mk_student_register, self).default_get(fields)

        mosques_ids = False
        user_id = self.env.user
        employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])
        category = employee_id.category2
        if category == 'edu_supervisor':
            mosques_ids = employee_id.mosque_sup.ids
        elif category in ['admin', 'teacher', 'supervisor', 'center_admin']:
            mosques_ids = employee_id.mosqtech_ids.ids

        if 'mosq_id' in fields:
            res.update({'mosq_id': mosques_ids and mosques_ids[0] or False})
        return res


    name               = fields.Char(track_visibility='onchange')
    display_name       = fields.Char(compute="_display_name", string="Name", store=True)
    second_name        = fields.Char('Second Name', track_visibility='onchange')
    third_name         = fields.Char('Third Name',  track_visibility='onchange')
    fourth_name        = fields.Char('Fourth Name', track_visibility='onchange')
    no_identity        = fields.Boolean('No Identity',         track_visibility='onchange')
    identity_no        = fields.Char('Identity No',   size=10, track_visibility='onchange')
    passport_no        = fields.Char('Passport No',   size=10, track_visibility='onchange')
    mobile             = fields.Char('Mobile',        size=14, track_visibility='onchange')
    mobile_add         = fields.Char('second Mobile', size=14, track_visibility='onchange')
    email              = fields.Char('Email',                  track_visibility='onchange')
    passwd             = fields.Char('Passwd', default=_generate_passwd)
    gender             = fields.Selection([('male', 'Male'),
                                           ('female', 'Female')], string="Gender",  default="male",  track_visibility='onchange')
    country_id         = fields.Many2one('res.country', default=default_country, ondelete="restrict", track_visibility='onchange')
    nationality        = fields.Char('الجنسية' , compute=get_nationality, store=True, track_visibility='onchange')
    nationality_group  = fields.Selection([('sa', 'سعودي'),
                                           ('non_sa', 'غير سعودي')], 'سعودي/غير سعودي' , compute=get_nationality_group, store=True)
    area_id            = fields.Many2one('res.country.state', string='Area',     required=True, domain=[('type_location','=','area'),
                                                                                                        ('enable','=',True)], ondelete="restrict", default=default_area, track_visibility='onchange')    
    city_id            = fields.Many2one('res.country.state', string='City',     required=True, domain=[('type_location','=','city'),
                                                                                                        ('enable','=',True)], ondelete="restrict", default=default_city, track_visibility='onchange')
    district_id        = fields.Many2one('res.country.state', string='District', required=True, domain=[('type_location','=','district'),
                                                                                                        ('enable','=',True)], ondelete="restrict", track_visibility='onchange')
    birthdate          = fields.Date('Birthdate', track_visibility='onchange')
    student_age        = fields.Integer('Student age', compute='get_student_age')
    student_name       = fields.Char('Student name', size=50, translate=True)
    mosque_name        = fields.Char('Mosque name',  size=50, translate=True)
    center_name        = fields.Char('Center name',  size=50, translate=True)
    mosque_id          = fields.Many2many('mk.mosque',  domain=[('state', '=', 'accept')])
    mosque_new         = fields.Many2one('mk.mosque', string='new mosque', domain=[('state','=','accept')], ondelete="set null")
    mosq_id            = fields.Many2one('mk.mosque', string='المسجد',     domain=[('state', '=', 'accept')], track_visibility='onchange')
    department_id      = fields.Many2one('hr.department', string='Center name', compute='get_department', store=True)
    company_id         = fields.Many2one('res.company', string='Company', ondelete='restrict', default=lambda self: self.env.user.company_id.id)
    request_draft_ids  = fields.One2many('mk.link', 'student_id', domain=[('state','=','draft')])
    current_request_draft_ids  = fields.One2many('mk.link', 'student_id', domain=[('state','=','draft'),('episode_id.study_class_id.is_default','=',True)])
    request_accept_ids = fields.One2many('mk.link', 'student_id', domain=[('state','=','accept')])
    request_reject_ids = fields.One2many('mk.link', 'student_id', domain=[('state','=','reject')])
    request_id         = fields.Many2one('mk.link', string='طلب الانضمام', compute=get_request, store=True)
    request_state      = fields.Selection([('draft',  'طلب إنضمام مبدئي'),
                                           ('accept', 'طلب إنضمام مقبول'),
                                           ('reject', 'طلب إنضمام مرفوض'),
                                           ('done',   'طلب إنضمام منتهي')], string='حالة طلب الانضمام', compute=get_request_state, store=True, track_visibility='onchange')
    #color              = fields.Integer(compute=get_request, store=True)
    grade_id           = fields.Many2one('mk.grade', string='Grade', domain=[('active', '=', True)], ondelete="restrict", default=lambda self: self.env.ref('mk_master_models.grade_18').id, track_visibility='onchange')
    part_id            = fields.Many2many("mk.parts", string="part")    
    job_type           = fields.Selection([('student',  'طالب'),
                                           ('employee', 'Employee')], string='Job type', default='student',          track_visibility='onchange')
    job_id             = fields.Many2one('mk.job',string='Job', domain=[('active', '=', True)], ondelete="restrict", track_visibility='onchange')                    
    parent_identity    = fields.Char('Parent identity', size=10, translate=True, track_visibility='onchange')
    st_parent_id       = fields.Many2one('res.partner', string='Parent',  domain=[('company_type','=','parent')], track_visibility='onchange')
    partner_id         = fields.Many2one('res.partner', string='partner', ondelete="restrict")
    iqama_expire       = fields.Date('Iqama Expire')    
    marital_status     = fields.Selection([('single',   'Single'),
                                           ('married',  'Married'),
                                           ('widower',  'Widower'),
                                           ('divorced', 'Divorced')], string='Marital status', track_visibility='onchange')
    image              = fields.Binary("Image", attachment=True, help="This field holds the image used as avatar for this contact, limited to 1024x1024px",)
    image_medium       = fields.Binary("Medium-sized image", attachment=True, help="Medium-sized image of this contact. It is automatically "\
                                                                                "resized as a 128x128px image, with aspect ratio preserved. "\
                                                                                "Use this field in form views or some kanban views.")
    image_small        = fields.Binary("Small-sized image", attachment=True, help="Small-sized image of this contact. It is automatically "\
                                                                            "resized as a 64x64px image, with aspect ratio preserved. "\
                                                                            "Use this field anywhere a small image is required.")
    is_student         = fields.Boolean('Is student')
    is_current_study_class = fields.Boolean('Current study class', compute='get_current_request_accept', store=True)
    check_filter       = fields.Char('Check filter', default='student')
    link_ids           = fields.One2many('mk.link',      inverse_name='student_id', string='Episodes')
    banking_accounts   = fields.One2many('account.bank', inverse_name='student_id', string="banking accounts")
    registeration_code = fields.Char(size=12,     readonly=True, track_visibility='onchange')
    latitude           = fields.Char('Latitude',  track_visibility='onchange')
    longitude          = fields.Char('Longitude', track_visibility='onchange')
    active             = fields.Boolean('Active', default=True, track_visibility='onchange')
    flag               = fields.Boolean("flag")
    flag2              = fields.Boolean('Flag')
    gender_mosque      = fields.Selection([('male','رجالي'),
                                           ('female','نسائي')],  string="Mosque gender",   compute='get_categ_gender', store=True)
    categ_mosque_id    = fields.Many2one('mk.mosque.category',   string="Mosque category", compute='get_categ_gender', store=True)
    episode_type_id    = fields.Many2one('mk.episode_type', string='Episode Type', ondelete='restrict', track_visibility='onchange')
    ep_type_id         = fields.Many2one('mk.programs', string='نوع الحلقة', ondelete='restrict', track_visibility='onchange')
    recruit_id           = fields.Many2one('hr.recruitment.degree', string='Recruit')
    residence_country_id = fields.Many2one('res.country', ondelete="restrict", track_visibility='onchange')
    notes              = fields.Text('Notes')
    is_online_student  = fields.Boolean('Online', default=False, track_visibility='onchange')
    is_duplicated_identity  = fields.Boolean('duplicated student identity', default=False)
    is_duplicated_passport  = fields.Boolean('طالب بنفس الجواز', default=False)

    _defaults = {'flag':lambda self, cr, uid, ctx:ctx.get('flag',False),}

    @api.model
    def upload_student_image(self, student_id, student_image):
        student = self.env['mk.student.register'].sudo().browse(int(student_id))
        upload = student.write({'image': base64.b64decode(student_image)})
        if upload:
            return 0
        else:
            return 1
    
    # @api.multi
    def action_request(self):
        view_id = self.env.ref('mk_student_register.mk_student_assign_form_view').id
        vals = {'name': 'تصديق طلب الانضمام',
                'view_type': 'form',
                'view_mode': 'tree',
                'views': [(view_id, 'form')],
                'res_model': 'mk.student.assign',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'target': 'new',
                }
        student_request = self.env['mk.link'].search([('student_id', '=', self.id),
                                                      ('state', 'in', ['draft', 'reject'])], order="create_date desc",  limit=1)
        mosque = self.mosq_id
        if student_request:
            context_vals = {'default_student_id': student_request.student_id.id,
                            'default_mosq_id': student_request.mosq_id.id,
                            'default_link_id': student_request.id,
                            'default_program_type': 'open'}
            request_state = self.request_state
            if request_state == 'draft':
                context_vals.update({'default_state': request_state})
        else:
            context_vals = {'default_student_id': self.id,
                            'default_mosq_id': mosque and mosque.id or False,
                            'default_program_type': 'open'}
        if self.is_online_student:
            vals.update({'domain': [('mosque_id', '=', mosque.id),
                                     ('is_online', '=', True),
                                     ('state','in',['draft','accept'])] })
        vals.update({'context': context_vals})
        return vals
    
    def action_make_presence_student(self):
        links = self.env['mk.link'].search([('student_id','=',self.id),
                                            ('episode_id.is_online','=',True),
                                            ('study_class_id.is_default', '=', True),
                                            ('state', '!=', 'cancel')])
        for link in links:
            try:
                link.action_cancel()
            except:
                continue
        self.is_online_student = False

    def action_make_online_student(self):
        self.is_online_student=True

    @api.model
    def check_id_validity(self, identification_id, student_id):
        # to trim and is digits
        if not identification_id or not identification_id.isdigit():
            return 'فضلا رقم الهوية المدخل لابد ان يتكون من ارقام فقط'

        if len(identification_id) != 10:        
            return 'فضلا رقم الهوية لابد ان بتكون من 10 ارقام'
                
        # if the id starts what other than 1 or 2
        if identification_id[0] != '1' and identification_id[0] != '2':
            return 'عذرا !! رقم الهوية المدخل غير صحيح'
    
        total = 0
        i = 0
        while i < len(identification_id):
            temp = int(identification_id[i]) * 2
            temp = str(temp).ljust(2, '0')
            # adding a "0" digit to the number in case the number is less than 10
            # to prevent index error in the next line
            # example: 3 * 2 = 6 => 60  ,  8 * 2 = 16 => 16
            total += int(temp[0]) + int(temp[1])
            i += 1
            total += int(identification_id[i])
            i += 1
    
        # check if the validation is correct
        if total % 10 != 0:
            return 'عذرا !! رقم الهوية المدخل غير صحيح'
        
        domain = [('identity_no','=',identification_id)]
        if student_id:
            domain += [('id','!=',student_id)]

        student = self.sudo().search(domain, limit=1)
        err = ''
        if student:
            if student.category:
                err = 'عذرا! رقم الهوية المدخل تابع لحساب موظف'
                return err
            else:
                err = 'عذرا! رقم الهوية موجود مسبقا'
        else:
            domain += [('active','=',False)]
            student = self.sudo().search(domain, limit=1)
            if student and student.mosq_id:
                err = 'عذرا! الطالب موجود في الأرشيف'
                
        if err:
            mosque = student.mosq_id
            if mosque:
                mosq_name = mosque and mosque.name or "  "
                err += ' ' + 'في مسجد' + '"' + mosq_name + '"' + '\n' + 'الرجاء إنشاء' + ' ' + '"'
            else :
                err += '\n' + 'الرجاء إنشاء' + ' ' + '"'
            err += 'طلب إخلاء الطرف' + '"' + ' '
            err += 'لنقل الطالب'

            return err
        # return the first digit of the input id
        return 1
    
    @api.model
    def check_id_passport(self, identification_id, student_id):
        if not identification_id or len(identification_id) < 7:        
            return 'الرقم المدخل خطأ !رقم جواز السفر يجب أن يتكون من سبعة أحرف على الأقل'
        
        domain = [('passport_no','=',identification_id)]
        if student_id:
            domain += [('id','!=',student_id)]

        student = self.sudo().search(domain, limit=1)
        err = ''
        if student:
            err =  'عذرا! رقم الجواز موجود مسبقا'
        else:
            domain += [('active','=',False)]
            student = self.sudo().search(domain, limit=1)
            if student and student.mosq_id:
                err =  'عذرا! الطالب موجود في الأرشيف'

        if err:
            mosque = student.mosq_id
            if mosque:
                mosq_name = mosque and mosque.name or "  "
                err += ' ' + 'في مسجد' + '"' + mosq_name + '"' + '\n' + 'الرجاء إنشاء' + ' ' + '"'
            else :
                err += '\n' + 'الرجاء إنشاء' + ' ' + '"'
            err += 'طلب إخلاء الطرف' + '"' + ' '
            err += 'لنقل الطالب'

            return err
        return 1

    @api.model
    def _check_unicity_identity_passport_no(self, identification_id, no_identity, passport_no, student_id):
        err = ''
        if no_identity:
            existing_student_identity = self.env['mk.student.register'].sudo().search([('identity_no', '=', passport_no),
                                                                                       ('id', '=', student_id),
                                                                                       '|', ('active', '=', True),
                                                                                            ('active', '=', False)], limit=1)

            if existing_student_identity:
                err = 'عفوا , رقم جواز السفر مستخدم كرقم هوية لطالب آخر.'
                return err

        else :
            existing_student_passport = self.env['mk.student.register'].sudo().search([('passport_no', '=', identification_id),
                                                                                       ('id','!=',student_id),
                                                                                       '|', ('active', '=', True),
                                                                                            ('active', '=', False)], limit=1)

            if existing_student_passport:
                err = 'عفوا , رقم الهوية مستخدم كرقم جواز سفر لطالب آخر.'
                return err
        return 1

    @api.model
    def data_clean_student(self, last_id, nbr_student):
        all_students = self.search([('active','in',[False,True])])
        students = self.search([('active','in',[False,True]),
                                ('id','>',last_id)])
        i = 1
        j = 1
        d = 0
        nbr = len(students)
        students = self.search([('active','in',[False,True]),
                                ('id','>',last_id)], order='id', limit=nbr_student)
        nbr = len(students)
        for student in students:
            if not student.no_identity:
                res = self.check_id_validity(student.identity_no, student.id)
            else:
                res = self.check_id_passport(student.passport_no, student.id)

            if isinstance(res, pycompat.string_types):
                d += 1
                student.unlink()

            if j == 50:
                j = 0
            i += 1
            j += 1


    # @api.one
    @api.constrains('no_identity','identity_no','passport_no')
    def _check_identification_id(self):
        if not self.no_identity:
            res = self.check_id_validity(self.identity_no, self.id)
        else:
            res = self.check_id_passport(self.passport_no, self.id)

        if isinstance(res, pycompat.string_types):
            raise ValidationError(res)#TO DO create from Portal
        
    @api.model
    def check_num_mobile(self, num_mobile, student_id):
        # to trim and is digits
        if not num_mobile or not num_mobile.isdigit():
            return 'فضلا رقم الجوال المدخل لابد ان يتكون من ارقام فقط'
        
        if not self.no_identity:
            if len(num_mobile) != 9:
                return 'فضلا رقم الجوال لابد ان بتكون من 9 ارقام'
                    
            # if the id starts what other than 1 or 2
            if num_mobile[0] != '5':
                return 'عذرا !! رقم الجوال المدخل غير صحيح'
        
#         domain = ['!',('mobile','=',num_mobile),
#                       ('mobile_add','=',num_mobile),]
#         if student_id:
#             domain += [('id','!=',student_id)]
# 
#         student = self.sudo().search(domain, limit=1)
#         if student:
#             return 'عذرا! رقم الجوال خاص بطالب آخر'

        return 1

    @api.onchange('mobile')
    def onchange_mobile(self):
        num_mobile = self.mobile
        if num_mobile:
            res = self.check_num_mobile(num_mobile, self.id)
            if isinstance(res, pycompat.string_types):
                raise ValidationError(res)   
            
    @api.onchange('mobile_add')
    def onchange_mobile_add(self):
        num_mobile = self.mobile_add
        if num_mobile:
            res = self.check_num_mobile(num_mobile, self.id)
            if isinstance(res, pycompat.string_types):
                raise ValidationError(res)                     
    
    # @api.one
    @api.constrains('mobile','mobile_add')
    def check_num_mobiles(self):
        res = self.check_num_mobile(self.mobile, self.id)
        if self.mobile_add:
            res = self.check_num_mobile(self.mobile_add, self.id)
            
        if isinstance(res, pycompat.string_types):
            raise ValidationError(res)#TO DO create from Portal

    @api.constrains('birthdate')
    def _check_birthdate(self):
        if self.birthdate:
            birthdate = self.birthdate.split('-')
            year = birthdate[0]
            if year[:2] not in ['19','20'] or len(year) != 4:
                raise ValidationError(_('Please enter valid date !'))
            if self.birthdate > fields.Datetime.now():
                raise ValidationError(_('Date of birth must be lower than actual date !'))

    @api.model
    def create(self, values):
        if values.get('student_name', False):
            values['mosque_id'] = [(4,values['mosque_new'])]
        episode_type_id = values.get('episode_type_id', False)
        if episode_type_id:
            values['ep_type_id'] = episode_type_id
            values.pop('episode_type_id')
        sequence = self.env['ir.sequence'].next_by_code('mk.student.serial')
        values['registeration_code'] = sequence
        tools.image_resize_images(values)

        identity_no = values.get('identity_no', False)
        passport_no = values.get('passport_no', False)
        no_identity = values.get('no_identity', False)
        
        if no_identity:
            values.update({'identity_no':False})
        else:
            values.update({'passport_no': False})
            

        existing_student = self.env['mk.student.register'].sudo().search([('active', '=', False),
                                                                          '|',('identity_no','=',str(identity_no)),
                                                                              ('passport_no','=',str(passport_no))], limit=1)

        if existing_student:
            values['active'] = True
            existing_student.write(values)
            student = existing_student
        else:
            student = super(mk_student_register, self).create(values)

        if self._context.get('is_from_supervisor') and not student.is_student_meqraa:
            request = self.env['mk.link'].sudo().create({'mosq_id': student.mosq_id.id,
                                                         'student_id': student.id,
                                                         'state': 'draft'})
            student.request_id = request.id
        #create notification for mosq supervisor
        mosque_responsible = student.mosq_id.responsible_id.user_id.partner_id
        mosque_admin= student.mosq_id.mosque_admin_id

        if mosque_responsible and not student.is_student_meqraa:
            vals = {'message_type': "notification",
                    "subtype": self.env.ref("mail.mt_comment").id,
                    'body': "تم تسجيل طالب جديد",
                    'subject': "تسجيل طالب جديد",
                    'needaction_partner_ids': [(4, mosque_responsible.id)],
                    'model': self._name,
                    'res_id': student.id}
            notif = self.env['mail.message'].create(vals)
            # send email to mosq supervisor
            template = self.env['mail.template'].search([('name','=','mk_send_mosq_responsible_for_new_student')], limit=1)
            if template:
                b = template.sudo().send_mail(student.id, force_send=True)
        # create notification for mosque admin
        mosque_admin= student.mosq_id.mosque_admin_id.user_id.partner_id
        if mosque_admin and student.mosq_id.is_send_to_mosque_admin and not student.is_student_meqraa:
            vals = {'message_type': "notification",
                    "subtype": self.env.ref("mail.mt_comment").id,
                    'body': "تم تسجيل طالب جديد",
                    'subject': "تسجيل طالب جديد",
                    'needaction_partner_ids': [(4, mosque_admin.id)],
                    'model': self._name,
                    'res_id': student.id}
            notif_mosque_admin = self.env['mail.message'].create(vals)
            # send email to mosq admin (moudir)
            template = self.env['mail.template'].search([('name','=','mk_send_mmosque_admin_id_for_new_student')], limit=1)
            if template:
                b = template.sudo().send_mail(student.id, force_send=True)
        return student
    
    # @api.one
    def write(self, vals):
        if 'mosq_id' in vals:
            mosq_id = vals.get('mosq_id', False)

            mosque = self.env['mk.mosque'].sudo().search([('id', '=', mosq_id)], limit=1)

            district_id = mosque.district_id
            vals.update({'district_id': district_id and district_id.id or False})
            vals.update({'is_student_meqraa': False})

        if 'parent_identity' in vals:
            parent_identity = vals.get('parent_identity', False)
            
            parent_student = False
            if parent_identity:
                parent_student = self.env['res.partner'].search([('identity_no','=',parent_identity),
                                                                 ('parent','=',True)], limit=1)
                if not parent_student:
                    parent_student = self.env['res.partner'].search([('passport_no','=',parent_identity),
                                                                     ('parent','=',True)], limit=1)  
            vals.update({'st_parent_id': parent_student and parent_student.id or False})                  
        tools.image_resize_images(vals)
        if 'active' in vals and vals.get('active') == False:
            links = self.env['mk.link'].sudo().search([('student_id', '=', self.id),
                                                      ('mosq_id', '=', self.mosq_id.id),
                                                      ('state', 'in', ['accept', 'draft'])])
            if links:
                for link in links:
                    student_test = self.env['student.test.session'].search([('student_id', '=', link.id),
                                                                            ('state', 'not in', ['cancel', 'absent', 'done'])],limit=1)
                    if student_test:
                        raise ValidationError(_('لا يمكنك أرشفة الطالب لارتباطه بجلسات اختبار مبرمجة في الحلقة'))
            else:
                if self.sudo().mosq_id:
                    student_link = self.env['mk.link'].sudo().search([('student_id', '=', self.id),
                                                                      ('mosq_id', '=', self.mosq_id.id),
                                                                      ('state', 'in', ['accept', 'draft'])])
                    if student_link:
                        student_link.write({'state': 'done',
                                            'action_done': 'clear'})
                # self.sudo().mosq_id = False
        if 'no_identity' in vals:
            if vals['no_identity']:
                vals.update({'identity_no': False})
            else:
                vals.update({'passport_no': False})
        return super(mk_student_register, self).write(vals)

    @api.model
    def remove_mosq_from_archived_students(self):
        archived_students = self.env['mk.student.register'].sudo().search([('mosq_id', '!=', False),
                                                                            ('active', '=', False)])
        for student in archived_students:
            student.sudo().mosq_id = False

    @api.model
    def clearance_for_archived_students_with_done_link(self):
        query = '''UPDATE mk_student_register
         		                SET mosq_id = null
         		                WHERE mk_student_register.active = false'''
        query1 = '''UPDATE mk_link
                    SET action_done = 'clear',
		                state = 'done' 
	                WHERE id in ( SELECT link.id as id
                                 from mk_link link
                                 left join mk_student_register student on  link.student_id = student.id
                                 left join mk_episode ep on link.episode_id = ep.id
                                 where student.active = false AND 
                                       link.action_done is null AND
                                       ep.study_class_id = 102 ) ; '''
        query2 = ''' UPDATE mk_link
			         SET action_done = 'ep_done',
				         state = 'done' 
			         WHERE id in ( SELECT link.id as id
								 from mk_link link
								 left join mk_student_register student on link.student_id = student.id
								 left join mk_episode ep on link.episode_id = ep.id
								 where link.action_done is null AND
									   ep.study_class_id != 102 ); '''
        self.env.cr.execute(query1)
        self.env.cr.execute(query2)
        self.env.cr.execute(query)

    @api.model
    def clearance_for_archived_students(self, id_from):
        archived_students = self.env['mk.student.register'].sudo().search([('mosq_id', '!=', False),
                                                                            ('active', '=', False),
                                                                           ('id', '>=', id_from)], order="id asc", limit = 500)
        for student in archived_students:
            if student.sudo().mosq_id:
                student_link = self.env['mk.link'].sudo().search([('student_id', '=', student.id),
                                                                  ('mosq_id', '=', student.mosq_id.id),
                                                                  ('action_done', '=', False),
                                                                  ('state', 'in', ['accept', 'draft'])], limit=1)
                if student_link:
                    student_link.write({'state': 'done',
                                        'action_done': 'clear'})
                student.sudo().mosq_id = False

    # @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active      
    
    # @api.one
    def check_parent_mobile(self,mobile):
        obj_res_partner = self.env['res.partner']
        #obj_std = self.env['mk.student.register']
        #brw = obj_std.browse(mobile)
        parent_search = obj_res_partner.search([('is_student', '=', False)])
        for parent in parent_search:
            if parent.mobile == mobile:
                return False
        return True

    # @api.one
    def check_parent_email(self,email):
        obj_res_partner = self.env['res.partner']
        parent_search = obj_res_partner.search([('is_student', '=', False)])
        for parent in parent_search:
            if parent.email == email:
                return False
            
        return True

    # @api.one
    def check_student_mobile(self,mobile):
        obj_res_partner = self.env['mk.student.register']
        student_search = obj_res_partner.search([('is_student', '=', True)])
        for student in student_search:
            if student.mobile == mobile:
                return False
        return True

    # @api.one
    def check_student_email(self,email):
        obj_res_partner = self.env['mk.student.register']
        student_search = obj_res_partner.search([('is_student', '=', True)])
        for student in student_search:
            if student.email == email:
                return False
        return True

    @api.onchange('city_id')
    def city_id_on_change(self):
        self.district_id = False

    ##########Testing#####
    
    # @api.multi
    def test(self):
        self.filter_mosque(1)            
            
    # @api.multi
    def filter_mosque(self,area_id, district_id=False):
        #msjed = False
        #epi= self.check_episode_occpy()
        list_msjd= []
        if district_id==False:
            for rec in self.env['mk.mosque'].search([('area_id','=',int(area_id))]):
                msjd = self.filter_episodes(rec.id)
                if len(msjd) > 0:
                    list_msjd.append(rec.id)
        elif area_id:
            for rec in self.env['mk.mosque'].search([('district_id','=',int(district_id))]):
                msjd = self.filter_episodes(rec.id)
                if len(msjd) > 0:
                    list_msjd.append(rec.id)
        return list_msjd

    # @api.multi
    def filter_episodes(self, mosque_id):
        list_epis= []

        epi_msjd = self.env['mk.episode'].search([('mosque_id','=',int(mosque_id))])
        for epi_rec in  epi_msjd:
            if self.check_episode_occpy(epi_rec.id):
                list_epis.append(epi_rec.id)
                
        return list_epis

    # @api.multi
    def check_episode_occpy(self,episode_id):
        academic_year = self.env['mk.study.year'].search([('active','=',True),('is_default','=',True)])
        obj_episode = self.env['mk.episode'].browse([int(episode_id)])
        for episode_year in academic_year:
            ###'academic',episode_year
            episode_search = self.env['mk.link'].search([('episode_id','=',int(obj_episode.id)),('year','=',episode_year.id)])
            count = len(episode_search)
            if (obj_episode.expected_students - count) > 0:
                return True
        
        return False             
          
    @api.onchange('identity_no','no_identity','passport_no')
    def invistigate_identity(self):
        identity_no = self.identity_no
        passport_no = self.passport_no
        if identity_no or passport_no:
            if not self.no_identity:
                res = self.check_id_validity(self.identity_no, self.id)

            else:
                res = self.check_id_passport(self.passport_no, self.id)

            if res == 1:
                res = self._check_unicity_identity_passport_no(self.identity_no, self.no_identity, self.passport_no, self._origin.id)

            if isinstance(res, pycompat.string_types):
                raise ValidationError(res)
            
            if not self.create_date:
                self.create_date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                                     
    # @api.multi
    def add_mosq(self):
        if self.identity_no:
            query="""SELECT id, display_name FROM mk_student_register where identity_no = '%s' and date(create_date) < date(now());""" %(str(self.identity_no))
        elif self.passport_no:
            query="""SELECT id, display_name FROM mk_student_register where passport_no = '%s' and date(create_date) < date(now());""" %(str(self.passport_no))

        self.env.cr.execute(query)
        student=self.env.cr.dictfetchall()
        if student:
            query_mosque=""" SELECT mk_mosque_id FROM mk_mosque_mk_student_register_rel where mk_student_register_id = %d;""" %(student[0]['id'])
            self.env.cr.execute(query_mosque)
            results=self.env.cr.dictfetchall()
            if self.mosque_new.id in [result['mk_mosque_id'] for result in results]:
                self.create_date=False
                res={}
                res = self.env.ref('mk_student_register.warning_form',False)
                return {'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                            'views': [(res.id, 'form')],
                            'view_id': res.id,
                            'res_model': 'wizard.message',
                            'context': {'default_name':'هذا الطالب موجود مسبقا بالمسجد','default_passport':self.passport_no,'default_identity':self.identity_no,'default_original_id':self.id},
                            'nodestroy': True,
                            'target': 'new',
                            'res_id':  False,}
                delete_query='delete from mk_student_register where id = %d' %(self.id)
                self.env.cr.execute(delete_query)
          
            else:
                query2 ="""INSERT INTO public.mk_mosque_mk_student_register_rel(
                mk_student_register_id, mk_mosque_id)
                VALUES (%d, %d);""" % (student[0]['id'], self.mosque_new.id)
                self.env.cr.execute(query2)

        self.env.cr.execute('select id from mk_student_register order by id desc limit 1')

        id_returned = self.env.cr.fetchone()
        delete_query='delete from mk_student_register where id = %d' %(self.id)
        self.env.cr.execute(delete_query)
        form_view=self.env.ref('mk_student_register.view_student_register_form')
        return {'type': 'ir.actions.act_window',
                'res_model': 'mk.student.register',
                'target': 'current',
                'res_id':student[0]['id'],
                'views': [(form_view.id,'form'),],
                'nodestroy': False,
                'tag':'reload'}
        
    # @api.one
    def send_passwd(self):
        prms = {}

        headers = {
            'content-type': 'application/json',
        }
        email = self.email
        # if not email:
        #     raise ValidationError('! يجب إضافة إيميل التواصل ')

        n = 4 
        range_start = 10 ** (n - 1)
        range_end = (10 ** n) - 1
        passwd = randint(range_start, range_end)

        
        self.passwd = passwd

        #user.sudo().write({'password': passwd,})
        try:
            template = self.env['mail.template'].search([('name','=','mk_send_pass_student')], limit=1)
            if template:
                b = template.send_mail(self.id, force_send=True)
        except:
            pass

        message = self.env['mk.sms_template'].search([('code', '=', 'mk_send_pass')],limit=1)

        message = message[0].sms_text

        mobile_phone = self.mobile

        if mobile_phone:
            message = re.sub(r'val1', self.passwd, message).strip()

            department_id = self.env['hr.department'].search([('id', '=', 42)])

            if department_id.send_time:
                hr_time = int(department_id.send_time)
                prms[department_id.gateway_config.time_send] = str(hr_time) + ":" + str(int((department_id.send_time - hr_time) * 60)) + ":" + '00'
            prms[department_id.gateway_config.user] = department_id.gateway_user
            prms[department_id.gateway_config.password] = department_id.gateway_password
            prms[department_id.gateway_config.sender] = department_id.gateway_sender
            prms[department_id.gateway_config.to] = '966'+mobile_phone
            prms[department_id.gateway_config.message] = message



            url = department_id.gateway_config.url

            if prms:
                try:
                    response = requests.post(url, data=json.dumps(prms), headers=headers)
                except:
                    pass

    @api.model
    def login_user(self, registeration_code, passwd):
        student = self.sudo().search([('passwd','=',passwd),
                                       '|', ('registeration_code','=',registeration_code),
                                            '|', '&', ('identity_no','=',registeration_code),('no_identity', '!=', True),
                                                 '&', ('passport_no','=',registeration_code),('no_identity', '=', True),], limit=1)
        student_id = student.id
        if student:

            return {'student_id': student.id,
                    'display_name': student.display_name,
                    'parent_id':student.partner_id.id}
        
        return {'student_id': 0}    
        
    # @api.constrains('is_student')
    # def check_student(self):
    #     if self.is_student==True:
    #         delta=datetime.strptime(str(fields.Date.today()),"%Y-%m-%d")-datetime.strptime(str(self.birthdate),"%Y-%m-%d")
    #         age=delta.days/365
    #         if self.is_student and int(age)<4:
    #             raise ValidationError(_('عمر الطالب اقل من 4 سنوات لايمكن ان يكون مسؤول عن نفسه'))
    
    # is_student on change

    @api.onchange('is_student')
    def is_student_onchange(self):
        if self.is_student:
            #current date
            self.st_parent_id=False
            #self.birthdate=datetime.strptime(str(fields.Date.today()),"%Y-%m-%d")-timedelta(days=4*365)
        else:
            self.birthdate=False
                
    # on_change birthdate
    @api.onchange('birthdate')
    def birthdate_on_change(self):
        if self.birthdate:
            # calcalute 
            delta = datetime.strptime(str(fields.Date.today()),"%Y-%m-%d")-datetime.strptime(str(self.birthdate),"%Y-%m-%d")
            age = delta.days/365

    # @api.one
    def unlink(self):
        student_test_sessions_ids = self.env['student.test.session'].search([('student_id.student_id','=', self.id),
                                                                           ('active', '=', True)], limit=1)
        if student_test_sessions_ids:
            raise UserError(_('لا يمكنك حذف الطالب لارتباطه بجلسات اختبار'))
        else:
            super(mk_student_register, self).unlink()

    @api.model
    def get_student_count(self):
        count = 0
        accepted_students = self.env['mk.student.register'].search(['|', ('active', '=', True),
                                                                         ('active', '=', False)])
        if accepted_students:
            count = len(accepted_students)
        return count

    @api.model
    def set_student_nationality_cron_fct(self):
        query = """UPDATE mk_student_register
                    SET nationality = 'سعودي'
                    WHERE country_id = 179;"""
        self.env.cr.execute(query)

    @api.model
    def parent_students(self, parent_id):
        try:
            parent_id = int(parent_id)
        except:
            pass

        query_string = ''' 
               select id, display_name, registeration_code
               from mk_student_register
               where st_parent_id={} and active=True order by id;
               '''.format(parent_id)

        self.env.cr.execute(query_string)
        parent_students = self.env.cr.dictfetchall()
        return parent_students

    @api.model
    def test_results(self, episode_id):
        try:
            episode_id = int(episode_id)
        except:
            pass

        query_string = ''' 
                SELECT student.display_name student_name,
                student.identity_no id_student,
                type_test.name test_type,
                branch.name branch_test,
                committe.name committe_test,
                employee.name committe_responsible,
                test_session.start_date test_start,
                test_session.done_date test_done,
                test_session.degree degree_test,
                test_session.appreciation appreciation_test

                FROM mk_student_register student
                LEFT JOIN mk_link link on student.id=link.student_id
                LEFT JOIN student_test_session test_session on test_session.student_id=link.id
                LEFT JOIN mk_test_names type_test on test_session.test_name=type_test.id
                LEFT JOIN mk_branches_master branch on test_session.branch=branch.id
                LEFT JOIN committee_tests committe on test_session.committe_id=committe.id
                LEFT JOIN res_users on test_session.user_id=res_users.id
                LEFT JOIN res_partner employee on res_users.partner_id=employee.id

                WHERE link.episode_id={} AND
                test_session.state='done';
                '''.format(episode_id)

        self.env.cr.execute(query_string)
        test_results = self.env.cr.dictfetchall()
        return test_results

    @api.model
    def best_students(self):
        query_string = ''' 
                 select rate, name display_name
                 from get_top_five_student
                 order by id desc
                 limit 5;
                 '''
        self.env.cr.execute(query_string)
        best_students = self.env.cr.dictfetchall()
        return best_students

    @api.model
    def get_registration_code(self, table, id):
        try:
            table = table
            id = int(id)
        except:
            pass

        query_string = ''' 
           select registeration_code
           from {}
           where id = {};
           '''.format(table, id)

        self.env.cr.execute(query_string)
        get_registration_code = self.env.cr.dictfetchall()
        return get_registration_code

    @api.model
    def teacher_student_episodes(self, episode_id):
        try:
            episode_id = int(episode_id)
        except:
            pass

        query_string = ''' 
                  select student.id, student.display_name, link.id link_id
                  from mk_student_register student left join mk_link link on student.id=link.student_id
                  where link.episode_id={} and
                  link.state = 'accept' and 
                  student.active=True;
                  '''.format(episode_id)
        self.env.cr.execute(query_string)

        teacher_student_episodes = self.env.cr.dictfetchall()
        return teacher_student_episodes

    @api.model
    def get_student_image(self, student_id):
        student = self.env['mk.student.register'].search_read(domain=[('id', '=', student_id),
                                                                      '|', ('active', '=', True),
                                                                           ('active', '=', False)], fields=['image','id'], limit=1)
        return student

    @api.model
    def upload_student_image(self, student_id, student_image):
        student = self.env['mk.student.register'].sudo().browse(int(student_id))
        upload = student.sudo().write({'image': student_image})
        if upload:
            return 0
        else:
            return 1

    @api.model
    def update_country_for_teacher_students_profile(self):
        employee_students = self.env['mk.student.register'].search([('category', '!=', False)])
        for student in employee_students:
            domain = ['|', ('active', '=', True), ('active', '=', False)]
            identification_id = student.identity_no
            if student.no_identity:
                identification_id = student.passport_no
            employee = self.env['hr.employee'].search(domain +[('identification_id', '=', identification_id)], limit =1)
            student.country_id = employee.country_id.id

    # @api.multi
    def action_student_request_multi(self):
        assign_episode_form = self.env.ref('mk_student_register.view_student_request_multi_form')
        vals = {
            'name': _('تنسيب لحلقة'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mk.student.internal_transfer',
            'views': [(assign_episode_form.id, 'form')],
            'view_id': assign_episode_form.id,
            'target': 'new',
            'context': {'default_student_ids': self.env.context.get('active_ids', []),
                        'default_type_order': 'assign'}
        }
        return vals

    @api.model
    def cron_duplicated_identities(self):
        query1 = '''update mk_student_register set is_duplicated_identity = False where is_duplicated_identity = True; '''
        self.env.cr.execute(query1)
        query = '''update mk_student_register set is_duplicated_identity = True 
                   where identity_no in(select identity_no FROM mk_student_register
                                         where no_identity=False 
                                         group by identity_no 
                                         having count(identity_no)>1); '''
        self.env.cr.execute(query)

    @api.model
    def cron_duplicated_passports(self):
        query1 = '''update mk_student_register set is_duplicated_passport = False where is_duplicated_passport = True; '''
        self.env.cr.execute(query1)
        query = '''update mk_student_register set is_duplicated_passport = True 
                   where passport_no in(select passport_no FROM mk_student_register
                                         where no_identity=True 
                                         group by passport_no 
                                         having count(passport_no)>1); '''
        self.env.cr.execute(query)

    # @api.multi
    def open_view_student_listen_lines(self):
        tree_view = self.env.ref('mk_student_managment.mk_listen_line_tree_view_student')
        search_id = self.env.ref('mk_student_managment.mk_listenline_search_view')
        return {'name':       " تسميع الطالب " ,
                'res_model': 'mk.listen.line',
                'res_id':     self.id,
                'views':     [(tree_view.id, 'tree'),(False, 'form')],
                'type':      'ir.actions.act_window',
                'target':    'current',
                'context': {'default_student_register_id': self.id},
                'domain':    [('student_register_id','=',self.id)],
                'search_view_id': search_id.id}

    # @api.multi
    def open_view_student_presence_lines(self):
        tree_view = self.env.ref('mk_student_managment.student_prepare_presence_tree_view_from_student')
        # form_view = self.env.ref('mk_student_managment.student_prepare_presence_form_view')
        search_id = self.env.ref('mk_student_managment.student_prepare_presence_search_view')
        return {'name':       "حضور الطالب" ,
                'res_model': 'mk.student.prepare.presence',
                'res_id':     self.id,
                'views':     [(tree_view.id, 'tree')],
                'type':      'ir.actions.act_window',
                'target':    'current',
                'context':    {'default_student_register_id': self.id},
                'domain':    [('student_register_id','=',self.id)],
                'search_view_id': search_id.id}


class MailMessageInherit(models.Model):
    _inherit ='mail.message'

    enable = fields.Boolean(String="Enable")

    @api.model
    def message_fetch(self, domain, limit=20):
        all_recors = self.search(domain, limit=limit)
        filtered_records = self.search(domain, limit=limit).filtered(lambda m: m.model in ['mk.student.register', 'transportation.request','mk.student_absence',
                                                                                           'mosque.permision','mosque.supervisor.request','student.test.session',
                                                                                           'mk.clearance','mak.test.center','mk.episode', 'mk.study.class',
                                                                                           'contest.preparation'])
        return filtered_records.message_format()


class PartnerInherit(models.Model):
    _inherit ='res.partner'

    @api.model
    def get_needaction_count(self):
        """ compute the number of needaction of the current user """
        if self.env.user.partner_id:
            self.env.cr.execute("""
                   SELECT count(*) as needaction_count
                   FROM mail_message_res_partner_needaction_rel R
                   INNER JOIN mail_message M
                   ON M.id = R.mail_message_id
                   WHERE R.res_partner_id = %s AND (R.is_read = false OR R.is_read IS NULL) and M.model in ('mk.student.register', 'transportation.request','mk.student_absence',
                                                                                              'mosque.permision','mosque.supervisor.request','student.test.session',
                                                                                              'mk.clearance','mak.test.center','mk.episode', 'mk.study.class',
                                                                                              'contest.preparation')""",(self.env.user.partner_id.id,))
            return self.env.cr.dictfetchall()[0].get('needaction_count')
        return 0


class wizard_message(models.TransientModel):
    _name = 'wizard.message'

    name        = fields.Text('Warning',  readonly=True)
    identity    = fields.Char(string='identity', size=50, translate=True)
    passport    = fields.Char(string="passport")
    original_id = fields.Integer('Original id')

    # @api.multi
    def ok(self):
        query=''
        if self._context.get('default_identity',False):
            query="""SELECT id, display_name FROM mk_student_register where identity_no = '%s' and date(create_date) < date(now());""" %(str(self._context.get('default_identity')))
        
        elif self._context.get('default_passport_no',False):
            query="""SELECT id, display_name FROM mk_student_register where passport_no = '%s' and date(create_date) < date(now());""" %(str(self._context.get('default_passport')))

        self.env.cr.execute(query)
        student=self.env.cr.dictfetchall()
        delete_query='delete from mk_student_register where id = %d' %(self._context.get('default_original_id',False))
        self.env.cr.execute(delete_query)
        form_view=self.env.ref('mk_student_register.view_student_register_form')
        
        return {'type': 'ir.actions.act_window',
                'res_model': 'mk.student.register',
                'target': 'current',
                'res_id':student[0]['id'],
                'views': [(form_view.id,'form'),],
                'nodestroy': False,
                'tag':'reload'}


class StudentAssign(models.TransientModel):
    _name = 'mk.student.assign'

    @api.depends('episode_id')
    def get_episode_days(self):
        days = set()
        for episode_day in self.episode_id.episode_days:
            days.add(episode_day.id)
        self.domain_days = list(days)

    @api.onchange('episode_id')
    def onchange_episode(self):
        self.student_days = ()
        episode = self.episode_id
        if episode:
            self.student_days = episode.episode_days
            self.selected_period = episode.selected_period

    registeration_code = fields.Char(related='student_id.registeration_code', size=12, string='رقم التسجيل', readonly=True)
    student_id         = fields.Many2one('mk.student.register', string="الطالب")
    link_id            = fields.Many2one('mk.link', string="Student link")
    academic_id        = fields.Many2one('mk.study.year',  string='العام الدراسي', related='episode_id.academic_id')
    study_class_id     = fields.Many2one('mk.study.class', string='الفصل الدراسي', related='episode_id.study_class_id')
    registeration_date = fields.Date(default=datetime.today().strftime('%Y-%m-%d'), string='التاريخ')
    period_id = fields.Many2one('mk.periods', string='Period')
    part_id   = fields.Many2many("mk.parts",  string="part", related='student_id.part_id')

    mosq_id      = fields.Many2one('mk.mosque',  string='المسجد', required=True)
    episode_id   = fields.Many2one('mk.episode', string="الحلقة")
    domain_days  = fields.Many2many('mk.work.days', 'mk_student_assign_mk_work_days_rel', 'mk_assign_id', 'mk_work_days_id', string='أيام الحلقة', compute=get_episode_days)
    student_days = fields.Many2many('mk.work.days', 'mk_student_assign_student_days_rel', 'mk_assign_id', 'mk_work_days_id', string='أيام الطالب')

    program_type       = fields.Selection([('open',  'مفتوح'),
                                           ('close', 'محدد')], string="نوع البرنامج", default='open')
    program_id         = fields.Many2one("mk.programs",   string="نوع البرنامج")
    approach_id        = fields.Many2one('mk.approaches', string='البرنامج')

    is_memorize        = fields.Boolean("الحفظ", default=True)
    is_big_review      = fields.Boolean("المراجعة الكبرى", default=True)
    is_min_review      = fields.Boolean("المراجعة الصغرى", default=True)
    is_tlawa           = fields.Boolean('التلاوة')
    state              = fields.Selection([('draft', 'مبدئي'),
                                           ('accept', 'مقبول'),
                                           ('reject', 'مرفوض')], string="State", default='draft')
    selected_period     = fields.Selection([('subh', 'subh'),
                                            ('zuhr', 'zuhr'),
                                            ('aasr', 'aasr'),
                                            ('magrib', 'magrib'),
                                            ('esha', 'esha')], string='period')

    @api.onchange('program_id')
    def onchange_program(self):
        self.approach_id = False
        if self.student_id and not self.student_id.is_student_meqraa:
            program = self.program_id
            if program:
                self.is_tlawa = program.reading
                self.is_big_review = program.maximum_audit
                self.is_min_review = program.minimum_audit
                self.is_memorize = program.memorize

    @api.onchange('episode_id')
    def _get_program_domain(self):
        self.program_id = False
        self.approach_id = False
        program_domain = [('program_type','=','open'),('state','=','active'),('is_required','=',True)]
        if self.episode_id.women_or_men == 'men':
            program_domain += [('program_gender','=','men')]
            return {'value':{'program_id': self.episode_id.program_id,
                             'approache':  self.episode_id.approache_id},
                    'domain':{'program_id': program_domain}}

        if self.episode_id.women_or_men == 'women':
            program_domain += [('program_gender', '=', 'women')]
            return {'value':{'program_id': self.episode_id.program_id,
                             'approache':  self.episode_id.approache_id},
                    'domain':{'program_id': program_domain}}

    @api.onchange('mosq_id')
    def onchange_mosq(self):
        self.episode_id = False
        mosque = self.mosq_id
        episodes = []
        domain = []
        if mosque:
            if self.student_id.is_online_student:
                domain += [('is_online', '=', True)]
            episodes = self.env['mk.episode'].search(domain + [('mosque_id','=',mosque.id),
                                                               ('state','in',['draft','accept'])]).ids
        return {'domain':{'episode_id': [('id', 'in', episodes)]}}

    # @api.one
    def action_reject(self):
        link = self.link_id
        vals = {'student_id':         self.student_id.id,
               'registration_code':   self.registeration_code,
               'registeration_date':  self.registeration_date,
               'academic_id':         self.academic_id.id,
               'study_class_id':      self.study_class_id.id,
               'mosq_id':             self.mosq_id.id,
               'episode_id':          self.episode_id.id,
               'state':              'reject'}
        if link:
            link.write(vals)
        else:
            link = self.env['mk.link'].create(vals)
        student_prepare = self.env['mk.student.prepare'].search([('link_id','=',link.id)])
        if len(student_prepare.ids):
            student_prepare.write({'archived':True})
        link.student_id.write({'active': False})

    # @api.one
    def action_accept(self):
        _logger.info('\n\n +++++++++ action_accept: %s * \n\n', self.episode_id)
        episode = self.episode_id
        student = self.student_id
        selected_period = self.selected_period
        link = self.env['mk.link'].search([('student_id', '=', student.id),
                                           ('episode_id.study_class_id', '=', episode.study_class_id.id),
                                           ('episode_id.active', '=', True),
                                           ('episode_id.state', '=', 'accept'),
                                           ('selected_period', '=', selected_period),
                                           ('state', 'not in', ['done', 'reject', 'cancel'])],limit=1)
        if not episode or not self.student_days or not self.program_id or not self.approach_id:
            raise ValidationError(_('الرجاء تحديد كل بيانات تنسيب الطالب'))
        elif not self.is_tlawa and not self.is_memorize and not self.is_big_review and not self.is_min_review:
            raise ValidationError(_('الرجاء تحديد على الأقل نوع متابعة في اعدادات البرنامج'))
        elif link:
            msg = 'الطالب'
            msg += ' "' + student.display_name + '" '
            msg += 'يدرس في حلقة في نفس الفترة' + ' ! '
            raise ValidationError(msg)
        elif not episode.teacher_id:
            raise ValidationError(_('عذرا ! لابد من اختيار معلم للحلقة أولا'))
        else:
            vals = {'student_id':         student.id,
                    'registration_code':  self.registeration_code,
                    'registeration_date': self.registeration_date,
                    'academic_id':        self.academic_id.id,
                    'study_class_id':     self.study_class_id.id,
                    'mosq_id':            self.mosq_id.id,
                    'episode_id':         episode.id,
                    'is_memorize':        self.is_memorize,
                    'is_min_review':      self.is_min_review,
                    'is_big_review':      self.is_big_review,
                    'is_tlawa':           self.is_tlawa,
                    'selected_period':    selected_period}

            link = self.env['mk.link'].create(vals)
            link.create_student_preparation()
            link.sudo().write({'state': 'accept'})
            has_link = self.env[('mk.link')].search([('id','!=',link.id),('student_id','=',link.student_id.id)], limit=1)
            if not has_link:
                link.student_id.send_passwd()
            return link

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(StudentAssign, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     context = self._context
    #     if context.get('active_model') == 'mk.student.register' and context.get('active_id'):
    #         student = self.env['mk.student.register'].browse(context['active_id'])
    #         student_vals = student.action_request()
    #         if 'domain' in student_vals:
    #             doc = etree.XML(res['arch'])
    #             for node in doc.xpath("//field[@name='episode_id']"):
    #                 node.set('domain', repr(student_vals.get('domain')))
    #                 setup_modifiers(node, res['fields']['episode_id'])
    #             res['arch'] = etree.tostring(doc, encoding='utf-8')
    #     return res