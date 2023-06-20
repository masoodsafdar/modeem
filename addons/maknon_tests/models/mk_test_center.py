# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class MkTestCenter(models.Model):
    _name = 'mak.test.center'
    _inherit=['mail.thread','mail.activity.mixin']
    _rec_name='display_name'

    @api.depends('center_id')
    def cheack_user_logged_in(self):
        for rec in self:
            rec.editable=True

        if self.env.user.has_group('maknon_tests.group_mak_test_center_read') and not self.env.user.has_group('maknon_tests.group_assembly_tests_full') :     
                for rec in self:
                    if rec.main_company==True:
                        if rec.create_date!=False:                        
                            rec.editable=False
                    else:
                        if rec.center_id.id in [self.env.user.department_id.id] or rec.center_id.id in self.env.user.department_ids.ids: 
                            rec.editable=True
                        else:
                            if rec.create_date!=False:
                                rec.editable=False

    @api.depends('gender','name','center_id')
    def _display_name(self):
        result = []
        for record in self:
            if record.center_id.id!=False:
                if record.gender=='male':
                    record.display_name = str(record.name) + '[' + ' ' +str(record.center_id.name)+' ]'+'['+'رجالي'+']'
                else:
                    record.display_name = str(record.name) + '[' + ' ' +str(record.center_id.name)+' ]'+'['+'نسائي'+']'       
            else:   
                if record.gender=='male':                
                    record.display_name = str(record.name) +'['+'رجالي'+']'
                else:
                    record.display_name = str(record.name) +'['+'نسائي'+']'

    academic_id              = fields.Many2one('mk.study.year',  string='Academic Year', ondelete='restrict', required=True, tracking=True)
    study_class_id           = fields.Many2one('mk.study.class', string='Study class',   ondelete='restrict', tracking=True)
    name                     = fields.Char('Center Name', tracking=True)
    company_id               = fields.Many2one('res.company',    string='Company', ondelete='restrict', default=lambda self: self.env['res.company']._company_default_get('mak.test.center'))
    center_id                = fields.Many2one("hr.department",  string='Test Center', tracking=True)
    department_ids           = fields.Many2many("hr.department", string="Departments")
    test_group               = fields.Selection([('student','Students'),
												('employee','Employee')], string="Test Group", default='student', required=True, tracking=True)
    test_names               = fields.Many2many("mk.test.names", string="Tests Names")
    all_branches             = fields.Boolean("ALL branches", default=True, tracking=True)
    branches_ids             = fields.Many2many("mk.branches.master", string="Branches")
    registeration_start_date = fields.Date('Registeration Start Date', tracking=True)
    registeration_end_date   = fields.Date('Registeration End Date', tracking=True)
    exam_start_date          = fields.Date('Exam Start Date',        tracking=True)
    exam_end_date            = fields.Date('Exam End Date',          tracking=True)
    gender                   = fields.Selection([('male','رجالي'),
												('female','نسائي')], string='Gender',     default='male', tracking=True)
    editable                 = fields.Boolean("show", compute='cheack_user_logged_in', default=True,)
    main_company             = fields.Boolean(" تحديد الادارة العامة كمركز رئيسي", tracking=True)
    display_name             = fields.Char("Name", compute="_display_name", store=True)
    active                   = fields.Boolean("active", default=True,  tracking=True)
    
    @api.onchange('city_id')
    def city_id_on_change(self):
        return {'domain':{'district_id':[('area_id', '=', self.city_id.id), 
										 ('enable', '=', True), 
										 ('district_id', '!=', False)]}}
        
    @api.model
    def create(self, vals):
        self.clear_caches()
        return super(MkTestCenter, self).create(vals) 

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.editable==False:
                raise ValidationError(_('عفوا , لاتمتلك صلاحية حذف مركز مستهدف'))

        return super(MkTestCenter, self).unlink()
       
    @api.constrains('registeration_start_date', 'registeration_end_date','exam_start_date','exam_end_date', 'study_class_id.start_date', 'study_class_id.end_date')
    def _check_date(self):
        study_class_start_date = self.study_class_id.start_date
        study_class_end_date = self.study_class_id.end_date

        if self.registeration_start_date < study_class_start_date :
            raise ValidationError(_('عفوا , تاريخ بداية التسجيل لايمكن ان يكون سابق لتاريخ بداية الفصل'))

        elif self.exam_end_date > study_class_end_date:
            raise ValidationError(_('عفوا , تاريخ نهاية الاختبارات لايمكن ان يكون بعد تاريخ نهاية الفصل'))

        elif (self.registeration_start_date > self.exam_start_date):
            raise ValidationError(_('عفوا ,, تاريخ بداية الاختبارات لايمكن ان يكون سابق لتاريخ التسجيل'))
           
        elif (self.registeration_end_date < self.registeration_start_date):
            raise ValidationError(_('عفوا , تاريخ نهاية التسجيل لايمكن ان يكون سابق لتاريخ بداية التسجيل'))
           
        elif (self.registeration_end_date > self.exam_end_date):
            raise ValidationError(_('عفوا , لايمكن ان يستمر التسجيل لما بعد نهاية الاختبارات'))

        elif (self.exam_end_date > study_class_end_date):
            raise ValidationError(_('عفوا , تاريخ نهاية الاختبارات لايمكن ان يستمر لما بعد نهاية الفصل'))
           
    @api.onchange('main_company')
    def main_company_change(self):
        if self.main_company==True:
            self.write({'center_id':False})

    @api.onchange('academic_id')
    def academic_id_change(self):
        if self.academic_id:
            self.study_class_id = False
            return {'domain': {'study_class_id': [ ('study_year_id', '=', self.academic_id.id) ]}}

    @api.model
    def _notify_for_upcoming_test(self):
        tomorrow_date = (date.today() + timedelta(days=1))
        upcoming_tests = self.env['mak.test.center'].search([('exam_start_date', '=', tomorrow_date),])
        for rec in upcoming_tests:
            for department in rec.department_ids:
                for mosque in department.mosque_ids:
                    if mosque.responsible_id.user_id.partner_id:
                        local_context = self.env.context.copy()
                        notif = self.env['mail.message'].create({'message_type': "notification",
                                                                "subtype": self.env.ref("mail.mt_comment").id,
                                                                'body': "الاختبارات التابعة لهذا المركز ستبدأ غدا",
                                                                'subject': "اشعار ببدء تاريخ اختبارات مركز",
                                                                'needaction_partner_ids': [(4, mosque.responsible_id.user_id.partner_id.id)],
                                                                'model': self._name,
                                                                'res_id': rec.id})
                        # send email to mosq supervisor
                        template = self.env['mail.template'].search([('name','=','upcoming_test_mail')], limit=1)
                        if template:
                            local_context['work_email'] = mosque.responsible_id.work_email
                            local_context['company_name'] = mosque.responsible_id.company_id.name
                            local_context['company_email'] = mosque.responsible_id.company_id.email
                            b = template.with_context(local_context).sudo().send_mail(rec.id, force_send=True)
                        for teacher in mosque.teacher_ids:
                            if teacher.user_id.partner_id:
                                local_context = self.env.context.copy()
                                notif = self.env['mail.message'].create({'message_type': "notification",
                                                                        "subtype": self.env.ref("mail.mt_comment").id,
                                                                        'body': "Upcoming test",
                                                                        'subject': "Upcoming test",
                                                                        'needaction_partner_ids': [(4, teacher.user_id.partner_id.id)],
                                                                        'model': self._name,
                                                                        'res_id': rec.id})
                                # send email to mosq supervisor
                                template = self.env['mail.template'].search([('name','=','upcoming_test_mail')], limit=1)
                                if template:
                                    local_context['work_email'] = teacher.work_email
                                    local_context['company_name'] = teacher.company_id.name
                                    local_context['company_email'] = teacher.company_id.email
                                    b = template.with_context(local_context).sudo().send_mail(rec.id, force_send=True)
