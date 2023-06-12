# -*- coding: utf-8 -*-

from odoo import models, fields, api

class mk_events_registration(models.Model):
    _name = 'event.registrations'

    _rec_name="invited"

    @api.depends('create_uid')
    def get_create_uid(self):
        for rec in self:
            if rec.create_uid:
                if rec.invited.user_id.id!=rec.create_uid.id:
                    rec.is_creator=True
                    #return True

    invited = fields.Many2one(
        string='Invited',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='hr.employee',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )
    is_creator = fields.Boolean(
        string='Is creator',
        required=False,
        readonly=False,
        index=False,
        help=False,
        compute='get_create_uid'
    )
    event_date = fields.Date(
        string='Event date',
        required=False,
        readonly=False,
        index=False,
        related='event_id.event_date'
    )
    event_start = fields.Float(
        string='Event start',
        required=False,
        readonly=False,
        index=False,
        related='event_id.event_start'
    )
    event_end = fields.Float(
        string='Event end',
        required=False,
        readonly=False,
        index=False,
        related='event_id.event_end'
    )
    event_id = fields.Many2one(
        string='Event id',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='event.event',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )
    
    state = fields.Selection(
        string='state',
        required=False,
        readonly=False,
        index=False,
        default='draft',
        #related='event_id.state',
        selection=[('draft', 'draft'), ('cancel', 'cancel'),('confirm', 'confirm'), ('done', 'done')]
    )
    
    @api.multi
    def confirm_attendance(self):    
        invite_line=self.env['event.invite'].search([('event_id','=',self.event_id.id),('employee_id','=',self.invited.id)])    
        if invite_line:
            invite_line.write({'attendance_confirm':True})
        else:
            attendee=self.env['event.attendee'].search([('event_id','=',self.event_id.id),('employee_id','=',self.invited.id)])
            if attendee:
                attendee.write({'attendance_confirm':True})


    @api.multi
    def confirm_recommondations(self):    
        invite_line=self.env['event.invite'].search([('event_id','=',self.event_id.id),('employee_id','=',self.invited.id)])    
        if invite_line:
            invite_line.write({'recommendation_acceptance':True})
        else:
            attendee=self.env['event.attendee'].search([('event_id','=',self.event_id.id),('employee_id','=',self.invited.id)])
            if attendee:
                attendee.write({'recommendation_acceptance':True})

	
