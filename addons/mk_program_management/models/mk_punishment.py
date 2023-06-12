#-*- coding:utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from odoo.tools.translate import _


class MkPunishment(models.Model):
    _name = 'mk.punishment'
    _inherit = ['mail.thread']
    
    
    # @api.one
    def act_draft(self):
        self.state = 'draft'
        
    # @api.one
    def act_active(self):
        self.state = 'active'
    
    company_id          = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mk.punishment'), track_visibility='onchange')
    name                = fields.Char('Name', track_visibility='onchange')
    deduct_from_degrees = fields.Float('Deduct From Degrees',    track_visibility='onchange')
    deduct_from_points  = fields.Float('Deduct From Points',     track_visibility='onchange')
    active              = fields.Boolean('Active', default=True, track_visibility='onchange')
    
    guardian_call      = fields.Boolean('Call the Guardian and write a Pledge', track_visibility='onchange')
    guardian_message   = fields.Boolean('Send Message to guardian',     track_visibility='onchange')
    mosque_message     = fields.Boolean('Send Message to Mosque Admin', track_visibility='onchange')
    freeze_study_class = fields.Boolean('Freeze the Study Class',       track_visibility='onchange')
    #temporary_freezing = fields.Boolean('Temporary Freezing for Membership and Adding to Black List on the Current Study Class')
    #permenant_freezing = fields.Boolean('Permenant Freezing and Adding to Permenant Black List')
    
    state = fields.Selection([('draft', 'Draft'),
                              ('active', 'Active')], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
	
	
    """@api.model    
    def fields_view_get(self, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(MkPunishment, self).fields_view_get(view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='company_id']")
        company_ids = []
        company_recs= self.env['mk.study.year'].search([])
        company_ids = [x.company_id.id for x in company_recs]
        domain = "[('id', 'in', " + str(company_ids) + ")]"
	    for node in nodes:
    		node.set('domain', domain)
            res['arch'] = etree.tostring(doc)
        return res """
    
