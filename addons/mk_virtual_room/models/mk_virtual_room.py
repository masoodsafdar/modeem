# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning, ValidationError
import logging
_logger = logging.getLogger(__name__)


class mk_virtual_room_provider(models.Model):
    _name = 'mk.virtual_room.provider'
    _description = 'Virtual room provider'
    _inherit =  ['mail.thread', 'mail.activity.mixin']
    
    name                     = fields.Char('Name', track_visibility='onchange', required=True)  
    type_subscription        = fields.Selection([('server','Server'),
                                                 ('room', 'Room')], string='Type subscription',                                  track_visibility='onchange', required=True)
    virtual_room_package_ids = fields.One2many('mk.virtual_room.provider.package', 'virtual_room_provider_id', string='Package', track_visibility='onchange', required=True)


class mk_virtual_room_provider_package(models.Model):
    _name = 'mk.virtual_room.provider.package'
    _description = 'Virtual room provider package'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.one
    @api.depends('virtual_room_provider_id','type_subscription_duration')
    def get_name_package(self):
        type_subscription_duration = self.type_subscription_duration
        if type_subscription_duration == 'month':
            type_subscription_duration = 'شهر'
        elif type_subscription_duration == 'two_months':
            type_subscription_duration = 'شهرين'
        elif type_subscription_duration == 'three_months':
            type_subscription_duration = 'ثلاثة أشهر'
        elif type_subscription_duration == 'four_months':
            type_subscription_duration = 'أربعة أشهر فصل دراسي'
        elif type_subscription_duration == 'eight_months':
            type_subscription_duration = 'ثمانية أشهر سنة دراسية'
        elif type_subscription_duration == 'full_year':            
            type_subscription_duration = 'إثنا عشر شهرا سنة كاملة'
        else:
            type_subscription_duration = ''
            
        self.name = 'باقة' + ' ' + (self.virtual_room_provider_id.name or '') + ' '+ type_subscription_duration
        
    name                       = fields.Char(compute=get_name_package, default='Package', store=True)
    virtual_room_provider_id   = fields.Many2one('mk.virtual_room.provider', string='Virtual room provider', track_visibility='onchange', required=True)  
    type_subscription_duration = fields.Selection([('month',        'Month'),
                                                   ('two_months',   'Two months'),
                                                   ('three_months', 'Three months'),
                                                   ('four_months',  'Four-month semester'),
                                                   ('eight_months', 'Eight-month academic year'),
                                                   ('full_year',    'full year is twelve months'),], string='Type subscription', track_visibility='onchange', required=True)  
    number_room                = fields.Integer('Number room',         track_visibility='onchange', required=True)  
    number_participant         = fields.Integer('Number participants', track_visibility='onchange', required=True)  
    cost                       = fields.Float('Cost',                  track_visibility='onchange', required=True)  

        
