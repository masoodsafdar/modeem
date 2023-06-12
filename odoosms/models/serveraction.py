# -*- coding: utf-8 -*-
from odoo import models, fields
import time

import logging
_logger = logging.getLogger(__name__)


class ServerAction(models.Model):
    _inherit = 'ir.actions.server'
    
    """
    Possibility to specify the SMS Gateway when configure this server action
    """
        
    def _get_states(self):
        """ Override me in order to add new states in the server action. Please
        note that the added key length should not be higher than already-existing
        ones. """
        return [('code', 'Execute Python Code'),
                ('trigger', 'Trigger a Workflow Signal'),
                ('client_action', 'Run a Client Action'),
                ('object_create', 'Create or Copy a new Record'),
                ('object_write', 'Write on a Record'),
                ('multi', 'Execute several actions'),
                ('sms', 'send sms')]
        
    mobile = fields.Char('Mobile')
    sms_server = fields.Many2one('smsclient', string='SMS Server')
    sms_template_id = fields.Many2one('mail.template', string='SMS Template', help='Select the SMS Template configuration to use with this action')

    def run(self):
        # if context is None:
        #     context = {}
        act_ids = []
        # for action in self.browse([]):
        for action in self:
            if action.state == 'sms':
                obj_pool = self.env[action.model_id.model]
                obj = obj_pool.browse(self._context['active_id'])
                email_template_obj = self.env['mail.template']
                cxt = {'context': self._context,
                       'object': obj,
                       'time': time,
                       'cr': self._cr,
                       'pool': self.pool,
                       'uid': self.env.uid}
                expr = eval(str(action.condition), cxt)
                if not expr:
                    continue
                sms_pool = self.env['smsclient']
                queue_obj = self.env['sms.smsclient.queue']
                mobile = str(action.mobile)
                to = None
                try:
                    cxt.update({'gateway': action.sms_server})
                    gateway = action.sms_template_id.gateway_id
                    if mobile:
                        to = eval(action.mobile, cxt)
                    else:
                        _logger.error('Mobile number not specified !')
                    res_id = self._context['active_id']
                    template = email_template_obj.get_email_template( action.sms_template_id.id, res_id)
                    values = {}
                    for field in ['subject', 'body_html', 'email_from',
                                  'email_to', 'email_recipients', 'email_cc', 'reply_to']:
                        values[field] = email_template_obj.render_template(getattr(template, field),template.model, res_id) or False
                    vals ={'name': gateway.url,
                           'gateway_id': gateway.id,
                           'state': 'draft',
                           'mobile': to,
                           'msg': values['body_html'],
                           'validity': gateway.validity, 
                            'classes': gateway.classes, 
                            'deferred': gateway.deferred, 
                            'priority': gateway.priority, 
                            'coding': gateway.coding,
                            'tag': gateway.tag, 
                            'nostop': gateway.nostop,
                    }
                    sms_in_q = queue_obj.search([
                        ('name','=',gateway.url),
                        ('gateway_id','=',gateway.id),
                        ('state','=','draft'),
                        ('mobile','=',to),
                        ('msg','=',values['body_html']),
                        ('validity','=',gateway.validity), 
                        ('classes','=',gateway.classes), 
                        ('deferred','=',gateway.deferred), 
                        ('priority','=',gateway.priority), 
                        ('coding','=',gateway.coding),
                        ('tag','=',gateway.tag), 
                        ('nostop','=',gateway.nostop)
                        ])
                    # print sms_in_q
                    if not sms_in_q:
                        queue_obj.create(vals)
                except Exception:
                    _logger.error('Failed to send SMS')
            else:
                return super(ServerAction, self).run()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
