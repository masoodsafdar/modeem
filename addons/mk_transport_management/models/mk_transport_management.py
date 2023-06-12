#-*- coding:utf-8 -*-

##############################################################################
#
#    Copyright (C) Appness Co. LTD **hosam@app-ness.com**. All Rights Reserved
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
    
class MKTransportManagement(models.Model):
    _name = 'mk.transport.management'
    _rec_name = 'student_id'
    

    @api.onchange('transport_type')
    def calculate_fees(self):
        for rec in self:
            if rec.transport_type in ['go_only','return_only']:
                rec.fees=rec.request_id.student_id.mosq_id.one_way_money

            elif rec.transport_type == 'go&return':
                rec.fees=rec.request_id.student_id.mosq_id.double_way_money

    request_id = fields.Many2one('transportation.request', string='request')
    student_id = fields.Many2one('mk.link',related="request_id.student_id", string='Student')
    days_ids= fields.Many2many(related="request_id.student_id.episode_id.episode_days", string='Days')
    transport_type=fields.Selection([('go&return','ذهاب وعودة'),('go_only','ذهاب فقط'),('return_only','عودة فقط')])
    period = fields.Selection([('subh', 'subh'), ('zuhr', 'zuhr'),('aasr','aasr'),('magrib','magrib'),('esha','esha')], 'Transaction Period')
    vehicle_id = fields.Many2one('vehicle.records', string='Vehicle')
    driver_id = fields.Many2one('drivers.records', string='Driver')
    driver_phone = fields.Char('Driver Phone No')
    supervisor_id = fields.Many2one('hr.employee','Bus Supervisor', domain="[('category','=','bus_sup')]")
    seates_no_fajer = fields.Integer('Seates No fajer', compute='compute_available_seats')
    seates_no_zuhr = fields.Integer('Seates No zuhr', compute='compute_available_seats')
    seates_no_aasr = fields.Integer('Seates No aasr', compute='compute_available_seats')
    seates_no_maghrib = fields.Integer('Seates No maghrib', compute='compute_available_seats')
    seates_no_esha = fields.Integer('Seates No isha', compute='compute_available_seats')
    cancling_reason = fields.Text('Cancling Reason')
    fees = fields.Float('Fees', compute='calculate_fees')
    deduct = fields.Float('Deduct')
    trans_period = fields.Selection([('subh', 'subh'),('zuhr', 'zuhr'),('aasr','aasr'),('magrib','magrib'),('esha','esha')], string='Transaction Period', related='request_id.trans_period')

    #asset_id = fields.Char('Asset',)#M2one
    state = fields.Selection([
    ('draft','Draft'),
    ('confirm','Confirm'),
    ('cancle','Cancle'),('biding', 'Biding')],'Status', default='draft')

    @api.onchange('request_id')
    def on_tstudent_select(self):
        self.days_ids=self.student_id.episode_id.episode_days.ids
        self.transport_type= self.request_id.transport_type
        if self.transport_type in ['go_only','return_only']:
            self.fees=self.request_id.student_id.mosq_id.one_way_money

        elif self.transport_type == 'go&return':
            self.fees=self.request_id.student_id.mosq_id.double_way_money


    @api.onchange('vehicle_id')
    def onchange_vehicle(self):
        self.driver_id=self.vehicle_id.driver.id
        self.supervisor_id=self.vehicle_id.superviser_id.id
        self.driver_phone=self.vehicle_id.driver.phone_no

    @api.depends('vehicle_id')
    def compute_available_seats(self):
        confirm_vehicle=self.search([('state','=','confirm'),('vehicle_id','=',self.vehicle_id.id)])
        #for rec in confirm_vehicle:
        #   if rec.transportation_days
        #    if availa
        #self.seates_no_fajer=
        #self.seates_no_zuhr
        #self.seates_no_aasr
        #self.seates_no_maghrib
        #self.seates_no_esha



    @api.one
    def act_confirm(self):
    	#self.state='confirm'
        
        days=self.request_id.transportation_days
        period=self.request_id.trans_period

        go_return=self.request_id.transport_type

        vehicle_management=self.env['vehicle.management'].sudo().search([('vehicle_id','=',self.vehicle_id.id)])
        if vehicle_management:
            for vehicle in vehicle_management:
                if go_return=='go_only':
                    vehicle_lines=self.env['vehicle.emanagement.line'].sudo().search([('avilable_seats','>',0),('vehicle_ide','=',vehicle.id),('work_periods','=',period),('work_days','in',days.ids),('go_return','=','go')])
                    if vehicle_lines and len(vehicle_lines)==len(days.ids):

                        for rec in vehicle_lines:
                            if rec.avilable_seats<1:
                                raise ValidationError(_('عفوا ! لا توجد مقاعد شاغرة'))
                            else:
                                
                                rec.avilable_seats-=1

                        self.request_id.approve_request()
                        self.write({'state':'confirm'})
                    elif not vehicle_lines or len(vehicle_lines)!=len(days.ids):
                        raise ValidationError('عفوا ! لا توجد مقاعد شاغرة')

                if go_return=='return_only':
                    vehicle_lines=self.env['vehicle.emanagement.line'].sudo().search([('avilable_seats','>',0),('vehicle_ide','=',vehicle.id),('work_periods','=',period),('work_days','in',days.ids),('go_return','=','return')])

                    if vehicle_lines and len(vehicle_lines)==len(days.ids):

                        for rec in vehicle_lines:
                            if rec.avilable_seats<1:
                                raise ValidationError(_('عفوا ! لا توجد مقاعد شاغرة'))
                            else:
                                
                                rec.avilable_seats-=1

                        self.request_id.approve_request()
                        self.write({'state':'confirm'})
                    elif vehicle_lines or len(vehicle_lines)!=len(days.ids):
                        raise ValidationError('عفوا ! لا توجد مقاعد شاغرة')
                if go_return=='go&return':

                    go_vehicle_lines=self.env['vehicle.emanagement.line'].sudo().search([('avilable_seats','>',0),('vehicle_ide','=',vehicle.id),('work_periods','=',period),('work_days','in',days.ids),('go_return','=','go')])
                    return_vehicle_lines=self.env['vehicle.emanagement.line'].sudo().search([('avilable_seats','>',0),('vehicle_ide','=',vehicle.id),('work_periods','=',period),('work_days','in',days.ids),('go_return','=','return')])

                    if go_vehicle_lines and return_vehicle_lines and len(return_vehicle_lines)==len(days.ids) and len(go_vehicle_lines)==len(days.ids):
                        for rec in go_vehicle_lines:
                            
                            
                                
                            rec.avilable_seats-=1
                        for rec in return_vehicle_lines:
                            
                                
                            rec.avilable_seats-=1
                        self.request_id.approve_request()
                        self.write({'state':'confirm'})
                    else:
                        raise ValidationError('عفوا ! لا توجد مقاعد شاغرة')


    '''
    @api.onchange('state')
    def cancleing_reeson

        if state=='canle'
         cancling_reason=self.env['transportation.request'].canceling_reason
    '''



    @api.one
    def act_cancle(self):
    	self.state='cancle'

