#-*- coding:utf-8 -*-
from odoo import models, fields, api


class link_wizerd(models.TransientModel):
    _name = 'episode.student.link'
        
    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """
    
    @api.depends('episode_current_program')
    def is_tlawa(self):
        for rec in self:
            rec.is_tlawa=rec.episode_current_program.reading
                
    students_ids            = fields.Many2many('mk.student.register', string='Student', ondelete="restrict", required=True)
    episode_id              = fields.Many2one('mk.episode',           string='Episode', ondelete='cascade')
    flag                    = fields.Boolean("determaine program for all student")
    program_type            = fields.Selection([('open','open'),
                                                ('close','close')], string="program type")
    episode_current_program = fields.Many2one("mk.programs",        string="current program" )
    almanhaj                = fields.Many2one("mk.approaches",      string="almanhaj", domain = "[('program_id','=',episode_current_program)]")
    is_tlawa                = fields.Boolean('is tlawa', compute=is_tlawa)
    part_id                 = fields.Many2many("mk.parts", string="part")    
    page_id                 = fields.Many2one('mk.memorize.method', string='Page', ondelete="restrict", domain=[('type_method','=','subject')])
    empty_seats             = fields.Integer(string="empty seats")

    @api.depends('episode_current_program')
    def is_big(self):
        for rec in self:
            rec.is_big_review=rec.episode_current_program.maximum_audit

    # @api.multi
    def ok(self):
        mk_link=self.env['mk.link']
        
        for rec in self.students_ids:
            mk_link.create({'student_id':      rec.id,
                            'episode_id':      self.episode_id.id,
                            'selected_period': self.episode_id.selected_period,
                            'approache':       self.almanhaj.id,
                            #'page_id':self.page_id.id,
                            'mosq_id':         self.episode_id.mosque_id.id,
                            'student_days':    [(4, id)for id in self.episode_id.episode_days.ids],
                            'part_id':         [(4, id)for id in self.part_id.ids],
                            'program_id':      self.episode_current_program.id,
                            'program_type':    self.program_type,
                            #'start_point':rec.start_point.id,
                            'is_tlawa':        self.is_tlawa})
