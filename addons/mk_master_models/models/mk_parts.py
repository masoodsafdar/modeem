#-*- coding:utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
    
    
class MkParts(models.Model):
    _name = 'mk.parts'
    _inherit = ['mail.thread']
    _order = 'order'
        
    name        = fields.Char('Name', track_visibility='onchange')
    order       = fields.Integer('Order', track_visibility='onchange')
    from_surah  = fields.Many2one('mk.surah', string='From Surah', track_visibility='onchange')
    to_surah    = fields.Many2one('mk.surah', string='To Surah',   track_visibility='onchange')
    from_verses = fields.Integer('From Verses ', track_visibility='onchange')
    to_verses   = fields.Integer('To Verses ', track_visibility='onchange')
    
    _sql_constraints = [('name_uniq', 'unique (name)', "هذا السجل موجود مسبقا !"),]

    @api.model
    def parts_quran(self, line_id):
        query_string = ''' 
                   SELECT id, name
                   FROM mk_parts
                   ORDER BY mk_parts.order;
                   '''.format(line_id)
        self.env.cr.execute(query_string)
        parts_quran = self.env.cr.dictfetchall()
        return parts_quran