# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from odoo.exceptions import Warning, ValidationError
from odoo import _


class episode_search_transfer(models.Model):
    _name = 'mk.episode_search_transfer'
    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """

    def _getDefault_academic_year(self):
        #self.ensure_one()
        academic_recs = self.env['mk.study.year'].search([('is_default','=',True),
                                                          ('active','=',True)])       
        if academic_recs:
            return academic_recs[0].id          
        return False

    # @api.multi
    def get_study_class(self):
        study_class_ids=self.env['mk.study.class'].search([('study_year_id', '=', self._getDefault_academic_year()),
                                                           ('is_default', '=', True)])
        if study_class_ids:
            return study_class_ids.ids[0]
        
    # SERACH OPERATION
    # @api.multi
    @api.onchange('student_id')
    def main_search(self):
        select_object = self.env['mk.episode_search_lines']
        result_rec = select_object.search([])
        #for rec in result_rec:
        #       rec.unlink()
        if self.student_id :
            res=[]
            resource = self.env['resource.resource'].search([('user_id','=',self.env.user.id)])
            supervisor_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id),
                                                            ('state', '=', 'accept'),
                                                            ('category', '=', 'supervisor')])
            masjed=self.env['mk.mosque'].search(['|',('supervisors','in',supervisor_id.ids),
                                                     ('responsible_id','=',self.env.user.id)])

            domain=[('state', '=', 'accept'),
                    ('mosque_id', 'in', masjed.ids),
                    ('id','!=',self.from_episode.id)]
            
            episode_ids=[]
            
            if self.student_id[0].student_id.gender == 'male':
                domain.append(('women_or_men','=','men'))
            else:
                domain.append(('women_or_men','=','women'))

            episodes = self.env['mk.episode'].search(domain)

            for episode in episodes:
                if (self.student_id[0].student_id.job_id.id in episode.job_ids.ids or episode.job_ids.ids==[] or self.student_id[0].student_id.job_id.id==False) and (self.student_id[0].student_id.grade_id.id in episode.grade_ids.ids or episode.grade_ids.ids==[] or self.student_id[0].student_id.grade_id.id==False):
                    res.append(episode)

            occupy_ids=self.search_occupy_episode_controller(res)
            result_dict={}
            ids=[]
            x=0
            for episode in occupy_ids:
                result_dict={}
                ids.append((0,0,{'episode_id':  self.from_episode.id,
                                 'episode_to':  episode[0].id,
                                 'student_ids': [(4, id) for id in self.student_id.ids],
                                 #'episode_current_program':episode[0].program_id.id,
                                 'subh_t':      episode[0].subh,
                                 'zuhr_t':      episode[0].zuhr,
                                 'aasr_t':      episode[0].aasr,
                                 'magrib_t':    episode[0].magrib,
                                 'esha_t':      episode[0].esha,
                                 'subh':        episode[0].subh,
                                 'zuhr':        episode[0].zuhr,
                                 'aasr':        episode[0].aasr,
                                 'magrib':      episode[0].magrib,
                                 'esha':        episode[0].esha,}))
                self.update({'epi_link':ids})        
        
    student_id     = fields.Many2many('mk.link',   string='Student', domain=[('state','=','accept')])
    from_episode   = fields.Many2one('mk.episode', string='from episode', required=False)
    #to_episode = fields.Many2one(string='To episode', comodel_name='mk.episode',)
    year           = fields.Many2one('mk.study.year',  string='Study Year', readonly=True, default=_getDefault_academic_year)
    study_class_id = fields.Many2one('mk.study.class', string='Study class', default=get_study_class, domain=[('is_default', '=', True)], ondelete='restrict',)
    subh_search    = fields.Boolean('Subh')
    zuhr_search    = fields.Boolean('Zuhr')
    aasr_serach    = fields.Boolean('Aasr')
    magrib_search  = fields.Boolean('Magrib')
    esha_serach    = fields.Boolean('Esha')
    episode_days   = fields.Many2many('mk.work.days',string='work days')
    flag           = fields.Boolean(string="flag",default=False)
    #student_link=fields.One2many("mk.link","search_link","link")    
    epi_link       = fields.One2many('mk.episode_search_lines', 'search_id', string='link', compute=main_search, store=  True)
    
    @api.onchange('from_episode')
    def get_students(self):
        return {'domain': {'student_id': [('state','=','accept'),
                                          ('episode_id','=',self.from_episode.id)]}}

    # @api.multi
    def search_for_episode(self):
        self.flag=True
        self.main_search()
        
        return {"type": "ir.actions.do_nothing",}

    def search_for_days(self):
        ret=[]
        episode_model=self.env['mk.episode']
        episode_ids=episode_model.search([])
        l=[]
        ep_ids=[]
        for d in self.episode_days:
            for episds in episode_ids:
                for days in episds.episode_days:
                    if days.id == d.id and episds.id not in ep_ids:
                        ep_ids.append(episds.id)
                        l.append(episds.id)
        return l
    
    def search_episode_by_periods(self, occupy_episodes):
        res=[]
        episode=[]
        #ids=self.search_episode_by_gender(self.student_id.id)            
        for rec in occupy_episodes:
            if self.subh_search == True and rec.subh == True and rec.id not in res:
                    res.append(rec.id)
                    
            if self.zuhr_search == True and rec.zuhr == True and rec.id not in res:
                res.append(rec.id)
            
            if self.aasr_serach ==True and rec.aasr == True and rec.id not in res:
                res.append(rec.id)
                
            if self.magrib_search==True and rec.magrib==True and rec.id not in res:
                res.append(rec.id)
                
            if self.esha_serach==True and rec.esha==True and rec.id not in res:
                res.append(rec.id)
                
        return res
        
    def search_occupy_episode_controller(self, gender_ids):
        res=[]
        episodes=[]
        for episode in gender_ids:
            link_ids=self.env['mk.link'].search([('episode_id', '=', episode.id), 
                                                 ('state', '!=', 'reject')])
            
            res.append({'id':         episode.id, 
                        'students':   len(link_ids), 
                        'unoccupied': episode.episode_type.students_no-len(link_ids)})
            
            if episode.episode_type.students_no-len(link_ids):
                episodes.append(episode)    

        return episodes    

    def domain_episodes(self):
        res=[]

        episodes=self.env['mk.episode'].search([])
        for episode in episodes:
            if (self.student_id.student_id.job_id.id in episode.job_ids.ids or episode.job_ids.ids==[] or self.student_id.student_id.job_id.id==False) and (self.student_id.student_id.grade_id.id in episode.grade_ids.ids or episode.grade_ids.ids==[] or self.student_id.student_id.grade_id.id==False):
                res.append(episode.id)

        return res

    def search_episodes_by_mosques(self):
        resource = self.env['resource.resource'].search([('user_id','=',self.env.user.id)])
        employee_id = self.env['hr.employee'].search([('resource_id','in',resource.ids)])
        msjd_id=self.env['mk.mosque'].search([('responsible_id', 'in',employee_id.ids)])
        
        return msjd_id.episode_id.ids
    
    # @api.multi
    def search_episode_by_gender(self):
        student_partner=self.env['mk.student.register'].browse(self.student_id.student_id.id)
        if student_partner.gender == 'male':
            episode_ids=self.env['mk.episode'].search([('women_or_men','=','men')]).ids
        else:
            episode_ids=self.env['mk.episode'].search([('women_or_men','=','women')]).ids
            
        return episode_ids

    # @api.multi
    def ok(self):
        internal_transfer=self.env['mk.internal_transfer']
        if len(self.env['mk.episode_search_lines'].search([('id','in',self.epi_link.ids),('flag','=',True)]).ids)>1:
            raise ValidationError(_('لا يمكنك إختيار أكثر من حلقة'))
        for rec in self.epi_link:
                if rec.flag==True:
                    for student in rec.student_ids:
                        transfer_rec=internal_transfer.create({'student':      student.id,
                                                               'to_episode':   rec.episode_to.id,
                                                               'from_episode': self.from_episode.id,
                                                               'subh':         rec.subh,
                                                               'zuhr':         rec.zuhr,
                                                               'aasr':         rec.aasr,
                                                               'magrib':       rec.magrib,
                                                               'esha':         rec.esha,
                                                               'student_days': [(4, day)for day in rec.student_days.ids]})
                        transfer_rec.action_accept_transfer()

        select_object = self.env['mk.episode_search_lines']
        result_rec = select_object.search([])
        for rec in result_rec:
            rec.unlink()
            
        for rec in self.search([]):
            rec.unlink()


class episode_search(models.Model):
    _name = 'mk.episode_search_lines'
    _rec_name = 'student_id'
        
    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """
    @api.one
    @api.depends('episode_to')
    def get_episode_days(self):
        episode_days=self.env['mk.episode'].search([('id', '=', self.episode_to.id)]).episode_days.ids
        return [('id', 'in', episode_days)]

    student_ids  = fields.Many2many('mk.link', string='Student', ondelete='restrict')
    student_id   = fields.Many2one('mk.link', string='Student', ondelete='restrict')
    episode_id   = fields.Many2one('mk.episode', string='Episode', ondelete='restrict',)
    episode_to   = fields.Many2one('mk.episode', string='to Episode', ondelete='restrict')
    search_id    = fields.Many2one('mk.episode_search_transfer', string="search")
    study_year   = fields.Many2one('mk.study.year', string='Study year', domain=[('active', '=', True)], ondelete='cascade',)
    subh         = fields.Boolean('Subh')
    zuhr         = fields.Boolean('Dhuhr')
    aasr         = fields.Boolean('Aasr')
    magrib       = fields.Boolean(string='Magherib')
    esha         = fields.Boolean('Eisha')
    subh_t       = fields.Boolean('Subh',)
    zuhr_t       = fields.Boolean('Dhuhr',)
    aasr_t       = fields.Boolean('Aasr',)    
    magrib_t     = fields.Boolean('Magherib',)
    esha_t       = fields.Boolean('Eisha')
    flag         = fields.Boolean('flag', default=False)
    student_days = fields.Many2many('mk.work.days',string='work days', domain=get_episode_days)
    # almanhajepisode_to.episode_days.ids//////
    episode_current_program = fields.Many2one("mk.programs","current program")
    almanhaj                = fields.Many2one("mk.approaches", string="almanhaj", domain="[('program_id','=',episode_current_program)]", ondelete='restrict')

    @api.one
    @api.onchange('episode_id')
    def period_onchange(self):
        self.student_id=self.episode_id.st_id
        self.subh_t=self.episode_id.subh
        self.aasr_t=self.episode_id.aasr

        self.zuhr_t=self.episode_id.zuhr
        self.magrib_t=self.episode_id.magrib
        self.esha_t=self.episode_id.esha
        self.student_days=self.episode_id.episode_days 
        