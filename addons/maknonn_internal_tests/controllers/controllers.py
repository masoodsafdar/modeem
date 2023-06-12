# -*- coding: utf-8 -*-
import odoo.http as http
from odoo.http import Response
from odoo import SUPERUSER_ID
import sys, json
import logging
_logger = logging.getLogger(__name__)
from odoo.http import request
from odoo import http
class internalTestController(http.Controller):


    @http.route('/test/question/<int:student_id>/<int:test_id>', type='json', auth='public',  csrf=False)
    def create_session(self, student_id=False,test_id=False ,**args):
        result=" "
        is_session=request.env['episode.student.test.session'].sudo().search([('student_id','=',student_id),('test_id','=',test_id),('state','=','start')])
        if is_session:
            q_states=request.env['test.questions'].sudo().search([('session_id','=',is_session[0].id),('state','=','draft')])
            if q_states:
                result=self.get_se_quations(is_session[0].id)
            else:
                is_session[0].write({'state':'done'})
                result="session closed"
        else:
            session=request.env['episode.student.test.session'].sudo().create({
                'test_id':test_id ,
                'student_id':student_id,
                'state':'draft'
                })
            session.start_exam()
            result=self.get_se_quations(session.id)
        
            #print("#####################,session",session.id)
        return str(result)

    def get_se_quations(self, session_id):
        session=request.env['episode.student.test.session'].sudo().search([('id','=',session_id)])
        if session:
            test_quatsions=[]
            review_qua=[]
            pages=[]
            pages2=[]
            next_q=request.env['test.questions'].sudo().search([('internal_session_id','=',session[0].id),('state','=','draft'),('follow_type','=','listen')],limit=1)
            print("################33",next_q)
            if next_q:
                test_quatsions.append({
                    'from_surah':next_q[0].from_surah.name,
                    'from_aya':next_q[0].from_aya.original_surah_order,
                    'to_surah':next_q[0].to_surah.name,
                    'to_aya':next_q[0].to_aya.original_surah_order,
                    'id':next_q[0].id
                })
                for page in range(next_q[0].from_aya.page_no,next_q[0].to_aya.page_no+1):
                    #get all verses in page
                    verses=[]
                    verses_ids=request.env['mk.surah.verses'].sudo().search([('page_no','=',page),('original_accumalative_order','<',next_q[0].to_aya.original_accumalative_order+1)])
                    if verses_ids:
                        for verse in verses_ids:
                            verses.append({'ordr':verse.original_surah_order,'id':verse.id})
                        pages.append({str(page):verses})                
            next_q_b=request.env['test.questions'].sudo().search([('internal_session_id','=',session[0].id),('state','=','draft'),('follow_type','=','big')],limit=1)
            if next_q_b:
                review_qua.append({
                    'from_surah':next_q_b[0].from_surah.name,
                    'from_aya':next_q_b[0].from_aya.original_surah_order,
                    'to_surah':next_q_b[0].to_surah.name,
                    'to_aya':next_q_b[0].to_aya.original_surah_order,
                    'id':next_q_b[0].id
                })

                for page in range(next_q_b[0].from_aya.page_no,next_q_b[0].to_aya.page_no+1):
                    #get all verses in page
                    verses1=[]
                    verses_ids=request.env['mk.surah.verses'].sudo().search([('page_no','=',page),('original_accumalative_order','<',next_q_b[0].to_aya.original_accumalative_order+1)])
                    if verses_ids:
                        for verse in verses_ids:
                            verses1.append({'ordr':verse.original_surah_order,'id':verse.id})

                        pages2.append({str(page):verses1})
                test_quatsions.append({'pages':pages})    
                review_qua.append({'pages':pages2})

            """test_ob=request.env['episode.internal.test'].sudo().search([('id','=',session[0].test_id.id)])
            items=[]
            if test_ob:
                for item in test_ob[0].evaluation_items:
                    items.append({'item_id':item.id,'name':item.name})
            """
        #print("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE",{'listen_q':test_quatsions,'listen_pages':pages,'review_q':review_qua,'review_q':pages2})
        return str({'listen_q':test_quatsions,'review_q':review_qua})

    @http.route('/test/start_session/<int:session_id>', type='json', auth='public',  csrf=False)
    def start_session(self, session_id=False,**args):
        session=request.env['episode.student.test.session'].sudo().search([('id','=',session_id)])
        if session:
            session[0].start_exam()
            return "DONE"

    @http.route('/test/get_quation/<int:session_id>', type='json', auth='public',  csrf=False)
    def get_quations(self, session_id=False,**args):
        session=request.env['episode.student.test.session'].sudo().search([('id','=',session_id)])
        if session:
            test_quatsions=[]
            review_qua=[]
            next_q=request.env['test.questions'].sudo().search([('internal_session_id','=',session[0].id),('state','=','draft'),('follow_type','=','listen')],limit=1)
            print("################33",next_q)
            if next_q:
                test_quatsions.append({
                    'from_surah':next_q[0].from_surah.id,
                    'from_aya':next_q[0].from_aya.id,
                    'to_surah':next_q[0].to_surah.id,
                    'to_aya':next_q[0].to_aya.id
                })
            next_q_b=request.env['test.questions'].sudo().search([('internal_session_id','=',session[0].id),('state','=','draft'),('follow_type','=','big')],limit=1)
            if next_q_b:
                review_qua.append({
                    'from_surah':next_q_b[0].from_surah.id,
                    'from_aya':next_q_b[0].from_aya.id,
                    'to_surah':next_q_b[0].to_surah.id,
                    'to_aya':next_q_b[0].to_aya.id
                })

            """ #session[0].start_exam()
            test_quatsions=[]
            review_qua=[]
            for rec in session[0].test_question:
                test_quatsions.append({
                    'from_surah':rec.from_surah.id,
                    'from_aya':rec.from_aya.id,
                    'to_surah':rec.to_surah.id,
                    'to_aya':rec.to_aya.id
                })

            for rec in session[0].test_question_big:
                test_quatsions.append({
                    'from_surah':rec.from_surah.id,
                    'from_aya':rec.from_aya.id,
                    'to_surah':rec.to_surah.id,
                    'to_aya':rec.to_aya.id
                })
            """
        return str({'listen_q':test_quatsions,'review_q':review_qua})

    @http.route('/test/close_session/<int:session_id>', type='http', auth='public',  csrf=False)
    def end_exam(self, session_id=False,**args):
        session=request.env['episode.student.test.session'].sudo().search([('id','=',session_id)])
        if session:
            #session[0].end_exam()
            return str({'total_degree':session[0].maximum_degree,'deserved_degree':session[0].degree,'appr':session[0].appreciation})

    def episode_type_test(self,episode_id):
        episode_lst = []
        ep_record = request.env['mk.episode'].sudo().browse([SUPERUSER_ID]).search([('id','=',episode_id)])
        if episode_id:
            for rec in ep_record.episode_tests:
                episode_lst.append({
                    'id':rec.id,
                    'test_name':rec.name,
                    'test_date':rec.test_date,
                    })
        return episode_lst

    @http.route('/test/all/<int:episode_id>', type='json', auth='public',  csrf=False,)
    def all_test(self,episode_id,**args):
        result=self.episode_type_test(episode_id)
        return str(result)

    @http.route('/test/question_error/<int:q_id>/<int:test_id>', type='json', auth='public',  csrf=False,)
    def q_error(self,q_id,test_id,**args):
        #result=self.episode_type_test(episode_id)
        result=[]
        q_id_obj=request.env['episode.internal.test'].sudo().search([('id','=',test_id)])
        if q_id_obj:
            print("####################3",q_id_obj)
            for item in q_id_obj[0].evaluation_items:
                print("####################3",item.name)
                item_errors=request.env['question.error'].sudo().search([('question_id','=',q_id),('evaluation_item','=',item.id)])
                if item_errors:
                    error_liss=[]
                    for error in item_errors:
                        name = request.env['mk.discount.item'].sudo().search([('id','=',error.item.id)])

                        error_liss.append({'id':error.id,'value':error.value,'name':name[0].name})
                result.append({str(item.id):error_liss})


        return str(result)
    
    @http.route('/test/close/question/<int:question_id>', type='json', auth='public',  csrf=False)
    def close_quation(self, question_id=False ,**args):
        q_object=request.env['test.questions'].sudo().search([('id','=',question_id)])
        if q_object:
            q_object[0].sudo().write({'state':'done'})
            return "done"