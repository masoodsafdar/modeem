# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class mk_subject_page(models.Model):
    _name = 'mk.subject.page'
    _inherit=['mail.thread','mail.activity.mixin']
    _description = 'Subjects Pages Configuration'
    _rec_name= 'subject_page_id'
    _order = "order"

    # @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "%s (%s) - %s (%s)" % (record.from_surah.name, record.from_verse.original_surah_order,record.to_surah.name, record.to_verse.original_surah_order)))

        return result
    
    # @api.one
    @api.depends('from_verse','to_verse')
    def get_parts(self):
        part_verse_from_id = self.from_verse.part_id.id
        part_verse_to_id = self.to_verse.part_id.id
        part_ids = [part_verse_from_id]
        
        if part_verse_from_id != part_verse_to_id:
            part_ids += [part_verse_to_id]
            
        self.part_id = part_ids
        
    @api.model
    def set_parts(self):
        subjects = self.search([])
        nbr = len(subjects)
        i = 1
        j = 1
        for subject in subjects:
            part_verse_from_id = subject.from_verse.part_id.id
            part_verse_to_id = subject.to_verse.part_id.id
            part_ids = [part_verse_from_id]
            
            if part_verse_from_id != part_verse_to_id:
                part_ids += [part_verse_to_id]
                
            subject.part_id = part_ids
            
            if j == 200:
                j = 0

            j += 1
            i += 1
                

    order			= fields.Integer('order', tracking=True)
    subject_page_id = fields.Many2one('mk.memorize.method', string='Subject or Page', tracking=True)
    from_surah 		= fields.Many2one('mk.surah',           string='From: Surah', tracking=True)
    from_verse 		= fields.Many2one('mk.surah.verses',    string='Verse',       tracking=True)
    to_surah 		= fields.Many2one('mk.surah',           string='To: Surah', tracking=True)
    to_verse 		= fields.Many2one('mk.surah.verses',    string='Verse',     tracking=True)
    is_test			= fields.Boolean("is test", tracking=True)
    #part_id=fields.Many2one("mk.parts","part")
    part_id 		= fields.Many2many('mk.parts', 'parts_subject', 'subject_id', 'part_id', string="parts", compute='get_parts', store=True, tracking=True)
    active 			= fields.Boolean('Active',default=True, tracking=True)
    
    from_sura       = fields.Integer()
    from_aya        = fields.Integer()
    to_sura         = fields.Integer()
    to_aya          = fields.Integer()

    # @api.one
    def unlink(self):
        try:
            super(mk_subject_page, self).unlink()
        except:
            raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))

    @api.model
    def set_subject_data(self):
        sbjs = self.search([('from_surah','=',False)])
        nbr_sbj = len(sbjs)
        i = 1
        j = 1
        for sbj in sbjs:
            from_sura = sbj.from_sura            
            to_sura = sbj.to_sura
            
            from_surah = self.env['mk.surah'].search([('order','=',from_sura)],limit=1)
            from_surah_id = from_surah.id
            if from_sura == to_sura:
                to_surah_id = from_surah_id
            else:
                to_surah = self.env['mk.surah'].search([('order','=',to_sura)],limit=1)
                to_surah_id = to_surah.id
        
            from_verse = self.env['mk.surah.verses'].search([('surah_id','=',from_surah_id),
                                                             ('original_surah_order','=',sbj.from_aya)], limit=1)
            
            to_verse = self.env['mk.surah.verses'].search([('surah_id','=',to_surah_id),
                                                           ('original_surah_order','=',sbj.to_aya)], limit=1)
            
            part_ids = []
            if from_verse.part_id.id:
                part_ids += [from_verse.part_id.id]
            
            if to_verse.part_id.id:
                part_ids += [to_verse.part_id.id]
                
            part_ids = list(set(part_ids))
            
            sbj.write({'from_surah': from_surah_id,
                       'to_surah':   to_surah_id,
                       'from_verse': from_verse.id,
                       'to_verse':   to_verse.id,
                       'part_id':    [(6,0,part_ids)]})
            
            if j == 20:
                j = 0

            i += 1
            j += 1

    @api.model
    def get_memorize_method_surah_lines(self, subject_page_id, surah_id):
        try:
            subject_page_id = int(subject_page_id)
            surah_id = int(surah_id)
        except:
            pass

        query_string = '''
               select m.id, 
               m.order, 
               m.from_surah, 
               m.to_surah, 
               m.from_verse, 
               v.original_surah_order as order_verse_from, 
                m.to_verse, 
                m.is_test 
                from mk_subject_page m, 
                mk_surah_verses v
                WHERE active = true and
        		m.from_verse = v.id and
                subject_page_id = {} and 
                from_surah = {} '''.format(subject_page_id, surah_id)
        self.env.cr.execute(query_string)
        memorize_method_surah_lines = self.env.cr.dictfetchall()
        return memorize_method_surah_lines

    @api.model
    def get_mushaf_part_lines(self, subject_page_id):
        try:
            subject_page_id = int(subject_page_id)
        except:
            pass

        query_string = '''
              select id, mk_subject_page.order, 
              from_surah, 
              to_surah, 
              from_verse, 
              to_verse, 
              is_test
              from mk_subject_page
              WHERE active = true and 
              subject_page_id = {}
              order by mk_subject_page.order;
              '''.format(subject_page_id)

        self.env.cr.execute(query_string)
        mushaf_part_lines = self.env.cr.dictfetchall()
        return mushaf_part_lines

    @api.model
    def get_mushaf_subject_surahs(self, subject_page_id):
        try:
            subject_page_id = int(subject_page_id)
        except:
            pass

        query_string = '''
            select id, name, mk_surah.order as surah_order 
            from mk_surah  where id in (
                select distinct from_surah
                from mk_subject_page
                WHERE active = true and 
                subject_page_id = {})
			    order by surah_order;'''.format(subject_page_id)

        self.env.cr.execute(query_string)
        mushaf_subject_surahs = self.env.cr.dictfetchall()
        return mushaf_subject_surahs

    @api.model
    def get_mushaf_subject_surah_verses(self, subject_page_id, surah_id):
        try:
            subject_page_id = int(subject_page_id)
            surah_id = int(surah_id)
        except:
            pass

        query_string = '''
        
         select id, original_surah_order , verse
                from mk_surah_verses  where id in (
                select from_verse
                from mk_subject_page
                WHERE active = true and 
                subject_page_id = {}
			    and from_surah = {} )
                order by original_surah_order;'''.format(subject_page_id, surah_id)

        self.env.cr.execute(query_string)
        mushaf_subject_surah_verses = self.env.cr.dictfetchall()
        return mushaf_subject_surah_verses

