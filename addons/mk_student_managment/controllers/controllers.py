# -*- coding: utf-8 -*-
import odoo.http as http
from odoo.http import Response
from odoo import SUPERUSER_ID
from odoo import models, fields, api, tools
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo import _
from odoo.osv import osv
import sys, json
import logging
_logger = logging.getLogger(__name__)
from odoo.http import request
from odoo import http
class mk_student_managment(http.Controller):
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

    def get_test_record(self,student_id) :
        #pre_obj=request.env['mk.student.prepare']
        obj_test = request.env['mk.test.line'].sudo().browse([SUPERUSER_ID]).search([('line_id.link_id.student_id','=',student_id)])
        #student_ids = self.line_id.link_id.student_id
        #test_student_ids=self.search([('line_id','=',line_id)])
       # ###'55555555555555555555555', test_student_ids
        
        records=[]
        rec_dict=[]
        dict_line1 = []
        dict_error = []

        teatcher_id = 0
        teacher_name = ''
        episode_id = 0
        episode_name = ''
        date = ''
        #type_follow = ''

        for rec in obj_test:
            #
            #object_mistakes=request.env['mk.details.mistake']
            episode_id=rec.line_id.stage_pre_id.id
            if rec.line_id.stage_pre_id:
                episode_name= rec.line_id.stage_pre_id.name 
            else:
                episode_name=False
            teacher_id=rec.line_id.name.id
            if rec.line_id.name.name:
               teacher_name=rec.line_id.name.name 
            else:
                teacher_name=False

            subject_id = rec.subject_id.name 
            date = rec.date
            day = rec.day
            actual_day = rec.actual_day
            actual_date = rec.actual_date
            check = rec.check
            degree = rec.degree
            date=rec.line_id.prepare_date
            state = rec.state
            line_id = rec.line_id

            for rec_que in rec.test_question_ids:

                from_verse = rec_que.from_verse.id
                to_verse = rec_que.to_verse.id
                from_surah = rec_que.from_surah.name 
                to_surah = rec_que.to_surah.name 
                mistake_q = rec_que.mistake
                for rec_error in rec_que.quest_mistake_ids:

                    name_mistake_id = rec_error.name_mistake_id.name 
                    number_mistake = rec_error.number_mistake
                    lst1 = []
                    dict_error=({
                        'name_mistake_id': name_mistake_id,
                        'number_mistake': number_mistake,
                    })
                    lst1.append(dict_error)           
                    
                dict_qute=({
                    'from_surah': from_surah,
                    'from_verse': from_verse,
                    'to_surah': to_surah,
                    'to_verse': to_verse,
                    'mistake_q': mistake_q,
                    'lst1':lst1,
                })
                records.append(dict_qute)

            rec_dict=({
                'line_id':line_id,
                'episode_name':str(episode_name),
                'teacher_name':str(teacher_name),
                'subject_id': subject_id,
                'actual_day':actual_day,
                'actual_date': actual_date,
                'check': check,
                'date':date,
                'degree':degree,
                'state':state,
            })
            records.append(rec_dict)
        return records

    def details_error(self,prep_id):
        dict_line = {}
        dict_error = {}
        lst = []
        dict_record={}
        line_ids = request.env['mk.listen.line'].sudo().browse([SUPERUSER_ID]).search([('id','=', int(prep_id))])
        if line_ids:
            for rec in line_ids:
                for record in rec.mistake_line_ids:
                    dict_error=({
                        'id':record.id,
                        'name_mistake_id':record.name_mistake_id.name,
                        'mistake_code':record.name_mistake_id.code,
                        'mistake_id':record.name_mistake_id.id,
                        'surah_id':record.surah_id.id,
                        'number_mistake':record.number_mistake,
                        'surah_id_name':record.surah_id.name,                    
                        'aya_id':record.aya_id.id,
                        'aya_name':record.aya_id.original_surah_order
                    })
                    lst.append(dict_error)
                dict_record= ({
                'mistake_dict':lst,
                })
        return dict_record

###### prepratin Ayat ################
    def verse_prepare_listen(self,prep_id):
        dict_lst = []
        pages=[]
        line_ids = request.env['mk.listen.line'].sudo().browse([SUPERUSER_ID]).search([('id','=', int(prep_id))])
        if line_ids:
            ayat=request.env['mk.surah.verses']
            aya_from=line_ids[0].from_aya.original_accumalative_order
            to_aya=line_ids[0].to_aya.original_accumalative_order
            dict_lst.append({'from_page':line_ids[0].from_aya.page_no,'to_page':line_ids[0].to_aya.page_no})
            for aya_id in list(range(aya_from,to_aya+1)):
                aya_data=ayat.sudo().browse([SUPERUSER_ID]).search([('original_accumalative_order','=',aya_id)])
                if aya_data:
                    pages.append(aya_data.page_no)
                    dict_lst.append({
                        'surah':aya_data.surah_id.name,
                        'surah_id':aya_data.surah_id.id,
                        'aya_num':aya_data.original_accumalative_order,
                        'page_num':aya_data.page_no,
                        'aya':aya_data.verse,
                        'aya_id':aya_data.id,
                        'aya_order_surah':aya_data.original_surah_order

                        })
        return dict_lst

    ###### Total mistake per line ################
    def line_total_mistake(self,line_id):
        dict_lst = []
        total_galy=0
        total_khafy = 0
        total_lafthy = 0
        total_tjweed = 0
        line_ids = request.env['mk.listen.line'].sudo().browse([SUPERUSER_ID]).search([('id','=', int(line_id))])
        for rec in line_ids:
            total_galy=0
            total_khafy = 0
            total_lafthy = 0
            total_tjweed = 0
            for record in rec.mistake_line_ids:
                if record.name_mistake_id.code== "galy":
                    total_galy+=record.number_mistake
                elif record.name_mistake_id.code== "khafy":
                     total_khafy+=record.number_mistake
                elif record.name_mistake_id.code== "lafzy":
                     total_lafthy+=record.number_mistake
                elif record.name_mistake_id.code== "Tjweed":
                    total_tjweed+=record.number_mistake
            dict_lst.append({
                        'total_galy':total_galy,
                        'total_khafy':total_khafy,
                        'total_lafthy':total_lafthy,
                        'total_tjweed':total_tjweed,
                        })
        return dict_lst


        

