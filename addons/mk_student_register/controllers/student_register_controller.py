# -*- coding: utf-8 -*-
import odoo.http as http
from odoo.http import Response
from odoo import SUPERUSER_ID
import sys, json
import logging
from random import randint
import re
_logger = logging.getLogger(__name__)
from odoo.http import request
from datetime import datetime,timedelta,date
from dateutil.relativedelta import relativedelta
from odoo import models,fields,api
# from odoo import fields
from passlib.context import CryptContext
class WebFormController(http.Controller):    
    
    default_crypt_contex = CryptContext(
    # kdf which can be verified by the context. The default encryption kdf is
    # the first of the list
    ['pbkdf2_sha512', 'md5_crypt'],
    # deprecated algorithms are still verified as usual, but ``needs_update``
    # will indicate that the stored hash should be replaced by a more recent
    # algorithm. Passlib 1.6 supports an `auto` value which deprecates any
    # algorithm but the default, but Ubuntu LTS only provides 1.5 so far.
    deprecated=['md5_crypt'],
    )

    def _getDefault_academic_year(self):
       #self.ensure_one()
        academic_recs = request.env['mk.study.year'].sudo().search([('is_default','=',True),('active','=',True)])       

        if academic_recs:
            return academic_recs[0].id          
        return False

    @http.route('/register/comment/get_punishment/<int:comment_id>', type='json', auth='public',  csrf=False)
    def get_punish_comment(self, comment_id,**args):
        result = []
        comments = request.env['mk.comment.behavior'].sudo().search([('id','=',comment_id)],limit=1)
        for rec in comments.punishment_ids:
            result.append({'id':rec.id, 'name':rec.name})
        return str(result)

    def get_default_study_class(self):
        study_class_ids=request.env['mk.study.class'].sudo().search([('study_year_id', '=', self._getDefault_academic_year()),('is_default', '=', True)])


        if study_class_ids:

            return study_class_ids.ids[0]
        else:

            return False


    @http.route('/register/get_link_days/<int:link_id>', type='json', auth='public',  csrf=False)
    def get_link_days(self,link_id=None,**args):
        link_obj = request.env['mk.link'].sudo().search([('id', '=', link_id)])

        if link_obj:
            return str({'days':link_obj.student_days.ids,'period':link_obj.selected_period})

    @http.route('/register/allowed_menus/<int:user_id>', type='json', auth='public',  csrf=False)
    def get_parent(self,user_id,**args):
        query="""select id, name, action from ir_ui_menu where parent_id is null and id in (select menu_id from ir_ui_menu_group_rel where gid in (select gid from res_groups_users_rel where uid = %d));""" %(user_id)
        request.env.cr.execute(query)
        result_dic=request.env.cr.dictfetchall()
        query2="""select id, name ,action from ir_ui_menu where parent_id is null and id not in (select menu_id from ir_ui_menu_group_rel)""" 
        request.env.cr.execute(query2)
        result=request.env.cr.dictfetchall()
        parent_menus=result+result_dic
        for menu in parent_menus:
            if menu['action']:
                menu['action']=menu['action'].strip('ir.actions.act_window,')
            query3="""select id , sequence, action from ir_ui_menu where parent_id = %d order by sequence limit 1;""" %(menu['id'])
            request.env.cr.execute(query3)
            result_no_action=request.env.cr.dictfetchall()
            if result_no_action:
                if result_no_action[0]['action']:
                    menu['first_child']= result_no_action[0]['id']
                    menu['action']=result_no_action[0]['action'].strip('ir.actions.act_window,')
                else:
                    query4="""select id , sequence, action from ir_ui_menu where parent_id = %d and action is not null order by sequence limit 1;""" %(result_no_action[0]['id'])
                    request.env.cr.execute(query4)
                    result_action=request.env.cr.dictfetchall()
                    if result_action:
                        if result_action[0]['action']:
                            menu['first_child']= result_action[0]['id']
                            menu['action']=result_action[0]['action'].strip('ir.actions.act_window,')
        for rec in parent_menus:
            if rec['action']==None:
                rec['action']=False
        return str(parent_menus)

    
    @http.route('/register/get_account_banks/<int:partner_id>', type='json', auth='public',  csrf=False)
    def get_account_banks(self,partner_id=None,**args):
        result =[]
        a=''
        bank_name=''
        partner_obj = request.env['res.partner'].sudo().search([('id', '=', partner_id)])
        banking_accounts=request.env['account.bank'].sudo().search([('id', 'in', partner_obj.banking_accounts.ids)])
        for account in banking_accounts:
            state=False            
            if account.state:
                state=account.state
            if account.bank_id.name:
                bank_name=account.bank_id.name
            ###"******************************", bank_name, state, account.state, account.bank_id.name
            result.append({'id':account.id,'account_number':account.account_no,'account_owner_name':account.account_owner_name, 'account_state':state, 'bank_id':account.bank_id.id, 'bank_name':str(bank_name)})
        # for r in result:
        #t     a+=str(r)+','
        #     a=a[:-1]
        return str(result)

    def list1InList2(self,list1, list2):
        if len(list1)==0 or len(list2)==0:
            return False
        for item in list1:
            if item not in list2:
                return False
        return True


    # CHECK EPISODE OCCPY

    def check_episode_occpy(self,episode_id):
        academic_year = request.env['mk.study.year'].sudo().search([('active','=',True)])
        obj_episode=request.env['mk.episode'].sudo().browse([int(episode_id)])
        episode = []
        for episode_year in academic_year:
            ###'academic',episode_year
            episode_search = request.env['mk.link'].sudo().search([('episode_id','=',int(obj_episode.id)),('year','=',episode_year.id)])
            count = len(episode_search)
            if (obj_episode.expected_students - count) > 0:
               return True
        return False
    #
    # Filter Episodes
    def filter_episodes(self, mosque_id):
        list_epis= []
        epi_msjd = request.env['mk.episode'].sudo().search([('mosque_id','=',int(mosque_id))])
        for epi_rec in  epi_msjd:
            if self.check_episode_occpy(epi_rec.id):
                list_epis.append(epi_rec.id)
        return list_epis

    @http.route('/note/<int:teacher>/<int:eposide>/<int:student_id>/<int:punish>/<int:comment>', type='json', auth='public',  csrf=False)
    def attendance_c(self,teacher,eposide,student_id,punish,comment,**args):

         #comment=args.get('comment','False')
         #punish=args.get('punish','False')
         epi_msjd = request.env['mk.episode'].sudo().search([('id','=',int(eposide))]).parent_episode.mosque_id.id

         obj_beh=request.env['mk.comments.behavior.students'].sudo().search([('teacher','=',teacher),('episode','=',eposide),('masjed','=',epi_msjd)])

         if obj_beh:
            for rec in obj_beh:
                rec.write({'student_ids':[(0,0,{'student':student_id,'comment_id':comment,'punishment_id':
		punish})]        })
         else:

              request.env['mk.comments.behavior.students'].sudo().create({'date':fields.Date.today(),'masjed':epi_msjd,'episode':eposide,'teacher':teacher,'student_ids':[(0,0,{'student':student_id,'comment_id':comment,'punishment_id':
		punish})]        })
         return str(True)
         
    @http.route('/register/filter_mosque/<string:area>/<string:district>/<string:purpose_id>', type='json', auth='public',  csrf=False)
    def filter_mosque_c(self,area, district=False,purpose_id='memorize_quran',**args):
        result=[]
        obj_res_partner=request.env['mk.student.register'].sudo().browse([SUPERUSER_ID])
        list_mosq= []
        list_mosq2=[]
        list_epis= []
        list_parts=[]
        list_suars=[]
        result2={}
        gender=args.get('gender','male')
        job_id=args.get('job',False)
        stage_id=args.get('grade',False)
        if district=='False' or district==False:

            for mosq in request.env['mk.mosque'].sudo().search([('area_id','=',int(area))]):

                epi_mosq = request.env['mk.episode'].sudo().search([('mosque_id','=',mosq.id),('state','=','accept')])

                for epi_rec in epi_mosq:

                    if self.check_episode_occpy(epi_rec.id):

                        if mosq.categ_id.mosque_type=='male':
                           list_mosq2.append({'mosque_id':mosq.id,'mosque_name':mosq.name ,'lat':mosq.latitude,'long':mosq.longitude,'type':mosq.categ_id.mosque_type})
                        if mosq.categ_id.mosque_type=='female':
                            list_mosq.append({'mosque_id':mosq.id,'mosque_name':mosq.name ,'lat':mosq.latitude,'long':mosq.longitude,'type':mosq.categ_id.mosque_type})
                        break
                      
        elif area:
            for mosq in request.env['mk.mosque'].sudo().search([('district_id','=',int(district)),('state','=','accept')]):
                epi_mosq = request.env['mk.episode'].sudo().search([('mosque_id','=',mosq.id)])
                for epi_rec in epi_mosq:
               
                    if self.check_episode_occpy(epi_rec.id):
                        if mosq.categ_id.mosque_type=='male':
                           list_mosq2.append({'mosque_id':mosq.id,'mosque_name':mosq.name ,'lat':mosq.latitude,'long':mosq.longitude,'type':mosq.categ_id.mosque_type})
                        if mosq.categ_id.mosque_type=='female':
                            list_mosq.append({'mosque_id':mosq.id,'mosque_name':mosq.name ,'lat':mosq.latitude,'long':mosq.longitude,'type':mosq.categ_id.mosque_type})
                        break;
        result2={'male':list_mosq2,'female':list_mosq}
        return str(result2)

    @http.route('/register/filter_episodes/<string:mosque>', type='json', auth='public',  csrf=False)
    def filter_episodes(self,mosque=None,**args):
        result=[]
        #obj_filter = request.env['mk.student.register'].sudo().browse([SUPERUSER_ID])
        result = self.filter_episodes(mosque)
        return str(result)

    @http.route('/register/check_episode_occpy/<string:episode>', type='json', auth='public',  csrf=False)
    def check_episode_occpy_n(self,episode=None,**args):
        result =[]
        #obj_episode = request.env['mk.student.register'].sudo().browse([SUPERUSER_ID])
        return str(self.check_episode_occpy(episode))
        
    # CHECK STUDENT EMAIL
    def check_student_email(self,email):
        obj_res_partner = request.env['mk.student.register']
        student_search = obj_res_partner.search([('is_student', '=', True)])
        for student in student_search:
            if student.email == email:
               return False
        return True    
    # CHECK STUDENT MOBILE
    def check_student_mobile(self,mobile):
        obj_res_partner = request.env['mk.student.register']
        student_search = obj_res_partner.search([('is_student', '=', True)])
        for student in student_search:
            if student.mobile == mobile:
               return False
        return True
    # CHECK PARENT EMAIL
    def check_parent_email(self,email):
        obj_res_partner = request.env['res.partner']
        parent_search = obj_res_partner.search([('is_student', '=', False)])
        for parent in parent_search:
            if parent.email == email:
                return False
        return True
    #CHECK PARENT MPBILE
    def check_parent_mobile(self,mobile):
        obj_res_partner = request.env['res.partner']
        #obj_std = request.env['mk.student.register']
        #brw = obj_std.browse(mobile)
        parent_search = obj_res_partner.search([('is_student', '=', False)])
        for parent in parent_search:
            if parent.mobile == mobile:
                return False
        return True

    @http.route('/register/validate/<string:person>/<string:check>/<string:value>', type='json', auth='public',  csrf=False)
    def index(self,person=None,check=None,value=None,**args):
        # get portal user record of patner to access all modules functions
        #obj_res_partner = request.env['mk.student.register'].sudo().browse([SUPERUSER_ID])
        if person=="student":
            if check=="email":
                return str(self.check_student_email(value))
            else:
                return str(self.check_student_mobile(value))
        elif person=="parent":
            if check=="email":                
                return str(self.check_parent_email(value))
            else:
                return str(self.check_parent_mobile(value))
        return str(False)

    @http.route('/register/get_registration_code/<string:registration_type>', type='json', auth='public',  csrf=False)
    def get_registration_code(self,registration_type=None,**args):
        # get portal user record of patner to access all modules functions
        code=""
        if registration_type=="parent":
            code=request.env['ir.sequence'].get('mk.perant.serial')
        if registration_type=="student":
            code=request.env['ir.sequence'].get('mk.student.serial')
        if registration_type=="teacher":
            code=request.env['ir.sequence'].get('mk.ep.teacher.serial')
        if registration_type=="mosque_responsiable":
            code=request.env['ir.sequence'].get('mk.mosque.responsiable.serial')
        if registration_type=="mosque_supervisor":
            code=request.env['ir.sequence'].get('mk.mosque.supervisor.serial')
        if registration_type=="center_manager":
            code=request.env['ir.sequence'].get('mk.center.manager.serial')
        if registration_type=="mosque":
            code=request.env['ir.sequence'].get('mk.mosque.serial')
        return str({'register_code':code})
    # SERACH METHODS
    def search_for_days_controllers(self,days):
        episode_model=request.env['mk.episode']
        episode_ids=episode_model.search([])
        l=[]
        ep_ids=[]
        for d in days:
            for episds in episode_ids:
                for dayss in episds.episode_days:

                    if dayss.id == int(d):
                        if episds.id not in ep_ids:
                            ep_ids.append(episds.id)
                            l.append(episds.id)
        return l

    def search_occupy_episode_controller(self):
        res=[]
        episodes=[]
        episode_ids=request.env['mk.episode'].sudo().search([])
        for episode in episode_ids:
            link_ids=request.env['mk.link'].sudo().search([('episode_id', '=', episode.id), ('state', '!=', 'reject')])
            res.append({'id':episode.id, 'students':len(link_ids), 'unoccupied':episode.episode_type.students_no-len(link_ids)})
            if episode.episode_type.students_no-len(link_ids):
                episodes.append(episode.id)    

        return episodes 

    def search_episode_by_periods_controller(self,periods):
        res=[]
        episode=[]
        episodes=request.env['mk.episode'].sudo().search([])            
        for rec in episodes:
            for record in periods:
                if record=='s':
                    if rec.subh==True:
                        if rec.id not in res:
                            res.append(rec.id)
                if record=='z':
                    if rec.zuhr==True:
                        if rec.id not in res:
                            res.append(rec.id)
                
                if record=='a':
                    if rec.aasr==True:
                        if rec.id not in res:
                            res.append(rec.id)
                if record=='m':
                    if rec.magrib==True:
                        if rec.id not in res:
                            res.append(rec.id)
                if record=='e':
                    if rec.esha==True:
                        if rec.id not in res:
                            res.append(rec.id)
        return res

    def search_episode_by_gender_controller(self,gender):
        if gender == 'men':
            episode_ids=request.env['mk.episode'].sudo().search([('women_or_men','=','men')]).ids
        else:
            episode_ids=request.env['mk.episode'].sudo().search([('women_or_men','=','women')]).ids
        return episode_ids

    def domain_episodes_controller(self,grade_id,job_id):
        res=[]
        episodes=request.env['mk.episode'].sudo().search([])
        for episode in episodes:
            
            if (job_id in episode.job_ids.ids or episode.job_ids.ids==[] or job_id==False) and (grade_id in episode.grade_ids.ids or episode.grade_ids.ids==[] or grade_id==False):
                res.append(episode.id)
        
            #for grade in episode.grade_ids:
        return res
        #res={'domain':{'search_line':[('mosque_id', 'in', msjd_id.ids),('id', 'in', stages)]}}


    def controller_main_search_for_episode(self,days,grade,job,gender,periods):
        """
        res=[]
        grade_job=self.domain_episodes_controller(grade,job)
        gender=self.search_episode_by_gender_controller(gender)
        period=self.search_episode_by_periods_controller(periods)
        seat=self.search_occupy_episode_controller()
        days=self.search_for_days_controllers(days) 
        ret= list(set(period).intersection(grade_job))
       
        days_occupy= list(set(gender).intersection(seat))
        days_period_grade= list(set(ret).intersection(days_occupy))
        result= list(set(days).intersection(days_period_grade))
        return result
        """
        res=[]
        days=[d for d in days]
        domain=[('state', '=', 'accept'), ('episode_days', 'in', days)]
        episode_ids=[]
        
        if gender == 'men':
            domain.append(('women_or_men','=','men'))

        else:

            domain.append(('women_or_men','=','women'))

        episodes=request.env['mk.episode'].search(domain)   
        for episode in episodes:           
            if (job in episode.job_ids.ids or episode.job_ids.ids==[] or job==False) and (grade in episode.grade_ids.ids or episode.grade_ids.ids==[] or grade==False):
                    res.append(episode)
    
        period=self.search_episode_by_periods_controller(res)
        
        period_objs=request.env['mk.episode'].search([('id', 'in',period)])   

        seat=self.search_occupy_episode_controller(period_objs)

       
        
        return seat.ids


    #-------------------
    @http.route('/register/search_for_episodes/', type='json', auth='public',  csrf=False)
    def search_for_episodes(self,**args):
        result=[]
        days=args.get('days',[])

        job_id=args.get('job_id',False)
        grade_id=args.get('grade_id',False)
        gender=args.get('gender',False)
        periods=args.get('periods',[])

        #obj_search = request.env['mk.search.episode'].sudo().browse([SUPERUSER_ID])
        result = self.controller_main_search_for_episode(days,int(grade_id),int(job_id),str(gender),
            periods)

        return str(result)
    #-------------------------------------------
    def link_prepare(self,student_id,ep_id):
        dic = {}
        lst = []
        l_days = []
        p_dates = []
        test_lst = []
        l_parts = []
        
        st=request.env['mk.link'].sudo().search([('id','=',student_id)])
        if st:

        ##ep_id, 'linkllllllllllllllllllllllllll'
            for day in st[0].student_days:
                l_days.append(day.order) 
        
        obj_subj = request.env['mk.subject.configuration']
        obj_prepare = request.env['mk.student.prepare']
        #obj_verses = request.env['mk.surah.verse']
        obj_page = request.env['mk.subject.page']
        obj_verse = request.env['mk.surah.verses']
        count = 0
        subject_ids = obj_subj.search([('approach_id','=', st[0].approache.id)], order='order asc')
        from_aya = False
        to_aya = False
        for s in subject_ids:
            if count == 0:
                from_aya = s.detail_id.from_verse
            to_aya = s.detail_id.to_verse
            count +=1
        if from_aya and to_aya and st[0] and st[0].page_id:    
            page_ids = obj_page.search([('from_verse.original_accumalative_order','>=', from_aya.original_accumalative_order),('to_verse.original_accumalative_order','<=', to_aya.original_accumalative_order),('subject_page_id','=', st[0].page_id.id)], order='id desc')
            c = 0
            cc = 0
            start_date =datetime.strptime(fields.Date.today(), '%Y-%m-%d') 
            check_test = False
            p_count= 0
            sub_test = []
            for pp in page_ids:
                p_count += 1
            for sub in subject_ids:
                if sub.is_test:
                    check_test = True
                    p_count += 1
                    sub_test.append(sub)
            if l_days:

                while(p_count != 0):
                    if start_date.weekday() not in l_days:
                        start_date =(start_date+relativedelta(days=1))
                    else:
                        p_dates.append({'d':str(start_date.weekday()),'dt':start_date})
                        p_count -= 1
                        start_date =(start_date+relativedelta(days=1))

            if not check_test:           
                
                for p in page_ids:

                    c+=1
                    cc+=1
                    lst.append(

                        (0,0,

                            {
                              'date':p_dates and p_dates[cc-1]['dt'] or False,
                              'day':p_dates and p_dates[cc-1]['d'] or False,
                              'order':c,
                              'from_surah':p.from_surah.id,
                              'from_aya':p.from_verse.id,
                              'to_surah':p.to_surah.id,
                              'to_aya':p.to_verse.id,
                              'type_follow':'listen',
                              'student_id':st[0].id,

                            }


                            )
                        )
            else:
                subj_lst = []
                for p in page_ids:

                    c+=1
                    cc+=1
                    is_test = False

                    for subj in sub_test:
                        if subj not in subj_lst:
                            if subj.detail_id.to_verse.original_accumalative_order == p.to_verse.original_accumalative_order :
                               is_test = True
                               subj_lst.append(subj)
                               break
                            if p.from_verse.original_accumalative_order > subj.detail_id.to_verse.original_accumalative_order:
                               subj_lst.append(subj)
                               lst_len = len(lst)
                               if lst_len >0:
                                    lst[lst_len - 1][2].update({'is_test':True})
                                    test_lst.append(

                                        (0,0,

                                            {
                                              'date':p_dates and p_dates[cc-1]['dt'] or False,
                                              'day':p_dates and p_dates[cc-1]['d'] or False,
                                              #'order':c,
                                              'subject_id':subj.id,
                                             
                                            }


                                            )
                                        )
                                    cc+=1
                               break

                    lst.append(

                        (0,0,

                            { 'is_test':is_test,
                              'date':p_dates and p_dates[cc-1]['dt'] or False,
                              'day':p_dates and p_dates[cc-1]['d'] or False,
                              'order':c,
                              'from_surah':p.from_surah.id,
                              'from_aya':p.from_verse.id,
                              'to_surah':p.to_surah.id,
                              'to_aya':p.to_verse.id,
                              'type_follow':'listen',
                              'student_id':st[0].id,
                            }


                            )
                        )
                    if is_test:
                        cc+=1
                        test_lst.append(

                            (0,0,

                                {
                                  'date':p_dates and p_dates[cc-1]['dt'] or False,
                                  'day':p_dates and p_dates[cc-1]['d'] or False,
                                  #'order':c,
                                  'subject_id':subj.id,
                                 
                                }


                                )
                            )
                for subj in sub_test:
                    if subj not in subj_lst:
                        cc+=1
                        lst_len = len(lst)
                        if lst_len >0:
                            lst[lst_len - 1][2].update({'is_test':True})
                        test_lst.append(

                            (0,0,

                                {
                                  'date':p_dates and p_dates[cc-1]['dt'] or False,
                                  'day':p_dates and p_dates[cc-1]['d'] or False,
                                  #'order':c,
                                  'subject_id':subj.id,
                                 
                                }


                                )
                            )
       
        min_list= []
        min_list_last= []
        max_list= []
        max_list_last= []
        read_list=[]
        read_list_last= []

        if st[0].approache.program_id.minimum_audit == True:
            min_list=lst
            min_quant= st[0].approache.lessons_minimum_audit
            if min_quant > 0:
                min_from_verse= False
                min_to_verse= False
                min_count= 0
                counte = 0
                for mi in min_list:
                    min_count +=1 
                    if not min_from_verse:
                        min_from_verse = mi[2]['from_aya']
                    if min_count== min_quant:
                        counte +=1
                        min_to_verse= mi[2]['to_aya']
                        min_list_last.append(

                                        (0,0,{
                                                 #'is_test':is_test,
                                                  'date':mi[2]['date'],
                                                  'day':mi[2]['day'],
                                                  'order':counte,
                                                  'from_surah':obj_verse.browse(min_from_verse).surah_id.id,
                                                  'from_aya':min_from_verse,
                                                  'to_surah':obj_verse.browse(min_to_verse).surah_id.id,
                                                  'to_aya':min_to_verse,
                                                  'type_follow':'review_small',
                                                  'student_id':mi[2]['student_id'],

                                            }


                                            )

                            )
                        min_count= 0
                        min_to_verse= False
                        min_from_verse= False
                if min_list and ((len(min_list)%min_quant !=0 )):
                    mi = min_list[len(min_list)-1]
                    counte +=1
                    if not min_from_verse:
                        min_from_verse= mi[2]['from_aya']
                    min_to_verse= mi[2]['to_aya']
                    min_list_last.append(

                                    (0,0,{
                                             #'is_test':is_test,
                                              'date':mi[2]['date'],
                                              'day':mi[2]['day'],
                                              'order':counte,
                                              'from_surah':obj_verse.browse(min_from_verse).surah_id.id,
                                              'from_aya':min_from_verse,
                                              'to_surah':obj_verse.browse(min_to_verse).surah_id.id,
                                              'to_aya':min_to_verse,
                                              'type_follow':'review_small',
                                              'student_id':mi[2]['student_id'],

                                        }


                                        )

                        )







        if st[0].approache.program_id.maximum_audit == True:
            max_list=lst

            max_quant= st[0].approache.lessons_maximum_audit
            if max_quant > 0:
                max_from_verse= False
                max_to_verse= False
                max_count= 0
                counte = 0
                for mi in max_list:
                    max_count +=1 
                    if not max_from_verse:
                        max_from_verse = mi[2]['from_aya']
                    if max_count== max_quant:
                        counte +=1
                        max_to_verse= mi[2]['to_aya']
                        max_list_last.append(

                                        (0,0,{
                                                 #'is_test':is_test,
                                                  'date':mi[2]['date'],
                                                  'day':mi[2]['day'],
                                                  'order':counte,
                                                  'from_surah':obj_verse.browse(max_from_verse).surah_id.id,
                                                  'from_aya':max_from_verse,
                                                  'to_surah':obj_verse.browse(max_to_verse).surah_id.id,
                                                  'to_aya':max_to_verse,
                                                  'type_follow':'review_big',
                                                  'student_id':mi[2]['student_id'],

                                            }


                                            )

                            )
                        max_count= 0
                        max_to_verse= False
                        max_from_verse= False
                if  max_list and ((len(max_list)%max_quant !=0 )):
                    mi = max_list[len(max_list)-1]
                    counte +=1
                    if not max_from_verse:
                        max_from_verse= mi[2]['from_aya']
                    max_to_verse= mi[2]['to_aya']
                    max_list_last.append(

                                    (0,0,{
                                             #'is_test':is_test,
                                              'date':mi[2]['date'],
                                              'day':mi[2]['day'],
                                              'order':counte,
                                              'from_surah':obj_verse.browse(max_from_verse).surah_id.id,
                                              'from_aya':max_from_verse,
                                              'to_surah':obj_verse.browse(max_to_verse).surah_id.id,
                                              'to_aya':max_to_verse,
                                              'type_follow':'review_big',
                                              'student_id':mi[2]['student_id'],

                                        }


                                        )

                        )

                        
        if st[0].approache.program_id.reading == True:
            read_list=lst
            read_quant= st[0].approache.lessons_reading
            if read_quant > 0:
                read_from_verse= False
                read_to_verse= False
                read_count= 0
                counte = 0
                for mi in read_list:
                    read_count +=1 
                    if not read_from_verse:

                        read_from_verse = mi[2]['from_aya']
                    if read_count== read_quant:
                        counte +=1
                        read_to_verse= mi[2]['to_aya']
                        read_list_last.append(

                                        (0,0,{
                                                 #'is_test':is_test,
                                                  'date':mi[2]['date'],
                                                  'day':mi[2]['day'],
                                                  'order':counte,
                                                  'from_surah':obj_verse.browse(read_from_verse).surah_id.id,
                                                  'from_aya':read_from_verse,
                                                  'to_surah':obj_verse.browse(read_to_verse).surah_id.id,
                                                  'to_aya':read_to_verse,
                                                  'type_follow':'tlawa',
                                                  'student_id':mi[2]['student_id'],

                                            }


                                            )

                            )
                        read_count= 0
                        read_to_verse= False
                        read_from_verse= False
                if read_list and ((len(read_list)%read_quant !=0 )):
                    mi = read_list[len(read_list)-1]
                    counte +=1
                    if not read_from_verse:
                        read_from_verse= mi[2]['from_aya']
                    read_to_verse= mi[2]['to_aya']
                    read_list_last.append(

                                    (0,0,{
                                             #'is_test':is_test,
                                              'date':mi[2]['date'],
                                              'day':mi[2]['day'],
                                              'order':counte,
                                              'from_surah':obj_verse.browse(read_from_verse).surah_id.id,
                                              'from_aya':read_from_verse,
                                              'to_surah':obj_verse.browse(read_to_verse).surah_id.id,
                                              'to_aya':read_to_verse,
                                              'type_follow':'tlawa',
                                              'student_id':mi[2]['student_id'],

                                        }


                                        )

                        )
        teacher=request.env['mk.episode'].sudo().search([('id', '=', ep_id)]).teacher_id

       
        dic={
            'name':teacher.id,
            'link_id':student_id,
            'test_ids':test_lst,
            'stage_pre_id':ep_id,
            'std_save_ids':lst,
            'smal_review_ids':min_list_last,
            'big_review_ids':max_list_last,
            'recitation_ids':read_list_last,
        }
        
        obj_prepare.create(dic)

    @http.route('/employee/change/password/', type='json', auth='public',  csrf=False)
    def employee_pass_change(self,**args):
        default_crypt_contex = CryptContext(['pbkdf2_sha512', 'md5_crypt'],deprecated=['md5_crypt'],)
        result = []
        identity=args.get('identity',False)
        n=4 
        range_start = 10**(n-1)
        range_end = (10**n)-1
        gpass=randint(range_start, range_end)
        employee = request.env['hr.employee'].sudo().search([('identification_id','=',identity)],limit=1)
        if employee and employee.user_id:    
            employee.user_id._set_password(str(gpass))
            employee.write({'passwd':gpass})

            if employee.work_email:
                returned=request.env['mk.general_sending'].send_by_template('mk_send_pass_employee', str(employee.id))
            message=request.env['mk.sms_template'].sudo().search([('code', '=', 'mk_send_pass')],limit=1)
            #message=message.
            message=message[0].sms_text
            if gpass and employee.mobile_phone:

                message=re.sub(r'val1', str(gpass), message).strip()
            
                obj_general_sending = request.env['mk.general_sending'].sudo()
                #phone_number=obj_general_sending.get_phone(self.mobile, self.country_id)
                a=obj_general_sending.send_sms(employee.mobile_phone,str(message))
                
            return "password is changed"
        else:
            return "0"
    
    @http.route('/register/prepration/generate_student_prepare_records/<string:student_id>/<string:episode>', type='json', auth='public',  csrf=False)
    def prepare_student(self,student_id,episode,**args):
        result = []
        academic_years = request.env['mk.study.year'].sudo().search([('is_default','=',True)])
        year=0
        if academic_years:
            year=academic_years[0].id
        student =request.env['mk.link'].sudo().search([('student_id','=',int(student_id)),('year','=',year),('episode_id','=',int(episode))])
        if student:
            self.link_prepare(student[0].id, int(episode))

        return str(result)
    
    @http.route('/register/teacher_login/', type='json', auth='public',  csrf=False)
    def get_teacher(self,**args):
        default_crypt_contex = CryptContext(['pbkdf2_sha512', 'md5_crypt'],deprecated=['md5_crypt'],)
        result = []
        identity_no=args.get('identity_no',False)
        password=args.get('password',False)
        employee = request.env['hr.employee'].sudo().search([('identification_id','=',identity_no)])
        episode = request.env['mk.episode'].sudo().search([('teacher_id','=',employee.id)])
        teachers_name=[]
        if episode:
            for ep in episode:
                teachers_name.append(ep.name)
        if employee.user_id:
            user=default_crypt_contex.verify(password,employee.user_id.password_crypt)
            if user:
               
                result.append({'id':employee.id,'status': employee.user_id.state, 'name':employee.name, 'category':employee.category, 'episode_id':teachers_name , 'work_phone':employee.work_phone,'work_email':employee.work_email,'center_id':employee.department_id.id })
        return str(result)

    @http.route('/register/portal_login', type='json', auth='public',  csrf=False)
    def get_teacher_super(self,**args):
        default_crypt_contex = CryptContext(['pbkdf2_sha512', 'md5_crypt'],deprecated=['md5_crypt'],)
        result = []
        identity_no=args.get('identity_no',False)
        password=args.get('password',False)
        employee = request.env['hr.employee'].sudo().search([('identification_id','=',identity_no),('category','in',['teacher','supervisor'])])
        
        if employee.user_id:
            user=default_crypt_contex.verify(password,employee.user_id.password_crypt)
            if user:
               
                result.append({'id':employee.id,'user_id':employee.user_id.id,'status': employee.user_id.state, 'name':employee.name, 'category':employee.category})
        return str(result)

    @http.route('/password/encrypt/decrypt/<int:encr_decr>', type='json', auth='public',  csrf=False)
    def encrypt_decrypt(self, encr_decr,**args):
        portal_user = request.env.ref('mk_student_register.portal_user_id')

        default_crypt_contex = CryptContext(['pbkdf2_sha512', 'md5_crypt'],deprecated=['md5_crypt'],)
        result = []
        user=args.get('user',False)
        password=args.get('password',False)
        user_id=request.env['res.users'].sudo().search([('id','=',user)])

        if user_id:
            if encr_decr==1:
                user_valid=default_crypt_contex.verify(password,user_id.password_crypt)
                if user_valid:
                    return "TRUE"
                else:
                    return "False"
            else:
                user_id.sudo(portal_user.id)._set_password(password)
                employee_id = request.env['hr.employee'].search([('user_id', '=', user)], limit=1)
                employee_id.sudo(portal_user.id).write({'passwd': password})
                return "password is changed"
        else:
            return "user is not available"
    '''

    @http.route('/teacher/change/password/', type='json', auth='public',  csrf=False)
    def teacher_pass_change(self,**args):
        default_crypt_contex = CryptContext(['pbkdf2_sha512', 'md5_crypt'],deprecated=['md5_crypt'],)
        result = []
        identity=args.get('identity',False)
        password=args.get('password',False)
        employee = request.env['hr.employee'].sudo().search([('identification_id','=',identity),('category','=','teacher')])
        if employee and employee.user_id:
            employee.user_id._set_password(password)
            return "password is changed"
        else:
            return "user is not available"
    '''


    @http.route('/teacher/change/password/', type='http', auth='public',  csrf=False)
    def teacher_pass_change(self,**args):
        default_crypt_contex = CryptContext(['pbkdf2_sha512', 'md5_crypt'],deprecated=['md5_crypt'],)
        result = []
        identity=args.get('identity',False)
        n=4 
        range_start = 10**(n-1)
        range_end = (10**n)-1
        gpass=randint(range_start, range_end)
        employee = request.env['hr.employee'].sudo().search([('identification_id','=',identity),('category','=','teacher')], limit=1)
        if employee and employee.user_id:    
            employee.user_id._set_password(str(gpass))
            employee.write({'passwd':gpass})

            if employee.work_email:
                returned=request.env['mk.general_sending'].send_by_template('mk_send_pass_employee', str(employee.id))

            message=request.env['mk.sms_template'].sudo().search([('code', '=', 'mk_send_pass')],limit=1)
            #message=message.
            message=message[0].sms_text
            if gpass and employee.mobile_phone:

                message=re.sub(r'val1', str(gpass), message).strip()
            
                obj_general_sending = request.env['mk.general_sending'].sudo()
                #phone_number=obj_general_sending.get_phone(self.mobile, self.country_id) 
                a=obj_general_sending.send_sms(employee.mobile_phone,str(message))
                
            return "password is changed"
        else:
            return "0"

    @http.route('/register/episode/get_students/<int:episode_id>', type='json', auth='public',  csrf=False)
    def get_students(self, episode_id,**args):
        result = []
        links = request.env['mk.link'].sudo().search([('state','=','accept'), ('episode_id', '=', episode_id)])
        for link in links:
            result.append({'id':link.student_id.id, 'first_name':link.student_id.name, 'second_name':link.student_id.second_name, 'third_name':link.student_id.third_name, 'fourth_name':link.student_id.fourth_name})
        return str(result)

    ###################################ORDER STUDENT##################
    @http.route('/register/episode/order_students/<int:episode_id>/<string:fillter>/', type='json', auth='public',  csrf=False)
    def order_students(self, episode_id,fillter,**args):
        student_ls = []
        delay_ls=[]
        links = request.env['mk.link'].sudo().search([('state','=','accept'),
                                                      ('episode_id', '=', episode_id)])
        for student in links:
            is_dely=0
            is_absent=0
            state=''
            lines = request.env['mk.listen.line'].sudo().search([('student_id','=',student.id),
                                                                 ('type_follow','=','listen'),
                                                                 ('state','!=','done')], limit=1, order="order asc")
            if lines:  
                state=lines[0].state
                if lines[0].delay == True:
                    is_dely=1
                    
                if lines[0].state=='absent':
                    is_absent=1
                    delay_ls.append({'id':student.id,
                                     'name':student.student_id.display_name,
                                     'rate':0,
                                     'age':0,
                                     'is_dely':is_dely,
                                     'is_absent':is_absent,
                                     'state':state})  
                elif fillter=='name':

                    student_ls.append({'id':student.id,
                                       'name':student.student_id.display_name,
                                       'rate':0,
                                       'age':0,
                                       'is_dely':is_dely,
                                       'is_absent':is_absent,
                                       'state':state})
    
                    #order list ABC
                elif fillter == 'rate':
                    listen_rate, total_listen ,done_listen, listen_quality, done_listen_degree, attendence_rate, attended_line = self.calculate_listen_rate(student.id,30)
                    student_ls.append({'id':student.id,
                                       'name':student.student_id.display_name,
                                       'rate':listen_rate,
                                       'age':0,
                                       'is_dely':is_dely,
                                       'is_absent':is_absent,
                                       'state':state})
                    
                elif fillter=='age':                    
                    age=0 
                    dob = student.student_id.birthdate
                    if dob:
                        d1 = datetime.strptime(dob, "%Y-%m-%d").date()
                        d2 = date.today()
                        age = relativedelta(d2, d1).years
                    
                    student_ls.append({'id':student.id,
                                       'name':student.student_id.display_name,
                                       'rate':0,
                                       'age':age,
                                       'is_dely':is_dely,
                                       'is_absent':is_absent,
                                       'state':state})

        student_ls = sorted(student_ls, key=lambda k: k[fillter])
        #student_ls = sorted(student_ls, key=lambda k:k['age'],reverse=True)
        #student_ls = sorted(student_ls, key=lambda k:k['rate'],reverse=True)


        return str(student_ls+delay_ls)

    #-----------------------------------------------------------------------------------

    def get_planned_lines(self,student_id,fillter_type,type_follow):
        lines_object=request.env['mk.listen.line']
        all_planned_lines=lines_object.sudo().search([('student_id','=',student_id),('type_follow','=',type_follow)],order='order')
        c=0
        if all_planned_lines:

            for line in all_planned_lines:
                c=c+1
                if line.state!='done':
                    all_planned_lines=all_planned_lines[:c]
                    break;
            if int(fillter_type)<len(all_planned_lines):
                return all_planned_lines[-(int(fillter_type)):]
            else:
                return all_planned_lines
        else:
            return []

    def get_test_planned_lines(self,student_id):
        prepare=request.env['mk.student.prepare'].sudo().search([('link_id','=',student_id)])
        all_planned_lines=[]
        if prepare:
            line_id=prepare[0].id
            lines_object=request.env['mk.test.line']
            all_planned_lines=lines_object.sudo().search([('line_id','=',line_id)],order='order')
            c=0
            if all_planned_lines:

                for line in all_planned_lines:
                    c=c+1
                    if line.state!='done':
                        all_planned_lines=all_planned_lines[:c]
                        break;
        return all_planned_lines



    def get_test_quality(self,student_id):

        planned_lines=self.get_test_planned_lines(student_id)
        done_lines=0
        done_degree=0
        for line in planned_lines:
            if line.check==True and line.state=='done':
                done_lines=done_lines+1
                done_degree=done_degree+line.degree
        #Step 1 get review total lines
        try:
            review_ratio_qu=(done_degree/(len(planned_lines)*100))*100
            return review_ratio_qu
        except ZeroDivisionError:
            return 0


    def get_review_small_rate(self,student_id,fillter_type):
        if fillter_type=='day':
            fillter_type=1
        if fillter_type=='week':
            fillter_type=7
        if fillter_type=='month':
            fillter_type=30
        
        planned_lines=self.get_planned_lines(student_id,fillter_type,'review_small')
        done_lines=0
        done_degree=0
        for line in planned_lines:
            if line.check==True and line.state=='done':
                done_lines=done_lines+1
                done_degree=done_degree+line.degree
        #Step 1 get review total lines
        try:
            review_ratio=done_lines/len(planned_lines)
            review_ratio_qu=(done_degree/(len(planned_lines)*100))*100
            return ((review_ratio)*100),len(planned_lines),done_lines,review_ratio_qu,done_degree
        except ZeroDivisionError:
            return 0, len(planned_lines), done_lines,0,done_degree


 
    def get_review_big_rate(self,student_id,fillter_type):
        if fillter_type=='day':
            fillter_type=1
        if fillter_type=='week':
            fillter_type=7
        if fillter_type=='month':
            fillter_type=30
        
        planned_lines=self.get_planned_lines(student_id,fillter_type,'review_big')
        done_lines=0
        done_degree=0
        for line in planned_lines: 
            if line.check==True and line.state=='done':
                done_lines=done_lines+1
                done_degree=done_degree+line.degree
        #Step 1 get review total lines
        try:
           review_ratio=done_lines/len(planned_lines)
           return review_ratio*100,len(planned_lines),done_lines,(done_degree)/(len(planned_lines)*100)*100,done_degree
        except ZeroDivisionError:
            return 0, len(planned_lines), done_lines,0,done_degree

    def calculate_listen_rate(self,student_id,fillter_type):
        if fillter_type=='day':
            fillter_type=1
        if fillter_type=='week':
            fillter_type=7
        if fillter_type=='month':
            fillter_type=30
        
        planned_lines=self.get_planned_lines(student_id,fillter_type,'listen')
        done_lines=0
        done_degree=0
        absent_counter=0
        for line in planned_lines:
            if line.check==True and line.state=='done':
                done_lines=done_lines+1
                done_degree=done_degree+line.degree
                #Step 1 get review total lines
            if line.check==False or line.state=='draft':
                absent_counter=absent_counter+1

        try:
            l_ratio=((len(planned_lines)-absent_counter)/len(planned_lines))*100
            review_ratio=(done_lines/len(planned_lines))*100
            return review_ratio,len(planned_lines),done_lines,(done_degree/(len(planned_lines)*100))*100,done_degree,l_ratio,(len(planned_lines)-absent_counter)
        except ZeroDivisionError:
            return 0, len(planned_lines), done_lines,0,done_degree,0,0

    
    @http.route('/register/student_dashboard/<string:student_id>/<string:episode_id>/<string:fillter_type>', type='json', auth='public',  csrf=False)
    def student_dashboard(self,student_id,episode_id,fillter_type,**args):

        review_ratio=0
        total_review=0
        qualty_review=0
        total_review_degree=0
        listen_ratio=0
        total_listen=0
        done_listen=0
        listen_quality=0
        total_listen_degree=0
        done_review=0
        done_review_degree=0
        done_listen=0
        done_listen_degree=0
        st_id=int(student_id)
        ep_id=int(episode_id)
        test_quality=0
        # ******************** STUDENT DADSBOARD PART ONE ******************************  
        if fillter_type=='0':
            test_quality=self.get_test_quality(st_id)

        small_review_rate,total_s_l,done_small,qualty_re_big,dgs=self.get_review_small_rate(st_id,fillter_type)
        big_review_rate,total_b_l,done_big,qualty_re_sm,dgb=self.get_review_big_rate(st_id,fillter_type)
        #--- review rate

        review_ratio=(small_review_rate+big_review_rate)/2
        total_review=total_s_l+total_b_l
        done_review=done_small+done_big 

        # -- review quality

        qualty_review=(qualty_re_sm+qualty_re_big)/2
        total_review_degree=(total_s_l*100)+(total_b_l*100)
        done_review_degree=dgs+dgb

        listen_ratio,total_listen ,done_listen,listen_quality,done_listen_degree,attendence_rate,attended_line =self.calculate_listen_rate(st_id,fillter_type)
        

        total_listen_degree=total_listen*100

        all_sub=total_listen
        
        student_ids=request.env['mk.link'].sudo().search([('episode_id','=',ep_id),('state','=','accept'),('id','!=',st_id)])
        all_students_order_by_review_quilty=[]
        all_students_order_by_review_quilty.append({
            'student':request.env['mk.link'].sudo().search([('id','=',st_id)])[0].student_id.display_name,
            'percentage':listen_quality
            })

        for student in student_ids:
            x,z,y,listen_qualit,done_listen_degre,m,n=self.calculate_listen_rate(student.id,fillter_type)

            all_students_order_by_review_quilty.append({
            'student':student.student_id.display_name,
            'percentage':listen_qualit
            })
  

        all_students_order_by_review_quilty = sorted(all_students_order_by_review_quilty, key=lambda k: k['percentage'],reverse=True)
        top_5_students_at_episode=[]
        i=0
        for rec in all_students_order_by_review_quilty:
            if i<5:
                top_5_students_at_episode.append(rec)
                i=i+1

        return str({'review_rate':review_ratio,'review_total_lines':total_review,'review_done_lines':done_review,
        'review_quality':qualty_review,'review_total_degree':total_review_degree,'review_done_degree':done_review_degree
        ,'listen_rate':listen_ratio,'listen_total_lines':total_listen,'listen_done_lines':done_listen,
        'listen_quality':listen_quality,'listen_total_degree':total_listen_degree,'listen_done_degree':done_listen_degree,
        'attendence_rate':attendence_rate,
        'all_lines':all_sub,
        'attended_line':attended_line,
        'test_quality':test_quality,
        'top_5_students_at_episode':top_5_students_at_episode
        })


    def calculate_listen_rate_student(self,student_id):
        
        lines_object=request.env['mk.listen.line']
        planned_lines=lines_object.sudo().search([('student_id','=',student_id),('type_follow','=','listen')],order='order')
        c=0
        done_lines=0
        done_degree=0
        if planned_lines:

            
        
            for line in planned_lines:
                if  line.state=='done':
                    #one_lines=done_lines+1
                    done_degree=done_degree+line.degree
                    #Step 1 get review total lines
                

            try:
                return done_degree/(len(planned_lines)*100.0)*100
            except ZeroDivisionError:
                return 0
        



    @http.route('/register/best/student_dashboard/<int:mosque_id>', type='json', auth='public',  csrf=False)
    def best_student_dashboard(self,mosque_id,**args):

        review_ratio=0
        total_review=0
        qualty_review=0
        total_review_degree=0
        listen_ratio=0
        total_listen=0
        done_listen=0
        listen_quality=0
        total_listen_degree=0
        done_review=0
        done_review_degree=0
        done_listen=0
        done_listen_degree=0
        
        test_quality=0
        


        
        if mosque_id==0:
            domain=[]
        else:
            domain=[('id','=',mosque_id)]
        mosques=request.env['mk.mosque'].sudo().search(domain).ids

        ep_id=request.env['mk.episode'].sudo().search([('mosque_id','in',mosques),('academic_id','=',self._getDefault_academic_year())]).ids
        student_ids=request.env['mk.link'].sudo().search([('episode_id','in',ep_id),('state','=','accept'),('year','=',self._getDefault_academic_year())])
        all_students_order_by_review_quilty=[]
        

        for student in student_ids:
            listen_quality=self.calculate_listen_rate_student(student.id)

            if listen_quality:
                all_students_order_by_review_quilty.append({
                    'student':student.student_id.display_name,
                    'percentage':listen_quality
                    })
  

        all_students_order_by_review_quilty = sorted(all_students_order_by_review_quilty, key=lambda k: k['percentage'],reverse=True)
        top_5_students_at_episode=[]
        i=0
        for rec in all_students_order_by_review_quilty:
            if i<5:
                top_5_students_at_episode.append(rec)
                i=i+1

        
        return str(top_5_students_at_episode)

    @http.route('/register/get/top/five', type='json', auth='public',  csrf=False)
    def get_top_five_record(self, **args):
        study_class=self.get_default_study_class()
        top_five_record=request.env['top.five'].sudo().search([('study_class','=',study_class)], order='id desc').ids
        if top_five_record:
            return str(top_five_record[0])
        else:
            return False


    



    @http.route('/register/best/episode_dashboard/<int:mosque_id>', type='json', auth='public',  csrf=False)
    def best_episode_dashboard(self,mosque_id,**args):


        done_listen=0
        listen_quality=0
        total_listen_degree=0
        done_listen_degree=0


        
        if mosque_id==0:
            domain=[]
        else:
            domain=[('id','=',mosque_id)]
        mosques=request.env['mk.mosque'].sudo().search(domain).ids

        ep_id=request.env['mk.episode'].sudo().search([('mosque_id','in',mosques),('academic_id','=',self._getDefault_academic_year())])

        all_students_order_by_review_quilty=[]
        ep_productivity=[]

        for ep in ep_id:
            ep_percentage=0
            student_ids=request.env['mk.link'].sudo().search([('episode_id','=',ep.id),('state','=','accept'),('year','=',self._getDefault_academic_year())])

            if student_ids:
                for student in student_ids:
                    listen_quality=self.calculate_listen_rate_student(student.id)
                    if listen_quality:
                        ep_percentage+=listen_quality
                ep_productivity.append({'episode name':ep.display_name,'rate':ep_percentage/len(student_ids)})
            

        sorted_episodes = sorted(ep_productivity, key=lambda k: k['rate'],reverse=True)
        top_5_episode=[]
        i=0
        for rec in sorted_episodes:
            if i<5:
                top_5_episode.append(rec)
                i=i+1
        
        return str(top_5_episode)


    def calculate_listen_rate_prepare(self, preparation_id):
        lines_object=request.env['mk.listen.line']
        planned_lines=lines_object.sudo().search([('preparation_id','=',preparation_id),
												  ('type_follow','=','listen')],order='order')
        c=0
        done_lines=0
        done_degree=0
        if planned_lines:

            
        
            for line in planned_lines:
                if  line.state=='done':
                    #one_lines=done_lines+1
                    done_degree=done_degree+line.degree
                    #Step 1 get review total lines
                

            try:
                
                return done_degree/(len(planned_lines)*100.0)*100
            except ZeroDivisionError:
                return 0
        else:
            return 0

    @http.route('/register/best/teacher_dashboard/<int:mosque_id>', type='json', auth='public',  csrf=False)
    def best_teacher_dashboard(self,mosque_id,**args):
        """
        review_ratio=0
        total_review=0
        qualty_review=0
        total_review_degree=0
        listen_ratio=0
        total_listen=0
        done_listen=0
        listen_quality=0
        total_listen_degree=0
        done_review=0
        done_review_degree=0
        done_listen=0
        done_listen_degree=0
        st_id=int(student_id)
        ep_id=int(episode_id)
        test_quality=0
        


        
        if mosque_id==0:
            domain=[]
        else:
            domain=[('id','=',mosque_id)]
        mosques=request.env['mk.mosque'].sudo().search(domain).ids
        #ep_id=request.env['mk.episode'].sudo().search([('mosque_id','in',mosques)])
        teachers=request.env['hr.employee'].sudo().search([('mosqtech_ids','in',mosques),('category2','=','teacher')]).ids
        all_students_order_by_review_quilty=[]
        ep_productivity=[]

        for teacher in teachers:
            ep_percentage=0
            preparation=request.env['mk.student.prepare'].sudo().search([('teacher_id','=',teacher)])
            for rec in preparation:
                students.append(rec.student.id)
            student_ids=request.env['mk.link'].sudo().search([('episode_id','=',ep),('state','=','accept')])
            for student in student_ids:
                x,z,y,listen_qualit,done_listen_degre,m,n=self.calculate_listen_rate(student.id,fillter_type)
                ep_percentage+=listen_qualit
            ep_productivity.append({'episode_id':ep,'rate':ep_percentage/len(student_ids)})
            

        sorted_episodes = sorted(ep_productivity, key=lambda k: k['rate'],reverse=True)
        top_5_episode=[]
        i=0
        for rec in sorted_episodes:
            if i<5:
                top_5_episode.append(rec)
                i=i+1

        return str({
        'top_5_episodes':top_5_episode
        })
        """

        done_listen=0
        listen_quality=0
        total_listen_degree=0
        done_listen_degree=0
        average_productivity=0

        
     
        ep_id=request.env['mk.episode'].sudo().search([('study_class_id','=',self.get_default_study_class()),('state','=','accept'),('mosque_id','=',mosque_id)])
        all_students_order_by_review_quilty=[]
        teachers_productivity={}
        listen_teacher=[]
        teacher_ep=[]

        ep_percentage=0
        student_prepare=request.env['mk.student.prepare'].search([('stage_pre_id','in',ep_id.ids)])
        if student_prepare:

            for rec in student_prepare:
                listen_quality=self.calculate_listen_rate_prepare(rec.id)
                #listen_teacher.append({'teacher':rec.name,'productivity':listen_quality,'student':rec.link_id.id})

                if rec.name in teachers_productivity:
                    
                    teachers_productivity[rec.name].append(listen_quality)
                else:
                    if listen_quality:
                        teachers_productivity[rec.name]=[listen_quality]
        '''
        for rec in listen_teacher:
            if rec['teacher'] in teachers_productivity:
                teachers_productivity[rec['teacher']].append(rec['productivity'])
            else:
                teachers_produsctivity[rec['teacher']]=[rec['productivity']]

        '''
        
        for key , value in teachers_productivity.items():
            total=0
            if value:
                for i in value:
                    if type(i) is int or type(i) is float:
                        total+=i
                average_productivity=total/len(value)
            teacher_ep.append({'productivity':average_productivity,'teacher':key.name})
        '''




        '''     
            
        sorted_ep = sorted(teacher_ep, key=lambda k: k['productivity'],reverse=True)
        top_5_ep=[]
        i=0
        for rec in sorted_ep:
            if i<5:
                top_5_ep.append(rec)
                i=i+1
        
        return str(top_5_ep)
            
    @http.route('/register/teacher_dashboard/<int:teacher_id>/<string:episode_id>/<string:fillter_type>', type='json', auth='public',  csrf=False)
    def test(self, teacher_id,episode_id, fillter_type, **args):
        ep_id=int(episode_id)
        tec_id=int(teacher_id)
        episodes_ids=[]
        # CASE 1 ALL EPISODES
        review_ratio=0
        total_review=0
        qualty_review=0
        total_review_degree=0
        listen_ratio=0
        total_listen=0
        done_listen=0
        listen_quality=0
        total_listen_degree=0
        done_review=0
        done_review_degree=0
        done_listen=0
        done_listen_degree=0
        attendence_rate=0
        all_sub=0
        attended_line=0
        if ep_id==0 :

                episodes_ids=request.env['mk.episode'].sudo().search([('teacher_id','=',tec_id),('state','=','accept')])
                

        else:
                episodes_ids=request.env['mk.episode'].sudo().search([('teacher_id','=',tec_id),('id','=',ep_id),('state','=','accept')])

                
                #link ids for all episodes ids 
        masjed_id=episodes_ids[0].mosque_id
                
        link_ids=request.env['mk.link'].sudo().search([('episode_id','in',episodes_ids.ids)])
        if link_ids:
            review_rato_for_all=0
            total_review_for_all=0
            done_review_for_all=0
            #////
            review_quality_for_all=0
            total_review_degree_for_all=0
            done_review_degree_for_all=0
            #///
            listen_ratio_for_all=0
            total_listen_for_all=0
            done_listen_for_all=0
            #///
            listen_quality_for_all=0
            total_listen_degree_for_all=0
            done_listen_degree_for_all=0
            #////
            attendence_rate_for_all=0
            total_lines_for_all=0
            done_lines_for_all=0
            for student in link_ids:
                # //////////////////////////////review ratio for single student

                small_review_rate,total_s_l,done_small,qualty_re_sm,done_sm_review_degree=self.get_review_small_rate(student.id,fillter_type)
                big_review_rate,total_b_l,done_big,qualty_re_big,done_big__review_degree=self.get_review_big_rate(student.id,fillter_type)
                # review ratio +++
                review_rato_for_all=review_rato_for_all+((small_review_rate+big_review_rate)/2)
                total_review_for_all=total_review_for_all+(total_s_l+total_b_l)
                done_review_for_all=done_review_for_all+(done_small+done_big) 

                # ////////////////////////////////////////////////////////////////////quality ratio
                review_quality_for_all=review_quality_for_all+((qualty_re_sm+qualty_re_big)/2)
                total_review_degree_for_all=total_review_degree_for_all+((total_s_l*100)+(total_b_l*100))
                done_review_degree_for_all=done_review_degree_for_all+(done_big__review_degree+done_sm_review_degree)

                #//////////////////////////////////////////////////// listen raito
                listen_ratio,total_listen ,done_listen,listen_quality,done_listen_degree,attendence_rate,attended_line=self.calculate_listen_rate(student.id,fillter_type)
                
                listen_ratio_for_all=listen_ratio_for_all+listen_ratio
                total_listen_for_all=total_listen_for_all+total_listen
                done_listen_for_all=done_listen_for_all+done_listen

                #////////////////////////////////////////////////////////////////// lq

                listen_quality_for_all=listen_quality_for_all+listen_quality
                total_listen_degree_for_all=total_listen_degree_for_all+(total_listen*100)
                done_listen_degree_for_all=done_listen_degree_for_all+done_listen_degree

                #////////////////////////////////////////////////// attendence quality
                attendence_rate_for_all=attendence_rate_for_all+attendence_rate
                total_lines_for_all=total_lines_for_all+total_listen
                done_lines_for_all=done_lines_for_all+attended_line

            review_ratio=review_rato_for_all/len(link_ids)
            total_review=total_review_for_all
            done_review=done_review_for_all           

            # STEP 4: GET REVIEW QUALITY TOTAL DEGREE,DONE DEGREE
    
            qualty_review=review_quality_for_all/len(link_ids)
            total_review_degree=total_review_degree_for_all
            done_review_degree=done_review_degree_for_all     

        #STEP 5: GET LISTEN RATE

            listen_ratio=listen_ratio_for_all/len(link_ids)
            done_listen= done_listen_for_all
            total_listen=total_listen_for_all

        #STEP 6 : GET LISTEN QUALITY
            listen_quality= listen_quality_for_all/len(link_ids)
            done_listen_degree=done_listen_degree_for_all 
            total_listen_degree=total_listen_degree_for_all

            attendence_rate=attendence_rate_for_all/len(link_ids)
            all_sub=total_lines_for_all
            attended_line=done_lines_for_all

        #--------------------- Dashboard teacher step2 --------------------------------------------------------------------------------
        
        #STEP 1: GET ALL EPISODES
        episodes=request.env['mk.episode'].sudo().search([('state','=','accept'),('mosque_id','=',masjed_id.id)])
        all_episode_order_listen_degree=[]
        for episode in episodes:
            #get all students 
            episode_students_list=request.env['mk.link'].sudo().search([('episode_id','=',episode.id)])
            if episode_students_list:
                listen_quality_for_ep_st=0
                for student in episode_students_list:

                    x,y,z,listen_qualit,done_listen_degre,x,c=self.calculate_listen_rate(student.id,fillter_type)
                    listen_quality_for_ep_st=listen_quality_for_ep_st+listen_qualit

                episode_quality=listen_quality_for_ep_st/len(episode_students_list)

                #get all lines for dtudents
                    
                all_episode_order_listen_degree.append({
                'episode':episode.name,
                'percentage':episode_quality
                })

        all_episode_order_listen_degree = sorted(all_episode_order_listen_degree, key=lambda k: k['percentage'],reverse=True)
        top_10_episodes=[]
        i=0
        for rec in all_episode_order_listen_degree:
            if i<8:
                top_10_episodes.append(rec)
                i=i+1
       
 
        return str({'review_rate':review_ratio,'review_total_lines':total_review,'review_done_lines':done_review,
            'review_quality':qualty_review,'review_total_degree':total_review_degree,'review_done_degree':done_review_degree
            ,'listen_rate':listen_ratio,'listen_total_lines':total_listen,'listen_done_lines':done_listen,
             'listen_quality':listen_quality,'listen_total_degree':total_listen_degree,'listen_done_degree':done_listen_degree,
             'attendence_rate':attendence_rate,
             'all_lines':all_sub,
             'attended_line':attended_line,
             'top_10_episodes_productivity':all_episode_order_listen_degree,
             'episodes_number':len(request.env['mk.episode'].sudo().search([('teacher_id','=',tec_id),('state','=','accept')]))
         })
        
    @http.route('/register/center_dashboard/<int:center_id>/<int:masjed_id>/<int:episode_id>/<string:fillter_type>', type='json', auth='public',  csrf=False)
    def center(self, center_id, masjed_id, episode_id, fillter_type, **args):

        review_ratio=0
        total_review=0
        qualty_review=0
        total_review_degree=0
        listen_ratio=0
        total_listen=0
        done_listen=0
        listen_quality=0
        total_listen_degree=0
        done_review=0
        done_review_degree=0
        done_listen=0
        done_listen_degree=0
        attendence_rate=0
        all_sub=0
        attended_line=0
        masjed_ids=[]
        episodes_ids=[]
        if masjed_id!=0:
            domain=[('id', '=', masjed_id),('state','=','accept')]
        else:
            if masjed_id ==0 and center_id !=0:
                domain=[('center_department_id','=',center_id),('state','=','accept')]
            else:   
                if center_id==0 and masjed_id ==0:
                    domain =[('state','=','accept')]
        

        masjed_ids=(request.env['mk.mosque'].sudo().search(domain)).ids
        # CASE 1 ALL EPISODES
        if episode_id==0 :

            #STEP 1 GET ALL STUDENDTS FOR THIS MASJED
                # 1-1 get teacher episodes
                episodes_ids=request.env['mk.episode'].sudo().search([('mosque_id','in',masjed_ids),('state','=','accept')])
                
        else:
                episodes_ids=request.env['mk.episode'].sudo().search([('id','=',episode_id)])


        # 1-2 get student list

            #1-1 get link id for each stuadent in masjed_students[]
        link_ids=request.env['mk.link'].sudo().search([('episode_id','in',episodes_ids.ids)])
        if link_ids:

                review_rato_for_all=0
                total_review_for_all=0
                done_review_for_all=0
                review_quality_for_all=0
                total_review_degree_for_all=0
                done_review_degree_for_all=0
                listen_ratio_for_all=0
                total_listen_for_all=0
                done_listen_for_all=0
                listen_quality_for_all=0
                total_listen_degree_for_all=0
                done_listen_degree_for_all=0
                attendence_rate_for_all=0
                total_lines_for_all=0
                done_lines_for_all=0
                
                for student in link_ids:

                    small_review_rate,total_s_l,done_small,qualty_re_sm,done_sm_review_degree=self.get_review_small_rate(student.id,fillter_type)
                    big_review_rate,total_b_l,done_big,qualty_re_big,done_big__review_degree=self.get_review_big_rate(student.id,fillter_type)
                    # review ratio +++
                    review_rato_for_all=review_rato_for_all+((small_review_rate+big_review_rate)/2)
                    total_review_for_all=total_review_for_all+(total_s_l+total_b_l)
                    done_review_for_all=done_review_for_all+(done_small+done_big) 

                    # ////////////////////////////////////////////////////////////////////quality ratio
                    review_quality_for_all=review_quality_for_all+((qualty_re_sm+qualty_re_big)/2)
                    total_review_degree_for_all=total_review_degree_for_all+((total_s_l*100)+(total_b_l*100))
                    done_review_degree_for_all=done_review_degree_for_all+(done_big__review_degree+done_sm_review_degree)

                    #//////////////////////////////////////////////////// listen raito
                    listen_ratio,total_listen ,done_listen,listen_quality,done_listen_degree,attendence_rate,attended_line=self.calculate_listen_rate(student.id,fillter_type)
                    
                    listen_ratio_for_all=listen_ratio_for_all+listen_ratio
                    total_listen_for_all=total_listen_for_all+total_listen
                    done_listen_for_all=done_listen_for_all+done_listen

                    #////////////////////////////////////////////////////////////////// lq

                    listen_quality_for_all=listen_quality_for_all+listen_quality
                    total_listen_degree_for_all=total_listen_degree_for_all+(total_listen*100)
                    done_listen_degree_for_all=done_listen_degree_for_all+done_listen_degree

                    #////////////////////////////////////////////////// attendence quality
                    attendence_rate_for_all=attendence_rate_for_all+attendence_rate
                    total_lines_for_all=total_lines_for_all+total_listen
                    done_lines_for_all=done_lines_for_all+attended_line

                review_ratio=review_rato_for_all/len(link_ids)
                total_review=total_review_for_all
                done_review=done_review_for_all           

            # STEP 4: GET REVIEW QUALITY TOTAL DEGREE,DONE DEGREE
    

                qualty_review=review_quality_for_all/len(link_ids)
                total_review_degree=total_review_degree_for_all
                done_review_degree=done_review_degree_for_all     

            #STEP 5: GET LISTEN RATE

                listen_ratio=listen_ratio_for_all/len(link_ids)
                done_listen= done_listen_for_all
                total_listen=total_listen_for_all

            #STEP 6 : GET LISTEN QUALITY
                listen_quality= listen_quality_for_all/len(link_ids)
                done_listen_degree=done_listen_degree_for_all 
                total_listen_degree=total_listen_degree_for_all

                attendence_rate=attendence_rate_for_all/len(link_ids)
                all_sub=total_lines_for_all
                attended_line=done_lines_for_all

        return str({'review_rate':review_ratio,'review_total_lines':total_review,'review_done_lines':done_review,
                'review_quality':qualty_review,'review_total_degree':total_review_degree,'review_done_degree':done_review_degree
                ,'listen_rate':listen_ratio,'listen_total_lines':total_listen,'listen_done_lines':done_listen,
                'listen_quality':listen_quality,'listen_total_degree':total_listen_degree,'listen_done_degree':done_listen_degree,
                'attendence_rate':attendence_rate,
                'all_lines':all_sub,
                'attended_line':attended_line,
                })
    
    @http.route('/register/center_counter/<int:center_id>/<string:type_categ>/<int:masjed_id>/<int:episode_id>/', type='json', auth='public',  csrf=False)
    def center_counter(self, center_id, type_categ, masjed_id, episode_id, **args):

      center_domain=[('level_type','=','c')]
      masjed_domain=[]
      episode_domain=[]
      student_domain=[]
      teachers_domain=[('category','=','teacher')]
      supervisors_domain=[('category','=','supervisor')]
      if center_id ==0 and masjed_id==0:
        if type_categ!='all':
            categ_ids=request.env['mk.mosque.category'].sudo().search([('mosque_type','=',type_categ)]).ids
            if categ_ids:
                masjed_domain=[('categ_id','in',categ_ids)]    
                mosque_ids=request.env['mk.mosque'].sudo().search([('categ_id','in',categ_ids)]).ids
                episode_domain=[('mosque_id','in',mosque_ids)]
                student_domain=[('mosque_id','in',mosque_ids)]
                teachers_domain=[('category','=','teacher'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]
                supervisors_domain=[('category','=','supervisor'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]
      

      if center_id !=0 and masjed_id==0:
        center_domain=[('level_type','=','c'),('id','=',center_id)]
        masjed_domain=[('center_department_id','=',center_id)]
        mosque_ids=request.env['mk.mosque'].sudo().search([('center_department_id','=',center_id)]).ids
        episode_domain=[('mosque_id','in',mosque_ids)]
        student_domain=[('mosque_id','in',mosque_ids)]
        teachers_domain=[('category','=','teacher'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]        
        if type_categ!='all':
            categ_ids=request.env['mk.mosque.category'].sudo().search([('mosque_type','=',type_categ)]).ids
            if categ_ids:
                masjed_domain=[('center_department_id','=',center_id),('categ_id','in',categ_ids)]    
                mosque_ids=request.env['mk.mosque'].sudo().search([('center_department_id','=',center_id),('categ_id','in',categ_ids)]).ids
                episode_domain=[('mosque_id','in',mosque_ids)]
                student_domain=[('mosque_id','in',mosque_ids)]
                teachers_domain=[('category','=','teacher'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]
                supervisors_domain=[('category','=','supervisor'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]

      else:
        if center_id!=0 and masjed_id!=0:
            center_domain=[('level_type','=','c'),('id','=',center_id)]
            masjed_domain=[('id','=',masjed_id)]
            mosque_ids=request.env['mk.mosque'].sudo().search([('id','=',masjed_id)]).ids
            episode_domain=[('mosque_id','in',mosque_ids)]
            student_domain=[('mosque_id','in',mosque_ids)]
            teachers_domain=[('category','=','teacher'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]
            supervisors_domain=[('category','=','supervisor'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]
      center_no=len(request.env['hr.department'].sudo().search(center_domain))
      masjed_no=len(request.env['mk.mosque'].sudo().search(masjed_domain))
      episode_no=len(request.env['mk.episode'].sudo().search(episode_domain))
      st_no= len(request.env['mk.student.register'].sudo().search(student_domain))
      tec_no=len(request.env['hr.employee'].sudo().search(teachers_domain))
      super_no=len(request.env['hr.employee'].sudo().search(supervisors_domain))


      return str({'centers':center_no,'masjeds':masjed_no,'episodes':episode_no,'supervisors':super_no,'students':st_no,'teachers':tec_no })
        
    @http.route('/register/counter_write_records/<int:center_id>/<string:type_categ>/<int:masjed_id>/<int:episode_id>/', type='json', auth='public',  csrf=False)
    def center_counter_write(self, center_id, type_categ, masjed_id, episode_id,**args):

      center_domain=[('level_type','=','c'),('write_date','!=',False)]
      masjed_domain=[('write_date','!=',False)]
      episode_domain=[('write_date','!=',False)]
      student_domain=[('birthdate','!=',False)]
      teachers_domain=[('write_date','!=',False),('category','=','teacher')]
      supervisors_domain=[('write_date','!=',False),('category','=','supervisor')]
      
      if center_id==0 and masjed_id==0:
        if type_categ!='all':
            categ_ids=request.env['mk.mosque.category'].sudo().search([('mosque_type','=',type_categ)]).ids
            if categ_ids:
                masjed_domain=[('write_date','!=',False),('categ_id','in',categ_ids)]    
                mosque_ids=request.env['mk.mosque'].sudo().search([('categ_id','in',categ_ids)]).ids
                episode_domain=[('write_date','!=',False),('mosque_id','in',mosque_ids)]
                student_domain=[('birthdate','!=',False),('mosque_id','in',mosque_ids)]
                teachers_domain=[('write_date','!=',False),('category','=','teacher'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]
                supervisors_domain=[('write_date','!=',False),('category','=','supervisor'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]


      if center_id !=0 and masjed_id==0:
        center_domain=[('level_type','=','c'),('id','=',center_id)]
        masjed_domain=[('write_date','!=',False),('center_department_id','=',center_id)]
        mosque_ids=request.env['mk.mosque'].sudo().search([('center_department_id','=',center_id)]).ids
        episode_domain=[('write_date','!=',False),('mosque_id','in',mosque_ids)]
        student_domain=[('birthdate','!=',False),('mosque_id','in',mosque_ids)]
        teachers_domain=[('write_date','!=',False),('category','=','teacher'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]        
        if type_categ!='all':
            categ_ids=request.env['mk.mosque.category'].sudo().search([('mosque_type','=',type_categ)]).ids
            if categ_ids:
                masjed_domain=[('write_date','!=',False),('center_department_id','=',center_id),('categ_id','in',categ_ids)]    
                mosque_ids=request.env['mk.mosque'].sudo().search([('center_department_id','=',center_id),('categ_id','in',categ_ids)]).ids
                episode_domain=[('write_date','!=',False),('mosque_id','in',mosque_ids)]
                student_domain=[('birthdate','!=',False),('mosque_id','in',mosque_ids)]
                teachers_domain=[('write_date','!=',False),('category','=','teacher'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]
                supervisors_domain=[('write_date','!=',False),('category','=','supervisor'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]

      else:
        if center_id!=0 and masjed_id!=0:
            center_domain=[('level_type','=','c'),('id','=',center_id)]
            masjed_domain=[('id','=',masjed_id)]
            mosque_ids=request.env['mk.mosque'].sudo().search([('id','=',masjed_id)]).ids
            episode_domain=[('write_date','!=',False),('mosque_id','in',mosque_ids)]
            student_domain=[('birthdate','!=',False),('mosque_id','in',mosque_ids)]
            teachers_domain=[('write_date','!=',False),('category','=','teacher'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]
            supervisors_domain=[('write_date','!=',False),('category','=','supervisor'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]
      center_no=len(request.env['hr.department'].sudo().search(center_domain))
      masjed_no=len(request.env['mk.mosque'].sudo().search(masjed_domain))
      episode_no=len(request.env['mk.episode'].sudo().search(episode_domain))
      st_no= len(request.env['mk.student.register'].sudo().search(student_domain))
      tec_no=len(request.env['hr.employee'].sudo().search(teachers_domain))
      super_no=len(request.env['hr.employee'].sudo().search(supervisors_domain))
      return str({'centers':center_no,'masjeds':masjed_no,'episodes':episode_no,'supervisors':super_no,'students':st_no,'teachers':tec_no
        })

    @http.route('/register/supervisor_center_counter/<int:center_id>/<string:type_categ>/<int:sup_id>/<int:masjed_id>/', type='json', auth='public',  csrf=False)
    def center_counter_super(self, center_id, type_categ, sup_id,masjed_id  , **args):

      center_domain=[('level_type','=','c')]
      masjed_domain=[]
      episode_domain=[]
      student_domain=[]
      teachers_domain=[('category','=','teacher')]
      supervisors_domain=[('category','=','supervisor')]
      if center_id ==0 and masjed_id==0 and sup_id==0:
        if type_categ!='all':
            categ_ids=request.env['mk.mosque.category'].sudo().search([('mosque_type','=',type_categ)]).ids
            if categ_ids:
                masjed_domain=[('categ_id','in',categ_ids)]    
                #mosque_ids=request.env['mk.mosque'].sudo().search([('state', '=', 'accept'),('categ_id','in',categ_ids)]).ids
                mosque_ids=request.env['mk.mosque'].sudo().search([('categ_id','in',categ_ids)]).ids
                # from masjeds 
                episode_domain=[('mosque_id','in',mosque_ids)]
                student_domain=[('mosque_id','in',mosque_ids)]
                teachers_domain=[('category','=','teacher'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]
                supervisors_domain=[('category','=','supervisor'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]
      

      if center_id!=0 and masjed_id==0 and sup_id==0:
        center_domain=[('level_type','=','c'),('id','=',center_id)]
        #masjed_domain=[('state', '=', 'accept'),('center_department_id','=',center_id)]
        masjed_domain=[('center_department_id','=',center_id)]
        mosque_ids=request.env['mk.mosque'].sudo().search([('center_department_id','=',center_id)]).ids
        #from masjeds
        episode_domain=[('mosque_id','in',mosque_ids)]
        student_domain=[('mosque_id','in',mosque_ids)]
        teachers_domain=[('category','=','teacher'),('department_id','=',center_id)]
        if type_categ!='all':
            categ_ids=request.env['mk.mosque.category'].sudo().search([('mosque_type','=',type_categ)]).ids
            if categ_ids:
                #masjed_domain=[('state', '=', 'accept'),('center_department_id','=',center_id),('categ_id','in',categ_ids)]
                masjed_domain=[('center_department_id','=',center_id),('categ_id','in',categ_ids)]
                mosque_ids=request.env['mk.mosque'].sudo().search([('center_department_id','=',center_id),('categ_id','in',categ_ids)]).ids
                #from masjeds
                episode_domain=[('mosque_id','in',mosque_ids)]
                student_domain=[('mosque_id','in',mosque_ids)]
                teachers_domain=[('category','=','teacher'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]
                supervisors_domain=[('category','=','supervisor'),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]

      
      if sup_id!=0 and masjed_id==0 and center_id!=0:
            center_domain=[('level_type','=','c'),('id','=',center_id)]
            
            # get supervisor mosques 
            mosque_ids=request.env['hr.employee'].sudo().search([('id','=',sup_id)])
            
            masjed_domain=[('id','in',mosque_ids[0].mosque_sup.ids)]
            #masjed_domain=[('state', '=', 'accept'),('id','in',mosque_ids[0].mosque_sup.ids)]
            episode_domain=[('mosque_id','in',mosque_ids[0].mosque_sup.ids)]
            student_domain=[('mosque_id','in',mosque_ids[0].mosque_sup.ids)]
            teachers_domain=[('category','=','teacher'),'|',('mosque_id','=',mosque_ids[0].mosque_sup.ids),('mosqtech_ids','in',mosque_ids[0].mosque_sup.ids)]
            supervisors_domain=[('category','=','supervisor'),'|',('mosque_id','=',mosque_ids[0].mosque_sup.ids),('mosqtech_ids','in',mosque_ids[0].mosque_sup.ids)]

      if sup_id!=0 and masjed_id!=0 and center_id!=0:
            center_domain=[('level_type','=','c'),('id','=',center_id)]
            
            # get supervisor mosques 
            #mosque_ids=request.env['hr.employee'].search([('id','=',sup_id)])
            
            #masjed_domain=[('state', '=', 'accept'),('id','=',masjed_id)]
            masjed_domain=[('id','=',masjed_id)]
            episode_domain=[('mosque_id','=',masjed_id)]
            student_domain=[('mosque_id','=',masjed_id)]
            teachers_domain=[('category','=','teacher'),'|',('mosque_id','=',masjed_id),('mosqtech_ids','in',masjed_id)]
            supervisors_domain=[('category','=','supervisor'),'|',('mosque_id','=',masjed_id),('mosqtech_ids','in',masjed_id)]


      center_no=len(request.env['hr.department'].sudo().search(center_domain))
      masjed_no=len(request.env['mk.mosque'].sudo().search(masjed_domain))
      episode_no=len(request.env['mk.episode'].sudo().search(episode_domain))
      st_no= len(request.env['mk.student.register'].sudo().search(student_domain))
      tec_no=len(request.env['hr.employee'].sudo().search(teachers_domain))
      super_no=len(request.env['hr.employee'].sudo().search(supervisors_domain))


      return str({'centers':center_no,'masjeds':masjed_no,'episodes':episode_no,'supervisors':super_no,'students':st_no,'teachers':tec_no })

    @http.route('/register/write_supervisor_center_counter/<int:center_id>/<string:type_categ>/<int:sup_id>/<int:masjed_id>/', type='json', auth='public',  csrf=False)
    def write_center_counter_super(self, center_id, type_categ,sup_id,masjed_id , **args):

      center_domain=[('level_type','=','c'),('write_date','!=',False)]
      masjed_domain=[('write_date','!=',False)]
      episode_domain=[('write_date','!=',False)]
      student_domain=[('birthdate','!=',False)]
      teachers_domain=[('category','=','teacher'),('write_date','!=',False)]
      supervisors_domain=[('category','=','supervisor'),('write_date','!=',False)]
      if center_id ==0 and masjed_id==0 and sup_id==0:
        if type_categ!='all':
            categ_ids=request.env['mk.mosque.category'].sudo().search([('mosque_type','=',type_categ)]).ids
            if categ_ids:
                masjed_domain=[('categ_id','in',categ_ids),('write_date','!=',False)]    
                mosque_ids=request.env['mk.mosque'].sudo().search([('categ_id','in',categ_ids)]).ids
                # from masjeds 
                episode_domain=[('mosque_id','in',mosque_ids),('write_date','!=',False)]
                student_domain=[('mosque_id','in',mosque_ids),('birthdate','!=',False)]
                teachers_domain=[('category','=','teacher'),('write_date','!=',False),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]
                supervisors_domain=[('category','=','supervisor'),('write_date','!=',False),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]
      

      if center_id!=0 and masjed_id==0 and sup_id==0:
        center_domain=[('level_type','=','c'),('id','=',center_id)]
        masjed_domain=[('center_department_id','=',center_id),('write_date','!=',False)]
        mosque_ids=request.env['mk.mosque'].sudo().search([('center_department_id','=',center_id)]).ids
        #from masjeds
        episode_domain=[('mosque_id','in',mosque_ids),('write_date','!=',False)]
        student_domain=[('mosque_id','in',mosque_ids),('birthdate','!=',False)]
        teachers_domain=[('category','=','teacher'),('write_date','!=',False),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]        
        if type_categ!='all':
            categ_ids=request.env['mk.mosque.category'].sudo().search([('mosque_type','=',type_categ)]).ids
            if categ_ids:
                masjed_domain=[('center_department_id','=',center_id),('categ_id','in',categ_ids),('write_date','!=',False)]    
                mosque_ids=request.env['mk.mosque'].sudo().search([('center_department_id','=',center_id),('categ_id','in',categ_ids)]).ids
                #from masjeds
                episode_domain=[('mosque_id','in',mosque_ids),('write_date','!=',False)]
                student_domain=[('mosque_id','in',mosque_ids),('birthdate','!=',False)]
                teachers_domain=[('category','=','teacher'),('write_date','!=',False),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]
                supervisors_domain=[('category','=','supervisor'),('write_date','!=',False),'|',('mosque_id','=',mosque_ids),('mosqtech_ids','in',mosque_ids)]

      
      if sup_id!=0 and masjed_id==0 and center_id!=0:
            center_domain=[('level_type','=','c'),('id','=',center_id)]
            
            # get supervisor mosques 
            mosque_ids=request.env['hr.employee'].sudo().search([('id','=',sup_id)])
            
            masjed_domain=[('id','in',mosque_ids[0].mosque_sup.ids),('write_date','!=',False)]
            episode_domain=[('mosque_id','in',mosque_ids[0].mosque_sup.ids),('write_date','!=',False)]
            student_domain=[('mosque_id','in',mosque_ids[0].mosque_sup.ids),('birthdate','!=',False)]
            teachers_domain=[('category','=','teacher'),('write_date','!=',False),'|',('mosque_id','=',mosque_ids[0].mosque_sup.ids),('mosqtech_ids','in',mosque_ids[0].mosque_sup.ids)]
            supervisors_domain=[('category','=','supervisor'),('write_date','!=',False),'|',('mosque_id','=',mosque_ids[0].mosque_sup.ids),('mosqtech_ids','in',mosque_ids[0].mosque_sup.ids)]

      if sup_id!=0 and masjed_id!=0 and center_id!=0:
            center_domain=[('level_type','=','c'),('id','=',center_id)]
            
            # get supervisor mosques 
            #mosque_ids=request.env['hr.employee'].search([('id','=',sup_id)])
            
            masjed_domain=[('id','=',masjed_id)]
            episode_domain=[('mosque_id','=',masjed_id),('write_date','!=',False)]
            student_domain=[('mosque_id','=',masjed_id),('birthdate','!=',False)]
            teachers_domain=[('category','=','teacher'),('write_date','!=',False),'|',('mosque_id','=',masjed_id),('mosqtech_ids','in',masjed_id)]
            supervisors_domain=[('category','=','supervisor'),('write_date','!=',False),'|',('mosque_id','=',masjed_id),('mosqtech_ids','in',masjed_id)]


      center_no=len(request.env['hr.department'].sudo().search(center_domain))
      masjed_no=len(request.env['mk.mosque'].sudo().search(masjed_domain))
      episode_no=len(request.env['mk.episode'].sudo().search(episode_domain))
      st_no= len(request.env['mk.student.register'].sudo().search(student_domain))
      tec_no=len(request.env['hr.employee'].sudo().search(teachers_domain))
      super_no=len(request.env['hr.employee'].sudo().search(supervisors_domain))


      return str({'centers':center_no,'masjeds':masjed_no,'episodes':episode_no,'supervisors':super_no,'students':st_no,'teachers':tec_no })
  
    @http.route('/register/write_details/<string:type_categ>/<int:masjed_id>', type='json', auth='public',csrf=False)
    def write_details(self,type_categ,masjed_id,**args):
        ids=[]
        write_ids=[]
        if type_categ=='ep':
            ep_ids=request.env['mk.episode'].sudo().search([('mosque_id','=',masjed_id),('write_date','=',False)])
            ids_write=request.env['mk.episode'].sudo().search([('mosque_id','=',masjed_id),('write_date','!=',False)])
            
            for ep in ep_ids:
                ids.append({'id':ep.id,'name':ep.display_name})

            for ep_w in ids_write:
                write_ids.append({'id':ep_w.id,'name':ep_w.display_name})    
        else:
            if type_categ=='st':
                write_st=request.env['mk.student.register'].sudo().search([('mosque_id','=',masjed_id),('birthdate','!=',False)])
                st_ids=request.env['mk.student.register'].sudo().search([('mosque_id','=',masjed_id),('birthdate','=',False)])
                for ep in st_ids:
                    ids.append({'id':ep.id,'name':ep.display_name})

                for ep_w in write_st:
                    write_ids.append({'id':ep_w.id,'name':ep_w.display_name})    
            else:
                if type_categ=='te':
                    te_ids=request.env['hr.employee'].sudo().search([('category','=','teacher'),('write_date','=',False),'|',('mosque_id','=',masjed_id),('mosqtech_ids','in',masjed_id)])
                    write_te=request.env['hr.employee'].sudo().search([('category','=','teacher'),('write_date','!=',False),'|',('mosque_id','=',masjed_id),('mosqtech_ids','in',masjed_id)])

                    for ep in te_ids:
                        ids.append({'id':ep.id,'name':ep.name})

                    for ep_w in write_te:
                        write_ids.append({'id':ep_w.id,'name':ep_w.name})    
        
                else:
                    if type_categ=='sup':
                        s_ids=request.env['hr.employee'].sudo().search([('category','=','supervisor'),('write_date','=',False),'|',('mosque_id','=',masjed_id),('mosqtech_ids','in',masjed_id)])
                        write_s=request.env['hr.employee'].sudo().search([('category','=','supervisor'),('write_date','!=',False),'|',('mosque_id','=',masjed_id),('mosqtech_ids','in',masjed_id)])

                        for ep in s_ids:
                            ids.append({'id':ep.id,'name':ep.name})

                        for ep_w in write_s:
                            write_ids.append({'id':ep_w.id,'name':ep_w.name})  

        return str({'ids':ids,'write_ids':write_ids})

    @http.route('/get/mosque/edu_supervisor/<int:center_id>/<string:gategory>/<int:edu_sup>', type='json', auth='public',  csrf=False)
    def get_study_class(self,center_id,gategory,edu_sup,**args):
        result=[]

        domain=[]

        if edu_sup==0:
            #1
            domain=[('center_department_id','=',center_id)]
            if gategory!='all':
                cat=request.env['mk.mosque.category'].sudo().search([('mosque_type','=',gategory)])
                #2
                domain=[('center_department_id','=',center_id),('categ_id','in',cat.ids)]
                    
        else:
            edu_supervisor=request.env['hr.employee'].sudo().search([('id','=',edu_sup)])
            #3
            domain=[('id','in',edu_supervisor.mosque_sup.ids)]

        mosques=request.env['mk.mosque'].sudo().search(domain)
        for mosq in mosques:
            result.append({'id':mosq.id,'name':mosq.name})
        return str(result)

    @http.route('/get/edu_supervisor/<int:center_id>/<string:gender>', type='json', auth='public',  csrf=False)
    def get_edu_supervisors(self, center_id,gender,**args):
        ids=[]
        result=[]
        mosque_ids=request.env['mk.mosque'].sudo().search([('center_department_id','=', center_id)])
        query='''select hr_employee_id from hr_employee_mk_mosque_rel where mk_mosque_id IN %(mosque)s'''


        cr=request.env.cr
        sup_ids=cr.execute(query,{'mosque':tuple(mosque_ids.ids)})
        sup = request.env.cr.dictfetchall()
        for rec in sup:
            if rec['hr_employee_id'] not in ids:
                ids.append(rec['hr_employee_id'])
        
        if gender=='all':
            edu_sups=request.env['hr.employee'].sudo().search([('id','in', ids)])
        else:
            edu_sups=request.env['hr.employee'].sudo().search([('gender', '=', gender),('id','in', ids)])
        if edu_sups:
            for edu_sup in edu_sups:
                result.append({'id':edu_sup.id,'name':edu_sup.name})
        return str(result)

    @http.route('/register/supervisor_details/<int:sup_id>/<int:masjed_id>', type='json', auth='public',csrf=False)
    def supervisor_details(self,sup_id,masjed_id,**args):
        result=[]
        if masjed_id==0:
            mosque_ids=request.env['hr.employee'].sudo().search([('id','=',sup_id)])
            masjed_domain=[('id','in',mosque_ids[0].mosque_sup.ids)]
        else:
            masjed_domain=[('id','=',masjed_id)]

        masjed_masjeds_ids=request.env['mk.mosque'].sudo().search(masjed_domain)

        for masjed in masjed_masjeds_ids:
            is_write=False
            if masjed.write_date:
                is_write=True
            episode_domain=[('mosque_id','=',masjed.id)]
            episode_write=[('mosque_id','=',masjed.id),('write_date','!=',False)]
            
            student_domain=[('mosque_id','=',masjed.id)]
            student_write_domain=[('mosque_id','=',masjed.id),('write_date','!=',False),('birthdate','!=',False)]
            
            teachers_domain=[('category','=','teacher'),'|',('mosque_id','=',masjed.id),('mosqtech_ids','in',masjed.id)]
            teachers_write_domain=[('category','=','teacher'),('write_date','!=',False),'|',('mosque_id','=',masjed.id),('mosqtech_ids','in',masjed.id)]
            
            supervisors_domain=[('category','=','supervisor'),'|',('mosque_id','=',masjed.id),('mosqtech_ids','in',masjed.id)]
            supervisors_write_domain=[('category','=','supervisor'),('write_date','!=',False),'|',('mosque_id','=',masjed.id),('mosqtech_ids','in',masjed.id)]

            dictt=({'mosque_name':masjed.name,
                    'mosque_is_write':is_write,
                    
                    'all_episodes':len(request.env['mk.episode'].sudo().search(episode_domain)),
                    'write_episodes':len(request.env['mk.episode'].sudo().search(episode_write)),
                    
                    'all_supervisors':len(request.env['hr.employee'].sudo().search(supervisors_domain)),
                    'write_supervisors':len(request.env['hr.employee'].sudo().search(supervisors_write_domain)),
                    
                    'all_teachers':len(request.env['hr.employee'].sudo().search(teachers_domain)), 
                    'write_teachers':len(request.env['hr.employee'].sudo().search(teachers_write_domain)),
                    
                    'all_students':len(request.env['mk.student.register'].sudo().search(student_domain)), 
                    'write_students':len(request.env['mk.student.register'].sudo().search(student_write_domain))})
            result.append(dictt)

        return str({'mosques_of_supervisor':result})

    @http.route('/get/mosque/<int:mosque_id>',type='json',auth='public',csrf=False)
    def get_mosque_id(self,mosque_id,**args):

        result=[]
        teacher_ids=request.env['hr.employee'].sudo().search([('mosqtech_ids', 'in', [mosque_id]), ('category','=','teacher')])
        for teacher in teacher_ids:
            result.append({'id':teacher.id,'name':teacher.name})
        return str(result)

    @http.route('/dashboard/teacher/<teaccher_id>/<type_follow>/<ep_id>',type='http',auth='public',csrf=False)
    def get_dashboard(self,teaccher_id,type_follow,ep_id,**args):

        result=request.env['get.top.five.teacher'].get_injaz(teaccher_id,type_follow,ep_id)

        
        return "Done"
