#-*- coding:utf-8 -*-
from odoo import models, fields, api


class MK_epsoide_works(models.Model):
	_name = 'mk.epsoide.works'
	_inherit=['mail.thread','mail.activity.mixin']

	name            = fields.Char('Name',      tracking=True)
	active          = fields.Boolean("Active", tracking=True)
	type_episode_id = fields.Many2one('mk.episode_type', string='نوع الحلقة', tracking=True)
	memorize        = fields.Boolean('Memorize',      tracking=True)
	minimum_audit   = fields.Boolean('Minimum Audit', tracking=True)
	maximum_audit   = fields.Boolean('Maximum Audit', tracking=True)
	reading         = fields.Boolean('Reading',       tracking=True)