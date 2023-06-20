# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.osv import osv
from odoo.exceptions import Warning, ValidationError

# Class MK Student Register
# class mk_student_rigister(models.Model):
#     _name = 'mk.student.register'
#     _description = 'Students Register'
            
    # def _getDefault_academic_year(self):
    #     academic_recs = self.env['mk.academic_year'].search([('is_default','=',True)])       
    #     if academic_recs:
    #         return academic_recs[0].id
                  
    #     return False            
            
    # second_name = fields.Char('Second Name', required=True)
    # third_name  = fields.Char('Third Name',  required=True)
    # forth_name  = fields.Char('Forth Name')
    # part_id     = fields.Many2many("mk.parts", string="part")
    # p_image     = fields.Binary('Image')
    # identity_no = fields.Integer('Identity No')
    # passport_no = fields.Char('Passport No', size=15)
    # mobile      = fields.Char('mobile', size=9)
    # email       = fields.Char('Email',  size=40)    
    # parent_tel  = fields.Integer('Parent Tel')
    # birth_date  = fields.Date('Birth Date')
    # job_id      = fields.Many2one('mk.job', string='Job', required=True)
    # gender      = fields.Selection([('male',   'Male'), 
    #                                 ('female', 'Female')], string="Gender", default="male")
    # country_id  = fields.Many2one('res.country')
    # area_id     = fields.Many2one('mk.area',     string='area')
    # city_id     = fields.Many2one('mk.city',     string='city')    
    # district_id = fields.Many2one('mk.district', string='district')
    # children_no = fields.Integer('children nunmber')
    # link_ids    = fields.Many2many('mk.link.student','mk_link_student_mk_student_register_rel','mk_student_register_id','mk_link_student_id', string = 'Student' )    
    # grade_id    = fields.Many2one('mk.grade',         string='Grade', required=True)
    # academic_id = fields.Many2one('mk.academic_year', string='Academic Year', readonly=True, default=_getDefault_academic_year)
    # note        = fields.Text('Note')
    # state       = fields.Selection([('draft',    'Draft'), 
    #                                 ('revised',  'Revised'),
    #                                 ('accepted', 'Accepted'),
    #                                 ('rejected', 'Rejected'),
    #                                 ('done',     'Done')], string='State')

    # category       = fields.Selection([('teacher',    'Teacher'), 
    #                                 ('supervisor',  'Supervisor')], string='Cateqory') 
    # is_student_meqraa = fields.Boolean(string="Is Student Meqraa")
        
    # def _auto_init(self, cr, context=None):
    #     result = super(mk_student_rigister, self)._auto_init(cr, context=context)
    #     cr.execute("""
    #     ALTER TABLE mk_student_register DROP CONSTRAINT IF EXISTS mk_student_register_city_id_fkey;
    #     ALTER TABLE public.mk_student_register
    #     ADD CONSTRAINT mk_student_register_city_id_fkey FOREIGN KEY (city_id)
    #     REFERENCES public.res_country_state (id) MATCH SIMPLE
    #     ON UPDATE NO ACTION ON DELETE RESTRICT;
    #     """)
        
    #     return result
    
    # @api.v7
    # def get_concat(self, cr, uid, ids, context=None):
    #     x={}
    #     ctr = self.pool.get('res.country')
    #     brw = ctr.browse(cr, uid, ids, context=context)
    #     for record in brw:
    #         x[record.id] = "%s--%s" % ( str(record.name), str(record.code))
            
    #     return x

    # # @api.multi
    # def accept_request(self):        
    #     if not self.parent_tel and self.p_country_id.phone_code:
    #         raise Warning(_('please insert parent phone number and country phone code'))
        
    #     else:
    #         if len(str(self.parent_tel))!=9:
    #             raise Warning(_('phone number of parent must contain 9 digits'))
            
    #         if str(self.parent_tel)[0]== '0':
    #             raise Warning(_('phone number must not be 0 at first digit')) 

    #         if len(str(self.p_country_id.phone_code))!=3:
    #             raise Warning(_('country code must contain 3 digits'))

    #         self.write({'state': 'draft'})

    #     return True
       
    # # @api.multi
    # def revise_registration(self):
    #     resource = self.env['resource.resource'].search([('user_id','=',self.env.user.id)])
    #     if resource.ensure_one():
    #         employee_id = self.env['hr.employee'].search([('resource_id','=',resource.id)])
    #         if not employee_id:
    #             raise Warning(_('you do not have permission to do this operation'))
            
    #         else:
    #             if self.email:
    #                 msjd_id=self.env['mk.masjed'].search([('supervisor', '=',employee_id.id)])
    #                 if msjd_id:
    #                     msjd_name=msjd_id.name
    #                     msjd_name=msjd_name.encode('utf-8','ignore')

    #                     email_message='شكرا لتسجيلكم بمسجد %s سيتم إشعاركم قريبا بعد مراجعة طلبكم' %msjd_name
    #                     decoded_mess=email_message.decode("utf-8")

    #                     values = {'subject': 'Student registration ',
    # 	                          'body_html': decoded_mess,
    # 	                          'email_to': self.email}
                        
    #                     self.env['mk.general_sending'].send(values)

    #             to=self.env['mk.general_sending'].get_phone(self.parent_tel, self.p_country_id)

    #             message= "تم تلقي طلبكم وسيتم اشعاركم بعد مراجعته".decode("utf-8")
    #             if to:
    #                 self.env['mk.general_sending'].send_sms(to, message)
                    
    #             self.write({'state': 'revised'})

    #             return True

    # # @api.multi
    # def action_accept(self):
    #     resource = self.env['resource.resource'].search([('user_id','=',self.env.user.id)])
    #     employee_id = self.env['hr.employee'].search([('resource_id','=',resource.id)])
        
    #     if not employee_id:
    #         raise Warning(_('you do not have permission to do this operation'))
        
    #     else:            
    #         msjd_id=self.env['mk.masjed'].search([('supervisor', '=',employee_id.id)])
    #         if msjd_id:
    #             msjd_name=msjd_id.name
        
    #     if msjd_name:
    #         msjd_name=msjd_name.encode('utf-8','ignore')
    #         email_message='تم قبول طلب التسجيل بمسجد %s نرجو التوجه للمسجد ﻹستكمال عملية التسجيل  و شكرا ﻹهتمامكم' %msjd_name
    #         decoded_mess=email_message.decode("utf-8")

    #         values = {'subject': 'Student registration ',
    #     		      'body_html': decoded_mess,
    #     		      'email_to': self.email,}
    #         #---------------------------------------------------------------
    #         self.env['mk.general_sending'].send(values)

    #         to=self.env['mk.general_sending'].get_phone(self.parent_tel, self.p_country_id)
        
    #         if to:        
    #             message= "تم قبول تسجيلكم نرجو التوجه للمسجد لاكمال التسجيل".decode("utf-8")
    #             self.env['mk.general_sending'].send_sms(to, message)
                
    #     self.write({'state': 'accepted'})
        
    #     return True

    # # @api.multi
    # def action_reject(self):
    #     resource = self.env['resource.resource'].search([('user_id','=',self.env.user.id)])
    #     employee_id = self.env['hr.employee'].search([('resource_id','=',resource.id)])
        
    #     if not employee_id:
    #         raise Warning(_('you do not have permission to do this operation'))
        
    #     else:            
    #         msjd_id=self.env['mk.masjed'].search([('supervisor', '=',employee_id[0].id)])
    #         if msjd_id:
    #             msjd_name=msjd_id.name

    #     if msjd_name:
    #         msjd_name=msjd_name.encode('utf-8','ignore')
    #         email_message='نشكر لكم إهتمامكم بالتسجيل و يعتذر مسجد %s عن قبول طلبكم و شكرا' %msjd_name
    #         decoded_mess=email_message.decode("utf-8")

    #         values = {'subject': 'Student registration ',
    #                   'body_html': decoded_mess,
    #                   'email_to': self.email,}
    #         self.env['mk.general_sending'].send(values)
            
    #         to = self.env['mk.general_sending'].get_phone(self.parent_tel, self.p_country_id)
    #         if to:                
    #             sms_partner_obj = self.pool.get('partner.sms.send')
    #             message= "نعتذر عن قبول طلبكم و شكرا".decode("utf-8")
    #             self.env['mk.general_sending'].send_sms(to, message)
                
    #     self.write({'state': 'rejected'})
        
    #     return True

    # # @api.multi
    # def action_cancel(self):
    #     pass

    # # @api.one
    # def unlink(self):
    #     try:
    #         super(mk_student_rigister, self).unlink()
    #     except:
    #         raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))


