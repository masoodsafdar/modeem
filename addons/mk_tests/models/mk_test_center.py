# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from odoo.tools.translate import _


class MkTestCenter(models.Model):
    _name = 'mk.test.center'
        
    name        = fields.Char('Center Name')
    company_id  = fields.Many2one('res.company',       string='Company', ondelete='restrict', default=lambda self: self.env['res.company']._company_default_get('mk.test.center'))
    city_id     = fields.Many2one('res.country.state', string='City',     required=True, domain=[('type_location','=','city'),
                                                                                                 ('enable','=',True)])
    area_id     = fields.Many2one('res.country.state', string='Area',     required=True, domain=[('type_location','=','area'),
                                                                                                 ('enable','=',True)])
    district_id = fields.Many2one('res.country.state', string='District', required=True, domain=[('type_location','=','district'),
                                                                                                 ('enable','=',True)])    
    longitude   = fields.Float('Longitude', required=True, digits=(12,8))
    latitude    = fields.Float('Latitude', required=True,  digits=(12,8))

    @api.onchange('city_id')
    def city_id_on_change(self):
        return {'domain':{'district_id':[('area_id', '=', self.city_id.id), 
                                         ('enable', '=', True), 
                                         ('district_id', '!=', False)]}}