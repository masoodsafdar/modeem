# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp import tools
from random import randint
import datetime
from openerp.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import logging
_logger = logging.getLogger(__name__)


class WebsiteSupportTicket(models.Model):
    _name = "website.support.ticket"
    _description = "Website Support Ticket"
    _rec_name = "subject"
    _order = "create_date desc"
    _inherit=['mail.thread','mail.activity.mixin']

    def _default_state(self):
        return self.env.ref('website_support.website_ticket_state_open').id

    def _default_priority_id(self):
        default_priority = self.env['website.support.ticket.priority'].search([('sequence','=','1')], limit=1)
        return default_priority
   
    def _default_email(self):
        default_email = self.env.user.partner_id.email 
        return default_email

    def default_employee(self):
            employee = self.env['hr.employee'].search([('user_id','=',self.env.uid)], limit=1).user_id
            return employee

    def _default_category_id(self):
        default_category = self.env['website.support.ticket.categories'].search([], limit=1).ids
        return default_category

    @api.model
    def default_user(self):
        ######## for security change g.ig=22 to 1#############
        cr = self.env.cr
        query = '''select g.uid from res_groups_users_rel as 
g,res_users as user_id where g.gid in (2884,3,2886)  and g.uid=user_id.id
 '''
        cr.execute(query)
        list1 = []
        user_ids = cr.dictfetchall()
        for user in user_ids:
            rec_user = user['uid']
            list1.append(rec_user)        
            #res['domain'] = {'user_id':[('id','in',list1)]}
        return [('id','in',list1)]

    def default_center(self):
        employee = self.env['hr.employee'].sudo().search([('user_id','=',self.env.uid)], limit=1)
        if employee:
            return employee.department_id.id 
    
    def default_category(self):
        employee = self.env['hr.employee'].sudo().search([('user_id','=',self.env.uid)], limit=1)
        if employee:
            return employee.category

    center_id             = fields.Many2one('hr.department', string="Center",default=default_center)
    category_emp          = fields.Char(string="Category",default=default_category)
    answer                = fields.One2many('website.support.ticket.compose','answer_id',string="Answers")
    #employee_id=fields.Many2many('res.users', string="emplyee",default=default_employee)
    #center_user=fields.Many2many('res.users',string= "center User",default=default_user_center)
    create_user_id        = fields.Many2one('res.users', "Create User")
    priority_id           = fields.Many2one('website.support.ticket.priority', default=_default_priority_id, string="Priority")
    partner_id            = fields.Many2one('res.partner', string="Partner")
    user_id               = fields.Many2one('res.users', string="Assigned User",domain=lambda self: self.default_user())
    person_name           = fields.Char(string='Person Name')
    email                 = fields.Char(string="Email",default=_default_email)
    support_email         = fields.Char(string="Support Email")
    category              = fields.Many2one('website.support.ticket.categories',default=_default_category_id,string="Category", tracking=True)
    sub_category_id       = fields.Many2one('website.support.ticket.subcategory', string="Sub Category")
    subject               = fields.Char(string="Subject")
    description           = fields.Text(string="Description")
    state                 = fields.Many2one('website.support.ticket.states', readonly=True, default=_default_state, string="State")
    conversation_history  = fields.One2many('website.support.ticket.message', 'ticket_id', string="Conversation History")
    attachment            = fields.Binary(string="Attachments")
    attachment_filename   = fields.Char(string="Attachment Filename")
    attachment_ids        = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'website.support.ticket')], string="Media Attachments")
    unattended            = fields.Boolean(string="Unattended", compute="_compute_unattend", store="True", help="In 'Open' state or 'Customer Replied' state taken into consideration name changes")
    portal_access_key     = fields.Char(string="Portal Access Key")
    ticket_number         = fields.Integer(string="Ticket Number")
    ticket_number_display = fields.Char(string="Ticket Number Display", compute="_compute_ticket_number_display")
    ticket_color          = fields.Char(related="priority_id.color", string="Ticket Color")
    company_id            = fields.Many2one('res.company', string="Company", default=lambda self: self.env['res.company']._company_default_get('website.support.ticket') )
    support_rating        = fields.Integer(string="Support Rating")
    support_comment       = fields.Text(string="Support Comment")
    close_comment         = fields.Text(string="Close Comment")
    close_time            = fields.Datetime(string="Close Time")
    close_date            = fields.Date(string="Close Date")
    closed_by_id          = fields.Many2one('res.users', string="Closed By")
    time_to_close         = fields.Integer(string="Time to close (seconds)")
    extra_field_ids       = fields.One2many('website.support.ticket.field', 'wst_id', string="Extra Details")
    check                 = fields.Boolean(string="check")
    no_hours              = fields.Integer(string="NO Hours")
    visible_ticket        = fields.Boolean(string="Visible", default=False)


    @api.model
    def add_ticket(self, user_id, subject):
        ticket = self.create({'create_user_id': user_id,
                              'subject':        subject,
                              'description':    ''})
        return ticket

    @api.model
    def add_complaints_ticket(self, user_id, subject, description):
        user = self.env['res.users'].search([('id', '=', user_id)], limit=1)
        category_id = self.env.ref('website_support.website_support_complaints').id
        vals = {'create_user_id': user_id,
                'center_id':      user.department_id.id,
                'email':          user.partner_id.email,
                'category':       category_id,
                'subject':        subject,
                'description':    str(description)}

        complaints_ticket = self.with_context(from_mobile=True).create(vals)
        res = complaints_ticket and complaints_ticket.id or 0

        return res
                    
    @api.one
    def set_to_draft(self):
            mail=self.env['mail.message']
            user = self.env['res.users'].search([('id','=',self.env.user.id)])
            resource = self.env['resource.resource'].search([('user_id','=',self.env.user.id)])
            employee_id = self.env['hr.employee'].search([('resource_id','in',resource.ids)])

            if  not user.partner_id.email:
                    user.partner_id.write({'email':employee_id.work_email})
            returned = self.env['mk.general_sending'].send_by_template('Support Ticket New', str(self.id))
            if self.user_id:
                vals={'message_type': 'notification',
                      'subject':      self.subject,
                      'body':         self.description,
                      'partner_ids':  [(6, 0, [self.user_id.partner_id.id])]}

                mail.create(vals)
                
            staff_replied = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_open')
            self.write({'state': staff_replied.id}) 
  
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.person_name = self.partner_id.name
        self.email = self.partner_id.email

    def message_new(self, msg, custom_values=None):
        """ Create new support ticket upon receiving new email"""

        defaults = {'support_email': msg.get('to'), 'subject': msg.get('subject')}

        #Extract the name from the from email if you can
        if "<" in msg.get('from') and ">" in msg.get('from'):
            start = msg.get('from').rindex( "<" ) + 1
            end = msg.get('from').rindex( ">", start )
            from_email = msg.get('from')[start:end]
            from_name = msg.get('from').split("<")[0].strip()
            defaults['person_name'] = from_name
        else:
            from_email = msg.get('from')

        defaults['email'] = from_email

        #Try to find the partner using the from email
        search_partner = self.env['res.partner'].sudo().search([('email','=', from_email)])
        if len(search_partner) > 0:
            defaults['partner_id'] = search_partner[0].id
            defaults['person_name'] = search_partner[0].name

        defaults['description'] = tools.html_sanitize(msg.get('body'))

        portal_access_key = randint(1000000000,2000000000)
        defaults['portal_access_key'] = portal_access_key

        #Assign to default category
        setting_email_default_category_id = self.env['ir.default'].get('website.support.settings', 'email_default_category_id')

        if setting_email_default_category_id:
            defaults['category'] = setting_email_default_category_id

        return super(WebsiteSupportTicket, self).message_new(msg, custom_values=defaults)

    def message_update(self, msg_dict, update_vals=None):
        """ Override to update the support ticket according to the email. """

        body_short = tools.html_sanitize(msg_dict['body'])
        #body_short = tools.html_email_clean(msg_dict['body'], shorten=True, remove=True)

        #Add to message history to keep HTML clean
        self.conversation_history.create({'ticket_id': self.id, 'by': 'customer', 'content': body_short })

        #If the to email address is to the customer then it must be a staff member
        if msg_dict.get('to') == self.email:
            change_state = self.env['ir.model.data'].get_object('website_support','website_ticket_state_staff_replied')
        else:
            change_state = self.env['ir.model.data'].get_object('website_support','website_ticket_state_customer_replied')

        self.state = change_state.id

        return super(WebsiteSupportTicket, self).message_update(msg_dict, update_vals=update_vals)

    @api.one
    @api.depends('ticket_number')
    def _compute_ticket_number_display(self):
        if self.ticket_number:
            self.ticket_number_display = str(self.id) + " / " + "{:,}".format( self.ticket_number )
        else:
            self.ticket_number_display = self.id

    @api.one
    @api.depends('state')
    def _compute_unattend(self):
        opened_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_open')
        customer_replied_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_customer_replied')

        if self.state == opened_state or self.state == customer_replied_state:
            self.unattended = True

    @api.multi
    def open_close_ticket_wizard(self):

        return {
            'name': "Close Support Ticket",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'website.support.ticket.close',
            'context': {'default_ticket_id': self.id},
            'target': 'new'
        }

    @api.model
    def _needaction_domain_get(self):
        open_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_open')
        custom_replied_state = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_customer_replied')
        return ['|',('state', '=', open_state.id ), ('state', '=', custom_replied_state.id)]

    @api.model
    def create(self, vals):
        new_id = super(WebsiteSupportTicket, self).create(vals)
        if self._context.get('from_mobile'):
            return new_id

        new_id.ticket_number = new_id.company_id.next_support_ticket_number
        mail=self.env['mail.message']
        #Add one to the next ticket number
        new_id.company_id.next_support_ticket_number += 1

        ticket_open_email_template = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_open').mail_template_id
        ticket_open_email_template.send_mail(new_id.id, True)

        #Send an email out to everyone in the category
        notification_template = self.env['ir.model.data'].sudo().get_object('website_support', 'new_support_ticket_category')
        support_ticket_menu = self.env['ir.model.data'].sudo().get_object('website_support', 'website_support_ticket_menu')
        support_ticket_action = self.env['ir.model.data'].sudo().get_object('website_support', 'website_support_ticket_action')

        for my_user in new_id.category.cat_user_ids:
            values = notification_template.generate_email(new_id.id)
            values['body_html'] = values['body_html'].replace("_ticket_url_", "web#id=" + str(new_id.id) + "&view_type=form&model=website.support.ticket&menu_id=" + str(support_ticket_menu.id) + "&action=" + str(support_ticket_action.id) ).replace("_user_name_",  my_user.partner_id.name)
            #values['body'] = values['body_html']
            values['email_to'] = my_user.partner_id.email

            send_mail = self.env['mail.mail'].create(values)
            send_mail.send()

            #Remove the message from the chatter since this would bloat the communication history by a lot
            send_mail.mail_message_id.unlink()
        
        cr = self.env.cr
        ###### for security change g.gid=22###########
        query = '''select g.uid,user_id.partner_id from res_groups_users_rel as g,res_users as user_id where g.gid=3
        and  g.uid=user_id.id '''
        cr.execute(query)

        user_ids = cr.dictfetchall()
        for user in user_ids:
                         
            valus={
                                'message_type': 'notification',
                                'subject': vals['subject'],
                                'body': vals['description'],
                                'partner_ids':[(6, 0, [user['partner_id']])] }

         
            mail.create(valus)   
           


        query2 = '''select g.uid from res_groups_users_rel as g,res_users as user_id where g.gid=2884 
        and  g.uid=user_id.id '''
        cr.execute(query2)
        res={}
        list1=[]
        user_ids = cr.dictfetchall()
        for user in user_ids:
            rec_user=user['uid']
            emp_obj=self.env['res.users'].sudo().search([('department_id','=',self.center_id.id)])
            for user_id in emp_obj:
                if rec_user==user_id.id:
                    user = self.env['res.users'].sudo().search([('id','=',user_id.id)])
                    resource = self.env['resource.resource'].sudo().search([('user_id','=',user_id.id)])
                    employee_id = self.env['hr.employee'].sudo().search([('resource_id','in',resource.ids)])
                    if  not user.partner_id.email:
                        user.partner_id.write({'email':employee_id.work_email})
                    values = notification_template.generate_email(new_id.id)
                    values['body_html'] = values['body_html'].replace("_ticket_url_", "web#id=" + str(new_id.id) + "&view_type=form&model=website.support.ticket&menu_id=" + str(support_ticket_menu.id) + "&action=" + str(support_ticket_action.id) ).replace("_user_name_",  user_id.partner_id.name)
                    values['email_to'] = user_id.partner_id.email

                    send_mail = self.env['mail.mail'].create(values)
                    send_mail.send()
                    message={}
                    message={
    		                 'message_type': 'notification',
    		                 'subject': vals['subject'],
    		                 'body': vals['description'],
    		                 'partner_ids':[(6, 0, [user.partner_id.id])] }


                    mail.create(message)
 
                    obj_general_sending = self.env['mk.general_sending']
                    message=self.env['mk.sms_template'].search([('code', '=', 'mk_send_support_open')],limit=1)
                    for mosque in user_id.mosque_ids:
                        if not mosque.gateway_config and not mosque.gateway_password:
                           if employee_id.mobile:
                              a=obj_general_sending.send_sms(employee_id.mobile_phone,str(message.sms_text))
                        if mosque.gateway_config and mosque.gateway_password and mosque.gateway_user and mosque.gateway_sender:
                           obj_employee_sending = self.env['mk.employee.sms']
                              
                           a=obj_employee_sending.send_gateway_employee_quta(message.sms_text, employee_id.mobile_phone,mosque)
        return new_id



    @api.multi
    def write(self, values, context=None):

        update_rec = super(WebsiteSupportTicket, self).write(values)
        mail=self.env['mail.message']
        if 'state' in values:
            if self.state.mail_template_id:
                self.state.mail_template_id.send_mail(self.id, True)

        #Email user if category has changed
        if 'category' in values:
            change_category_email = self.env['ir.model.data'].sudo().get_object('website_support', 'new_support_ticket_category_change')
            change_category_email.send_mail(self.id, True)

        if 'user_id' in values:
            setting_change_user_email_template_id = self.env['ir.default'].get('website.support.settings', 'change_user_email_template_id')

            if setting_change_user_email_template_id:
                email_template = self.env['mail.template'].browse(setting_change_user_email_template_id)
            else:
                #Default email template
                email_template = self.env['ir.model.data'].get_object('website_support','support_ticket_user_change')

            email_values = email_template.generate_email([self.id])[self.id]
            email_values['model'] = "website.support.ticket"
            email_values['res_id'] = self.id
            assigned_user = self.env['res.users'].browse( int(values['user_id']) )
            email_values['email_to'] = assigned_user.partner_id.email
            email_values['body_html'] = email_values['body_html'].replace("_user_name_", assigned_user.name)
            email_values['body'] = email_values['body'].replace("_user_name_", assigned_user.name)
            send_mail = self.env['mail.mail'].create(email_values)
            send_mail.send()
            vals={
                    'message_type': 'notification',
                    'subject': self.subject,
                    'body': self.description,
                    'partner_ids':[(6, 0, [self.user_id.partner_id.id])] }
     

           
            obj_general_sending = self.env['mk.general_sending']
            message=self.env['mk.sms_template'].search([('code', '=', 'mk_send_support_open')],limit=1)
            if self.create_user_id.mobile:
               a=obj_general_sending.send_sms(self.create_user_id.mobile,str(message.sms_text))
           
        return update_rec

    def send_survey(self):

        notification_template = self.env['ir.model.data'].sudo().get_object('website_support', 'support_ticket_survey')
        values = notification_template.generate_email(self.id)
        surevey_url = "support/survey/" + str(self.portal_access_key)
        values['body_html'] = values['body_html'].replace("_survey_url_",surevey_url)
        send_mail = self.env['mail.mail'].create(values)
        send_mail.send(True)


