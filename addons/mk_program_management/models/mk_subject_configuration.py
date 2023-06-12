#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from odoo.tools.translate import _


class MkSubjectConfiguration(models.Model):
    _name = 'mk.subject.configuration'

    @api.model
    def get_center(self):
        emp_obj= self.env['hr.employee']
        emp_ids = emp_obj.search([('user_id','=',self._uid)])
        if emp_ids:
            employee= emp_ids[0]
            if employee.department_id.level_type == 'c':
                return employee.department_id.id
            elif employee.department_id.level_type == 'mc':
                if employee.department_id.parent_id.level_type == 'c':
                    return employee.department_id.parent_id.id
        return False
       
    @api.model
    def get_mosque(self):
        emp_obj= self.env['hr.employee']
        emp_ids = emp_obj.search([('user_id','=',self._uid)])
        if emp_ids:
            employee= emp_ids[0]
            if employee.department_id.level_type == 'mc':
                return employee.department_id.id
        return False
        
    company_id			 = fields.Many2one('res.company',   string='Company', default=lambda self: self.env['res.company']._company_default_get('mk.approaches'))  
    center_department_id = fields.Many2one('hr.department', string='Center', default=get_center)
    mosque_id			 = fields.Many2one('mk.mosque',     string='Mosque', default=get_mosque)
    program_id			 = fields.Many2one('mk.programs',   string='Program') 
    approach_id			 = fields.Many2one('mk.approaches', string='Approach') 
    name				 = fields.Char('Name') 
    order				 = fields.Integer('order')
    num_words			 = fields.Char('Day')    
    part_id				 = fields.Many2one('mk.parts', string='Part')
    from_surah			 = fields.Many2one('mk.surah',        related='detail_id.from_surah', string='From: Surah', store=True)
    from_verse			 = fields.Many2one('mk.surah.verses', related='detail_id.from_verse', string='Verse',       store=True)
    to_surah			 = fields.Many2one('mk.surah',        related='detail_id.to_surah',   string='To: Surah',   store=True)
    to_verse			 = fields.Many2one('mk.surah.verses', related='detail_id.to_verse',   string='Verse',       store=True)    
    is_test				 = fields.Boolean('Test After End of Subject')
    subject_id			 = fields.Many2one('mk.memorize.method', string='Subject')
    detail_id			 = fields.Many2one('mk.subject.page',    string='Detail')
    state				 = fields.Selection([('draft', 'Draft'), 
											 ('active', 'Active'),], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')

    # @api.one
    def unlink(self):
        if self.state == "active":
            raise ValidationError(_('لا يمكنك حذف سجل تم تأكيده'))

        try:
            super(MkSubjectConfiguration, self).unlink()
        except:
            raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))

    # @api.one
    def act_draft(self):
        self.state = 'draft'

    # @api.one
    def act_active(self):
        self.state = 'active'
