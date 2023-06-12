#-*- coding:utf-8 -*-
from odoo import models, fields, api
from lxml import etree    


class episode_search(models.Model):
    _name = 'mk.episode_searc'    
    _rec_name = 'student_id'
        
    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """
    
    student_id = fields.Many2one('mk.student.register', string='Student',    ondelete='cascade')
    episode_id = fields.Many2one('mk.episode',          string='Episode',    ondelete='cascade')
    study_year = fields.Many2one('mk.study.year',       string='Study year', ondelete='cascade', domain=[('active', '=', True)])
    
    _defaults = {'episode_id':lambda self, cr, uid, ctx:ctx.get('ep_id',False),}

    # @api.multi
    def test(self):
        episode_days=self.env['mk.episode'].browse(self.episode_id.ids).episode_days.ids
        return [('id', 'in', episode_days)]
    
    student_days=fields.Many2many('mk.work.days',string='work days')
    flag=fields.Boolean(string='flag',default=False)    

    # almanhaj
    program_type=fields.Selection([('open','open'),('close','close')],string="program type")
    episode_current_program=fields.Many2one("mk.programs","current program" )
    almanhaj=fields.Many2one("mk.approaches","almanhaj",domain = "[('program_id','=',episode_current_program)]")

    @api.depends('episode_current_program')
    def is_tlawa(self):
        for rec in self:
            rec.is_tlawa=rec.episode_current_program.reading

    @api.depends('episode_current_program')
    def is_big(self):
        for rec in self:
            #rec.is_tlawa=rec.episode_current_program.reading
            rec.is_big_review=rec.episode_current_program.maximum_audit

    @api.depends('student_id')
    def review_parts(self):
        for rec in self:
            self.big_part_ids=rec.student_id.part_id.ids

    is_tlawa=fields.Boolean(string='is tlawa',default=False, compute=is_tlawa)
    part_id=fields.Many2many("mk.parts",string="part")
    page_id = fields.Many2one('mk.memorize.method', string='Page', ondelete="restrict",) 
    big_part_ids=fields.Many2many("mk.parts",string="part",compute=review_parts)
    is_big_review=fields.Boolean(string="is big review",default=False,compute=is_big)
    big_part_ids=fields.Many2many("mk.parts",string="part",compute=review_parts)
    start_point=fields.Many2one("mk.subject.page","from subject")
    save_start_point=fields.Many2one("mk.subject.page","save start point")
    review_direction = fields.Selection([('up', 'up'), 
                                         ('down', 'down')], string='Big review direction',)
    @api.onchange('page_id')
    def onchange_page_id(self):
        ids=self.env['mk.subject.page'].search([('subject_page_id','=',self.page_id.id),('part_id','in',self.student_id.part_id.ids)])
        ids_2=self.env['mk.subject.page'].search([('subject_page_id','=',self.page_id.id),('part_id','in',self.almanhaj.part_ids.ids)])
        return {'domain': {'start_point': [('id', 'in', ids.ids)],
                           'save_start_point': [('id', 'in', ids_2.ids)]}}

    # @api.multi
    def open_after_detach_event(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window',
                'res_model': 'mk.episode_searc',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new',
                'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}}
        