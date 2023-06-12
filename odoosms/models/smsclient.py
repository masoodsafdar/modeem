# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
import urllib.request

import logging
_logger = logging.getLogger(__name__)


class partner_sms_send(models.Model):
    _name = "partner.sms.send"

    def _default_get_mobile(self):
        partner_pool = self.env['res.partner']
        res = {}
        return res

    def _default_get_gateway(self):
        sms_obj = self.env['smsclient']
        gateway_ids = sms_obj.search([], limit=1)
        return gateway_ids[0].id or False

    def onchange_gateway(self, gateway_id):
        sms_obj = self.env['smsclient']
        if not gateway_id:
            return {}
        gateway = sms_obj.browse([gateway_id])
        return {
            'value': {
                'validity': gateway.validity, 
                'classes': gateway.classes,
                'deferred': gateway.deferred,
                'priority': gateway.priority,
                'coding': gateway.coding,
                'tag': gateway.tag,
                'nostop': gateway.nostop,
            }
        }
    mobile_to = fields.Char('To', size=256, required=True)
    app_id = fields.Char(string='App ID', size=256)
    user = fields.Char('Login', size=256)
    password = fields.Char('Password', size=256)
    text = fields.Text('SMS Message', required=True)
    gateway_id = fields.Many2one('smsclient', string='SMS Gateway', required=True,default=_default_get_gateway)
    validity = fields.Integer('Validity', help='the maximum time -in minute(s)- before the message is dropped')
    classes=fields.Selection([('0', 'Flash'),
                              ('1', 'Phone display'),
                              ('2', 'SIM'),
                              ('3', 'Toolkit')], 'Class', help='the sms class: flash(0), phone display(1), SIM(2), toolkit(3)')
    deferred = fields.Integer('Deferred', help='the time -in minute(s)- to wait before sending the message')
    priority=fields.Selection([('0','0'),
                               ('1','1'),
                               ('2','2'),
                               ('3','3')], 'Priority', help='The priority of the message')
    coding=fields.Selection([('1', '7 bit'),
                             ('2', 'Unicode')], 'Coding', help='The SMS coding: 1 for 7 bit or 2 for unicode')

    tag = fields.Char('Tag', size=256, help='an optional tag')
    nostop = fields.Boolean('NoStop', help='Do not display STOP clause in the message, this requires that this is not an advertising message')
    
    def sms_send(self):
        client_obj = self.env['smsclient']
        for data in self.browse([]):
            if not data.gateway_id:
                raise Warning(_('No Gateway Found'))
            else:
                client_obj._send_message(data)
        return {}
     

