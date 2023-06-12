#-*- coding:utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from odoo.tools.translate import _

class MkTestError(models.Model):
    _name = 'mk.test.error'
    _inherit = ['mail.thread']


    company_id    = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mk.test.error'), track_visibility='onchange')
    code          = fields.Char(string='Code', required=True, track_visibility='onchange')
    error_type    = fields.Selection([('at','Applied Tajweed'),('s','Saving')], string='Error Type', default='at', track_visibility='onchange')
    name          = fields.Char('Error Name', track_visibility='onchange')
    active        = fields.Boolean('Active', default=True, track_visibility='onchange')
    degree_deduct = fields.Float('Degree Deduct', track_visibility='onchange')
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "موجود مسبقاً !"),
    ]

    """
    @api.model    
    def fields_view_get(self, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(MkTestError, self).fields_view_get(view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
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
    