############ Std_prep#############################
    def student_prep(self,student_id) :
        academic_recs = request.env['mk.study.year'].sudo().browse([]).search([('active','=',True)])
        year=0
        if academic_recs:
            year=academic_recs[0].id
        student_prepare_obj=request.env['mk.listen.line'].sudo().browse([SUPERUSER_ID])
        st=request.env['mk.link'].sudo().browse([SUPERUSER_ID]).search([('student_id','=',int(student_id)),('year','=',year)])
        if st:
            student_id=st[0].id
        save_student_ids=student_prepare_obj.sudo().browse([SUPERUSER_ID]).search([('student_id','=',student_id),
																				   ('type_follow','=','listen'),
																				   ('state','!=','done')],limit=1,order="order asc")
        smal_rev_student_ids=student_prepare_obj.sudo().browse([SUPERUSER_ID]).search([('student_id','=',student_id),
																					   ('type_follow','=','review_small'),
																					   ('state','!=','done')],limit=1,order="order asc")
        big_rev_student_ids=student_prepare_obj.sudo().browse([SUPERUSER_ID]).search([('student_id','=',student_id),
																					  ('type_follow','=','review_big'),
																					  ('state','!=','done')],limit=1,order="order asc")
        read_student_ids=student_prepare_obj.sudo().browse([SUPERUSER_ID]).search([('student_id','=',student_id),
																				   ('type_follow','=','tlawa'),
																				   ('state','!=','done')],limit=1,order="order asc")

    
        records=[]
        dict_line=[]
        period=''
        teatcher_id = 0
        teacher_name = ''
        episode_id = 0
        episode_name = ''
        date = ''
        type_follow = ''

        #if save_student_ids:
        for rec in save_student_ids:
            #if rec.save_id:
            object_mistakes=request.env['mk.details.mistake'].sudo().browse([SUPERUSER_ID])
            #episode_name= rec.save_id.stage_pre_id.name 
            #teacher_name=rec.save_id.name.name 
            # episode_id=rec.save_id.stage_pre_id.id
            if rec.preparation_id.stage_pre_id:
                episode_name= rec.preparation_id.stage_pre_id.name 
            else:
                episode_name=False
            teacher_id=rec.preparation_id.name.id
            if rec.preparation_id.name.name:
                teacher_name=rec.preparation_id.name.name 
            else:
                    teacher_name=False

            date=rec.preparation_id.prepare_date
            type_follow = 'listen'

            actual_date = rec.actual_date
            student_name=rec.student_id.display_name 
            actual_day = rec.actual_day
            is_test = rec.is_test
            check = rec.check
            delay = rec.delay
            permission_id = rec.permission_id.id
            state = rec.state
            degree = rec.degree
            mistake = rec.mistake
            from_sura_name = rec.from_surah.name 
            from_aya = rec.from_aya.original_surah_order
            to_sura_name = rec.to_surah.name 
            to_aya = rec.to_aya.original_surah_order
            lst=[]
            
            for record in rec.mistake_line_ids:
                dict_line=({
                    'id':record.id,
                    'mistake_code':record.name_mistake_id.code,
                    'mistake_id':record.name_mistake_id.id,
                    'surah_id':record.surah_id.id,
                    'number_mistake':record.number_mistake,
                    'surah_id_name':record.surah_id.name,                    
                    'aya_id':record.aya_id.id,
                    'aya_name':record.aya_id.original_surah_order
                })
                lst.append(dict_line)
            #return lst
            
 
            rec_dict=({
                #'mistakes':lst,
                'type_follow':type_follow,
                'actual_day':actual_day,
                'actual_date': actual_date,
                'student_name':str(student_name),
                'is_test':is_test,
                'date':date,
                'prep_id':rec.id,
                'episode_name':str(episode_name),
                'teacher_name':str(teacher_name),
                #'subject_name':str(subject_name),
                'from_sura_name':str(from_sura_name),
                'from_aya':from_aya,
                'to_sura_name':str(to_sura_name),
                'to_aya':to_aya,
                'check':check,
                'delay':delay,
                'permission_id':permission_id,
                'state':state,
                'period':period,
                'degree':degree,
                'mistake':mistake,
                'mistake_dict':lst,
            })
            records.append(rec_dict)
            
        
    

#################### Small Review #####################
        #if smal_rev_student_ids:
        for rec in smal_rev_student_ids:
            ####rec, '######################################Rec'
            object_mistakes=request.env['mk.details.mistake'].sudo().browse([SUPERUSER_ID])
            if rec.preparation_id.stage_pre_id:
                episode_name= rec.preparation_id.stage_pre_id.name 
            else:
                episode_name=False
            #episode_id=rec.sr_line_id.stage_pre_id.id
            #episode_name= rec.sr_line_id.stage_pre_id.name 
            #teacher_id=rec.save_id.name.id
            if rec.preparation_id.name.name:
               teacher_name=rec.preparation_id.name.name 
            else:
                teacher_name=False
            #teacher_id=rec.sr_line_id.name.id
            #teacher_name=rec.sr_line_id.name 
            date=rec.preparation_id.prepare_date
            type_follow = 'review_small'

            actual_date = rec.actual_date
            student_name=rec.student_id.display_name 
            actual_day = rec.actual_day
            is_test = rec.is_test
            check = rec.check
            delay = rec.delay
            permission_id = rec.permission_id.id
            state = rec.state
            degree = rec.degree
            mistake = rec.mistake
            degree = rec.degree
            from_aya = rec.from_aya.original_surah_order
            to_aya = rec.to_aya.original_surah_order
            from_sura_name = rec.from_surah.name 
            to_sura_name = rec.to_surah.name 
            lst=[]
            
            for record in rec.mistake_line_ids:
                dict_line=({
                    'id':record.id,
                    'name_mistake_id':record.name_mistake_id.name,
                    'mistake_code':record.name_mistake_id.code,
                    'mistake_id':record.name_mistake_id.id,
                    'surah_id':record.surah_id.id,
                    'number_mistake':record.number_mistake,
                    'surah_id_name':record.surah_id.name,                    
                    'aya_id':record.aya_id.id,
                    'aya_name':record.aya_id.original_surah_order
                })
                lst.append(dict_line)
            #return lst
            
 
            rec_dict1=({
                #'mistakes':lst,
                'type_follow':type_follow,
                'actual_day':actual_day,
                'actual_date': actual_date,
                'student_name':str(student_name),
                'is_test':is_test,
                'date':date,

                'prep_id':rec.id,
                'episode_name':str(episode_name),
                'teacher_name':str(teacher_name),
                #'subject_name':str(subject_name),
                'from_sura_name':str(from_sura_name),
                'from_aya':from_aya,
                'to_sura_name':str(to_sura_name),
                'to_aya':to_aya,
                'check':check,
                'delay':delay,
                'permission_id':permission_id,
                'state':state,
                'period':period,
                'degree':degree,
                'mistake':mistake,
                'mistake_dict':lst,
            })
            records.append(rec_dict1)
                #return records
  
            #(episode id , episode_name ,teacher_name,date ,mosque ,)