class WebsiteSupportTicketField(models.Model):

    _name = "website.support.ticket.field"

    wst_id = fields.Many2one('website.support.ticket', string="Support Ticket")
    name = fields.Char(string="Label")
    value = fields.Char(string="Value")


class WebsiteSupportTicketMessage(models.Model):

    _name = "website.support.ticket.message"

    ticket_id = fields.Many2one('website.support.ticket', string='Ticket ID')
    by = fields.Selection([('staff','Staff'), ('customer','Customer')], string="By")
    content = fields.Html(string="Content")


class WebsiteSupportTicketCategories(models.Model):
    _name = "website.support.ticket.categories"
    _inherit=['mail.thread','mail.activity.mixin']
    _order = "sequence asc"

    sequence     = fields.Integer(string="Sequence", tracking=True)
    name         = fields.Char(required=True, translate=True, string='Category Name', tracking=True)
    cat_user_ids = fields.Many2many('res.users', string="Category Users")

    @api.model
    def create(self, values):
        sequence=self.env['ir.sequence'].next_by_code('website.support.ticket.categories')
        values['sequence']=sequence
        return super(WebsiteSupportTicketCategories, self).create(values)


class WebsiteSupportTicketSubCategories(models.Model):
    _name = "website.support.ticket.subcategory"
    _inherit=['mail.thread','mail.activity.mixin']
    _order = "sequence asc"

    sequence             = fields.Integer(string="Sequence", tracking=True)
    name                 = fields.Char(required=True, translate=True, string='Sub Category Name', tracking=True)
    parent_category_id   = fields.Many2one('website.support.ticket.categories', required=True, string="Parent Category", tracking=True)
    category_type        = fields.Selection([('website','From Website'),('system','From System'),('both','Both')], string="Category Type", tracking=True)
    additional_field_ids = fields.One2many('website.support.ticket.subcategory.field', 'wsts_id', string="Additional Fields")
 
    @api.model
    def create(self, values):
        sequence=self.env['ir.sequence'].next_by_code('website.support.ticket.subcategory')
        values['sequence']=sequence
        return super(WebsiteSupportTicketSubCategories, self).create(values)