class mk_parent_rigister(models.Model):
    _name = 'mk.parent.register'
    _description = 'Parents Register'

    @api.depends('first_name','second_name', 'third_name', 'forth_name')
    def __getname(self):
        for record in self:
            record.name = record.first_name + ' ' + record.second_name + ' ' + record.third_name
            
    name           = fields.Char('Student Name', compute=__getname, size=50, translate=True)
    no_identity    = fields.Boolean('No Identity')
    first_name     = fields.Char('First Name',  required=True)
    second_name    = fields.Char('Second Name', required=True)
    third_name     = fields.Char('Third Name',  required=True)
    forth_name     = fields.Char('Forth Name')
    # country_id     = fields.Many2one('res.country', compute="get_concat()")
    country_id     = fields.Many2one('res.country')
    parent_tel     = fields.Char('mobile', size=9)
    email          = fields.Char('Email',  size=40)
    identity_no    = fields.Integer('Identity No')
    passport_no    = fields.Char('Passport No', size=15)
    birth_date     = fields.Date('Birth Date')
    gender         = fields.Selection([('male',   'Male'), 
                                       ('female', 'Female')], string="Gender", default="male")
    job_id         = fields.Many2one('hr.job', string='Job')
    marital_status = fields.Selection([('single',   'Single'), 
                                       ('married',  'Married'),
                                       ('widower',  'Widower'),
                                       ('divorced', 'Divorced')], string='Marital status')
    grade_id = fields.Many2one('mk.grade', string='Grade')
    

