#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime
import logging
_logger = logging.getLogger(__name__)


class MkepisodeMaster(models.Model):    
    _inherit = 'mk.episode.master'

    # @api.multi
    def go_to_subh_period(self):
        tree_view = self.env.ref('mk_episode_management.mk_episode_form_view')
        # res_id=self.env['mk.episode'].search([('parent_episode','=',self.id),('selected_period','=','subh')])
        query = """ select id from  mk_episode where parent_episode=%d  and selected_period='subh' """ % (self.id)
        self.env.cr.execute(query)
        res_id = self.env.cr.dictfetchall()
        return {  # 'name': _('Opportunity'),
            'res_model': 'mk.episode',
            'res_id': res_id[0]['id'],
            'views': [(tree_view.id, 'form'), ],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('parent_episode', '=', self.id), ('selected_period', '=', 'subh')]}

    # @api.multi
    def go_to_zuhr_period(self):
        tree_view = self.env.ref('mk_episode_management.mk_episode_form_view')
        # res_id=self.env['mk.episode'].search([('parent_episode','=',self.id),('selected_period','=','zuhr')])
        query = """ select id from  mk_episode where parent_episode=%d  and selected_period='zuhr' """ % (self.id)
        self.env.cr.execute(query)
        res_id = self.env.cr.dictfetchall()
        return {  # 'name': _('Opportunity'),
            'res_model': 'mk.episode',
            'res_id': res_id[0]['id'],
            'views': [(tree_view.id, 'form'), ],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('parent_episode', '=', self.id), ('selected_period', '=', 'zuhr')]}

    # @api.multi
    def go_to_asaar_period(self):
        tree_view = self.env.ref('mk_episode_management.mk_episode_form_view')
        # res_id=self.env['mk.episode'].search([('parent_episode','=',self.id),('selected_period','=','aasr')])
        query = """ select id from  mk_episode where parent_episode=%d  and selected_period='aasr' """ % (self.id)
        self.env.cr.execute(query)
        res_id = self.env.cr.dictfetchall()
        return {  # 'name': _('Opportunity'),
            'res_model': 'mk.episode',
            'res_id': res_id[0]['id'],
            'views': [(tree_view.id, 'form'), ],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('parent_episode', '=', self.id), ('selected_period', '=', 'aasr')]}

    # @api.multi
    def go_to_magrib_period(self):
        tree_view = self.env.ref('mk_episode_management.mk_episode_form_view')
        # res_id=self.env['mk.episode'].search([('parent_episode','=',self.id),('selected_period','=','magrib')])
        query = """ select id from  mk_episode where parent_episode=%d  and selected_period='magrib' """ % (self.id)
        self.env.cr.execute(query)
        res_id = self.env.cr.dictfetchall()
        return {  # 'name': _('Opportunity'),
            'res_model': 'mk.episode',
            'res_id': res_id[0]['id'],
            'views': [(tree_view.id, 'form'), ],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('parent_episode', '=', self.id), ('selected_period', '=', 'magrib')]}

    # @api.multi
    def go_to_esha_period(self):
        tree_view = self.env.ref('mk_episode_management.mk_episode_form_view')
        # res_id=self.env['mk.episode'].search([('parent_episode','=',self.id),('selected_period','=','esha')])
        query = """ select id from  mk_episode where parent_episode=%d  and selected_period='esha' """ % (self.id)
        self.env.cr.execute(query)
        res_id = self.env.cr.dictfetchall()
        return {  # 'name': _('Opportunity'),
            'res_model': 'mk.episode',
            'res_id': res_id[0]['id'],
            'views': [(tree_view.id, 'form'), ],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('parent_episode', '=', self.id), ('selected_period', '=', 'esha')]}