class SMSClient2(models.Model):
    _name = 'smsclient'
    _description = 'SMS Client'
    
    name         = fields.Char('Gateway Name', required=True)
    url          = fields.Char('Gateway URL', size=256, required=True,help="Base url for message")
    property_ids = fields.One2many('sms.smsclient.parms', 'gateway_id', string='Parameters')
    history_line = fields.One2many('sms.smsclient.history', 'gateway_id', string='History')
    method       = fields.Selection([('http', 'HTTP Method'),
                             ('smpp', 'SMPP Method')], 'API Method', default='http')
    state=fields.Selection([('new', 'Not Verified'),
                            ('waiting', 'Waiting for Verification'),
                            ('confirm', 'Verified'),], 'Gateway Status', readonly=True, default='new')
    users_id = fields.Many2many('res.users', string='Users Allowed')
    code = fields.Char(string='Verification Code', size=256)
    body = fields.Text('Message', help="The message text that will be send along with the email which is send through this server")
    validity = fields.Integer('Validity', help='The maximum time -in minute(s)- before the message is dropped', default=10)
    classes = fields.Selection([('0', 'Flash'),
                                ('1', 'Phone display'),
                                ('2', 'SIM'),
                                ('3', 'Toolkit')], 'Class', default='1', help='The SMS class: flash(0),phone display(1),SIM(2),toolkit(3)')
    deferred = fields.Integer(string='Deferred', default=0, help='The time -in minute(s)- to wait before sending the message')
    priority = fields.Selection([('0', '0'),
                                 ('1', '1'),
                                 ('2', '2'),
                                 ('3', '3')], 'Priority', default='3',help='The priority of the message ')
    coding = fields.Selection([('1', '7 bit'),
                              ('2', 'Unicode')],'Coding', default='1', help='The SMS coding: 1 for 7 bit or 2 for unicode')

    tag = fields.Char('Tag', required=False, size=256, help='an optional tag')
    nostop = fields.Boolean('NoStop', default=True, help='Do not display STOP clause in the message, this requires that this is not an advertising message')
    char_limit = fields.Boolean('Character Limit',default=True)

    def _check_permissions(self):
        self._cr.execute('select * from res_smsserver_group_rel where sid=%s and uid=%s' % (id, self._uid))
        data = self._cr.fetchall()
        if len(data) <= 0:
            return False
        return True

    def _prepare_smsclient_queue(self, data, name):
        return {'name': name,
                'gateway_id': data.gateway_id.id,
                'state': 'draft',
                'mobile': data.mobile_to,
                'msg': data.text,
                'validity': data.validity, 
                'classes': data.classes, 
                'deffered': data.deferred, 
                'priorirty': data.priority, 
                'coding': data.coding, 
                'tag': data.tag, 
                'nostop': data.nostop,}

    def _send_message(self, data):
        if self._context is None:
            self._context = {}
        gateway = data.gateway_id
        if gateway:
            url = gateway.url
            name = url
            if gateway.method == 'http':
                prms = {}
                for p in data.gateway_id.property_ids:
                    if p.type == 'user':
                        prms[p.name] = p.value
                    elif p.type == 'password':
                        prms[p.name] = p.value
                    elif p.type == 'to':
                        prms[p.name] = data.mobile_to
                    elif p.type == 'sms':
                        prms[p.name] = str(data.text)
                    elif p.type == 'sender':
                        prms[p.name] = p.value
                    elif p.type == 'extra':
                        prms[p.name] = p.value
                        
                params = urllib.parse.urlencode(prms)
                name = url + "?" + params + "&lang=3"
                
            queue_obj = self.env['sms.smsclient.queue']
            vals = self._prepare_smsclient_queue(data, name)
            queue_obj.create(vals)
        return True

    @api.model
    def _check_queue(self, cron_mode=True):
        queue_obj = self.env['sms.smsclient.queue']
        history_obj = self.env['sms.smsclient.history']
        sids = queue_obj.search([('state', '!=', 'send'),
                                 ('state', '!=', 'sending')], limit=30)
        record_sids=queue_obj.search([('id', 'in', sids.ids)])
        record_sids.write({'state': 'sending'})

        error_ids = []
        sent_ids = []
        
        for sms in record_sids:
            if sms.gateway_id.method == 'http':
                urllib.request.urlopen(sms.name)
                
            if sms.gateway_id.method == 'smpp':
                for p in sms.gateway_id.property_ids:
                    if p.type == 'user':
                        login = p.value
                        
                    elif p.type == 'password':
                        pwd = p.value
                        
                    elif p.type == 'sender':
                        sender = p.value
                        
                    elif p.type == 'sms':
                        account = p.value
                try:
                    soap = WSDL.Proxy(sms.gateway_id.url)
                    message = ''
                    if sms.coding == '2':
                        message = str(sms.msg)
                        
                    if sms.coding == '1':
                        message = str(sms.msg)
                        
                    result = soap.telephonySmsUserSend(str(login), str(pwd),
                        str(account), str(sender), str(sms.mobile), message,
                        int(sms.validity), int(sms.classes), int(sms.deferred),
                        int(sms.priority), int(sms.coding),str(sms.gateway_id.tag), int(sms.gateway_id.nostop))
                    ### End of the new process ###
                except Exception:
                    raise Warning(_('Error'))
                
            history_obj.create({'name': _('SMS Sent'),
                                'gateway_id': sms.gateway_id.id,
                                'sms': sms.msg,
                                'to': sms.mobile,})
            sent_ids.append(sms.id)
        queue_ids=queue_obj.search([('id', 'in', sent_ids)])
        
        
        queue_error=queue_obj.search([('id', 'in', error_ids)])
        queue_ids.write({'state': 'send'})
        queue_ids.unlink()
        queue_error.write({
                            'state': 'error',
                            'error': 'Size of SMS should not be more then 160 char'
                        })
        return True

