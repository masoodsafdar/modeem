#-*- coding:utf-8 -*-
from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

    
class Surah(models.Model):
    _name = 'mk.surah'
    _inherit = ['mail.thread']
    _order = 'order'
        
    name         = fields.Char('Name', track_visibility='onchange')
    order        = fields.Integer('Order', required=True, track_visibility='onchange')
    start_verses = fields.Integer('Start Verses ', track_visibility='onchange')
    end_verses   = fields.Integer('End Verses ', track_visibility='onchange')
    nbr_lines    = fields.Integer('عدد الأسطر', track_visibility='onchange')
    #part_ids = fields.One2many('mk.parts', 'part_id' , string='parts', )
    
    _sql_constraints = [('name_uniq', 'unique (name)', "هذا السجل موجود مسبقا !"),]
    
    @api.model
    def create(self, vals):
        #raise ValidationError('لا يمكنك إضافة أي سورة')
        return super(Surah, self).create(vals)

    @api.model
    def mk_surahs(self):
        query_string = ''' 
                select id, name, mk_surah.order as surah_order from mk_surah order by surah_order;
                '''
        self.env.cr.execute(query_string)
        surahs = self.env.cr.dictfetchall()
        return surahs

    
class Verse(models.Model):
    _name = 'mk.surah.verses'
    _inherit = ['mail.thread']
    _rec_name = 'original_surah_order'
    
    surah_id		 			= fields.Many2one('mk.surah', string='Surah', track_visibility='onchange')
    part_id 					= fields.Many2one('mk.parts', string='Part',  track_visibility='onchange')
    verse 						= fields.Text('Verse', track_visibility='onchange')
    original_accumalative_order = fields.Integer('Original Accumalative Order', track_visibility='onchange')
    reverse_accumalative_order  = fields.Integer('Reverse Accumalative Order',  track_visibility='onchange')
    original_surah_order 		= fields.Integer('Original Surah Order', track_visibility='onchange')
    reverse_surah_order 		= fields.Integer('Reverse Surah Order',  track_visibility='onchange')
    difficulty_level 			= fields.Selection([('easy', 'Easy'),
                                                    ('middle', 'Middle'),
                                                    ('difficult', 'Difficult')], string='Difficulty Level', track_visibility='onchange')
    line_start                  = fields.Integer('سطر البداية', track_visibility='onchange')
    line_end                    = fields.Integer('سطر النهاية', track_visibility='onchange')

    line_no 					= fields.Integer('Number of Lines per Verse', track_visibility='onchange')
    page_no						= fields.Integer('page no.', track_visibility='onchange')

    @api.model
    def get_listen_line_page(self, line_id):
        try:
            line_id = int(line_id)
        except:
            pass
        listen_line = self.env['mk.listen.line'].search([('id', '=', line_id)], limit=1)
        result = []
        from_aya = listen_line.from_aya.id
        to_aya = listen_line.to_aya.id
        if from_aya and to_aya:
            surah_verses = self.env['mk.surah.verses'].search([('original_accumalative_order', '>=', from_aya),
                                                               ('original_accumalative_order', '<=', to_aya)])
            if surah_verses:
                for verse in surah_verses:
                    result.append({'page_no': verse.page_no,
                                   'original_surah_order': verse.original_surah_order})
        return result

    @api.model
    def get_aya(self, page_no):
        try:
            page_no = int(page_no)
        except:
            pass

        surah_verses = self.env['mk.surah.verses'].search([('page_no', '=', page_no)])
        item_list = []
        if surah_verses:
            for verse in surah_verses:
                item_list.append({'original_surah_order': verse.original_surah_order})
        return item_list

    @api.model
    def mk_surah_verses(self):
        query_string = ''' 
              select id, surah_id, verse, original_surah_order, page_no 
              from mk_surah_verses 
              order by page_no,original_surah_order;
              '''
        self.env.cr.execute(query_string)
        surah_verses = self.env.cr.dictfetchall()
        return surah_verses