class mk_virtual_room_subscription(models.Model):
    _name = 'mk.virtual_room.subscription'
    _description = 'Virtual room subscription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    @api.one
    @api.depends('virtual_room_package_id')
    def get_package_detail(self):
        virtual_room_package = self.virtual_room_package_id
        number_participant = 0
        cost = 0
        type_subscription_duration = False
        if virtual_room_package:
            number_participant = virtual_room_package.number_participant
            cost = virtual_room_package.cost
            type_subscription_duration = virtual_room_package.type_subscription_duration
            
        self.number_participant = number_participant
        self.cost = cost
        self.type_subscription_duration = type_subscription_duration
        
    @api.one
    @api.depends('mosque_id','virtual_room_package_id','date_start')
    def get_name_subscription(self):
        self.name = 'إشتراك' + ' ' + self.mosque_id.name + ' '+ self.virtual_room_package_id.name + ' ' + self.date_start
         
    name                       = fields.Char('Name', default='إشتراك', compute=get_name_subscription, store=True)  
    mosque_id                  = fields.Many2one('mk.mosque',                        string='Mosque',                track_visibility='onchange', required=True, ondelete='cascade')
    virtual_room_provider_id   = fields.Many2one('mk.virtual_room.provider',         string='Virtual room provider', track_visibility='onchange', required=True)
    virtual_room_package_id    = fields.Many2one('mk.virtual_room.provider.package', string='Virtual room package',  track_visibility='onchange', required=True)   
    type_subscription_duration = fields.Selection([('month',        'month'),
                                                   ('two_months',   'Two months'),
                                                   ('three_months', 'Three months'),
                                                   ('four_months',  'Four-month semester'),
                                                   ('eight_months', 'Eight-month academic year'),
                                                   ('full_year',    'full year is twelve months')], string='Type subscription', compute=get_package_detail, store=True)
    number_participant         = fields.Integer('Number participants', compute=get_package_detail, store=True)  
    cost                       = fields.Float('Cost',                  compute=get_package_detail, store=True)  
    date_start                 = fields.Date('Date start', track_visibility='onchange', required=True)
    date_end                   = fields.Date('Date End',   track_visibility='onchange', required=True)    
    note                       = fields.Text('Note', track_visibility='onchange')  
    type_payment_method        = fields.Selection([('from_account', 'withdraw from Account'),
                                                   ('cash_deposit', 'Cash deposit')], string='Payment method', track_visibility='onchange') 
    bank_id                    = fields.Many2one('res.bank', string="Bank", track_visibility='onchange') 
    number_account             = fields.Char('Bank account number',      track_visibility='onchange') 
    attachment                 = fields.Many2many('ir.attachment', string='Attachement')
    state                      = fields.Selection([('draft',           'Draft'),
                                                   ('under_procedure', 'Under the procedure'),
                                                   ('confirm',         'confirm'),
                                                   ('refused',         'Refused')], string='State', default='draft', track_visibility='onchange')   

    @api.multi
    def action_under_procedure(self):
        type_payment_method = self.type_payment_method
        bank_id = self.bank_id
        number_account = self.number_account
        
        if not type_payment_method:
            raise ValidationError(_('Please confirm the payment method!')) 
        elif not bank_id:
            raise ValidationError(_('Please check with the bank!')) 
        elif not number_account:
            raise ValidationError(_('Please verify the bank account number!')) 
        
        self.write({'state': 'under_procedure'})

    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirm'})

    @api.multi
    def action_refused(self):
        self.write({'state': 'refused'})

    @api.onchange('date_start','virtual_room_package_id')
    def get_date_end(self):
        date_start = self.date_start
        type_subscription_duration = self.type_subscription_duration

        if date_start: 
            if type_subscription_duration == 'month':
                date_end = datetime.datetime.strptime(date_start, '%Y-%m-%d') + relativedelta(months=1)
            elif type_subscription_duration == 'two_months':
                date_end = datetime.datetime.strptime(date_start, '%Y-%m-%d') + relativedelta(months=2)
            elif type_subscription_duration == 'three_months':
                date_end = datetime.datetime.strptime(date_start, '%Y-%m-%d') + relativedelta(months=3)
            elif type_subscription_duration == 'four_months':
                date_end = datetime.datetime.strptime(date_start, '%Y-%m-%d') + relativedelta(months=4)
            elif type_subscription_duration == 'eight_months':
                date_end = datetime.datetime.strptime(date_start, '%Y-%m-%d') + relativedelta(months=8)
            else:
                date_end = datetime.datetime.strptime(date_start, '%Y-%m-%d') + relativedelta(months=12)
            self.date_end = date_end