#######################Big Review#####################################
        #if big_rev_student_ids:
        for rec in big_rev_student_ids:
            object_mistakes=request.env['mk.details.mistake'].sudo().browse([SUPERUSER_ID])
            #episode_id=rec.save_id.stage_pre_id.id
            #episode_name= rec.save_id.stage_pre_id.name 
            #teacher_id=rec.save_id.name.id
            #teacher_name=rec.save_id.name.name 
            if rec.preparation_id.stage_pre_id:
                episode_name= rec.preparation_id.stage_pre_id.name 
            else:
                episode_name=False
            if rec.preparation_id.name.name:
                teacher_name=rec.preparation_id.name.name 
            else:
                teacher_name=False
            date=rec.preparation_id.prepare_date
            type_follow = 'review_big'

            actual_date = rec.actual_date
            student_name=rec.student_id.display_name 
            actual_day = rec.actual_day
            is_test = rec.is_test
            check = rec.check
            delay = rec.delay
            permission_id = rec.permission_id.id
            state = rec.state
            mistake = rec.mistake
            degree = rec.degree
            from_aya = rec.from_aya.original_surah_order
            to_aya = rec.to_aya.original_surah_order
            from_sura_name = rec.from_surah.name 
            to_sura_name = rec.to_surah.name 
            lst = []
            
            for record in rec.mistake_line_ids:
                dict_line=({
                    'id':record.id,
                    'name_mistake_id':record.name_mistake_id.name,
                    'mistake_code':record.name_mistake_id.code,
                    'mistake_id':record.name_mistake_id.id,
                    'surah_id':record.surah_id.id,
                    'number_mistake':record.number_mistake,
                    'surah_id_name':record.surah_id.name,                    
                    'aya_id':record.aya_id.id,
                    'aya_name':record.aya_id.original_surah_order
                })
                lst.append(dict_line)
            
 
            rec_dict=({
                'type_follow':type_follow,
                'actual_day':actual_day,
                'actual_date': actual_date,
                'student_name':str(student_name),
                'is_test':is_test,
                'date':date,
                'prep_id':rec.id,
                'episode_name':str(episode_name),
                'teacher_name':str(teacher_name),
                #'subject_name':str(subject_name),
                'from_sura_name':str(from_sura_name),
                'from_aya':from_aya,
                'to_sura_name':str(to_sura_name),
                'to_aya':to_aya,
                'check':check,
                'delay':delay,
                'permission_id':permission_id,
                'state':state,
                'period':period,
                'degree':degree,
                'mistake':mistake,
                'mistake_dict':lst,
            })
            records.append(rec_dict)
            
#################### Reading Tajweed##################################
        for rec in read_student_ids:
            object_mistakes=request.env['mk.details.mistake'].sudo().browse([SUPERUSER_ID])
            #episode_id=rec.save_id.stage_pre_id.id
            #episode_name= rec.save_id.stage_pre_id.name 
            #teacher_id=rec.save_id.name.id
            #teacher_name=rec.save_id.name.name 
            if rec.preparation_id.stage_pre_id:
                episode_name= rec.preparation_id.stage_pre_id.name 
            else:
                episode_name=False
            if rec.preparation_id.name.name:
                teacher_name=rec.preparation_id.name.name 
            else:
                    teacher_name=False
            date=rec.preparation_id.prepare_date
            type_follow = 'tlawa'

            actual_date = rec.actual_date
            student_name=rec.student_id.display_name 
            actual_day = rec.actual_day
            is_test = rec.is_test
            check = rec.check
            delay = rec.delay
            permission_id = rec.permission_id.id
            state = rec.state
            degree = rec.degree
            mistake = rec.mistake
            from_aya = rec.from_aya.original_surah_order
            to_aya = rec.to_aya.original_surah_order
            from_sura_name = rec.from_surah.name 
            to_sura_name = rec.to_surah.name 
            lst = []
            
            for record in rec.mistake_line_ids:
                dict_line=({
                    'id':record.id,
                    'name_mistake_id':record.name_mistake_id.name,
                    'mistake_code':record.name_mistake_id.code,
                    'mistake_id':record.name_mistake_id.id,
                    'surah_id':record.surah_id.id,
                    'number_mistake':record.number_mistake,
                    'surah_id_name':record.surah_id.name,                    
                    'aya_id':record.aya_id.id,
                    'aya_name':record.aya_id.original_surah_order
                })
                lst.append(dict_line)
            
            
            rec_dict=({
                'type_follow':type_follow,
                'actual_day':actual_day,
                'actual_date': actual_date,
                'student_name':str(student_name),
                'is_test':is_test,
                'date':date,
                'prep_id':rec.id,
                'episode_name':str(episode_name),
                'teacher_name':str(teacher_name),
                #'subject_name':str(subject_name),
                'from_sura_name':str(from_sura_name),
                'from_aya':from_aya,
                'to_sura_name':str(to_sura_name),
                'to_aya':to_aya,
                'check':check,
                'delay':delay,
                'permission_id':permission_id,
                'state':state,
                'period':period,
                'degree':degree,
                'mistake':mistake,
                'mistake_dict':lst,
            })
            records.append(rec_dict)
        return records


    def get_prepration_record(self,student_id,episode) :
        academic_recs = request.env['mk.study.year'].sudo().browse([SUPERUSER_ID]).search([('active','=',True)])
        year=0
        if academic_recs:
            year=academic_recs[0].id
        student_prepare_obj=request.env['mk.listen.line']
        #st=request.env['mk.link'].sudo().browse([SUPERUSER_ID]).search([('id','=',int(student_id)),('episode_id','=',int(episode)),('year','=',year)])
        #if st:
        #    student_id=st[0].id
        save_student_ids=student_prepare_obj.sudo().browse([SUPERUSER_ID]).search([('student_id','=',student_id),('type_follow','=','listen')])
        smal_rev_student_ids=student_prepare_obj.sudo().browse([SUPERUSER_ID]).search([('student_id','=',student_id),('type_follow','=','review_small')])
        big_rev_student_ids=student_prepare_obj.sudo().browse([SUPERUSER_ID]).search([('student_id','=',student_id),('type_follow','=','review_big')])
        read_student_ids=student_prepare_obj.sudo().browse([SUPERUSER_ID]).search([('student_id','=',student_id),('type_follow','=','tlawa')])



        records=[]
        dict_line=[]
        period=''
        teatcher_id = 0
        teacher_name = ''
        episode_id = 0
        episode_name = ''
        date = ''
        type_follow = ''

        

        #if save_student_ids:
        for rec in save_student_ids:
                        #if rec.save_id:
            object_mistakes=request.env['mk.details.mistake'].sudo().browse([SUPERUSER_ID])
            #episode_name= rec.save_id.stage_pre_id.name 
            #teacher_name=rec.save_id.name.name 
            # episode_id=rec.save_id.stage_pre_id.id
            if rec.preparation_id.stage_pre_id:
                episode_name= rec.preparation_id.stage_pre_id.name 
            else:
                episode_name=False
            teacher_id=rec.preparation_id.name.id
            if rec.preparation_id.name.name:
                teacher_name=rec.preparation_id.name.name 
            else:
                    teacher_name=False

            date=rec.preparation_id.prepare_date
            type_follow = 'listen'

            actual_date = rec.actual_date
            student_name=rec.student_id.display_name 
            #actual_day = rec.actual_day
            actual_day = ""
            is_test = rec.is_test
            check = rec.check
            delay = rec.delay
            permission_id = rec.permission_id.id
            state = rec.state
            degree = rec.degree
            mistake = rec.mistake
            from_sura_name = rec.from_surah.name 
            from_aya = rec.from_aya.original_surah_order
            to_sura_name = rec.to_surah.name 
            to_aya = rec.to_aya.original_surah_order
            lst=[]
            
            for record in rec.mistake_line_ids:
                dict_line=({
                    'name_mistake_id':record.name_mistake_id.name,
                    'mistake_code':record.name_mistake_id.code,
                    'mistake_id':record.name_mistake_id.id,
                    'surah_id':record.surah_id.id,
                    'number_mistake':record.number_mistake,
                    'surah_id_name':record.surah_id.name,            
                    'aya_id':record.aya_id.id,
                    'aya_name':record.aya_id.original_surah_order
                })
                lst.append(dict_line)
                #return lst
            
 
            rec_dict=({
                'mistakes':lst,
                'type_follow':type_follow,
                'actual_day':actual_day,
                'actual_date': actual_date,
                'student_name':str(student_name),
                'is_test':is_test,
                'date':date,
                'prep_id':rec.id,
                'episode_name':str(episode_name),
                'teacher_name':str(teacher_name),
                #'subject_name':str(subject_name),
                'from_sura_name':str(from_sura_name),
                'from_aya':from_aya,
                'to_sura_name':str(to_sura_name),
                'to_aya':to_aya,
                'check':check,
                'delay':delay,
                'permission_id':permission_id,
                'state':state,
                'mistake_dict':lst,
                'mistake':mistake,
                'period':period,
            })
            records.append(rec_dict)
            
                
            #(episode id , episode_name ,teacher_name,date ,mosque ,)
        
    

