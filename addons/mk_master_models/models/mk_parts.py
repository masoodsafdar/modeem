#-*- coding:utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
    
    
class MkParts(models.Model):
    _name = 'mk.parts'
    _inherit=['mail.thread','mail.activity.mixin']
    _order = 'order'
        
    name        = fields.Char('Name', tracking=True)
    order       = fields.Integer('Order', tracking=True)
    from_surah  = fields.Many2one('mk.surah', string='From Surah', tracking=True)
    to_surah    = fields.Many2one('mk.surah', string='To Surah',   tracking=True)
    from_verses = fields.Integer('From Verses ', tracking=True)
    to_verses   = fields.Integer('To Verses ', tracking=True)
    
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