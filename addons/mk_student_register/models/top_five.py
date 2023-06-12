# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class top_five(models.Model):
    _name = 'top.five'

    # @api.multi
    def get_study_class(self):
        study_class_ids=self.env['mk.study.class'].search([('study_year_id', '=', self.get_year_default()),('is_default', '=', True)])
        if study_class_ids:
            return study_class_ids.ids[0]

    # @api.multi
    def get_year_default(self):
        academic_year = self.env['mk.study.year'].search([('is_default','=',True)], limit=1)
        return academic_year and academic_year.id or False 

    study_class   = fields.Many2one('mk.study.class', string='Study class', default=get_study_class, ondelete='cascade', auto_join=False)
    best_students = fields.One2many('get.top.five.student', inverse_name='top_five', string='Best students', auto_join=False,)
    best_episodes = fields.One2many('get.top.five.episode', inverse_name='top_five', string='Best episode', auto_join=False)
    best_teachers = fields.One2many('get.top.five.teacher', inverse_name='top_five',string='Best teachers', auto_join=False)

    # @api.multi
    def get_best_studant_episode_dashboard(self):
        best_teachers=self.best_teacher()
        best_students= self.best_student_dashboard()
        best_episods=self.best_episode_dashboard()
        self.write({'best_students':[(5,0,{'rate':4,'name':'a'})]})
        self.write({'best_episodes':[(5,0,{'rate':4,'name':'a'})]})
        self.write({'best_teachers':[(5,0,{'rate':4,'name':'a'})]})
        #self.write({'best_episodes':[(5,0,{'rate':rec['rate'],'name':rec['episode name']})]})
        #self.write({'best_teachers':[(5,0,{'rate':rec['productivity'],'name':rec['teacher']})]})
        for rec in best_episods:
            self.write({'best_episodes':[(0,0,{'rate':rec['rate'],'name':rec['episode name']})]})
        for student in best_students:
            self.write({'best_students':[(0,0,{'rate':student['percentage'],'name':student['student']})]})
        for teacher in best_teachers:
            self.write({'best_teachers':[(0,0,{'rate':teacher['productivity'],'name':teacher['teacher']})]})


    def _getDefault_academic_year(self):
       #self.ensure_one()
        academic_recs = self.env['mk.study.year'].sudo().search([('is_default','=',True),('active','=',True)])       
        if academic_recs:
            return academic_recs[0].id          
        return False

    def calculate_listen_rate_prepare(self, preparation_id):
        lines_object=self.env['mk.listen.line']
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

    def best_teacher(self):
        done_listen=0
        listen_quality=0
        total_listen_degree=0
        done_listen_degree=0
        ep_id=self.env['mk.episode'].sudo().search([('study_class_id','=',self.get_study_class()),('state','=','accept')])
        all_students_order_by_review_quilty=[]
        teachers_productivity={}
        listen_teacher=[]
        teacher_ep=[]
    
        ep_percentage=0
        student_prepare=self.env['mk.student.prepare'].search([('stage_pre_id','in',ep_id.ids)])
        if student_prepare:
            for rec in student_prepare:
                listen_quality=self.calculate_listen_rate_prepare(rec.id)
                #listen_teacher.append({'teacher':rec.name,'productivity':listen_quality,'student':rec.link_id.id})
                if rec.name in teachers_productivity:
                    teachers_productivity[rec.name].append(listen_quality)
                else:
                    if listen_quality:
                        teachers_productivity[rec.name]=[listen_quality]
       
        for key , value in teachers_productivity.items():
            total=0
            if value:
                for i in value:
                    if type(i) is int or type(i) is float:
                        total+=i
                average_productivity=total/len(value)
        teacher_ep.append({'productivity':average_productivity,'teacher':key.name})
            
        sorted_ep = sorted(teacher_ep, key=lambda k: k['productivity'],reverse=True)
        top_5_ep=[]
        i=0
        for rec in sorted_ep:
            if i<5:
                top_5_ep.append(rec)
                i=i+1
        
        return top_5_ep

    def calculate_listen_rate_student(self,student_id):
        lines_object=self.env['mk.listen.line']
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

    def best_student_dashboard(self):
        listen_ratio=0
        total_listen=0
        done_listen=0
        listen_quality=0

        ep_id = self.env['mk.episode'].sudo().search([('study_class_id','=',self.study_class.id),
                                                      ('state','=','accept')]).ids
        #student_ids=self.env['mk.link'].sudo().search([('episode_id','in',ep_id),('state','=','accept'),('year','=',self._getDefault_academic_year())])
        student_ids = self.env['mk.link'].sudo().search([('state','=','accept'),
                                                         ('year','=',self._getDefault_academic_year()),
                                                         ('episode_id','in',ep_id),
                                                         ('student_id.gender', '=', 'male')])
        all_students_order_by_review_quilty = []
        for student in student_ids:
            listen_quality=self.calculate_listen_rate_student(student.id)
            if listen_quality:
                all_students_order_by_review_quilty.append({'student'   : student.student_id.display_name,
                                                            'percentage': listen_quality})
        all_students_order_by_review_quilty = sorted(all_students_order_by_review_quilty, key=lambda k: k['percentage'],reverse=True)
        top_5_students_at_episode=[]
        i = 0
        for rec in all_students_order_by_review_quilty:
            if i < 5:
                top_5_students_at_episode.append(rec)
                i = i + 1
        return top_5_students_at_episode

    def best_episode_dashboard(self):
        done_listen=0
        listen_quality=0
        total_listen_degree=0
        done_listen_degree=0
        '''
        if mosque_id==0:
            domain=[]
        else:
            domain=[('id','=',mosque_id)]
        mosques=self.env['mk.mosque'].sudo().search(domain).ids
        '''
        ep_id=self.env['mk.episode'].sudo().search([('state','=','accept'),
                                                    ('study_class_id','=',self.study_class.id),
                                                    ('academic_id','=',self._getDefault_academic_year())])
        all_students_order_by_review_quilty=[]
        ep_productivity=[]
        for ep in ep_id:
            ep_percentage=0
            student_ids=self.env['mk.link'].sudo().search([('episode_id','=',ep.id),
                                                           ('state','=','accept'),
                                                           ('year','=',self._getDefault_academic_year())])
            if student_ids:
                for student in student_ids:
                    listen_quality=self.calculate_listen_rate_student(student.id)
                    if listen_quality:
                        ep_percentage+=listen_quality
                ep_productivity.append({'episode name':ep.display_name,'rate':ep_percentage/len(student_ids)})
        sorted_episodes = sorted(ep_productivity, key=lambda k: k['rate'],reverse=True)
        top_5_episode=[]
        i = 0
        for rec in sorted_episodes:
            if i < 5:
                top_5_episode.append(rec)
                i = i + 1
        return top_5_episode
