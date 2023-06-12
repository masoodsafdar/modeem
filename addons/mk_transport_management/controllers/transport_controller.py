# -*- coding: utf-8 -*-
import odoo.http as http
from odoo.http import Response
from odoo import SUPERUSER_ID
import sys, json
import logging
_logger = logging.getLogger(__name__)
from odoo.http import request
from datetime import datetime,timedelta,date
from dateutil.relativedelta import relativedelta
from odoo import models,fields,api
from openerp import fields
class WebFormController(http.Controller):    
    
    

    @http.route('/register/create/transport/request/days/<int:request_id>', type='json', auth='public',  csrf=False)
    def create_request_days(self,request_id,**args):
        days=args.get('days',[])
        day_ids=[]
        for day in days:
            if day != ',':
                query="""INSERT INTO public.mk_work_days_transportation_request_rel(transportation_request_id, mk_work_days_id) VALUES (%d, %d);""" %(request_id, int(day))
                request.env.cr.execute(query)
            
            
        
        return "True"

    @http.route('/register/get_link_days/from_episode/<int:link_id>', type='json', auth='public',  csrf=False)
    def get_link_days(self,link_id=None,**args):
        link_obj = request.env['mk.link'].sudo().search([('id', '=', link_id)])
        if link_obj:
            return str({'days':link_obj.episode_id.episode_days.ids,'period':link_obj.episode_id.selected_period})

    @http.route('/send/transport/request/<int:rquest_id>', type='json', auth='public',  csrf=False)
    def send_request(self,rquest_id=None,**args):
        request_obj = request.env['transportation.request'].sudo().search([('id', '=', rquest_id)])
        if request_obj:
            request_obj.send_request()
            return "True"
        else:
            return "False"






    
   
    #-------------------------------------------
    


    
