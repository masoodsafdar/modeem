# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.osv import osv
from odoo.exceptions import Warning, ValidationError
from random import randint
import re

import logging
_logger = logging.getLogger(__name__)


class mk_parent_rigister(models.Model):
    #_name="mk.parent_profile"
    _inherit = "res.partner"
    _description = 'parents profile'
    _rec_name='display_name'
    
    # @api.multi
    def name_get(self):
        result = []
        for record in self:
            second=''
            third=''
            first=''
            fourth=''
            name=''
            if record.name:
                first=str(record.name)
                
            if record.second_name:
                second=str(record.second_name)
                
            if record.third_name:
                third=str(record.third_name)
                
            if first and second and third:
                record.display_name=first+' '+second+' '+ third
                
            if record.fourth_name:
                fourth=str(record.fourth_name)

            name=first+' '+second+' '+ third+' '+fourth

            name = name
            result.append((record.id, name))
            
        return result

    # @api.multi
    @api.depends('name','second_name', 'third_name', 'fourth_name')
    def _display_name(self):
        for rec in self:
            second=''
            third=''
            first=''
            fourth=''
            if rec.name:
                first=str(rec.name)
            if rec.second_name:

                second=str(rec.second_name)

            if rec.third_name:
                third=str(rec.third_name)

            if first and second and third:
                rec.display_name=first+' '+second+' '+ third
                
            if rec.fourth_name:
                fourth= str(rec.fourth_name)

            rec.display_name=first+' '+second+' '+ third+' '+fourth

    def get_default_city(self):
        #return self.env.ref('data_security.City_1').id
        return False
       
    def get_default_country(self):
        return self.env.ref("base.sa").id
       
    def _generate_passwd(self):
        n=4
        range_start = 10**(n-1)
        range_end = (10**n)-1
        gpass=randint(range_start, range_end)
        #obj_general_sending = self.env['mk.general_sending']
        #status=obj_general_sending.send_by_template(template_ext_id,ids)
        return gpass

    passwd                         = fields.Char('Passwd', default=_generate_passwd,)
    property_account_payable_id    = fields.Many2one(required=False,ondelete="restrict")
    property_account_receivable_id = fields.Many2one(required=False,ondelete="restrict")
    
    name               = fields.Char('First Name', required=True)
    display_name       = fields.Char("Name", compute="_display_name", store=True)
    second_name        = fields.Char('Second Name', required=True,)
    third_name         = fields.Char(string='Third Name', required=True)
    fourth_name        = fields.Char('Fourth Name')
    no_identity        = fields.Boolean('No Identity')
    identity_no        = fields.Char('Identity No', size=10)
    passport_no        = fields.Char('Passport No', size=10,)
    mobile             = fields.Char('Mobile', size=9)
    gender             = fields.Selection([('male', 'Male'),
										   ('female', 'Female'),],"Gender", default="male")
    job_id             = fields.Many2one(string='Job', comodel_name='mk.job', domain=[('active', '=', True)], ondelete="restrict",)
    city_id                 = fields.Many2one('res.country.state', string='City',     ondelete="restrict", domain=[('type_location','=','city'), 
                                                                                                               ('enable','=',True)], default=get_default_city)
    area_id                 = fields.Many2one('res.country.state', string='Area',     ondelete="restrict", domain=[('type_location','=','area'), 
                                                                                                               ('enable','=',True)])
    district_id             = fields.Many2one('res.country.state', string='District', ondelete="restrict", domain=[('type_location','=','district'),
                                                                                                             ('enable','=',True)])    
    marital_status     = fields.Selection([('single', 'Single'),
										   ('married', 'Married'),
									       ('widower','Widower'),
									       ('divorced','Divorced')], string='Marital status',)
    mobile_add         = fields.Char(string='second Mobile', size=9)    
    student_ids        = fields.One2many('mk.student.register', 'st_parent_id', string="Parent")    
    country_id         = fields.Many2one(domain=[('active', '=', True)], ondelete="restrict", default=get_default_country)
    banking_accounts   = fields.One2many(comodel_name='account.bank',inverse_name='account_owner', string="banking accounts")
    registeration_code = fields.Char(size=12, readonly=False)
    
    create_uid  = fields.Many2one(readonly=False)
    write_uid   = fields.Many2one(readonly=False)
    create_date = fields.Datetime(readonly=False)
    write_date  = fields.Datetime(readonly=False)
    
    grade_id           = fields.Many2one('mk.grade', string='Grade', domain=[('is_parent','=',True)], ondelete="restrict",)
    iqama_expire       = fields.Date('Iqama Expire')
    company_type       = fields.Selection([('person', 'Individual'),
										('company', 'Company'),
										('parent', 'Parent')], default='parent')
    parent             = fields.Boolean('parent')
    latitude           = fields.Char('Latitude')
    longitude          = fields.Char('Longitude')
    is_student         = fields.Boolean('Is student', default=False)

    _defaults = {'company_type':lambda self, cr, uid, ctx:ctx.get('company_type',False),}
    
    @api.model
    def create(self,values):
        sequence=self.env['ir.sequence'].next_by_code('mk.perant.serial')
        values['registeration_code']=sequence
        values['lang']='ar_SY'
        #values['company_type']='parent'
        return super(mk_parent_rigister, self).create(values) 

    # @api.multi
    def unlink(self):
        if len(self)  > 3:
            raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))
         
        try:
            super(mk_parent_rigister, self).unlink()
        except:
            raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى')) 

    @api.onchange('city_id')
    def city_id_on_change(self):
        return {'domain':{'district_id':[('area_id', '=', self.city_id.id), 
										 ('enable', '=', True), 
										 ('district_id', '!=', False)]}}
        
    # @api.one
    def send_passwd(self):
        email = self.email
        
        if not email:
            raise ValidationError('! يجب إضافة إيميل التواصل ')
        
        n = 4 
        range_start = 10 ** (n - 1)
        range_end = (10 ** n) - 1
        passwd = randint(range_start, range_end)
        
        self.passwd = passwd
                
        template = self.env['mail.template'].search([('name','=','mk_send_pass_parent')], limit=1)
        if template:
            b = template.send_mail(self.id, force_send=True)
            
        message = self.env['mk.sms_template'].search([('code', '=', 'mk_send_pass')],limit=1)
        message = message[0].sms_text
        
        mobile_phone = self.mobile
        if mobile_phone:
            message = re.sub(r'val1', self.passwd, message).strip()
        
            obj_general_sending = self.env['mk.general_sending']
            a = obj_general_sending.send_sms(mobile_phone, str(message))
            
            return a
        
    @api.model
    def reset_password(self, registeration_code):
        user = self.env.ref('mk_student_register.portal_user_id')

        n = 4 
        range_start = 10 ** (n - 1)
        range_end = (10 ** n) - 1
        passwd = randint(range_start, range_end)   
        
        template = False     
        mobile_phone = False
        
        parent_student = self.sudo().search([('registeration_code','=',registeration_code)], limit=1)
        if not parent_student:
            parent_student = self.sudo().search([('identity_no','=',registeration_code)], limit=1)
            
        if parent_student:
            email = parent_student.email
            
            if not email:
                return {'result': '! يجب إضافة إيميل التواصل لولي الأمر'}
            
            parent_student.sudo(user.id).passwd = passwd
            template = self.env['mail.template'].search([('name','=','mk_send_pass_parent')], limit=1)
            b = template.send_mail(parent_student.id, force_send=True)
            
            mobile_phone = parent_student.mobile
        
        else:
            student = self.env['mk.student.register'].sudo().search([('registeration_code','=',registeration_code)], limit=1)
            
            if not student:
                student = self.env['mk.student.register'].sudo().search([('identity_no','=',registeration_code)], limit=1)
                
            if student:
                email = student.email
                
                if not email:
                    return {'result': '! يجب إضافة إيميل التواصل للطالب'}
                
                student.sudo(user.id).passwd = passwd
                template = self.env['mail.template'].search([('name','=','mk_send_pass_student')], limit=1)
                b = template.send_mail(student.id, force_send=True)
                
                mobile_phone = student.mobile
                            
        if mobile_phone:
            try:
                message = self.env['mk.sms_template'].search([('code', '=', 'mk_send_pass')], limit=1)
                message = message[0].sms_text
    
                message = re.sub(r'val1', str(passwd), message).strip()
    
                obj_general_sending = self.env['mk.general_sending']
                a = obj_general_sending.sudo(user.id).send_sms(mobile_phone, str(message))
            except:
                pass
            
        if parent_student:
            return {'result': 1}
        
        elif student:
            return {'result': 2}
        
        else:
            return {'result': 'رقم التسجيل أو الهوية غير مسجل'}

    @api.model
    def login_user(self, registeration_code, passwd):
        parent_student = self.sudo().search([('passwd','=',passwd),
                                             '|',('registeration_code','=',registeration_code),
                                             ('identity_no','=',registeration_code)], limit=1)
        if parent_student:
            return {'parent_id': parent_student.id,
                    'display_name': parent_student.display_name}
        
        return {'parent_id': 0,}


class banking_account(models.Model):
    _name = 'account.bank'
    _description = 'Bank accounts'
    
    account_owner      = fields.Many2one('res.partner',         string="Account owner",                                      ondelete="cascade")
    student_id         = fields.Many2one('mk.student.register', string="Account owner", domain=[('is_student', '=', False)], ondelete="cascade")
    bank_id            = fields.Many2one('res.bank',            string="Bank",          domain=[('active', '=', True)],      ondelete="restrict")
    identity_no        = fields.Char(string='Identity No', size=10)
    account_no         = fields.Char()
    state              = fields.Selection([('enabled', 'Enabled'), 
                                           ('disabled', 'Disabled')], string='state')
    account_owner_name = fields.Char('Account owner name',)
