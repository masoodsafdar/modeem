#-*- coding:utf-8 -*-
from odoo import models, fields, api


class MK_epsoide_works(models.Model):
	_name = 'mk.epsoide.works'
	_inherit = ['mail.thread']

	name            = fields.Char('Name',      track_visibility='onchange')
	active          = fields.Boolean("Active", track_visibility='onchange')
	type_episode_id = fields.Many2one('mk.episode_type', string='نوع الحلقة', track_visibility='onchange')
	memorize        = fields.Boolean('Memorize',      track_visibility='onchange')
	minimum_audit   = fields.Boolean('Minimum Audit', track_visibility='onchange')
	maximum_audit   = fields.Boolean('Maximum Audit', track_visibility='onchange')
	reading         = fields.Boolean('Reading',       track_visibility='onchange')