class WebsiteSupportTicketSubCategoryField(models.Model):

    _name = "website.support.ticket.subcategory.field"

    wsts_id = fields.Many2one('website.support.ticket.subcategory', string="Sub Category")
    name = fields.Char(string="Label")
    type = fields.Selection([('textbox','Textbox')], default="textbox", string="Type")


class WebsiteSupportTicketStates(models.Model):

    _name = "website.support.ticket.states"

    name = fields.Char(required=True, translate=True, string='State Name')
    mail_template_id = fields.Many2one('mail.template', domain="[('model_id','=','website.support.ticket')]", string="Mail Template")
    sms_template_id= fields.Many2one('mk.sms_template', string="SMS Template")


class WebsiteSupportTicketPriority(models.Model):
    _name = "website.support.ticket.priority"
    _order = "sequence asc"

    sequence = fields.Integer(string="Sequence")
    name     = fields.Char(required=True, translate=True, string="Priority Name")
    color    = fields.Char(string="Color")

    @api.model
    def create(self, values):
        sequence=self.env['ir.sequence'].next_by_code('website.support.ticket.priority')
        values['sequence']=sequence
        return super(WebsiteSupportTicketPriority, self).create(values)


class WebsiteSupportTicketUsers(models.Model):

    _inherit = "res.users"

    cat_user_ids = fields.Many2many('website.support.ticket.categories', string="Category Users")