#################### Small Review #####################
        #if smal_rev_student_ids:
        for rec in smal_rev_student_ids:
            ####rec, '######################################Rec'
            object_mistakes=request.env['mk.details.mistake'].sudo().browse([SUPERUSER_ID])
            if rec.preparation_id.stage_pre_id:
                episode_name= rec.preparation_id.stage_pre_id.name 
            else:
                episode_name=False
            #episode_id=rec.sr_line_id.stage_pre_id.id
            #episode_name= rec.sr_line_id.stage_pre_id.name 
            #teacher_id=rec.save_id.name.id
            if rec.preparation_id.name.name:
               teacher_name=rec.preparation_id.name.name 
            else:
                teacher_name=False
            #teacher_id=rec.sr_line_id.name.id
            #teacher_name=rec.sr_line_id.name 
            date=rec.preparation_id.prepare_date
            type_follow = 'review_small'

            actual_date = rec.actual_date
            student_name=rec.student_id.display_name 
            #actual_day = rec.actual_day
            actual_day = ""
            is_test = rec.is_test
            check = rec.check
            delay = rec.delay
            permission_id = rec.permission_id.id
            state = rec.state
            degree = rec.degree
            mistake = rec.mistake
            degree = rec.degree
            from_aya = rec.from_aya.original_surah_order
            to_aya = rec.to_aya.original_surah_order
            from_sura_name = rec.from_surah.name 
            to_sura_name = rec.to_surah.name 
            lst=[]

            for record in rec.mistake_line_ids:
                dict_line=({
                    'name_mistake_id':record.name_mistake_id.name,
                    'mistake_code':record.name_mistake_id.code,
                    'mistake_id':record.name_mistake_id.id,
                    'surah_id':record.surah_id.id,
                    'number_mistake':record.number_mistake,
                    'surah_id_name':record.surah_id.name,
                    'aya_id':record.aya_id.id,
                    'aya_name':record.aya_id.original_surah_order
                })
                lst.append(dict_line)
            #return lst
 
            rec_dict1=({
                #'mistakes':lst,
                'type_follow':type_follow,
                'actual_day':actual_day,
                'actual_date': actual_date,
                'student_name':str(student_name),
                'is_test':is_test,
                'date':date,
                'prep_id':rec.id,
                'episode_name':str(episode_name),
                'teacher_name':str(teacher_name),
                #'subject_name':str(subject_name),
                'from_sura_name':str(from_sura_name),
                'from_aya':from_aya,
                'to_sura_name':str(to_sura_name),
                'to_aya':to_aya,
                'check':check,
                'delay':delay,
                'permission_id':permission_id,
                'state':state,
                'period':period,
                'degree':degree,
                'mistake':mistake,
                'mistake_dict':lst,
            })
            records.append(rec_dict1)
                #return records
  
            #(episode id , episode_name ,teacher_name,date ,mosque ,)
#######################Big Review#####################################
        #if big_rev_student_ids:
        for rec in big_rev_student_ids:
            object_mistakes=request.env['mk.details.mistake'].sudo().browse([SUPERUSER_ID])
            #episode_id=rec.save_id.stage_pre_id.id
            #episode_name= rec.save_id.stage_pre_id.name 
            #teacher_id=rec.save_id.name.id
            #teacher_name=rec.save_id.name.name 
            if rec.preparation_id.stage_pre_id:
                episode_name= rec.preparation_id.stage_pre_id.name 
            else:
                episode_name=False
            if rec.preparation_id.name.name:
                teacher_name=rec.preparation_id.name.name 
            else:
                teacher_name=False
            date=rec.preparation_id.prepare_date
            type_follow = 'review_big'

            actual_date = rec.actual_date
            student_name=rec.student_id.display_name 
            #actual_day = rec.actual_day
            actual_day = ""
            is_test = rec.is_test
            check = rec.check
            delay = rec.delay
            permission_id = rec.permission_id.id
            state = rec.state
            mistake = rec.mistake
            degree = rec.degree
            from_aya = rec.from_aya.original_surah_order
            to_aya = rec.to_aya.original_surah_order
            from_sura_name = rec.from_surah.name 
            to_sura_name = rec.to_surah.name 
            lst = []
            for record in rec.mistake_line_ids:
                dict_line=({
                   'name_mistake_id':record.name_mistake_id.name,
                    'mistake_code':record.name_mistake_id.code,
                    'mistake_id':record.name_mistake_id.id,
                    'surah_id':record.surah_id.id,
                    'number_mistake':record.number_mistake,
                    'surah_id_name':record.surah_id.name,
                    'aya_id':record.aya_id.id,
                    'aya_name':record.aya_id.original_surah_order
                })
                lst.append(dict_line)
      
            rec_dict=({
                'type_follow':type_follow,
                'actual_day':actual_day,
                'actual_date': actual_date,
                'student_name':str(student_name),
                'is_test':is_test,
                'date':date,
                'prep_id':rec.id,
                'episode_name':str(episode_name),
                'teacher_name':str(teacher_name),
                #'subject_name':str(subject_name),
                'from_sura_name':str(from_sura_name),
                'from_aya':from_aya,
                'to_sura_name':str(to_sura_name),
                'to_aya':to_aya,
                'check':check,
                'delay':delay,
                'permission_id':permission_id,
                'state':state,
                'period':period,
                'degree':degree,
                'mistake':mistake,
                'mistake_dict':lst,
            })
            records.append(rec_dict)
            
