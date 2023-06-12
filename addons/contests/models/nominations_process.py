# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import pycompat

import logging
_logger = logging.getLogger(__name__)


class NominationTypes(models.Model):
    _name = 'nomination.process'
    rec_name='name'

    @api.depends('candidate_student','candidate_hr','candidate_outsource','out_source')
    def get_candidate_name(self):
        for rec in self:
            if rec.candidate_student:
                rec.name = rec.candidate_student.student_id.display_name
                
            elif rec.candidate_hr and not rec.out_source:
                    rec.name = rec.candidate_hr.name   
                    
            else:
                rec.name = rec.candidate_outsource
                                
    @api.one
    @api.depends('mosque','mosque_outsource','out_source')
    def get_mosque_name(self):
        mosque_name = False
        out_source = self.out_source
        
        if not out_source:
            mosque_name = self.mosque.name
   
        else:
            mosque_name = self.mosque_outsource
            
        self.mosque_name = mosque_name
        
    @api.one
    @api.depends('episode','episode_outsource','out_source')
    def get_episode_name(self):
        episode_name = False
        out_source = self.out_source
        
        if self.nomination_type == 'student':
            if not out_source:
                episode_name = self.episode.name
       
            else:
                episode_name = self.episode_outsource
            
        self.episode_name = episode_name                        
 
    @api.one
    @api.depends('birthdate')
    def get_age(self):
        birthdate = self.birthdate
        if birthdate:
            delta = datetime.strptime(str(fields.Date.today()),"%Y-%m-%d")-datetime.strptime(str(birthdate),"%Y-%m-%d")
            self.age = int(delta.days/365.25)
            
    request             = fields.Many2one("nomination.request.managment", string="request")
    name                = fields.Char("student name", compute=get_candidate_name)
    out_source          = fields.Boolean("out of company")
    mosque              = fields.Many2one('mk.mosque',   string='mosque')
    episode             = fields.Many2one('mk.episode',  string='episode')
    mosque_outsource    = fields.Char('المسجد')
    episode_outsource   = fields.Char('الحلقة')
    
    ong_name            = fields.Char('الجمعية')
    mosque_name         = fields.Char('المسجد', compute='get_mosque_name',  store=True)
    episode_name        = fields.Char('الحلقة', compute='get_episode_name', store=True)    
        
    candidate_student   = fields.Many2one('mk.link',     string='student name')
    identity_num        = fields.Char("Identitiy number")
    identity            = fields.Many2many("ir.attachment",string="identity")    
    nationality         = fields.Many2one("res.country",string="nationality")
    email               = fields.Char("Email")
    student_phone       = fields.Char("student phone")
    parent_phone        = fields.Char('parent phone')
    birthdate           = fields.Date("birthdate")
    birth_place         = fields.Char("birth place")
    age                 = fields.Integer("Age", compute=get_age, store=True)    
    agree_terms         = fields.Boolean("i agree all terms")
    
    candidate_outsource = fields.Char("employee name")
    candidate_hr        = fields.Many2one('hr.employee', string='employee name',domain=[('category','in',('others','teacher'))])     
    degree              = fields.Many2one("hr.recruitment.degree", string="edud egree")
                 
    nomation_date       = fields.Date("Nomation Date", required=True, default=fields.Date.today())
    nomination_type     = fields.Selection([('student','student'),
                                            ('ref',    'refree'),
                                            ('manager','manager')], string='nomination type', required=True, default='student')
    state               = fields.Selection(string='state', default='draft', selection=[('draft',         'Draft'),
                                                                                       ('accept_admin',  'تصديق الإدارة'),
                                                                                       ('accept_mosque', 'Accept mosque'),
                                                                                       ('accept_center', 'Accept center'),
                                                                                       ('initial_accept','ترشيح اولي'),
                                                                                       ('accept',        'ترشيح نهائي'),
                                                                                       ('reject',        'Reject')])       
    is_quran            = fields.Boolean('is quran')                
    contest             = fields.Many2one('contest.preparation', string='contest',required=False)
    branch              = fields.Many2one('mk.branches.master',  string='Branch')
    track               = fields.Selection([('up',  'من الناس إلى الفاتحة'),
                                            ('down','من الفاتحة إلى الناس')], related='branch.trackk')
    
    previous_contests   = fields.Many2many('contest.preparation', string='previous contests')
            
    test_type           = fields.Many2one('mk.test.names',      string='Test Type', domain=[('is_contest','=', True)])
    test_branches       = fields.Many2one('mk.branches.master', string='Branches')
    
    @api.model
    def create(self, vals):
        nomination = super(NominationTypes, self).create(vals)
        if not nomination.out_source:
            nomination.ong_name = 'جمعية مكنون'
                    
        return nomination
    
    @api.model
    def add_contest_request(self, vals):
        vals.update({'out_source': True})
        contest_request = self.create(vals)
        return contest_request
    
    @api.model
    def get_branches(self, contest_id):
        contest = self.env['contest.preparation'].search([('id','=',contest_id)], limit=1)
        branches = []
        for branche in contest.branches:
            name_branche = ''
            
            if branche.trackk == 'up':
                name_branche = branche.name + " - " + "من الناس إلى الفاتحة"
            else:
                name_branche = branche.name + " - " + "من الفاتحة إلى الناس"
                
            name_branche += " [" + branche.from_surah.name + " - " + branche.to_surah.name + " ]"
                        
            branches += [{'id':   branche.id, 
                          'name': name_branche}]
            
        return branches    
    
    @api.model
    def check_id_validity(self, identification_id):
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

            total += int(temp[0]) + int(temp[1])
            i += 1
            total += int(identification_id[i])
            i += 1
    
        # check if the validation is correct
        if total % 10 != 0:
            return 'عذرا !! رقم الهوية المدخل غير صحيح'
        
        student = self.env['mk.student.register'].sudo().search([('identity_no','=',identification_id)], limit=1)
        
        if student:
            return 'هذه الشاشة مخصصة لتسجيل طلاب من خارج الجمعية'
     
        # return the first digit of the input id
        return 1

    @api.one
    @api.constrains('out_source','identity_num','contest')
    def _check_identification_id(self):
        out_source = self.out_source
        identity_num = self.identity_num
        res = False
        if out_source:
            res = self.check_id_validity(identity_num)
            
        if res and isinstance(res, pycompat.string_types):
            raise ValidationError(res)
        
        else:
            nomination = self.env['nomination.process'].search([('id','!=',self.id),
                                                                ('contest','=',self.contest.id),
                                                                ('identity_num','=',identity_num)], limit=1)
            if nomination:
                raise ValidationError('تم تسجيل صاحب رقم هذه الهوية في هذه المسابقة مسبقا')
                
    @api.onchange('out_source')
    def is_outsource(self):
        if self.out_source==True:
            self.candidate_hr=False
            self.candidate_student=False
            self.birthdate=False
            self.email=False
            self.identity_num=False
            self.degree=False
            self.nationality=False
        else:
            self.candidate_outsource=False
            
    @api.onchange('candidate_student')
    def on_candidate_student(self):
        #self.mosque=self.candidate_student.mosque_id.id
        self.parent_phone=self.candidate_student.student_id.st_parent_id.mobile
        self.birthdate=self.candidate_student.student_id.birthdate
        self.email=self.candidate_student.student_id.email
        self.identity_num=self.candidate_student.student_id.identity_no
        self.nationality=self.candidate_student.student_id.country_id.id
        self.student_phone=self.candidate_student.student_id.mobile

    @api.onchange('candidate_hr')
    def on_candidate_hr(self):
        self.birthdate=self.candidate_hr.birthday
        self.email=self.candidate_hr.work_email
        self.identity_num=self.candidate_hr.identification_id
        self.degree=self.candidate_hr.recruit_ids.id
        self.nationality=self.candidate_hr.country_id.id

    @api.onchange('contest')
    def _get_branches(self):
        if self.contest.is_quran and self.contest.branches:
            return {'domain':{'branch':[('contsets','=', True),
                                        ('id','in', self.contest.branches.ids)]}}    

    @api.onchange('nomination_type')
    def on_nomination_type(self):
        if self.nomination_type=='student':
            self.candidate_hr = False
            
        if self.nomination_type == 'manager' or self.nomination_type=='ref':
            self.candidate_student=False

    @api.onchange('episode')
    def on_episode(self):
        self.candidate_student=False

    @api.onchange('mosque')
    def on_mosque(self):
        episode_ids = self.env['mk.episode'].sudo().search([('mosque_id','=',self.mosque.id)]).ids
        return {'domain':{'episode':[('id', 'in', episode_ids)]}}

    @api.multi
    def reject(self):
        self.write({'state':'reject'})

    @api.multi
    def reject_center(self):
        self.write({'state':'reject'})

    @api.multi
    def reject_mosque(self):
        self.write({'state':'reject'})

    @api.multi
    def accept_mosque(self):
        self.sudo().write({'state':'accept_mosque'})

    @api.multi
    def accept_center(self):
        self.sudo().write({'state':'accept_center'})
        
    @api.multi
    def action_accept_admin(self):
        self.sudo().write({'state':'accept_admin'})

    @api.multi
    def initial_accept(self):
        self.write({'state':'initial_accept'})
        
    @api.multi
    def accept(self):
        self.write({'state':'accept'})  

    @api.constrains('age')
    def check_age(self):
        max_list=[]
        if self.nomination_type == 'student':
            for item in self.contest.Target_age_cat:
                max_list.append(item.to_age)
            if max_list and self.age > max(max_list):
                raise ValidationError(_('عذرا! عمر الطالب اكبر من المسموح به في المسابقة'))
