#-*- coding:utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class MkCommentBehavior(models.Model):
    _name = 'mk.comment.behavior'
    _inherit = ['mail.thread']
    
    
    # @api.one
    def act_draft(self):
        self.state = 'draft'
        
    # @api.one
    def act_active(self):
        self.state = 'active'
    
    company_id     = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mk.comment.behavior'), track_visibility='onchange')
    punishment_ids = fields.Many2many('mk.punishment', string='Punishment')
    name           = fields.Char('Name', track_visibility='onchange')
    active         = fields.Boolean('Active', default=True, track_visibility='onchange')
    type           = fields.Selection([('general_comment', 'General Comment'),
                                       ('behavior', 'Behavior')], 'Type', default='general_comment', track_visibility='onchange')
	
	
    """@api.model    
    def fields_view_get(self, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(MkCommentBehavior, self).fields_view_get(view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
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

    @api.model
    def get_comment(self):
        comments = self.env['mk.comment.behavior'].search([('type', '=', 'general_comment')])
        item_list = []
        if comments:
            for comment in comments:
                item_list.append({'id': comment.id,
                                  'name': comment.name})
        return item_list

    @api.model
    def get_behavior(self):
        comments = self.env['mk.comment.behavior'].search([('type', '=', 'behavior')])
        item_list = []
        if comments:
            for comment in comments:
                item_list.append({'id': comment.id,
                                  'name': comment.name})
        return item_list



    