#################### Reading Tajweed##################################
        for rec in read_student_ids:
            object_mistakes=request.env['mk.details.mistake'].sudo().browse([SUPERUSER_ID])
            #episode_id=rec.save_id.stage_pre_id.id
            #episode_name= rec.save_id.stage_pre_id.name 
            #teacher_id=rec.save_id.name.id
            #teacher_name=rec.save_id.name.name 
            if rec.preparation_id.stage_pre_id:
                episode_name= rec.preparation_id.stage_pre_id.name 
            else:
                episode_name=False
            if rec.preparation_id.name.name:
                teacher_name=rec.preparation_id.name.name 
            else:
                    teacher_name=False
            date=rec.preparation_id.prepare_date
            type_follow = 'tlawa'

            actual_date = rec.actual_date
            student_name=rec.student_id.display_name 
            #actual_day = rec.actual_day
            actual_day = ""
            is_test = rec.is_test
            check = rec.check
            delay = rec.delay
            permission_id = rec.permission_id.id
            state = rec.state
            degree = rec.degree
            mistake = rec.mistake
            from_aya = rec.from_aya.original_surah_order
            to_aya = rec.to_aya.original_surah_order
            from_sura_name = rec.from_surah.name 
            to_sura_name = rec.to_surah.name 
            lst = []
            for record in rec.mistake_line_ids:
                dict_line=({
                    'name_mistake_id':record.name_mistake_id.name,
                    'mistake_code':record.name_mistake_id.code,
                    'mistake_id':record.name_mistake_id.id,
                    'surah_id':record.surah_id.id,
                    'number_mistake':record.number_mistake,
                    #'total_tjweed':total_tjweed,
                    'surah_id_name':record.surah_id.name,
                    'aya_id':record.aya_id.id,
                    'aya_name':record.aya_id.original_surah_order,
                })

                lst.append(dict_line)
      
 
            rec_dict=({
                'type_follow':type_follow,
                'actual_day':actual_day,
                'actual_date': actual_date,
                'student_name':str(student_name),
                'is_test':is_test,
                'date':date,
                'prep_id':rec.id,
                'episode_name':str(episode_name),
                'teacher_name':str(teacher_name),
                #'subject_name':str(subject_name),
                'from_sura_name':str(from_sura_name),
                'from_aya':from_aya,
                'to_sura_name':str(to_sura_name),
                'to_aya':to_aya,
                'check':check,
                'delay':delay,
                'permission_id':permission_id,
                'state':state,
                'period':period,
                'degree':degree,
                'mistake':mistake,
                'mistake_dict':lst,
            })
            records.append(rec_dict)
        return records

    @http.route('/register/get_report/<string:student_id>/<string:date_from>/<string:date_to>', type='http', auth='public',  csrf=False)
    def get_report(self, student_id, date_from, date_to, **args):

        obj_attendance = request.env['attendance.certificate'].sudo().browse([SUPERUSER_ID])

        pdf = obj_attendance.get_pdf(int(student_id), date_from, date_to)[0]
        
        pdfhttpheaders = [('Content-Type',        'application/pdf'),
                          ('Content-Length',      len(pdf)),
                          ('Content-Disposition', 'attachment; filename="report.pdf"'),]
        
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route('/register/get_comment/<int:student_id>/<string:date>/<int:episode_id>', type='json', auth='public',  csrf=False)
    def get_comment(self,student_id,date,episode_id,**args):
        result=[]
        obj_comment_lines = request.env['mk.comments.behavior.student.lines']
        obj_comments = request.env['mk.comments.behavior.students']
        link_id=request.env['mk.link'].sudo().search([('student_id','=',student_id),('episode_id','=',episode_id)]).id
        episode_rec=obj_comments.sudo().search([('date','=',date),('episode','=',episode_id)]).id
        lines=obj_comment_lines.sudo().search([('link_id','=',episode_rec),('student','=',link_id)])
        for line in lines:
            result.append({'behavior':line.comment_id.name,'punishment':line.punishment_id.name,'type':line.comment_id.type})

        
        return str(result)

    @http.route('/register/create_comment/<int:student_id>/<string:date>/<int:episode_id>/<int:comment>', type='http', auth='public',  csrf=False)
    def create_comment(self,student_id,date,episode_id,comment,**args):
        punishment=args.get('punishment',False)
        comment_rec=0
        obj_comment_lines = request.env['mk.comments.behavior.student.lines']
        obj_comments = request.env['mk.comments.behavior.students']
        link_id=request.env['mk.link'].sudo().search([('student_id','=',student_id),('episode_id','=',episode_id)]).id
        episode_rec=obj_comments.sudo().search([('date','=',date),('episode','=',episode_id)])
        episode=request.env['mk.episode'].sudo().browse([episode_id])
        comment_obj=request.env['mk.comment.behavior'].sudo().search([('id','=',comment)])
        if comment_obj:
            if episode_rec:
                comment_rec=episode_rec.id
            else:
                comment_rec=obj_comments.sudo().create({'date':date,'teacher':episode.teacher_id.id,'masjed':episode.mosque_id.id,'episode':episode_id,'Period':episode.selected_period}).id
            
            if punishment and request.env['mk.punishment'].sudo().search([('id','=',punishment)]):
                line=obj_comment_lines.sudo().create({'student':link_id,'comment_id':comment,'punishment_id':punishment,'link_id':comment_rec})
            else:
                line=obj_comment_lines.sudo().create({'student':link_id,'comment_id':comment,'link_id':comment_rec})
            if line:
                return "True"
            else:
                return "False"

        
        else:
            return "False"

    @http.route('/register/get_comments/behaviors/<int:type>', type='json', auth='public',  csrf=False)
    def get_comments_behaviors(self,type,**args):
        result=[]
        obj_comments = request.env['mk.comment.behavior']
        if type == 1:
            domain=[('type','=','general_comment')]
        else:
            domain=[('type','=','behavior')]
        records=obj_comments.sudo().search(domain)
        for rec in records:
            result.append(rec.name)

        
        return str(result)

    @http.route('/register/create_ticket/<string:teacher_identity>/<int:center_id>/<string:subject>', type='http', auth='public',  csrf=False)
    def create_ticket(self,teacher_identity,center_id,subject,**args):
        user=9792
        email=args.get('email','')
        suggest=args.get('suggestion','')
        teacher=request.env['hr.employee'].sudo().search([('identification_id','=',teacher_identity),('category','=','teacher')])
        if teacher and teacher.user_id:

            user=teacher.user_id.id
        
        tickets = request.env['website.support.ticket']
        line=tickets.sudo().create({'create_user_id':user,'email':email,'description':suggest,'subject':subject,'center_id':center_id})
        if line:
            return "True"

        
        else:
            return "False"

    def get_student_behavior_rec(self,student_id):
        #this fuction is return student behavior record of Entred student_id
        behavior_obj = request.env['mk.comments.behavior.student.lines']

        student_ids = behavior_obj.sudo().search([('student','=',student_id)])


        records=[]
        rec_dict=[]
        for rec in student_ids:
            links_id = rec.student
            student_name = links_id.student_id.display_name
            episode_id =links_id.episode_id
            episode_name =links_id.episode_id.name
            comment_name =rec.comment_id.name
            if rec.punishment_id:
                punishment_name = rec.punishment_id.name
            else:
                punishment_name = ''
            date=rec.link_id.date
            teach_name =rec.link_id.teacher.name
            masjed_name =rec.link_id.masjed.name

            rec_dict=({
                'id':rec.id,
                'student_id':student_id,
                'student_name':str(student_name),
                'episode_id':episode_id.id,
                'episode_name':str(episode_name),
                'comment_name':str(comment_name),
                'punishment_name':str(punishment_name),
                'teacher_name':str(teach_name),
                'masjed_name':str(masjed_name),
                'punish_date':date,
                'period':rec.link_id.period_id.id,
                'date':rec.create_date,
            })
            records.append(rec_dict)
        return records

    @http.route('/register/punishment/<int:pun_id>',type='json',auth='public',csrf=False)
    def get_behavior_record(self,pun_id=None,**args):
        result=[]
        pun_obj=request.env['mk.punishment'].sudo().browse([SUPERUSER_ID])
        punishments=pun_obj.search([('id', '=', pun_id)])
        for record in punishments:
            rec_dict=({
                'id':record.id,
                'name':record.name,
                'deduct_from_degrees':record.deduct_from_degrees,
                'deduct_from_points':record.deduct_from_points,
                'guardian_call':record.guardian_call,
                'guardian_message':record.guardian_message,
                'mosque_message':record.mosque_message,
                'freeze_study_class':record.freeze_study_class,


            })

            result.append(rec_dict)
        
        #records=records[:-2]
        #records=records[2:]
        return str(result)
    @http.route('/register/behavior/<int:student_id>/<string:episode>',type='json',auth='public',csrf=False)
    def get_student_behavior(self,student_id,episode,**args):
        res = []
        academic_recs = request.env['mk.study.year'].sudo().browse([SUPERUSER_ID]).search([('active','=',True)])
        year=0
        if academic_recs:
            year=academic_recs[0].id
        mk_student_object=request.env['mk.link'].sudo().browse([SUPERUSER_ID]).search([('student_id','=',int(student_id)),('year','=',year),('episode_id','=',int(episode))])
        if mk_student_object:
            student_id=mk_student_object[0].id
            obj_behavior = request.env['mk.comments.behavior.student.lines'].sudo().browse([SUPERUSER_ID])
            res = self.get_student_behavior_rec(student_id)
            return str(res)
        else:
            return str(res)

    @http.route('/register/student_attendance_records/<string:student_id>/<string:episode>',type='json',auth='public',csrf=False)
    def student_attendance(self,student_id,episode,**args):
        academic_recs = request.env['mk.study.year'].sudo().browse([SUPERUSER_ID]).search([('active','=',True)])
        year=0
        if academic_recs:
            year=academic_recs[0].id
        mk_student_object=request.env['mk.link'].sudo().browse([SUPERUSER_ID]).search([('id','=',int(student_id)),('year','=',year),('episode_id','=',int(episode))])
        #if mk_student_object:
        records=[]
        if mk_student_object:
            mk_student_id=mk_student_object[0].id

            student_object=request.env['mk.student.attendace']
            student_ids=student_object.sudo().browse([SUPERUSER_ID]).search([('student','=',mk_student_id)])
            episode_id=0
            episode_name=''
            teacher_id=0
            teacher_name=''
            date=''
            mosque_id=0
            mosque=''
            student_id=0
            student_name=''
            status=''            
            period=''
            if student_ids:
                for rec in student_ids:
                    episode_id=rec.episode_attendace_id.episode.id
                    if rec.episode_attendace_id.episode:
                        episode_name= rec.episode_attendace_id.episode.name
                    else:
                        episode_name=False
                    teacher_id=rec.episode_attendace_id.teacher.id
                    if rec.episode_attendace_id.teacher:
                        teacher_name=rec.episode_attendace_id.teacher.name
                    else:
                        teacher_name=False
                    date=rec.episode_attendace_id.date
                    mosque_id=rec.episode_attendace_id.masjed.id
                    if rec.episode_attendace_id.masjed.name:
                        mosque=rec.episode_attendace_id.masjed.name
                    else:
                        mosque=False
                    student_id=rec.student.student_id.id
                    if rec.student.student_id.display_name:
                        student_name=rec.student.student_id.display_name
                    status=rec.state
                    time=''
                    if rec.student.subh==True:
                        period="subh"
                    if rec.student.aasr==True:
                        period="asar"
                    if rec.student.zuhr==True:
                        period="zuhr"
                    if rec.student.esha==True:
                        period="esha"
                    if rec.student.magrib==True:
                        period="magrib"
                    if period=='subh':
                        time = 'from ' +  str(rec.episode.period_id.subh_period_from) +' ' +'to ' + str(rec.episode.period_id.subh_period_to)
                    if period=='zuhr':
                        time = 'from ' +  str(rec.episode.period_id.zuhr_period_from) +' ' +'to ' + str(rec.episode.period_id.zuhr_period_to)
                    if period=='aasr':
                        time = 'from ' +  str(rec.episode.period_id.aasr_period_from) +' ' +'to ' + str(rec.episode.period_id.aasr_period_to)
                    if period=='magrib':
                        time = 'from ' +  str(rec.episode.period_id.magrib_period_from) +' ' +'to ' + str(rec.episode.period_id.magrib_period_to)
                    if period=='esha':
                        time = 'from ' +  str(rec.episode.period_id.esha_period_from) +' ' +'to ' + str(rec.episode.period_id.esha_period_to)
                    #self.period_time=time
                    rec_dict=({
                        'id':rec.id,
                        'student_id':student_id,
                        'student_name':str(student_name),
                        'date':date,
                        'episode_id':episode_id,
                        'episode_name':str(episode_name),
                        'mosque_id':mosque_id,
                        'mosque_name':str(mosque),
                        'teacher_id':teacher_id,
                        'teacher_name':str(teacher_name),
                        'status':str(status),
                        'att_time':time,
                        'period':period
                    })

                    records.append(rec_dict)

        return str(records)


    def wkf_done(self,line_id):
        line_ids = request.env['mk.listen.line'].sudo().browse([SUPERUSER_ID]).search([('id','=',int(line_id))])
        rec_line = line_ids.search([('preparation_id','=',line_ids[0].preparation_id.id),
								    ('type_follow','=',line_ids[0].type_follow),
								    ('order','<',line_ids[0].order),
								    ('state','!=','done')])
        if rec_line:
           raise osv.except_osv(_('Error'),_('Check your previous preprations.'))
        rec_line = line_ids.search([('preparation_id','=',line_ids[0].preparation_id.id),
								    ('type_follow','=',line_ids[0].type_follow),
								    ('order','<',line_ids[0].order),
								    ('is_test','=',True)], order='order desc')
        count=0
        for l in rec_line:
            count +=1
        test_ids= request.env['mk.test.line'].sudo().browse([SUPERUSER_ID]).search([('line_id','=',line_ids[0].preparation_id.id),
																				    ('state','=','done')])   
        test_count=0
        for test in test_ids:
            test_count+=1
        if count !=test_count and line_ids:
            raise osv.except_osv(_('Error'),_('Check your previous tests.'))
        start_date =datetime.strptime(fields.Date.today(), '%Y-%m-%d')
        line_ids.actual_day=str(start_date.weekday())
        line_ids.actual_date = start_date
        line_ids.state = 'done'
        return True
    
    def wkf_absent(self,line_id):
        line_ids = request.env['mk.listen.line'].sudo().browse([SUPERUSER_ID]).search([('id','=',int(line_id))])
        rec_line = line_ids.search([('preparation_id','=',line_ids[0].preparation_id.id),
								    ('order','<',line_ids[0].order),
								    ('state','!=','done'),
								    ('type_follow','=',line_ids[0].type_follow)])
        if rec_line:
            raise osv.except_osv(_('Error'),_('Check your previous preprations.'))
        rec_line = line_ids.search([('type_follow','=',line_ids[0].type_follow),
								    ('preparation_id','=',line_ids[0].preparation_id.id),
								    ('order','<',line_ids[0].order),
								    ('is_test','=',True)], order='order desc')
        count=0
        for l in rec_line:
            count +=1
        test_ids= request.env['mk.test.line'].sudo().browse([SUPERUSER_ID]).search([('line_id','=',line_ids[0].preparation_id.id),('state','=','done')])   
        test_count=0
        for test in test_ids:
            test_count+=1
        if count !=test_count and rec_line:
            raise osv.except_osv(_('Error'),_('Check your previous tests.'))
        line_ids.state = 'absent'
        line_ids.check = False
        return True

   ###############################################
    def update_student_state(self,std_id,state):

        line_ids = request.env['mk.listen.line'].sudo().search([('student_id','=',int(std_id))])
        rec_line = line_ids.search([('state','!=','done'),('type_follow','=','listen'),('student_id','=',int(std_id))])
        rec_line2 = line_ids.search([('state','!=','done'),('type_follow','=','review_small'),('student_id','=',int(std_id))])
        rec_line3 = line_ids.search([('state','!=','done'),('type_follow','=','review_big'),('student_id','=',int(std_id))])
        rec_line4 = line_ids.search([('state','!=','done'),('type_follow','=','tlawa'),('student_id','=',int(std_id))])

        ##### listen #####
        if rec_line:
           if state == 'absent':
              rec_line[0].state='absent'
           elif state == 'draft':
                rec_line[0].state='draft'
                rec_line[0].delay=False
           elif state == 'delay':
                rec_line[0].delay=True
           elif state == 'no_delay':
                rec_line[0].delay=False
        ######### Review_small#####
        if rec_line2:
           if state == 'absent':
              rec_line2[0].state='absent'
           elif state == 'draft':
                rec_line2[0].state='draft'
                rec_line2[0].delay=False
           elif state == 'delay':
                rec_line2[0].delay=True
           elif state == 'no_delay':
                rec_line2[0].delay=False
        ######## Review big########
        if rec_line3:
           if state == 'absent':
              rec_line3[0].state='absent'
           elif state == 'draft':
                rec_line3[0].state='draft'
                rec_line3[0].delay=False
           elif state == 'delay':
                rec_line3[0].delay=True
           elif state == 'no_delay':
                rec_line3[0].delay=False
        ########## Telawa##########
        if rec_line4:
           if state == 'absent':
              rec_line4[0].state='absent'
           elif state == 'draft':
                rec_line4[0].state='draft'
                rec_line4[0].delay=False
           elif state == 'delay':
                rec_line4[0].delay=True
           elif state == 'no_delay':
                rec_line4[0].delay=False
        return True   

    @http.route('/register/prepration/students_state/<string:std_id>/<string:state>', type='json', auth='public',  csrf=False,)
    def student_stste(self,std_id,state,**args):
        result = self.update_student_state(int(std_id),state)
        return str(result)
 

    @http.route('/register/prepration/student_prepare_records/<string:student_id>/<string:episode>', type='json', auth='public',  csrf=False)
    def student_prepration(self,student_id,episode,**args):
        obj_prepration = request.env['mk.listen.line'].sudo().browse([SUPERUSER_ID])
        result=self.get_prepration_record(int(student_id),int(episode))
        return str(result)

    @http.route('/register/prepration/std_prep/<string:student_id>', type='json', auth='public',  csrf=False,)
    def std_prep(self,student_id,**args):
        obj_std_prep = request.env['mk.listen.line'].sudo().browse([SUPERUSER_ID])
        result=self.student_prep(int(student_id))
        return str(result)

    @http.route('/register/prepration/prep_verses/<string:prep_id>', type='json', auth='public',  csrf=False,)
    def prepration_verses(self,prep_id,**args):
        obj_verses = request.env['mk.listen.line'].sudo().browse([SUPERUSER_ID])
        result=self.verse_prepare_listen(int(prep_id))
        return str(result)

    @http.route('/register/prepration/details_error/<string:prep_id>', type='json', auth='public',  csrf=False,)
    def details_error_c(self,prep_id,**args):
        obj_error = request.env['mk.listen.line'].sudo().browse([SUPERUSER_ID])
        result=self.details_error(int(prep_id))
        return str(result)
   
    @http.route('/register/prepration/line_total_mistake/<string:line_id>', type='json', auth='public',  csrf=False,)
    def line_mistake_tot(self,line_id,**args):
        #obj_listen= request.env['mk.listen.line'].sudo().browse([SUPERUSER_ID])
        result=self.line_total_mistake(int(line_id))
        return str(result)
    

    @http.route('/register/prepration_testing/student_test_records/<string:student_id>', type='json', auth='public',  csrf=False)
    def student_prepration_test(self,student_id,**args):
        obj_prepration_test = request.env['mk.test.line'].sudo().browse([SUPERUSER_ID])
        result=self.get_test_record(int(student_id))
        return str(result)


    @http.route('/register/update_supjects/update_supjects_records/', type='json', auth='public',  csrf=False)
    def update_supjects(self,**args):
        data=args.get('data',{})
        '''data={           

            'teacher':teacher,'episode':episode,'mosque':mosque,
            'students':
                    [[student_id,[prepr_id,type_follow,is_test,from_surah,from_aya,to_surah,to_aya,delay,[[surah_id,aya_id,name_mistake_id,number_mistake]]]]]
            ,            
            'note':[[student,comment_id]]
    
            }
        '''
        obj_subjects = request.env['mk.listen.line'].sudo().browse([SUPERUSER_ID])
        obj_subjects.update_supjects(data)
        return str("True")

    
    

    @http.route('/register/prepration/update_state_done/<string:line_id>', type='json', auth='public',  csrf=False,)
    def update_state_done(self,line_id,**args):
        result=self.wkf_done(int(line_id))
        return str(result)
        #obj_line = request.env['mk.listen.line'].sudo().browse([SUPERUSER_ID])
        #line = obj_line.sudo().search([('id','=',int(line_id))])
        #for rec in line:
        #    rec.write({
        #        'state':'done'
        #    })
        #return str('True')

    @http.route('/register/prepration/update_preperation_state/', type='json', auth='public',  csrf=False,)
    def update_line_state_done(self,**args):
        prep_ids=args.get('prep_ids',[])
        prep_ids=prep_ids.split(',')
        #for l in prep_ids:
        #return str(data[0])
        result=''
        line_ids=request.env['mk.listen.line'].search([('id','in',prep_ids)])
        if line_ids:
            for line in line_ids:
                line.write({'state':'done'})
            result='done'
        return result

    @http.route('/register/prepration/insert_mistake_line/<string:line_id>/<string:type_id>/<string:value>/<string:aya_id>', type='json', auth='public', csrf=False,)
    def insert_mistake_line(self,line_id,type_id,value,aya_id,**args):
        res=request.env['mk.details.mistake'].sudo().create({
            'name_mistake_id':int(type_id),
            'number_mistake':int(value),
            'aya_id':int(aya_id),
            'mistake_id':int(line_id)
        })
        return str(res)

    @http.route('/register/prepration/update_state_absent/<string:line_id>', type='json', auth='public',  csrf=False,)
    def update_state_absent(self,line_id,**args):
        result=self.wkf_absent(int(line_id))
        return str(result)

          
    @http.route('/register/attendance/permission_request/<string:student_id>/<string:episode>', type='json', auth='public',  csrf=False)
    def get_permission_requests(self, student_id,episode, **args):
        res=[]
        academic_recs = request.env['mk.study.year'].sudo().search([('active','=',True)])
        year=0
        if academic_recs:
            year=academic_recs[0].id
        mk_student_object=request.env['mk.link'].sudo().search([('student_id','=',int(student_id)),('year','=',year),('episode_id','=',int(episode))])
        #if mk_student_object:
        mk_student_id=mk_student_object[0].id
        absence_ids=request.env['mk.student_absence'].sudo().search([('student_id', '=', mk_student_id)])
        mosque_name=''
        display_name=''
        leave_type=''
        episode_name=''
        if absence_ids:
            for absence in absence_ids:
                if absence.mosque_id:
                    mosque_name=absence.mosque_id.name
                if absence.student_id:
                    display_name=absence.student_id.display_name
                if absence.leave_type:
                    leave_type=absence.leave_type.name
                if absence.episode_id:
                    episode_name=absence.episode_id.name
                rec_dict=({
                        'id':absence.id,
                        'mosque_name':str(mosque_name),
                        'student_id':absence.student_id.id,
                        'date_to':absence.date_to,
                        'date':absence.create_date,
                        'date_from':absence.date_from,
                        'student_name':str(display_name),
                        'leave_type':str(leave_type),
                        'episode_id':absence.episode_id.id,
                        'episode_name':str(episode_name),
                        'state':absence.state,
                        
                    })
                res.append(rec_dict)
        return str(res)

    def calculate_listen_rate(self, listen_lines, all_lines):
        
        
        all_count=0
        if all_lines:
            for line in all_lines:
                if line.type_follow=='listen':
                    all_count+=1

        listener_count=0.0
        if listen_lines:
            for line in listen_lines:
                if line.type_follow=='listen':
                    listener_count+=1
        ratio=listener_count/all_count*100.0
        return ratio, listener_count, all_count
        

    def calculate_listen_quality(self, listen_lines, all_lines):
        lines_count=0
        degree_count=0
        if listen_lines:
            for line in listen_lines:
                if line.type_follow=='listen':
                
                    lines_count+=1
                    degree_count+=line.degree
                
        ratio= degree_count/(100.0*lines_count)*100.0
        return ratio, lines_count, lines_count


    
    @http.route('/register/get_errors_types_list/', type='json', auth='public',  csrf=False)
    def get_error_list(self, **args):
        test = request.env['mk.test.error'].sudo().browse([SUPERUSER_ID]).search([])
        error_list=[]
        for rec in test:
            error_list.append({'id':rec.id,'name':rec.name})

        return str(error_list)

    @http.route('/close_prepration/<string:lines>/', type='json', auth='public',  csrf=False)
    def close_lines(self,lines,**args):
        lines=lines.split(',')
        for line in lines:
            line_id=request.env['mk.listen.line'].sudo().search([('id','=',int(line))])
            if line_id:
                line_id[0].sudo().write({'state':'done',
                    'actual_date':datetime.now()})
        return str("done")
#