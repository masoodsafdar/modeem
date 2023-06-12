#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _


class mk_courses_evalution(models.Model):
    _name = 'mk.course.calibration'
    _inherit = ['mail.thread']
    _rec_name = 'display_name'

    @api.multi
    def get_display_name(self):
        for rec in self:
            rec.display_name = rec.course_id.course_name + " / " + rec.type_course_id.name

    @api.depends('standards_id')
    def _get_total(self):
        total=0
        for standard in self.standards_id:
            total += standard.due
            
        self.update({'total':total})

    students_no    = fields.Integer('Students no', required=True, track_visibility='onchange')
    teachers_no    = fields.Integer('Teachers no', required=True, track_visibility='onchange')
    subh           = fields.Boolean('Subah', track_visibility='onchange')
    zaher          = fields.Boolean('Zaher', track_visibility='onchange')
    asor           = fields.Boolean('Asor', track_visibility='onchange')
    esha           = fields.Boolean('Esha', track_visibility='onchange')
    mog            = fields.Boolean('mogreb', track_visibility='onchange')
    type_course_id = fields.Many2one('mk.types.courses', string='نوع الدورة', required=True, track_visibility='onchange')
    mosque_ids     = fields.Many2many('mk.mosque')
    mosque_id      = fields.Many2one('mk.mosque', string='المسجد/المدرسة', required=True, track_visibility='onchange')
    course_id      = fields.Many2one('mk.course.request', string='Course', required=True, ondelete='cascade', track_visibility='onchange')
    total          = fields.Integer('Total', compute=_get_total, track_visibility='onchange')
    state          = fields.Selection([('draft',  'Draft'), 
                                       ('accept', 'Accept'),
                                       ('reject', 'Reject')], default='draft', string='State', track_visibility='onchange')
    standards_id   = fields.One2many('mk.course.calibration.standard', 'calibration_id', string='standards')
    display_name   = fields.Char(compute="get_display_name", string="Name")

    @api.onchange('type_course_id')
    def on_change_type_course_id(self):
        type_course = self.type_course_id
        self.mosque_id = False
        self.course_id = False
        self.mosque_ids = ()
        mosque_ids = []
        if type_course:
            courses = self.env['mk.course.request'].search([('mosque_id','!=',False),
                                                            ('state','=','accept'),
                                                            ('course','=',type_course.id)])
            mosque_ids = [course_request.mosque_id.id for course_request in courses]
            
        self.mosque_ids = mosque_ids
        
    @api.onchange('mosque_id')
    def on_change_mosque_id(self):
        self.course_id = False        

    @api.onchange('course_id')
    def on_change_course_id(self):
        course = self.course_id
        
        students_no = 0
        teachers_no = 0
        
        subh = False
        zaher = False
        asor = False
        mog = False
        esha = False
        
        if course:
            if course.subh:
                subh = True
              
            if course.zaher:
                zaher = True
                
            if course.asor:
                asor = True

            if course.mogreb:
                mog = True
                
            if course.esha:
                esha = True  
               
            students_no = course.no_student
            teachers_no = course.no_teacher
            
        self.students_no = students_no
        self.teachers_no = teachers_no
        
        self.subh = subh
        self.zaher = zaher
        self.asor = asor
        self.mog = mog
        self.esha = esha            

    @api.multi
    def draft_validate(self):
        self.write({'state':'draft'})
        
    @api.multi
    def reject_validate(self):
        self.write({'state':'reject'})
        
    @api.multi
    def accept_validate(self):
        self.write({'state':'accept'})


