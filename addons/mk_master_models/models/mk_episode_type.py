# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.osv import osv
from datetime import datetime
from odoo.exceptions import Warning
from odoo.exceptions import UserError


class episode_type(models.Model):
    _name = 'mk.episode_type'
    _inherit = ['mail.thread']
    _description = u'episode_type'

    _rec_name = 'name'
    _order = 'name ASC'

    name        = fields.Char(string='Name',          required=True, index=True, size=50, translate=True, track_visibility='onchange')
    students_no = fields.Integer(string='Student no', required=True, track_visibility='onchange')
    active      = fields.Boolean( string='Active', default=True, track_visibility='onchange')

    # @api.multi
    def unlink(self):
        episode_ids=self.env['mk.episode'].search([('episode_type','=', self.id)])
        if episode_ids.ids:
            raise UserError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))
        else:
            super(episode_type, self).unlink()