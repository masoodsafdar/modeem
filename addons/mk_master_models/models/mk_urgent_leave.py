#-*- coding:utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class MkUrgentLeave(models.Model):
    _name = 'mk.urgent.leave'
    _inherit = ['mail.thread']
    _rec_name = 'leave_id'
        
    company_id         = fields.Many2one('res.company', string='Company', default=lambda self:self.env.user.company_id.id, track_visibility='onchange')
    study_year_id      = fields.Many2one('mk.study.year', 'Study Year', track_visibility='onchange')
    leave_id           = fields.Many2one('hr.holidays.status', 'Leave', track_visibility='onchange')
    start_date         = fields.Date('Start Date', track_visibility='onchange')
    end_date           = fields.Date('End Date', track_visibility='onchange')
    islamic_start_date = fields.Date('Islamic Start Date', track_visibility='onchange')
    islamic_end_date   = fields.Date('Islamic End Date', track_visibility='onchange')
    active             = fields.Boolean('Active', default=True, track_visibility='onchange')
    
    # @api.one
    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        if (self.start_date < self.study_year_id.start_date):
                raise ValidationError(_('تاريخ البداية اقل من تاريخ بداية السنة الدراسية'))
        if (self.end_date > self.study_year_id.end_date):
                raise ValidationError(_('تاريخ النهاية اكبر من تاريخ نهاية السنة الدراسية'))
                
                
    """@api.model    
    def fields_view_get(self, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(MkUrgentLeave, self).fields_view_get(view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='company_id']")
        company_ids = []
        company_recs= self.env['mk.study.year'].search([])
        company_ids = [x.company_id.id for x in company_recs]
        domain = "[('id', 'in', " + str(company_ids) + ")]"
        for node in nodes:
            node.set('domain', domain)
            res['arch'] = etree.tostring(doc)
        return res
    """

    @api.model
    def types_student_permission(self):
        query_string = ''' 
              select id, name
              from hr_holidays_status
              where active=True order by id;
              '''
        self.env.cr.execute(query_string)
        holidays_status = self.env.cr.dictfetchall()
        return holidays_status

