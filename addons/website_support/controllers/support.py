# -*- coding: utf-8 -*-
import odoo.http as http
from odoo.http import Response
from odoo import SUPERUSER_ID
import sys, json
import logging
import datetime
import time
_logger = logging.getLogger(__name__)
from odoo.http import request
from odoo import http
class website_support(http.Controller):

    @http.route('/get/ticket/info/<int:center_id>/<int:user_id>/<string:category>/<int:month>/<int:year>', type='json', auth='public',  csrf=False)
    def ticket_info(self,center_id,user_id,category,year,month ,**args):
        sum=0 ; results=[]
        start_y= datetime.datetime(year,month,1, 12,00,00 )
        end_y= datetime.datetime (year,month,30, 12,00,00  )
        state=request.env['website.support.ticket.states'].sudo().search([('name','=','مفتوح')])
        state_an=request.env['website.support.ticket.states'].sudo().search([('name','=','رد الموظفين')])
        state_close=request.env['website.support.ticket.states'].sudo().search([('name','=','التذكرة مغلقة')])
        
        if center_id==0 and user_id==0  and category=='all' :
           

           for st in state:
                 
               count_ticket=request.env['website.support.ticket'].sudo().search_count([('create_date','>=',str (start_y)),('create_date','<=',str(end_y)),('state','=',st.id)])
               results.append({'total_ticket':count_ticket})
           for st_cl in state_close:
          

               close_ticket=request.env['website.support.ticket'].sudo().search_count([('close_time','>=',str (start_y)),('close_time','<=',str(end_y)),('state','=',st_cl.id)])
               results.append({'close_ticket':close_ticket})
           for st_an in state_an: 
               count_answer=request.env['website.support.ticket'].sudo().search_count([('create_date','>=',str (start_y)),('create_date','<=',str(end_y)),('state','=',st_an.id)])
               results.append({'answer':count_answer,'not_answer':count_ticket-count_answer})


        if center_id!=0 and user_id==0 and category=='all' :
           for st in state:
                 
               count_ticket=request.env['website.support.ticket'].sudo().search_count([('create_date','>=',str (start_y)),('create_date','<=',str(end_y)),('state','=',st.id),('center_id','=',center_id)])

               results.append({'total_ticket':count_ticket})
           for st_cl in state_close:
          

               close_ticket=request.env['website.support.ticket'].sudo().search_count([('close_time','>=',str (start_y)),('close_time','<=',str(end_y)),('state','=',st_cl.id),('center_id','=',center_id)])
               results.append({'close_ticket':close_ticket})
           for st_an in state_an: 
               count_answer=request.env['website.support.ticket'].sudo().search_count([('create_date','>=',str (start_y)),('create_date','<=',str(end_y)),('state','=',st_an.id),('center_id','=',center_id)])
               results.append({'answer':count_answer,'not_answer':count_ticket-count_answer})

        if center_id!=0 and user_id!=0  and  category=='all':
           user=request.env['res.users'].sudo().search('department_id','=',center_id)
           for rec in user:
               if user_id==rec.id:
                  for st in state:
               
                      count_ticket=request.env['website.support.ticket'].sudo().search_count([('create_date','>=',str (start_y)),('create_date','<=',str(end_y)),('state','=',st.id),('center_id','=',center_id),('center_id','=',user.department_id.id)])

                      results.append({'total_ticket':count_ticket})
                  for st_cl in state_close:
          

                      close_ticket=request.env['website.support.ticket'].sudo().search_count([('close_time','>=',str (start_y)),('close_time','<=',str(end_y)),('state','=',st_cl.id),('center_id','=',center_id),('close_by_id','=',user_id)])
                      results.append({'close_ticket':close_ticket})
                  for st_an in state_an: 
                      count_answer=request.env['website.support.ticket'].sudo().search_count([('create_date','>=',str (start_y)),('create_date','<=',str(end_y)),('state','=',st_an.id),('center_id','=',center_id),('center_id','=',user.department_id.id)])
                      results.append({'answer':count_answer,'not_answer':count_ticket-count_answer})


        if center_id!=0 and user_id==0  and category!='all' :


                          for st in state:
                              count_ticket=request.env['website.support.ticket'].sudo().search_count([('create_date','>=',str (start_y)),('create_date','<=',str(end_y)),('state','=',st.id),('category_emp','=',category),('center_id','=',center_id)])

                              results.append({'total_ticket':count_ticket})
                          for st_cl in state_close:          

                              close_ticket=request.env['website.support.ticket'].sudo().search_count([('close_time','>=',str (start_y)),('close_time','<=',str(end_y)),('state','=',st_cl.id),('category_emp','=',category),('center_id','=',center_id)])
                              results.append({'close_ticket':close_ticket})
                          for st_an in state_an: 
                              count_answer=request.env['website.support.ticket'].sudo().search_count([('create_date','>=',str (start_y)),('create_date','<=',str(end_y)),('state','=',st_an.id),('category_emp','=',category),('center_id','=',center_id)])
                              results.append({'answer':count_answer,'not_answer':count_ticket-count_answer})
                       
        return str(results)           
           
           