class mk_virtual_room(models.Model):
    _name = 'mk.virtual_room'
    _description = 'Virtual Room'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('virtual_room_subscription_id')
    def get_subscription(self):
        for room in self:
            subscription = room.virtual_room_subscription_id
            room.mosque_id = subscription.mosque_id.id
            room.virtual_room_provider_id = subscription.virtual_room_provider_id.id
            room.virtual_room_package_id = subscription.virtual_room_package_id.id
            
    name                           = fields.Char('Name', track_visibility='onchange', required=True)  
    virtual_room_subscription_id   = fields.Many2one('mk.virtual_room.subscription',     string='Virtual room subscription', track_visibility='onchange', required=True, ondelete='cascade')
    virtual_room_provider_id       = fields.Many2one('mk.virtual_room.provider',         string='Virtual room provider',     compute=get_subscription)
    virtual_room_package_id        = fields.Many2one('mk.virtual_room.provider.package', string='Virtual room package',      compute=get_subscription)      
    type_room_id                   = fields.Many2one('mk.virtual_room.type',             string='Room Type', track_visibility='onchange', required=True) 
    mosque_id                      = fields.Many2one('mk.mosque',                        string='Mosque',    compute=get_subscription) 
    room_objective                 = fields.Char('Room objective',               track_visibility='onchange', required=True)  
    admin_link                     = fields.Char('Admin link',                   track_visibility='onchange', required=True)  
    participant_link               = fields.Char('Participant link',             track_visibility='onchange', required=True)  
    date_expiration                = fields.Date('Subscription expiration date', track_visibility='onchange', required=True)
    state                          = fields.Selection([('draft',   'Draft'),
                                                       ('confirm', 'Confirm'),
                                                       ('stopped', 'Stopped')], string='State', default='draft', track_visibility='onchange')   

    @api.onchange('virtual_room_provider_id')
    def get_package(self):
        self.virtual_room_package_id = False 

    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirm'})

    @api.multi
    def action_stopped(self):
        self.write({'state': 'stopped'})
        
    @api.onchange('virtual_room_subscription_id')
    def get_date_expiration(self):
        self.date_expiration = self.virtual_room_subscription_id.date_end

    @api.model
    def link_virtual_room(self, episode_id):

        query_string = ''' 
             SELECT vr.id,
             vr.name,
             vr.admin_link,
             vr.participant_link,
             e.time_from,
             e.time_to

             FROM mk_episode e
             LEFT JOIN mk_virtual_room vr on e.virtual_room_id = vr.id

             WHERE e.id={};
             '''.format(episode_id)

        self.env.cr.execute(query_string)
        virtual_room = self.env.cr.dictfetchall()
        return virtual_room
        
        
class mk_virtual_room_type(models.Model):
    _name = 'mk.virtual_room.type'
    _description = 'Virtual room type'
    _order = 'order_type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
 
    name        = fields.Char('Name',     track_visibility='onchange', required=True)  
    order_type  = fields.Integer('Order', track_visibility='onchange', required=True)  
    
    
class mk_episode(models.Model):
    _inherit = 'mk.episode'
    
    virtual_room_id = fields.Many2one('mk.virtual_room', string='Virtual room')
    room_day_ids    = fields.Many2many('mk.work.days','epiode_rel','virtual_room_rel', string='work days',)    
    time_from       = fields.Float('From time',)  
    time_to         = fields.Float('To time',)  

    @api.one  
    @api.constrains('virtual_room_id','room_day_ids')
    def _check_virtual_room_id(self):
        list_self_room_day = []
        list_exist_room_day = []
        return True
    
        room_day    = self.room_day_ids
        
        for day in room_day:
            list_self_room_day += [day.id]
            
        for episode in self:
            virtual_room = self.search([('virtual_room_id','=',episode.virtual_room_id.id),('id','!=',episode.id)])#TODO 1: case episode without VR // 2: add clause study_class

            for day in virtual_room: 
                exist_days = day.room_day_ids
                for x in exist_days:
                    list_exist_room_day += [x.id]
                    for rec in list_exist_room_day:
                            if rec in list_self_room_day:
                                raise ValidationError(_('This virtual room is used on this day in a other episode!'))

                            