class banking_account(models.Model):
    _name = 'account.bank'
    _description = 'Bank accounts'
        
    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """

    student_register_id = fields.Many2one('mk.student.register', ondelete='cascade')
    bank_id             = fields.Many2one('res.bank')


class mk_link_student(models.Model):
    _name = 'mk.link.student'
    _description = 'Link Student With Stage'
    _rec_name = 'name_stage_id'

    name_stage_id = fields.Many2one('mk.stage',   string='Name Stage')
    remain_num    = fields.Integer('Remaining number', compute='total_student')
    level_id      = fields.Many2one('mk.levels',  string='Levels')
    level2_ids    = fields.Many2many('mk.levels', string='Field Label')
    student_ids   = fields.Many2many('mk.student.register', 'mk_link_student_mk_student_register_rel', 'mk_link_student_id', 'mk_student_register_id', string = 'Student')
    category = fields.Selection([
        ('teacher', 'Teacher'),
        ('supervisor', 'Supervisor')
    ], string="Category",tracking=True)
        
    @api.onchange('name_stage_id')
    def onchange_name_stage(self):
        res = []
        if self.name_stage_id:
            self.remain_num = self.name_stage_id.max_number
            res = {'domain':{'level_id': [('id', 'in', self.name_stage_id.level_ids.ids)]}}
            
        return res

    # @api.multi
    def save_student(self):
        obj_level = self.env['level.student']
        obj_level.create({'level_id': self.level_id.id,
                          'student_ids': [(6, 0,[y.id for y in self.student_ids])],
                          'name': self.id})

    @api.onchange('level_id')
    def onchange_name_level(self):
        if self.level_id:
            #onchange remain number
            self.remain_num = self.name_stage_id.max_number
            obj_leve = self.env['level.student']
            lev_search = obj_leve.search([('level_id', '=', self.level_id.id)])
            list1 = []
            for rec in lev_search:
                for student in rec.student_ids:

                    list1.append(student.id)
            self.student_ids = list1
    
    # @api.one
    @api.depends('student_ids')
    def total_student(self):
        student = []
        count = 0
        max_num = self.name_stage_id.max_number
        for rec in self:
            for student in rec.student_ids.ids:
                count = count+1
            rec.remain_num = max_num - count
               

class mk_link_student_new(models.Model):
    _name = 'mk.link.student.new'
    _description = 'Link Student With Stage'
    _rec_name = 'name_stage_id'

    name_stage_id = fields.Many2one('mk.stage',   string='Name Stage')    
    level_id      = fields.Many2one('mk.levels',  string='Levels')
    level2_ids    = fields.Many2many('mk.levels', string='Field Label')
    remain_num    = fields.Integer('Remaining number', compute='total_student')
    student_ids   = fields.Many2many('mk.student.register', 'mk_link_student_mk_student_register_rel_new','mk_link_student_id', 'mk_student_register_id', string='Student')
        
    @api.onchange('name_stage_id')
    def onchange_name_stage(self):
        res = []
        if self.name_stage_id:
            self.remain_num = self.name_stage_id.max_number
            res = {'domain':{'level_id': [('id', 'in', self.name_stage_id.level_ids.ids)]}}
            
        return res

    # @api.multi
    def save_student(self):
        obj_level = self.env['mk.link.student']
        if self.remain_num < 0:
            raise osv.except_osv(_('Error !'), _('Number of Students Biger than remain number'))
        
        else:
            obj_level.create({'level_id': self.level_id.id,
                              'student_ids': [(6, 0,[y.id for y in self.student_ids])],
                              'name': self.id,
                              'name_stage_id':self.name_stage_id.id})

    @api.onchange('level_id')
    def onchange_name_level(self):
        if self.level_id:
            self.remain_num = self.name_stage_id.max_number
            obj_leve = self.env['mk.link.student']
            lev_search = obj_leve.search([('level_id', '=', self.level_id.id)])
            list1 = []
            for rec in lev_search:
                for student in rec.student_ids:
                    list1.append(student.id)
            self.student_ids = list1
    
    # @api.one
    @api.depends('student_ids')
    def total_student(self):
        student = []
        count = 0
        max_num = self.name_stage_id.max_number
        for rec in self:
            for student in rec.student_ids.ids:
                count = count+1
            rec.remain_num = max_num - count


class level_student(models.Model):
    _name = 'level.student'
    _description = 'Level Student'
    
    name        = fields.Many2one('mk.link.student',      string='Student') 
    level_id    = fields.Many2one('mk.levels',            string='level')
    student_ids = fields.Many2many('mk.student.register', string='Student')  
