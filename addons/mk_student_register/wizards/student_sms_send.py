# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011 SYLEAM (<http://syleam.fr/>)
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#    Copyright (C) 2015 SIAT TUNISIE <contact@siat.com.tn>
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
import time
import urllib
from odoo.osv import fields, orm
from odoo.tools.translate import _

import logging
class student_sms_send(orm.Model):
    _name = "student.sms.send"

    def _default_get_mobile(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        
        partner_pool = self.pool.get('mk.student.register')
        active_ids = fields.get('active_ids')
        ##"active_ids//////////////////////////////////////", active_ids
        res = {}
        i = 0
        for partner in partner_pool.browse(cr, uid, active_ids, context=context): 
            i += 1           
            res = partner.mobile
            ##"/////////////////////////mobile", res
        if i > 1:
            raise orm.except_orm(_('Error'), _('You can only select one student'))
        return res

    def _default_get_gateway(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        sms_obj = self.pool.get('sms.smsclient')
        gateway_ids = sms_obj.search(cr, uid, [], limit=1, context=context)
        return gateway_ids and gateway_ids[0] or False

    def onchange_gateway(self, cr, uid, ids, gateway_id, context=None):
        if context is None:
            context = {}
        sms_obj = self.pool.get('sms.smsclient')
        if not gateway_id:
            return {}
        gateway = sms_obj.browse(cr, uid, gateway_id, context=context)
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

    _columns = {
        'mobile_to': fields.char('To', size=256, required=True),
        'app_id': fields.char('API ID', size=256),
        'user': fields.char('Login', size=256),
        'password': fields.char('Password', size=256),
        'text': fields.text('SMS Message', required=True),
        'gateway': fields.many2one('sms.smsclient', 'SMS Gateway', required=True,ondelete="restrict",),
        'validity': fields.integer('Validity',
            help='the maximum time -in minute(s)- before the message is dropped'),
        'classes': fields.selection([
                ('0', 'Flash'),
                ('1', 'Phone display'),
                ('2', 'SIM'),
                ('3', 'Toolkit')
            ], 'Class', help='the sms class: flash(0), phone display(1), SIM(2), toolkit(3)'),
        'deferred': fields.integer('Deferred',
            help='the time -in minute(s)- to wait before sending the message'),
        'priority': fields.selection([
                ('0','0'),
                ('1','1'),
                ('2','2'),
                ('3','3')
            ], 'Priority', help='The priority of the message'),
        'coding': fields.selection([
                ('1', '7 bit'),
                ('2', 'Unicode')
            ], 'Coding', help='The SMS coding: 1 for 7 bit or 2 for unicode'),
        'tag': fields.char('Tag', size=256, help='an optional tag'),
        'nostop': fields.boolean('NoStop', help='Do not display STOP clause in the message, this requires that this is not an advertising message'),
    }

    _defaults = {
        'mobile_to': _default_get_mobile,
        'gateway': _default_get_gateway,        
    }

    
    def sms_send(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        client_obj = self.pool.get('sms.smsclient')
        for data in self.browse(cr, uid, ids, context=context):
            if not data.gateway:
                raise orm.except_orm(_('Error'), _('No Gateway Found'))
            else:
                client_obj._send_message(cr, uid, data, context=context)
        return {}
     
