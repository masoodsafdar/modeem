#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)
    
class mk_memorize_method(models.Model):
    _name = 'mk.memorize.method'
    _inherit = ['mail.thread']

        
    name             = fields.Char('Name', track_visibility='onchange')
    type_method      = fields.Selection([('subject', 'Subject'),
								         ('page',    'Page')],   string='Type',  default='subject', track_visibility='onchange')
    direction        = fields.Selection([('up',   'من الفاتحة للناس'),
									     ('down', 'من الناس للفاتحة')], string='مسار الحفظ', default='up',      track_visibility='onchange')
    subject_page_ids = fields.One2many('mk.subject.page', 'subject_page_id', string='lines')
    type_qty         = fields.Selection([('qty001','آية'),
                                         ('qty025','ربع صفحة'),
                                         ('qty050','نصف صفحة'),
                                         ('qty075','ثلاثة ارباع صفحة'),
                                         ('qty100','صفحة واحدة'),
                                         ('qty125','صفحة وربع'),
                                         ('qty150','صفحة ونصف'),
                                         ('qty175','صفحة وثلاثة ارباع'),
                                         ('qty200','صفحتان'),], string='المقدار')    

    # @api.one
    def unlink(self):
        try:
            super(mk_memorize_method, self).unlink()
        except:
            raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))

    @api.model
    def get_mushaf_parts(self, direction):
        try:
            direction = direction
        except:
            pass

        query_string = ''' 
                       select id, name, direction from mk_memorize_method 
                       WHERE type_method = 'subject' and
                              direction = '{}'
                       order by id;
                       '''.format(direction)

        self.env.cr.execute(query_string)
        mushaf_parts = self.env.cr.dictfetchall()
        return mushaf_parts

