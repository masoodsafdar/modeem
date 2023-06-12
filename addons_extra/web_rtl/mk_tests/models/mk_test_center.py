#-*- coding:utf-8 -*-

##############################################################################
#
#    Copyright (C) Appness Co. LTD **hosam@app-ness.com**. All Rights Reserved
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from odoo.tools.translate import _

class MkTestCenter(models.Model):
    _name = 'mk.test.center'
        
    name = fields.Char('Center Name')
    company_id = fields.Many2one('res.company', string='Company',ondelete='restrict', default=lambda self: self.env['res.company']._company_default_get('mk.test.center'))
    city_id = fields.Many2one(
        'res.country.state', domain=['&',('area_id','=',False),('district_id','=',False),('enable','=',True)],string='City',
        required=True,
    )
    area_id = fields.Many2one(
        'res.country.state', domain=['&',('area_id','!=',False),('district_id','=',False),('enable','=',True)],string='Area',
        required=True,
    )
    district_id = fields.Many2one(
        'res.country.state', domain=[('district_id','!=',False),('enable','=',True)],string='District',
        required=True,
    )
    longitude = fields.Float(
        string='Longitude',
        required=True, digits=(12,8)
    )
    latitude = fields.Float(
        string='Latitude',
        required=True,  digits=(12,8)       
    )






    #active = fields.Boolean('Active', default=True)
    """
    @api.model    
    def fields_view_get(self, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(MkTestCenter, self).fields_view_get(view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
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
    

