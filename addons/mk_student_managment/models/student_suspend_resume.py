#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class mk_student_suspend_and_resume(models.Model):
    _name='mk.student.suspend.resume'
    _rec_name="student"

    def _getDefault_academic_year(self):
        academic_year = self.env['mk.study.year'].search([('active','=',True),
                                                          ('is_default','=',True)])
        if academic_year:
            return academic_year[0].id
        return False

    # @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == "accept":
                raise ValidationError(_('لا يمكنك حذف سجل تم تأكيده'))
            else:
                try:
                    super(mk_student_suspend_and_resume, rec).unlink()
                except:
                    raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))

    @api.onchange('year')
    def get_study_class(self):
        study_class_ids=self.env['mk.study.class'].search([('study_year_id', '=', self.year.id),
                                                           ('is_default', '=', True)])
        if study_class_ids:
            self.study_class_id=study_class_ids[0]
   
    def get_user_id(self):
        masjed=False
        resource = self.env['resource.resource'].search([('user_id','=',self.env.user.id)])
        employee_ids = self.env['hr.employee'].search([('resource_id','in',resource.ids)])
        ###"-----------------",employee_ids
        for rec in employee_ids:
            masjed = rec.department_id.masjed.id
        return masjed
    
    #masjed = fields.Many2one('mk.mosque', string='Masjed')domain="[]"
    masjed         = fields.Many2one('mk.mosque',              string='Masjed',     readonly=True, default=get_user_id, ondelete='restrict')
    year           = fields.Many2one('mk.study.year',          string='Study Year', readonly=True, default=_getDefault_academic_year)
    student        = fields.Many2one('mk.link',                string='Student',     ondelete='restrict')
    episode        = fields.Many2one('mk.episode',             string='Episode',     ondelete='restrict')    
    study_class_id = fields.Many2one('mk.study.class',         string='Study Class', ondelete='restrict', readonly=True)
    suspend_type   = fields.Many2one('mk.suspend.resume.type', string='Type')
    details        = fields.Text(string='Details')
    sus_date       = fields.Date('Date', default=datetime.today().strftime('%Y-%m-%d'))
    state          = fields.Selection([('draft',   'Draft'),
                                       ('suspend', 'Suspended'), 
                                       ('resume',  'Resumed'), 
                                       ('accept',  'Accepted'),
                                       ('reject',  'Rejected')], string='State', default='draft')

    @api.one
    def act_susped(self):
        self.state = 'suspend'

    @api.one
    def act_resume(self):
        self.state = 'resume'
    
    @api.one
    def act_accept(self):
        self.state = 'accept'

    @api.one
    def act_reject(self):
        self.state = 'reject'
        
    @api.one
    def set_draft(self):
        self.state = 'draft'
        
    # @api.multi
    def get_suspend_resume_record(self,student_id):
        student_ids = self.search([('student','=',student_id)])#student is id not string m21
    
        records=[]
        rec_dict={}
        for rec in student_ids:
            links_id = rec.student
            rec_dict = {'Student_id':   rec.student,
                        'Student_name': str(links_id.student_id.display_name).encode('utf-8','ignore'),
                        'episode_id':   links_id.episode_id.id,
                        'Episode_name': str(links_id.episode_id.name).encode('utf-8','ignore'),
                        'Acad_year':    str(rec.year.name).encode('utf-8','ignore'),
                        'Study_class':  str(rec.study_class_id.name).encode('utf-8','ignore'),
                        'Type':         str(rec.suspend_type.name).encode('utf-8','ignore'),
                        'Date':         rec.sus_date,
                        'State':         str(rec.state).encode('utf-8','ignore')}
            records.append(rec_dict)
        return records


class mk_suspend_reume_type(models.Model):
    _name ='mk.suspend.resume.type'
    _rec_name ="name"
    
    name = fields.Char('Type' ,required=True)


class mk_hr_department(models.Model):
    _inherit ='hr.department'
    
    masjed = fields.Many2one('mk.mosque', string='Masjed', ondelete='restrict')

    @api.model
    def get_center(self):
        departments = self.env['hr.department'].search([('active', '=', True)])
        item_list = []
        if departments:
            for department in departments:
                item_list.append({'id': department.id,
                                  'name': department.name})
        return item_list