class WebsiteSupportTicketCompose(models.Model):

    _name = "website.support.ticket.close"

    ticket_id = fields.Many2one('website.support.ticket', string="Ticket ID")
    message = fields.Text(string="Close Message")

    def close_ticket(self):

        self.ticket_id.close_time = datetime.datetime.now()

        #Also set the date for gamification
        self.ticket_id.close_date = datetime.date.today()

        diff_time = datetime.datetime.strptime(self.ticket_id.close_time, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.datetime.strptime(self.ticket_id.create_date, DEFAULT_SERVER_DATETIME_FORMAT)
        self.ticket_id.time_to_close = diff_time.seconds

        closed_state = self.env['ir.model.data'].sudo().get_object('website_support', 'website_ticket_state_staff_closed')

        #We record state change manually since it would spam the chatter if every 'Staff Replied' and 'Customer Replied' gets recorded
        message = "<ul class=\"o_mail_thread_message_tracking\">\n<li>State:<span> "  + " </span><b>-></b> " + closed_state.name + " </span></li></ul>"

        self.ticket_id.message_post(body=message, subject="Ticket Closed by Staff")

        self.ticket_id.close_comment = self.message
        self.ticket_id.closed_by_id = self.env.user.id
        self.ticket_id.state = closed_state.id

        #Auto send out survey
        setting_auto_send_survey = self.env['ir.default'].get('website.support.settings', 'auto_send_survey')
        if setting_auto_send_survey:
            self.ticket_id.send_survey()

        closed_state_mail_template = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_staff_closed').mail_template_id

        if closed_state_mail_template:
            closed_state_mail_template.send_mail(self.ticket_id.id, True)


            
        
        obj_general_sending = self.env['mk.general_sending']
        message=self.env['mk.sms_template'].search([('code', '=', 'mk_send_support')],limit=1)

        if self.ticket_id.create_user_id.mobile:
              a=obj_general_sending.send_sms(self.ticket_id.create_user_id.mobile,str(message.sms_text))
        notification_template = self.env['ir.model.data'].sudo().get_object('website_support', 'support_ticket_error')
        cr = self.env.cr
        query2 = '''select g.uid from res_groups_users_rel as g,res_users as user_id where g.gid=2886 
        and  g.uid=user_id.id '''
        cr.execute(query2)
        res={}
        list1=[]
        user_ids = cr.dictfetchall()
        for user in user_ids:
            rec_user=user['uid']
            emp_obj=self.env['res.users'].sudo().search([('department_id','=',self.ticket_id.center_id.id)])
            for user_id in emp_obj:
                if rec_user==user_id.id:
                    user = self.env['res.users'].sudo().search([('id','=',user_id.id)])
                    resource = self.env['resource.resource'].sudo().search([('user_id','=',user_id.id)])
                    employee_id = self.env['hr.employee'].sudo().search([('resource_id','in',resource.ids)])
                    if  not user.partner_id.email:
                        user.partner_id.write({'email':employee_id.work_email})
                    email_values =notification_template.generate_email(self.ticket_id.id)
                    email_values['model'] = "website.support.ticket.close"

                    email_values['res_id'] = self.id
                    email_values['email_to'] = user_id.partner_id.email
                    email_values['body_html'] = email_values['body_html'].replace("_user_name_", user_id.name)
                    email_values['body'] = email_values['body'].replace("_user_name_",user_id.name)
                    send_mail = self.env['mail.mail'].create(email_values)
                    send_mail.send()
                    obj_general_sending = self.env['mk.general_sending']
                    message=self.env['mk.sms_template'].search([('code', '=', 'mk_send_support')],limit=1)
                    for mosque in user_id.mosque_ids:
                        if not mosque.gateway_config and not mosque.gateway_password:
                           if employee_id.mobile:
                              a=obj_general_sending.send_sms(employee_id.mobile_phone,str(message.sms_text))
                        if mosque.gateway_config and mosque.gateway_password and mosque.gateway_user and mosque.gateway_sender:
                           obj_employee_sending = self.env['mk.employee.sms']
                              
                           a=obj_employee_sending.send_gateway_employee_quta(message.sms_text, employee_id.mobile_phone,mosque)

            self.ticket_id.check=True


class WebsiteSupportTicketCompose(models.Model):

    _name = "website.support.ticket.compose"

    ticket_id = fields.Many2one('website.support.ticket', string='Ticket ID')
    partner_id = fields.Many2one('res.partner', string="Partner", readonly="True")
    email = fields.Char(string="Email", readonly="True")
    subject = fields.Char(string="Subject", readonly="True")
    body = fields.Text(string="Message Body")
    text = fields.Text(string="Message")
    answer_id=fields.Many2one('website.support.ticket', string='Answer ID')
    template_id = fields.Many2one('mail.template', string="Mail Template", domain="[('model_id','=','website.support.ticket'), ('built_in','=',False)]")

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            values = self.env['mail.compose.message'].generate_email_for_composer(self.template_id.id, [self.ticket_id.id])[self.ticket_id.id]
            self.body = values['body']


    @api.one
    def send_reply(self):
        #Send email
       
        values = {}
        vals={}
        mail=self.env['mail.message']

        obj_general_sending = self.env['mk.general_sending']

        

        vals={
                'message_type': 'notification',
               'subject': self.subject,
               'body': self.body,
               'partner_ids':[(6, 0, [self.ticket_id.create_user_id.partner_id.id])] }
     
        mail.create(vals)

        user = self.env['res.users'].search([('id','=',self.env.user.id)])
        resource = self.env['resource.resource'].search([('user_id','=',self.env.user.id)])
        employee_id = self.env['hr.employee'].search([('resource_id','in',resource.ids)])


        if  not user.partner_id.email:
            user.partner_id.write({'email':employee_id.work_email})
        returned=self.env['mk.general_sending'].send_by_template('Support Ticket Reply Wrapper (User)', str(self.id))

        staff_replied = self.env['ir.model.data'].search([('name','=','website_ticket_state_staff_replied'),('model','=','website.support.ticket.states')])
        #truncated_text = self.env["ir.fields.converter"].text_from_html(
        #self.body)
        self.text=self.body.split("<")[0].strip()
        self.ticket_id.write({'state' :int(staff_replied.res_id),'answer':[(4,self.id)]})
       # self.ticket_id.write({'answer':[(0, 0, {'body':self.body})]})
        message=self.env['mk.sms_template'].search([('code', '=', 'mk_send_support_reply')],limit=1)
        if self.ticket_id.create_user_id.mobile:
            a=obj_general_sending.send_sms(self.ticket_id.create_user_id.mobile,str(message.sms_text))
        notification_template = self.env['ir.model.data'].sudo().get_object('website_support', 'support_ticket_reply_wrapper')
        cr = self.env.cr
        query2 = '''select g.uid from res_groups_users_rel as g,res_users as user_id where g.gid=2884 
        and  g.uid=user_id.id '''
        cr.execute(query2)
        res={}
        list1=[]
        user_ids = cr.dictfetchall()
        for user in user_ids:
            rec_user=user['uid']
            emp_obj=self.env['res.users'].sudo().search([('department_id','=',self.ticket_id.center_id.id)])
            for user_id in emp_obj:
                if rec_user==user_id.id:
                    user = self.env['res.users'].sudo().search([('id','=',user_id.id)])
                    resource = self.env['resource.resource'].sudo().search([('user_id','=',user_id.id)])
                    employee_id = self.env['hr.employee'].sudo().search([('resource_id','in',resource.ids)])
                    if  not user.partner_id.email:
                        user.partner_id.write({'email':employee_id.work_email})

                    email_values =notification_template.generate_email(self.id)
                    email_values['model'] = "website.support.ticket.compose"
                    email_values['res_id'] = self.id
                    email_values['email_to'] = user_id.partner_id.email
                    email_values['body_html'] = email_values['body_html'].replace("_user_name_", user_id.name)
                    email_values['body'] = email_values['body'].replace("_user_name_",user_id.name)
                    send_mail = self.env['mail.mail'].create(email_values)
                    send_mail.send()
                    obj_general_sending = self.env['mk.general_sending']
                    message=self.env['mk.sms_template'].search([('code', '=', 'mk_send_support_reply')],limit=1)
                    for mosque in user_id.mosque_ids:
                        if not mosque.gateway_config and not mosque.gateway_password:
                           if employee_id.mobile:
                              a=obj_general_sending.send_sms(employee_id.mobile_phone,str(message.sms_text))
                        if mosque.gateway_config and mosque.gateway_password and mosque.gateway_user and mosque.gateway_sender:
                           obj_employee_sending = self.env['mk.employee.sms']
                              
                           a=obj_employee_sending.send_gateway_employee_quta(message.sms_text, employee_id.mobile_phone,mosque)
