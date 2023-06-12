# -*- coding: utf-8 -*-
import odoo.http as http
from odoo.http import Response
from string import Template
import sys, json, re
from odoo import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)
from odoo.http import request

class WebFormController(http.Controller):
    
    @http.route('/sending/email/<string:subj>/<string:email>', type='json', auth='public',  csrf=False)
    def send_email(self, subj=False, email=False, **args):
        body=args.get('body',False)
        vals={'subject':subj,'body_html':body,'email_to':email}
        obj_general_sending = request.env['mk.general_sending'].sudo().browse([SUPERUSER_ID])
        sms_send = obj_general_sending.send(vals)

        if sms_send:
            return "Success"
        else:
            return "Failed"

	
    


    @http.route('/sending/email/<string:template_id>', type='json', auth='public',  csrf=False)
    def index(self,template_id='mk_send_pass', **args):
        ids=args.get('ids',False)
        obj_general_sending = request.env['mk.general_sending'].sudo().browse([SUPERUSER_ID])
        a=obj_general_sending.send_by_template(template_id,ids)
        if a:
            return "success"
        else:
            return "failed"

    @http.route('/get/phone/<int:country_id>/<string:phone_number>', type='http', auth='public',  csrf=False)
    def get_phone(self, country_id=False, phone_number=False, **args):
        output=False
        country = request.env['res.country'].sudo().browse([SUPERUSER_ID])
        country_obj = country.browse([country_id])
        obj_general_sending = request.env['mk.general_sending'].sudo().browse([SUPERUSER_ID])
        returned=obj_general_sending.get_phone(phone_number,country_obj, output)
        if returned =="please enter country phone code":
            return "code"
        elif returned =="phone number must contain 9 digits":
            return "digits"
        elif returned =="Please insert phone number and country code":
            return "failed"
        else:
            return returned 

    @http.route('/send/sms/<string:phone_number>', type='json', auth='public',  csrf=False)
    def send_sms(self, phone_number=False, **args):
        message=args.get('message','False')

        obj_general_sending = request.env['mk.general_sending'].sudo().browse([SUPERUSER_ID])
        a=obj_general_sending.send_sms(phone_number,message)
        if a:
            return "success"
        else:
            return "Failed"


    @http.route('/sending/sms/<string:phone_number>/<string:template_code>', type='json', auth='public',  csrf=False)
    def send_sms_by_template(self, phone_number=False, template_code='mk_send_pass', **args):
        value1=args.get('val1',False)
        value2=args.get('val2',False)
        message=request.env['mk.sms_template'].sudo().browse([SUPERUSER_ID]).search([('code', '=', template_code)])
        #message=message.
        message=message[0].sms_text
        if value1!=False:
            message=re.sub(r'val1', value1, message).strip()
        if value2!=False:
            message=re.sub(r'val2', value1, message).strip()
        #d=message
        #message = Template(message)

        
        #message=message.safe_substitute(val1=value1, val2=value2)
        #m2=message.substitute(val1=value1, val2=value2)
        #d=d%(value1)
        obj_general_sending = request.env['mk.general_sending'].sudo().browse([SUPERUSER_ID])
        a=obj_general_sending.send_sms(phone_number,message)
        if a:
            return "success"
        else:
            return "Failed"



                
