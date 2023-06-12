# -*- coding: utf-8 -*-
import odoo.http as http
from odoo.http import Response
from odoo import SUPERUSER_ID
import sys, json
import logging
import datetime
_logger = logging.getLogger(__name__)
from odoo.http import request
from odoo import http
class mk_episode_managment(http.Controller):
#     @http.route('/mk.student.managment/mk.student.managment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mk.student.managment/mk.student.managment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mk.student.managment.listing', {
#             'root': '/mk.student.managment/mk.student.managment',
#             'objects': http.request.env['mk.student.managment.mk.student.managment'].search([]),
#         })

#     @http.route('/mk.student.managment/mk.student.managment/objects/<model("mk.student.managment.mk.student.managment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mk.student.managment.object', {
#             'object': obj
#         })
    def get_history(self,ep_id):
        records=[]
        self_ob=request.env['mk.episode.program.archive']
        ep_ids=self_ob.search([('episode_id','=',ep_id)])
        for rec in ep_ids:
            rec_dict=({
                'academic_year_id':rec.academic_id.id,
                'academic_year_name':str(rec.academic_id.name),
                'study_class_id':rec.study_class_id.id,
                'study_class_name':str(rec.study_class_id.name),
                'program_id':rec.program_id.id,
                'program_name':str(rec.program_id.name)
                })
            records.append(rec_dict)
        return records

    @http.route('/register/episode_archive/<int:ep_id>', type='json', auth='public',  csrf=False)
    def get_episode_archive(self, ep_id=False, **args):
        #archive_object = request.env['mk.episode.program.archive'].sudo().browse([SUPERUSER_ID])
        ep_history=self.get_history(ep_id)
        records=str(ep_history)
        records=records[:-1]
        records=records[1:]
        return records

    @http.route('/register/episodes/<int:teacher_id>', type='json', auth='public',  csrf=False)
    def get_episodes_for_teacher(self, teacher_id=False, **args):
        result=[]
        episodes = request.env['mk.episode'].sudo().browse([SUPERUSER_ID]).search([('teacher_id', '=', teacher_id), ('state', '=', 'accept')])
        for episode in episodes:
            result.append({'id':episode.id, 'mosque':episode.mosque_id.name, 'name':episode.name, 'status':episode.state})
        return str(result)
    
    @http.route('/register/episodes/run', type='http', auth='public',  csrf=False)
    def get_episodes(self, **args):

        request.env.cr.execute("select  from injaaz_rate(2239)")
        result_dic=request.env.cr.dictfetchall()
        return str(result_dic)



    @http.route('/get/permision/info/<int:center_id>/<string:categ_type>/<int:responsible_id>/<int:year>', type='json', auth='public',  csrf=False)
    def write_permision_info(self,center_id,categ_type,responsible_id,year, **args):
        sum=0 ; results=[]
        start_y=datetime.date(year,1,1)
        end_y=datetime.date(year,12,31)

        if center_id==0 and categ_type=='all' and responsible_id==0 :
            count_d=request.env['mosque.permision'].sudo().search_count([('state','=','draft'),('date_request','>=',start_y),('date_request','<=',end_y)]) 
            count_r=request.env['mosque.permision'].sudo().search_count([('state','=','review'),('date_request','>=',start_y),('date_request','<=',end_y)]) 
            count_renew=request.env['mosque.permision'].sudo().search_count([('state','=','renew'),('date_request','>=',start_y),('date_request','<=',end_y)]) 
            count_accept=request.env['mosque.permision'].sudo().search_count([('state','=','accept'),('date_request','>=',start_y),('date_request','<=',end_y)]) 
            count_reject=request.env['mosque.permision'].sudo().search_count([('state','=','reject'),('date_request','>=',start_y),('date_request','<=',end_y)])
            count_f=request.env['mosque.permision'].sudo().search_count([('state','=','tajmeed'),('date_request','>=',start_y),('date_request','<=',end_y)])
            count_t=request.env['mosque.permision'].sudo().search_count([('state','=','new'),('date_request','>=',start_y),('date_request','<=',end_y)]) 
            sum=count_d+count_r+count_renew+count_accept+count_reject+count_f+count_t
            results.append({'draft':count_d})
            results.append({'review':count_r})
            results.append({'tempary':count_renew})
            results.append({'permanat':count_accept})
            results.append({'reject':count_reject})
            results.append({'firze':count_f})
            results.append({'renew':count_t})
            results.append({'sum':sum})




        if center_id!=0 and categ_type=='all' :
            count_d=request.env['mosque.permision'].sudo().search_count([('state','=','draft'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id)]) 
            count_r=request.env['mosque.permision'].sudo().search_count([('state','=','review'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id)]) 
            count_renew=request.env['mosque.permision'].sudo().search_count([('state','=','renew'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id)]) 
            count_accept=request.env['mosque.permision'].sudo().search_count([('state','=','accept'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id)]) 
            count_reject=request.env['mosque.permision'].sudo().search_count([('state','=','reject'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id)])
            count_f=request.env['mosque.permision'].sudo().search_count([('state','=','tajmeed'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id)])
            count_t=request.env['mosque.permision'].sudo().search_count([('state','=','new'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id)]) 
            sum=count_d+count_r+count_renew+count_accept+count_reject+count_f+count_t

            results.append({'draft':count_d})
            results.append({'review':count_r})
            results.append({'tempary':count_renew})
            results.append({'permanat':count_accept})
            results.append({'reject':count_reject})
            results.append({'firze':count_f})
            results.append({'renew':count_t})
            results.append({'sum':sum})


        if center_id!=0 and categ_type!='all' and responsible_id==0 :            
            count_d=request.env['mosque.permision'].sudo().search_count([('state','=','draft'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id),('categ_type','=',categ_type)]) 
            count_r=request.env['mosque.permision'].sudo().search_count([('state','=','review'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id),('categ_type','=',categ_type)]) 
            count_renew=request.env['mosque.permision'].sudo().search_count([('state','=','renew'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id),('categ_type','=',categ_type)]) 
            count_accept=request.env['mosque.permision'].sudo().search_count([('state','=','accept'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id),('categ_type','=',categ_type)]) 
            count_reject=request.env['mosque.permision'].sudo().search_count([('state','=','reject'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id),('categ_type','=',categ_type)])
            count_f=request.env['mosque.permision'].sudo().search_count([('state','=','tajmeed'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id),('categ_type','=',categ_type)])
            count_t=request.env['mosque.permision'].sudo().search_count([('state','=','new'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id),('categ_type','=',categ_type)]) 
            sum=count_d+count_r+count_renew+count_accept+count_reject+count_f+count_t
            results.append({'draft':count_d})
            results.append({'review':count_r})
            results.append({'tempary':count_renew})
            results.append({'permanat':count_accept})
            results.append({'reject':count_reject})
            results.append({'firze':count_f})
            results.append({'renew':count_t})
            results.append({'sum':sum})

           
        if center_id!=0 and categ_type!='all' and responsible_id!=0:
            mosque=request.env['mk.mosque'].sudo().search([('responsible_id','=',responsible_id)])
            for record in mosque:


                   count_d=request.env['mosque.permision'].sudo().search_count([('state','=','draft'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id),('categ_type','=',categ_type),('masjed_id','=',record.id)]) 
                   count_r=request.env['mosque.permision'].sudo().search_count([('state','=','review'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id),('categ_type','=',categ_type)]) 
                   count_renew=request.env['mosque.permision'].sudo().search_count([('state','=','renew'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id),('categ_type','=',categ_type),('masjed_id','=',record.id)]) 
                   count_accept=request.env['mosque.permision'].sudo().search_count([('state','=','accept'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id),('categ_type','=',categ_type),('masjed_id','=',record.id)]) 
                   count_reject=request.env['mosque.permision'].sudo().search_count([('state','=','reject'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id),('categ_type','=',categ_type),('masjed_id','=',record.id)])
                   count_f=request.env['mosque.permision'].sudo().search_count([('state','=','tajmeed'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id),('categ_type','=',categ_type),('masjed_id','=',record.id)])
                   count_t=request.env['mosque.permision'].sudo().search_count([('state','=','new'),('date_request','>=',start_y),('date_request','<=',end_y),('center_id','=',center_id),('categ_type','=',categ_type),('masjed_id','=',record.id)]) 
                   sum=count_d+count_r+count_renew+count_accept+count_reject+count_f+count_t
                   results.append({'draft':count_d})
                   results.append({'review':count_r})
                   results.append({'renew':count_renew})
                   results.append({'accept':count_accept})
                   results.append({'reject':count_reject})
                   results.append({'sum':count_reject}) 
                   results.append({'firze':count_f})
                   results.append({'renew':count_t})                                  
                   results.append({'sum':sum})
        
        return str(results)

    @http.route('/get/suprvisor/permision/state/<int:center_id>/<int:responsible_id>/<int:year>', type='json', auth='public',  csrf=False)
    def get_permision_info(self,center_id,responsible_id,year, **args):
        result=[]
        start_y=datetime.date(year,1,1)
        end_y=datetime.date(year,12,31)
        mosque=request.env['mk.mosque'].sudo().search([('center_department_id','=',center_id),('responsible_id','=',responsible_id)])
        for record in mosque:
            msjed = request.env['mosque.permision'].sudo().browse([SUPERUSER_ID]).search([('masjed_id', '=', record.id),('date_request','>=',start_y),('date_request','<=',end_y)])
            for sup in msjed:
                result.append({'name':sup.masjed_id.name,'state':sup.state})
        return str(result)
  
    @http.route('/get/suprvisor/permision/info/<int:masjed_id>/<int:responsible_id>/<int:year>', type='json', auth='public',  csrf=False)
    def get_permision_state_for_masjed(self, masjed_id,responsible_id,year, **args):
        result=[]
        start_y=datetime.date(year,1,1)
        end_y=datetime.date(year,12,31)
        msjed = request.env['mosque.permision'].sudo().browse([SUPERUSER_ID]).search([('masjed_id', '=', masjed_id),('date_request','>=',start_y),('date_request','<=',end_y)])
        #responsible= request.env['mk.mosque'].sudo().browse([SUPERUSER_ID]).search([('responsible_id', '=',responsible_id)])
        responsib= request.env['mosque.supervisor.request'].sudo().browse([SUPERUSER_ID]).search([('employee_id', '=',responsible_id),('date_request','>=',start_y),('date_request','<=',end_y)])
 
        if masjed_id and year:
            for rec in msjed:
                result.append({'name':rec.masjed_id.name,'state':rec.state})
        if responsible_id and year:
            for mosq in responsib:
                #msjed = request.env['mosque.permision'].sudo().browse([SUPERUSER_ID]).search([('masjed_id', '=', mosq.id)], limit=1)
                #result.append({'state':msjed.state,'name':mosq.name})
                result.append({'name':mosq.employee_id.name,'state':mosq.state})
        return str(result)
    @http.route('/super/add_mosque/<int:target_id>/<int:masjed_id>',type='json',auth='public',csrf=False)
    def add_mosque_id(self,target_id,masjed_id,**args):
        sup_recs = request.env['mosque.supervisor.request'].sudo().search([('id','=',target_id)])
        for sup in sup_recs:
            sup.update({'mosque_ids':[(4,masjed_id)]})
        return "done"

        

                   
          



