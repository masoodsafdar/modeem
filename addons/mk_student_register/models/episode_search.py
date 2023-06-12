#-*- coding:utf-8 -*-
from odoo import models, fields, api
from lxml import etree

    
class episode_search(models.TransientModel):
    _name = 'mk.episode_search'    
    _rec_name = 'student_id'
    
    student_id   = fields.Many2one('mk.student.register', string='Student',    ondelete='cascade', required=True)
    episode_id   = fields.Many2one('mk.episode',          string='Episode',    ondelete='cascade')
    study_year   = fields.Many2one('mk.study.year',       string='Study year', ondelete="restrict", domain=[('active', '=', True)])
    subh         = fields.Boolean('Subh')
    zuhr         = fields.Boolean('Dhuhr')
    aasr         = fields.Boolean('Aasr')
    magrib       = fields.Boolean('Magherib')
    esha         = fields.Boolean('Eisha')
    subh_t       = fields.Boolean('Subh')
    zuhr_t       = fields.Boolean('Dhuhr')
    aasr_t       = fields.Boolean('Aasr')
    magrib_t     = fields.Boolean('Magherib')
    esha_t       = fields.Boolean('Eisha')
    student_days = fields.Many2many('mk.work.days',string='work days')
    
    _defaults = {'episode_id':lambda self, cr, uid, ctx:ctx.get('ep_id',False)}

    @api.onchange('episode_id')
    def period_onchange(self):
        self.student_id = self.episode_id.st_id
        self.subh_t = self.episode_id.subh
        self.zuhr_t = self.episode_id.zuhr
        self.magrib_t = self.episode_id.magrib
        self.esha_t = self.episode_id.esha
        self.student_days = self.episode_id.episode_days

    # @api.multi
    def ok(self):
        mk_link=self.env['mk.link']
        mk_link.create({'student_id':   self.student_id.id,
                        'episode_id':   self.episode_id.id,
                        'subh':         self.subh,
                        'zuhr':         self.zuhr,
                        'aasr':         self.aasr,
                        'magrib':       self.magrib,
                        'esha':         self.esha,
                        'student_days': [(4,[self.student_days.ids])]})
