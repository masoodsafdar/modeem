# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.exceptions import Warning, ValidationError

import logging
_logger = logging.getLogger(__name__)


class episode(models.Model):
    _inherit="mk.episode"
    
    st_id = fields.Integer("st")
    
    _defaults={'st_id':lambda self, cr, uid, ctx:ctx.get('st_id',False),}


class link_student(models.TransientModel):
    _name = 'mk.search.episode'
    
    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """
    
    def _getDefault_academic_year(self):
        academic_year = self.env['mk.study.year'].search([('is_default','=',True)], limit=1)
        return academic_year and academic_year.id or False
    
    # SERACH OPERATION
    @api.depends('student_id')
    def get_result(self):
        for rec in self:
            if rec.student_id:
                rec.epi_link=False
                select_object=rec.env['mk.episode_searc']
                result_rec=select_object.search([])
                res=[]

                resource = rec.env['resource.resource'].search([('user_id','=',rec.env.user.id)])
                supervisor_id = rec.env['hr.employee'].search([('user_id','=',rec.env.user.id),
                                                               ('state', '=', 'accept'),
                                                               ('category2', 'in', ['supervisor','admin'])])
                masjed=rec.env['mk.mosque'].search(['|',('supervisors','in',supervisor_id.ids),
                                                        ('responsible_id','=',rec.env.user.id)])

                domain=[('state', '=', 'accept'),
                        ('mosque_id', 'in', masjed.ids)]
                
                episode_ids=[]
                student_partner=rec.env['mk.student.register'].browse(rec.student_id.id)
                if student_partner.gender == 'male':
                    domain.append(('women_or_men','=','men'))
                    
                else:
                    domain.append(('women_or_men','=','women'))

                episodes=rec.env['mk.episode'].search(domain)


                for episode in episodes:
            
                    if (rec.student_id.job_id.id in episode.job_ids.ids or episode.job_ids.ids==[] or rec.student_id.job_id.id==False) and (rec.student_id.grade_id.id in episode.grade_ids.ids or episode.grade_ids.ids==[] or rec.student_id.grade_id.id==False):
                        res.append(episode)
                        
                occupy_ids = rec.search_occupy_episode_controller(res)

                result_dict = {}
                ids = []
                x = 0
                for episode in occupy_ids:
                    result_dict = {}
                    result_dict.update({'episode_id':   episode[0].id,
                                        'student_id':   rec.student_id.id,
                                        'student_days': [(4, id)for id in episode[0].episode_days.ids],})
                    
                    x=rec.env['mk.episode_searc'].create(result_dict)
                    ids.append(x.id)
                if ids:
                    rec.epi_link=ids    
    
    student_id   = fields.Many2one('mk.student.register', string="Student",    required=True, ondelete='cascade')
    year         = fields.Many2one('mk.study.year',       string='Study Year', readonly=True, default=_getDefault_academic_year, ondelete="restrict")
    episode_days = fields.Many2many('mk.work.days',       string='work days')
    flag         = fields.Boolean("flag", default=False)
    epi_link     = fields.Many2many("mk.episode_searc", "search", compute=get_result, store=True)
    
    # @api.multi
    def ok(self):
        mk_link=self.env['mk.link']
        for rec in self.epi_link:
            if rec.flag==True:
                m=rec.student_id.mosque_id.ids
                mk_link.create({'student_id':       rec.student_id.id,
                                'episode_id':       rec.episode_id.id,
                                'approache':        rec.almanhaj.id,
                                'page_id':          rec.page_id.id,
                                'selected_period':  rec.episode_id.selected_period,
                                'mosq_id':          m[0],
                                'student_days':     [(4, id)for id in rec.student_days.ids],
                                'part_id':          [(4, id)for id in rec.part_id.ids],
                                'program_id':       rec.episode_current_program.id,
                                'program_type':     rec.program_type,
                                'start_point':      rec.start_point.id,
                                'save_start_point': rec.save_start_point.id,
                                'review_direction': rec.review_direction})   
                
    #-------------------------------- GARBAGE ----------------------------------
    # @api.multi
    def search_for_episode(self):
        self.flag=True

        self.main_search()
        return {"type": "ir.actions.do_nothing",}
        
#     def search_episodes_by_mosques(self):
#         return self.env['mk.episode'].search([('id', 'in', msjd_id.episode_id.ids), ('state','=','accept')]).ids

    def domain_episodes(self):
        res=[]
        student_partner=self.env['mk.student.register'].browse(self.student_id.id)
        episodes=self.env['mk.episode'].search([('state', '=', 'accept'),])
        for episode in episodes:
    
            if (self.student_id.job_id.id in episode.job_ids.ids or episode.job_ids.ids==[] or self.student_id.job_id.id==False) and (self.student_id.grade_id.id in episode.grade_ids.ids or episode.grade_ids.ids==[] or self.student_id.grade_id.id==False):
                res.append(episode.id)
        return res

    def search_episode_by_gender(self,grade_ids):
        student_partner=self.env['mk.student.register'].browse(self.student_id.id)
        if student_partner.gender == 'male':
            episode_ids=self.env['mk.episode'].search([('women_or_men','=','men'),('id', 'in', grade_ids)])
        else:
            episode_ids=self.env['mk.episode'].search([('women_or_men','=','women'),('id', 'in', grade_ids)])
        return episode_ids

    #------------------------------CONTROLLERS MOTHEDS ( SEARCH ) ----------------------
    def search_occupy_episode_controller(self, gender_ids):
        res=[]
        episodes=[]
        for episode in gender_ids:
            link_ids=self.env['mk.link'].search([('episode_id', '=', episode.id), ('state', '!=', 'reject')])
            res.append({'id':episode.id, 'students':len(link_ids), 'unoccupied':episode.episode_type.students_no-len(link_ids)})#?? res unused
            if episode.episode_type.students_no-len(link_ids):
                episodes.append(episode)    

        return episodes
        
    def controller_main_search_for_episode(self,days,grade,job,gender,periods):
        res=[]
        days=[int(d) for d in days]
        domain=[('state', '=', 'accept'), ('episode_days', 'in', days)]
        episode_ids=[]
        
        if gender == 'men':
            domain.append(('women_or_men','=','men'))

        else:
            domain.append(('women_or_men','=','women'))

        episodes=self.env['mk.episode'].search(domain)   
        for episode in episodes:           
            if (job in episode.job_ids.ids or episode.job_ids.ids==[] or job==False) and (grade in episode.grade_ids.ids or episode.grade_ids.ids==[] or grade==False):
                    res.append(episode)
    
        period=self.search_episode_by_periods_controller(res)
        period_objs=self.env['mk.episode'].search([('id', 'in',period)])   
        seat=self.search_occupy_episode_controller(period_objs)
        
        return seat.ids

    def search_for_days_controllers(self,days):
        episode_model=self.env['mk.episode']
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

    def domain_episodes_controller(self,grade_id,job_id):
        res=[]
        episodes=self.env['mk.episode'].search([])
        for episode in episodes:
            if (job_id in episode.job_ids.ids or episode.job_ids.ids==[] or job_id==False) and (grade_id in episode.grade_ids.ids or episode.grade_ids.ids==[] or grade_id==False):
                res.append(episode.id)
        return res
    
    def search_episode_by_gender_controller(self,gender):
        if gender == 'men':
            episode_ids=self.env['mk.episode'].search([('women_or_men','=','men')]).ids
        else:
            episode_ids=self.env['mk.episode'].search([('women_or_men','=','women')]).ids
        return episode_ids
