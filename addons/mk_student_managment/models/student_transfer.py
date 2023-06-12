# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _ 
from odoo.exceptions import UserError, ValidationError


class mk_student_transfer(models.Model):
    _name='mk.internal_transfer'
    _rec_name="display_name"

    # @api.multi          
    def get_name(self):
        for record in self:
            record.display_name = "طلب نقل " + str(record.id)
            
    def _getDefault_academic_year(self):
        academic_year = self.env['mk.study.year'].search([('is_default','=',True)], limit=1)
        return academic_year and academic_year.id or False
    
    # @api.multi
    def get_study_class(self):
        study_class = self.env['mk.study.class'].search([('study_year_id', '=', self._getDefault_academic_year()),('is_default', '=', True)], limit=1)
        return study_class and study_class.id or False                

    display_name   = fields.Char("Name", compute="get_name")
    from_episode   = fields.Many2one('mk.episode', string='from episode', required=True, ondelete='cascade', related='student.episode_id', store=True)
    to_episode     = fields.Many2one('mk.episode', string='To episode',   required=True, ondelete='cascade')
    year           = fields.Many2one('mk.study.year',  string='Study Year',  default=_getDefault_academic_year, readonly=True)
    study_class_id = fields.Many2one('mk.study.class', string='Study class', default=get_study_class, domain=[('is_default', '=', True)], ondelete='restrict')
    state          = fields.Selection([('draft',  'Draft'), 
                                       ('accept', 'Accept'), 
                                       ('reject', 'Reject')], string='State', readonly=True, default='draft')
    student_id     = fields.Many2one('mk.student.register',   string='Student', ondelete='cascade')
    student        = fields.Many2one('mk.link', string='Student', domain=[('state','=','accept')], required=True, ondelete='cascade')
    subh           = fields.Boolean('Subh')
    zuhr           = fields.Boolean('Zuhr')
    aasr           = fields.Boolean('Aasr')
    magrib         = fields.Boolean('Magrib')
    esha           = fields.Boolean('Esha')
    approache      = fields.Many2one("mk.approaches", string="Approaches", ondelete='restrict')
    student_days   = fields.Many2many('mk.work.days', string='work days', required=True)
    
    @api.onchange('student_id')
    def onchange_student_id(self):
        student = self.student_id
        request = student and student.request_id or False
        self.student = request and request.id or False
    
    @api.one
    def unlink(self):
        if self.state == "accept":
            raise ValidationError(_('لا يمكنك حذف سجل تم تأكيده'))
        
        try:
            super(mk_student_transfer, self).unlink()
        except:
            raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))
   
    @api.onchange('student')
    def get_current_masjed(self):
        stages=[]
        res={}
        resource = self.env['resource.resource'].search([('user_id','=',self.env.user.id)])
        if resource:
            employee_id = self.env['hr.employee'].search([('resource_id','in',resource.ids)])
            if employee_id:
                msjd_id = self.env['mk.mosque'].search([('responsible_id', 'in',employee_id.ids)])
                
                link_recs = self.env['mk.link'].search([('student_id', '=', self.student.id), 
                                                        ('state', '=', 'accept')])
                for link in link_recs:
                    stages.append(link.episode_id.id)
                    
                res = {'domain':{'from_episode':[('mosque_id', 'in', msjd_id.ids),
                                                 ('id', 'in', stages)],
                                 'to_episode':[('mosque_id', 'in', msjd_id.ids)]}}
                return res     

    @api.onchange('to_episode')
    def to_episode_onchange(self):
        approaches_ids=self.env['mk.approaches'].search(['&',('state','=','active'),
                                                             ('program_id','=',self.to_episode.program_id.id)])
        return {'domain':{'approache': [('id', 'in', approaches_ids.ids)]}}
    
    # @api.multi
    def action_draft(self):
        self.write({'state':'draft'})

    # @api.multi
    def action_accept_transfer(self):
        self.student.action_reject()

        values={'student_id':         self.student.student_id.id, 
                'registeration_code': self.student.student_id.registeration_code, 
                'episode_id':         self.to_episode.id,
                'subh':               self.subh,
                'zuhr':               self.zuhr,
                'aasr':               self.aasr,
                'magrib':             self.magrib,
                'esha':               self.esha,
                'mosq_id':            self.to_episode.mosque_id.id,
                'program_id':         self.student.program_id.id,
                'approache':          self.student.approache.id,
                'program_type':       self.student.program_type,
                'page_id':            self.student.page_id.id,
                'selected_period':    self.student.selected_period,
                'part_id':            [(4,part) for part in self.student.part_id.ids],
                'start_point':        self.student.start_point.id,
                'review_direction':   self.student.review_direction,
                'student_days':       [(4,day) for day in self.from_episode.episode_days.ids]}
        
        self.env['mk.link'].create(values)
        self.write({'state':'accept'})

    @api.one
    def action_reject(self):
        self.write({'state':'reject'})
    
    @api.onchange('from_episode')
    def onchange_from_episode(self):
        stage = self.env['mk.episode']
        stage_ids = stage.search([('state','=','accept'),
                                  ('mosque_id', '=', self.from_episode.mosque_id.id)])
        res = {'domain':{'to_episode':[('id','in',stage_ids.ids)]}}
        return res
