from odoo import models, fields, api
from odoo.tools.translate import _

import logging
_logger = logging.getLogger(__name__)


class transportation_request(models.Model):
    _name = 'transportation.request'  
    _rec_name = 'student_id'
            
    student_id          = fields.Many2one('mk.link',       string='Student')
    transportation_days = fields.Many2many('mk.work.days', string='Days',)
    trans_period        = fields.Selection([('subh',   'subh'),
                                            ('zuhr',   'zuhr'),
                                            ('aasr',   'aasr'),
                                            ('magrib', 'magrib'),
                                            ('esha',   'esha')], string='Transaction Period', )
    transport_type      = fields.Selection([('go&return',   'ذهاب وعودة'),
                                            ('go_only',     'ذهاب فقط'),
                                            ('return_only', 'عودة فقط')])
    payment_voucher     = fields.Many2many('ir.attachment')
    canceling_reason    = fields.Char('Cancling Reason')
    state               = fields.Selection(selection=[('draft',        'Draft'), 
                                                      ('send_request', 'Send Request'), 
                                                      ('approvel',     'Approvel'),
                                                      ('biding',       'Biding'), 
                                                      ('cancle',       'Cancle'), 
                                                      ('stop_transportation', 'Stop transportation')], default='draft')
    latitude            = fields.Char('Latitude')
    longitude           = fields.Char('Longitude')
    
    @api.model
    def create(self, vals):
        transportation_days = vals.get('transportation_days', False)        
        is_from_portal = False
        try:
            transportation_days = transportation_days[0][2]
        except:
            is_from_portal = True
        user = self.env.ref('mk_student_register.portal_user_id')

        if is_from_portal:
            vals.update({'transportation_days': [(6, 0, transportation_days)]})

        trans_request = super(transportation_request, self.sudo(user.id)).create(vals)
        student = trans_request.student_id
         #create notification for mosq supervisor
        mosq_supervisor = student.mosq_id.responsible_id.user_id.partner_id
        if mosq_supervisor:
            notif = self.env['mail.message'].create({'message_type': "notification",
                                                                   "subtype": self.env.ref("mail.mt_comment").id,
                                                                   'body': "تم انشاء طلب نقل جديد",
                                                                   'subject': "طلب نقل جديد",
                                                                   'needaction_partner_ids': [(4, mosq_supervisor.id)],
                                                                   'model': self._name,
                                                                   'res_id': trans_request.id,
                                                                   })
        return trans_request

    @api.onchange('student_id')
    def get_transportation_days(self):
        self.transportation_days = self.student_id.episode_id.episode_days.ids
        self.trans_period = self.student_id.episode_id.selected_period
        self.longitude = self.student_id.student_id.longitude
        self.latitude = self.student_id.student_id.latitude

    @api.one
    def send_request(self):
        fees=0
        obj_general_sending = self.env['mk.general_sending']
        #stud_period=self.env['mk.link'].search([('student.id','=','request_id.id')])
        self.sudo().write({'state':'send_request'})
        if self.transport_type in ['go_only','return_only']:
            fees = self.student_id.mosq_id.one_way_money

        elif self.transport_type == 'go&return':
            fees = self.student_id.mosq_id.double_way_money
            
        if not self.search_vehicle_mosque():
            state = 'biding'
            returned = self.env['mk.general_sending'].send_by_template('mk_biding_transport_request', str(self.id))
            obj_general_sending.send_sms("966"+self.student_id.student_id.mobile,"تم إرسال الطلب و سيتم وضعه في قائمة اﻹحتياطي")
            
        else:
            state = 'draft'
            returned = self.env['mk.general_sending'].send_by_template('mk_accept_transport_request', str(self.id))
            obj_general_sending.send_sms("966"+self.student_id.student_id.mobile,"تم إرسال الطلب , يرجى مراجعة المسجد ﻹكمال إجراءات التسجيل")
            
        transport_management = self.env['mk.transport.management'].sudo().create({'request_id':self.id,'transport_type':self.transport_type,'days_ids':self.student_id.episode_id.episode_days.ids,'period':self.student_id.episode_id.selected_period,'fees':fees,'state':state})

    @api.one
    def approve_request(self):
        self.sudo().write({'state':'approvel'})

    @api.one
    def stop_transportation(self):
        transport_management_model=self.env['mk.transport.management']
        vehicle_rec=transport_management_model.sudo().search([('request_id','=', self.id),('state','=','confirm')])
        
        #biding_recs=self.search([('state','=','biding')],limit=1, order="create_date ascen")
        #to_approve_rec=transport_management_model.search([('request_id','in',biding_recs.ids),('vehicle_id','=',vehicle_rec.id)])
        #if to_approve_rec:
        #    to_approve_rec.request_id.write({'state':approvel})

        vehicle_management=self.env['vehicle.management'].sudo().search([('vehicle_id','=',vehicle_rec.vehicle_id.id)])

        if vehicle_management:
            for rec in vehicle_management:
                vehicle_lines = self.env['vehicle.emanagement.line'].sudo().search([('vehicle_ide','=',rec.id),
                                                                                    ('work_periods','=',self.trans_period),
                                                                                    ('work_days','in',self.transportation_days.ids)])

                for line in vehicle_lines:
                    line.avilable_seats+=1

                self.sudo().write({'state':'stop_transportation'})
                
            vehicle_rec.sudo().write({'state':           'cancle',
                                      'cancling_reason': self.canceling_reason})

    def search_vehicle_mosque(self):
        vehicle_mosq_std  = self.env['vehicle.records'].search([('mosque','=',self.student_id.mosq_id.id)])
        for rec in vehicle_mosq_std:
            vehicle_management=self.env['vehicle.management'].search([('vehicle_id','=',rec.id)])
            if vehicle_management:
                if self.transport_type == 'go_only':
                    search_domain=[('work_periods','=',self.trans_period),
                                   ('work_days','in',self.student_id.episode_id.episode_days.ids),
                                   ('avilable_seats','>',0),
                                   ('go_return','=','go'),
                                   ('vehicle_ide','=',vehicle_management.id)]
                    
                elif self.transport_type == 'return_only':
                    search_domain=[('work_periods','=',self.trans_period),
                                   ('work_days','in',self.student_id.episode_id.episode_days.ids),
                                   ('avilable_seats','>',0),
                                   ('go_return','=','return'),
                                   ('vehicle_ide','=',vehicle_management.id)]
                    
                elif self.transport_type == 'go&return':
                    search_domain=[('work_periods','=',self.trans_period),
                                   ('work_days','in',self.student_id.episode_id.episode_days.ids),
                                   ('avilable_seats','>',0),
                                   ('vehicle_ide','=',vehicle_management.id)]
                    
                vehicle_lines = self.env['vehicle.emanagement.line'].search(search_domain)
                
                if vehicle_lines:
                    if self.transport_type == 'go_only' or self.transport_type == 'return_only' and len(vehicle_lines.ids)==len(self.transportation_days.ids):
                        return True
                    
                    elif self.transport_type == 'go&return' and len(vehicle_lines.ids)==2*len(self.transportation_days.ids):
                        return True
        return False
