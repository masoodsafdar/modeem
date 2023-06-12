# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.osv import osv
from datetime import datetime
from odoo.exceptions import Warning
from odoo.exceptions import UserError
import itertools
from operator import itemgetter


class productivity_teach_masjed(models.Model):

    _name = 'mk.productivity.teach'
    
    """
    @api.multi
    def cal_productivity(self):
        episode_links=[]
        episode_type=self.env['mk.episode_type'].search([])
        for rec in episode_type:
            parts=0
            link_ids=[]
            

            query='''SELECT  mk_link.id FROM 
                      public.mk_episode, 
                      public.mk_episode_type, 
                      public.mk_link
                    WHERE 
                      mk_episode.episode_type = mk_episode_type.id AND
                      mk_link.episode_id = mk_episode.id and mk_episode.teacher_id=%s and mk_episode_type.id=%d;'''%(self.teacher_id.id,rec.id)
            result=self.env.cr.execute(query)
            ex_result = self.env.cr.dictfetchall()
            for item in ex_result:
                link_ids.append(item['id'])

            episode_links.append({rec.name:link_ids})

            test_recs=self.env['mk.test.result.student'].search([('student_id','in',link_ids)])
            for  test_rec in test_recs:
                if test_rec.total_dgrees>test_rec.min_score:
                    student_test=self.env['mk.test.internal.registerations'].search([('student_id','=',test_rec.student_id.id)])
                    parts+=len(test_rec.test_type_id.test_branch_ids.part_ids.ids)

            self.env['mk.productivity.teach.line'].create({'line_id':self.id,'episode_type':rec.id,'productivity':parts})

    """

    # @api.multi
    def cal_productivity(self):
        episode_links=[]
        episode_ids=self.env['mk.episode'].search([('teacher_id','=', self.teacher_id.id),('state','=','accept')])
        result=[]
        episode_types=[]
        epi_dic={}
        for episode in episode_ids:
            episode_productivity=0
            ep_parts=0
            test_student_model=self.env['mk.test.result.student']
            test_recs=test_student_model.search([('student_id','in',episode.students_list.ids)])
            for  test_rec in test_recs:
                if test_rec.total_dgrees>test_rec.min_score:
                    student_test=self.env['mk.test.internal.registerations'].search([('student_id','=',test_rec.student_id.id)])
                    #ep_parts+=len(test_rec.test_type_id.test_branch_ids.part_ids.ids)
                    if student_test:
                        ep_parts+=len(student_test.test_branch_id.part_ids.ids)

            result.append({'episode':episode,'episode type':episode.episode_type,'productivity':ep_parts})
        for rec in result:
            if rec['episode type'] in epi_dic:
                epi_dic[rec['episode type']].append(rec['productivity'])
            else:
                epi_dic[rec['episode type']]=[rec['productivity']]



        for key , value in epi_dic.items():


            total=0;motivate='';rate=''
            for i in value:
                total+=i
            for rec_rate in key.performance:


                if total <= rec_rate.max_degree and total >=rec_rate.min_degree:

                    rate=rec_rate.rate
                    motivate=rec_rate.name

                    break
            #self.write({'productivity_line':[(0,0,{'episode_type':key.id,'productivity':total,'rate':rate,'motivate':motivate})]})
            self.write({'productivity_line':[(5,0,{'episode_type':key.id,'productivity':total,'rate':rate,'motivate':motivate})]})
            self.write({'productivity_line':[(0,0,{'episode_type':key.id,'productivity':total,'rate':rate,'motivate':motivate})]})
            
       

    teacher_id = fields.Many2one('hr.employee',
        string='Teacher Name',
        required=True,
        domain=[('category2','=','teacher')]
       
    )
    productivity_line=fields.One2many('mk.productivity.teach.line','line_id',string='Productivity')

class productivity_teach_masjed_line(models.Model):

    _name = 'mk.productivity.teach.line'

    episode_id = fields.Many2one('mk.episode',
        string='Episode',
       
    )
    episode_type=fields.Many2one('mk.episode_type',
        string='Episode',
       
    )
    productivity = fields.Float(
        string='Productivity',
       
    )

    rate=fields.Char('Rate')
    motivate=fields.Char('Motivate')

    line_id=fields.Many2one('mk.productivity.teach',
        string='Productivity',
       
    )