class SMSQueue(models.Model):
    _name = 'sms.smsclient.queue'
    _description = 'SMS Queue'
    
    name = fields.Text('SMS Request', required=True, size=256, readonly=True, states={'draft': [('readonly', False)]})
    msg = fields.Text(string='SMS Text', required=True, readonly=True, size=256, states={'draft': [('readonly', False)]})
    mobile = fields.Char(string='Mobile No', size=256, required=True, readonly=True, states={'draft': [('readonly', False)]})
    gateway_id = fields.Many2one('smsclient', string='SMS Gateway', readonly=True, states={'draft': [('readonly', False)]})
    state=fields.Selection([('draft', 'Queued'),
                            ('sending', 'Waiting'),
                            ('send', 'Sent'),
                            ('error', 'Error'),], 'Message Status',  readonly=True,default='draft')
    error = fields.Text(string='Last Error', size=256,readonly=True, states={'draft': [('readonly', False)]})
    date_create = fields.Datetime('Date',readonly=True,default=fields.Datetime.now)
    validity = fields.Integer('Validity',help='The maximum time -in minute(s)- before the message is dropped')
    classes=fields.Selection([('0', 'Flash'),
                              ('1', 'Phone display'),
                              ('2', 'SIM'),
                              ('3', 'Toolkit')], 'Class', help='The sms class: flash(0), phone display(1), SIM(2), toolkit(3)')
    
    deferred = fields.Integer(string='Deferred', help='The time -in minute(s)- to wait before sending the message')
    priority=fields.Selection([('0', '0'),
                               ('1', '1'),
                               ('2', '2'),
                               ('3', '3')], 'Priority', help='The priority of the message ')
    coding=fields.Selection([('1', '7 bit'),
                             ('2', 'Unicode')], 'Coding', help='The sms coding: 1 for 7 bit or 2 for unicode')

    tag = fields.Char('Tag', size=256, help='An optional tag')
    nostop = fields.Boolean('NoStop', help='Do not display STOP clause in the message, this requires that this is not an advertising message')


class Properties(models.Model):
    _name = 'sms.smsclient.parms'
    _description = 'SMS Client Properties'
    
    name = fields.Char('Property Name', help='Name of the property whom appear on the URL', size=256)
    value = fields.Char('Property Value', size=256, help='Value associate on the property for the URL')
    gateway_id = fields.Many2one('smsclient', string='SMS Gateway')
    type=fields.Selection([('user', 'User'),
                           ('password', 'Password'),
                           ('sender', 'Sender Name'),
                           ('to', 'Recipient No'),
                           ('sms', 'SMS Message'),
                           ('extra', 'Extra Info')], 'API Method', help='If parameter concern a value to substitute, indicate it')


class HistoryLine(models.Model):
    _name = 'sms.smsclient.history'
    _description = 'SMS Client History'
    
    name = fields.Char('Description', size=160, required=True, readonly=True)
    date_create = fields.Datetime('Date', readonly=True,default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='Username', readonly=True, default=lambda self: self.env.user.id)
    gateway_id = fields.Many2one('smsclient', string='SMS Gateway', required=True)
    to = fields.Char(string='Mobile No', size=15, readonly=True)
    sms = fields.Text(string='SMS', size=160, readonly=True)
    
    def create(self,vals):
        super(HistoryLine, self).create( vals)
        self._cr.commit()
