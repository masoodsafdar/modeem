# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class mk_clearance(models.Model):
    _name='mk.clearance'
    _inherit=['mail.thread','mail.activity.mixin']
    _rec_name="display_name"

    def _getDefault_academic_year(self):
        #self.ensure_one()
        academic_year = self.env['mk.study.year'].sudo().search([('is_default','=',True)], limit=1)          
        return academic_year and academic_year.id or False

    # @api.multi
    def get_study_class(self):
        study_class = self.env['mk.study.class'].sudo().search([('study_year_id', '=', self._getDefault_academic_year()),
                                                                ('is_default', '=', True)], limit=1)
        return study_class and study_class.id or False

    # @api.multi          
    def get_name(self):
        for record in self:
            record.display_name = "خلو طرف" + str(record.id)

    # @api.one
    @api.depends('id_student')
    def get_mosque_student(self):
        id_student = self.id_student
        
        student = False
        if id_student:
            student = self.env['mk.student.register'].sudo().search(['|',('identity_no','=',str(id_student)),
                                                                         ('passport_no','=',str(id_student)),
                                                                     '|', ('active', '=', True),
                                                                          ('active', '=', False)], limit=1)
        
        student_id = False
        mosque_id = False
        name_student = False
        name_mosque = False

        if student:
            student_id = student.id
            name_student = student.display_name

            mosque = student.mosq_id            
            if mosque:
                mosque_id = mosque.id
                name_mosque = mosque.display_name
        self.student = student_id
        self.mosque_id = mosque_id

        self.name_student = name_student
        self.name_mosque = name_mosque

    @api.one
    @api.depends('mosque_to_id')
    def get_name_mosque_to(self):
        mosque = self.mosque_to_id
        name_mosque = False
        if mosque:
            name_mosque = mosque.display_name

        self.name_mosque_to = name_mosque        



    display_name   = fields.Char("Name", compute="get_name")
    mosque_id      = fields.Many2one('mk.mosque',      string='mosque',      required=False, compute=get_mosque_student, store=True)
    year           = fields.Many2one('mk.study.year',  string='Study Year',  readonly=True,                      default=_getDefault_academic_year, tracking=True)
    study_class_id = fields.Many2one('mk.study.class', string='Study class', domain=[('is_default', '=', True)], default=get_study_class,           tracking=True)
    episode_id     = fields.Many2one('mk.episode',     string='Episode',     ondelete='cascade', domain=[('state','=','accept')])
    state          = fields.Selection([('draft',   'Draft'),
                                       ('request', 'إنتظار الرد'),
                                       ('accept',  'Accept'), 
                                       ('reject',  'Reject')], string='الحالة', default='draft', tracking=True)
    student        = fields.Many2one('mk.student.register',   string='Student', required=False, compute=get_mosque_student, store=True)
    
    user_id        = fields.Many2one('res.users', default=lambda self: self.env.user.id, tracking=True)
    id_student     = fields.Char('رقم الهوية / جواز السفر', tracking=True)
    name_student   = fields.Char('الطالب',             compute=get_mosque_student, store=True)
    mosque_to_id   = fields.Many2one('mk.mosque',      string='للإنتقال إلى المسجد', tracking=True)
    name_mosque_to = fields.Char('للإنتقال إلى المسجد', compute=get_name_mosque_to, store=True)
    name_mosque    = fields.Char('من المسجد',          compute=get_mosque_student, store=True)
    date_request   = fields.Date('تاريخ الطلب', default=fields.Date.today(), tracking=True)
    is_same_admin_mosque = fields.Boolean( default=False) #compute='check_is_same_admin_mosque', store=True,
    is_change_admin_mosque = fields.Boolean( dafault=False) #compute='get_admin_mosque_to', store=True,


    _order = "date_request desc"

    # @api.multi
    @api.depends('mosque_to_id','mosque_to_id.mosque_admin_id','user_id.mosque_ids')
    def get_admin_mosque_to(self):
        for rec in self:
            rec.is_change_admin_mosque = not (rec.mosque_to_id.mosque_admin_id.id == rec.user_id.id)

    @api.model
    def cron_admin_mosque_to(self):
        query='''   UPDATE mk_clearance
                    SET is_change_admin_mosque = (SELECT NOT (mk_mosque.mosque_admin_id = mk_clearance.user_id)
                                                  FROM mk_mosque
                                                  WHERE mk_clearance.mosque_to_id = mk_mosque.id); '''
        self.env.cr.execute(query)

    # @api.multi
    @api.depends('mosque_id','mosque_to_id')
    def check_is_same_admin_mosque(self):
        for rec in self :
            if rec.mosque_to_id.mosque_admin_id and rec.mosque_id.mosque_admin_id:
                rec.is_same_admin_mosque = (rec.mosque_id.mosque_admin_id.id == rec.mosque_to_id.mosque_admin_id.id)

    @api.model
    def cron_compute_is_same_admin_mosque(self):
        query=''' UPDATE mk_clearance
                  SET is_same_admin_mosque = (  SELECT (mk_mosque1.mosque_admin_id = mk_mosque2.mosque_admin_id)
                                                FROM mk_mosque mk_mosque1
                                                JOIN mk_mosque mk_mosque2 ON mk_clearance.mosque_id = mk_mosque1.id
                                                                          AND mk_clearance.mosque_to_id = mk_mosque2.id); '''
        self.env.cr.execute(query)


    @api.onchange('name_mosque')
    def oncange_mosque(self):
        return {'domain': {'mosque_to_id': [('id', '!=', self.mosque_id.id)]}}

    # @api.multi
    def action_request(self):
        if not self.sudo().student:
            raise ValidationError('رقم الهوية لا يتبع أي طالب')
        self.write({'state': 'request'})
        if not self.sudo().student.active or not self.sudo().mosque_id or not self.sudo().mosque_id.active:
            self.action_accept()

    # @api.one
    def action_accept(self):
        self.write({'state':'accept'})
        if self.sudo().mosque_id:
            student_link = self.env['mk.link'].sudo().search([('student_id','=',self.student.id),
                                                              ('year','=',self.year.id),
                                                              ('mosq_id','=',self.mosque_id.id),
                                                              ('state','in',['accept','draft'])])
            if student_link:
                student_link.write({'state':       'done',
                                    'action_done': 'clear'})
        
        self.sudo().student.mosq_id = self.sudo().mosque_to_id.id
        if not self.sudo().student.active:
            self.sudo().student.active = True

        responsible = self.mosque_id.sudo().responsible_id.user_id.partner_id
        clearance_id = self.id

        if responsible:
            notif = self.env['mail.message'].sudo().create({'message_type': "notification",
                                                           "subtype": self.env.ref("mail.mt_comment").id,
                                                           'body': "تم قبول طلب اخلاء طرف من مسجدكم",
                                                           'subject': "طلب اخلاء طرف",
                                                           'needaction_partner_ids': [(4, responsible.id)],
                                                           'model': self._name,
                                                           'res_id': clearance_id,
                                                           })

            # send email to mosq supervisor
            template = self.env['mail.template'].search([('name', '=', 'accept_mk_clearance_notify_mail')], limit=1)

            if template:
                b = template.sudo().send_mail(clearance_id, force_send=True)

    # @api.multi
    def action_reject(self):
        self.write({'state':'reject'})
        responsible = self.mosque_id.sudo().responsible_id.user_id.partner_id
        clearance_id= self.id

        if responsible:
            notif = self.env['mail.message'].sudo().create({'message_type': "notification",
                                                            'subtype': self.env.ref("mail.mt_comment").id,
                                                            'body': "تم رفض طلب اخلاء طرف من مسجدكم",
                                                            'subject': "طلب اخلاء طرف",
                                                            'needaction_partner_ids': [(4, responsible.id)],
                                                            'model': self._name,
                                                            'res_id': clearance_id,
                                                           })
            # send email to mosq supervisor
            template = self.env['mail.template'].search([('name', '=', 'reject_mk_clearance_notify_mail')], limit=1)

            if template:
                b = template.sudo().send_mail(clearance_id, force_send=True)

    @api.model
    def add_mk_clearance(self, identification_id, mosque_to_id):
        mosque_to_id = int(mosque_to_id)
        clearance =  False
        student_id = self.env['mk.student.register'].search([('mosq_id', '!=', mosque_to_id),
                                                             '|',('identity_no', '=',str(identification_id)),
                                                                 ('passport_no', '=',str(identification_id)),
                                                             '|', ('active', '=', True),
                                                                  ('active', '=', False)], limit=1)
        if student_id:
            vals = {'id_student': str(identification_id),
                    'mosque_to_id': mosque_to_id,
                    'state': 'request'}

            clearance = self.sudo().create(vals)
        res = clearance and clearance.id or 0
        return res

    @api.model
    def create(self, vals):
        clearance = super(mk_clearance, self).create(vals)
        responsible = clearance.mosque_id.sudo().responsible_id.user_id.partner_id

        if responsible:
            notif = self.env['mail.message'].sudo().create({'message_type': "notification",
                                                                   "subtype": self.env.ref("mail.mt_comment").id,
                                                                   'body': "تم تسجيل طلب اخلاء طرف من مسجدكم",
                                                                   'subject': "طلب اخلاء طرف",
                                                                   'needaction_partner_ids': [(4, responsible.id)],
                                                                   'model': self._name,
                                                                   'res_id': clearance.id,
                                                                   })
            # send email to mosq supervisor
            template = self.env['mail.template'].search([('name', '=', 'add_mk_clearance_notify_mail')], limit=1)

            if template:
                b = template.sudo().send_mail(clearance.id, force_send=True)
        return clearance

    @api.model
    def auto_accept_student_clearance_cron_fct(self):
        limit_date = datetime.now().date() - timedelta(days=3)
        student_clearance_ids = self.env['mk.clearance'].search([('date_request', '<=', limit_date),
                                                                 ('state', '=', 'request')])
        if len(student_clearance_ids) != 0:
            for request in student_clearance_ids:
                try:
                    request.action_accept()
                except:
                    pass