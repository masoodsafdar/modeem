# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools import pycompat

from odoo.exceptions import Warning, ValidationError


class mk_supervisor_mosque(models.Model):
    _name = 'mk.supervisor.mosque'
    _description = 'Supervisor'

    # @api.one
    @api.depends('name','second_name', 'third_name', 'fourth_name')
    def _display_name(self):
        first_name = self.name
        second_name = self.second_name
        third_name = self.third_name
        fourth_name = self.fourth_name
        
        display_name = first_name + ' ' + second_name + ' ' + third_name
        if fourth_name:
            display_name += ' ' + fourth_name 

    name               = fields.Char('First Name',   required=True)
    second_name        = fields.Char('Second Name',  required=True)
    third_name         = fields.Char('Third Name',   required=True)
    fourth_name        = fields.Char('Fourth Name')
    display_name       = fields.Char("Name", compute="_display_name", store=True)
    user_id            = fields.Many2one('res.users', string='User')
    mosque_id          = fields.Many2one('mk.mosque', string='Mosque')
    no_identity        = fields.Boolean('No Identity')
    identity_no        = fields.Char('Identity No', size=10)
    passport_no        = fields.Char('Passport No', size=15)
    email              = fields.Char('Email')
    mobile             = fields.Char('Mobile',size=12)
    country_id         = fields.Many2one('res.country', string='Country')
    gender             = fields.Selection([('male', 'Male'),
                                           ('female', 'Female'),],"Gender", default="male")
    job_id             = fields.Many2one('hr.job', string='Job',  domain=[('active', '=', True)])
    marital_status     = fields.Selection([('single',   'Single'),
                                           ('married',  'Married'),
                                           ('widower',  'Widower'),
                                           ('divorced', 'Divorced')], string='Marital status',)
    registeration_code = fields.Char(size=12)
    grade_id           = fields.Many2one('mk.grade', string='Grade', domain=[('active', '=', True)],)
    iqama_expire       = fields.Date('Iqama Expire')
    emam               = fields.Boolean("Emam", default=False)
    state              = fields.Selection([('draft',  'Draft'),
                                           ('accept', 'Accepted'),
                                           ('reject', 'Rejected')], string='State',  default='draft')    
    
    @api.model
    def create(self, vals):
        sequence=self.env['ir.sequence'].get('mk.mosque.supervisor.serial')
        vals['registeration_code'] = sequence
        return super(mk_supervisor_mosque, self).create(vals)

    # @api.one
    def unlink(self):
        if self.state == "accept":
            raise ValidationError(_('لا يمكنك حذف سجل تم تأكيده'))

        try:
            super(mk_supervisor_mosque, self).unlink()
        except:
            raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))    

    # @api.multi
    def act_draft(self):
        self.state = 'draft'

    # @api.multi
    def act_accept(self):
        self.state = 'accept'

    # @api.multi
    def act_reject(self):
        self.state = 'reject'    
    
    @api.model
    def check_id_validity(self, identification_id, employee_id):
        # to trim and is digits
        if not identification_id.isdigit():
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
        
        domain = [('identification_id','=',identification_id)]
        if employee_id:
            domain += [('id','!=',employee_id)]

        employee = self.sudo().search(domain, limit=1)
        if employee:
            return 'عذرا! رقم الهوية موجود مسبقا'
        else:
            domain += [('active','=',False)]
            employee = self.sudo().search(domain, limit=1)
            if employee:
                return 'عذرا! رقم الهوية موجود في الأرشيف'
    
        # return the first digit of the input id
        return 1    
    
    # @api.one
    @api.constrains('identity_no')
    def check_identity_no(self):
        res = self.check_id_validity(self.identity_no, self.id)
        if isinstance(res, pycompat.string_types):
            raise ValidationError(res)
