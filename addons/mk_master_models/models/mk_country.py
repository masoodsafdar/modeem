# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class mk_country(models.Model):
    _inherit = 'res.country'
    
    active      = fields.Boolean('Active', default=True,)
    is_default  = fields.Boolean('Default')
    ar_name     = fields.Char()
    nationality = fields.Char()
    
    def unlink(self):
        try:
            super(mk_country, self).unlink()
        except:
            raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))
        
    @api.model
    def fix_translation(self):
        countries = self.search([('nationality','!=',False)])
        i = 1
        for country in countries:
            tr = self.env['ir.translation'].search([('name','=','res.country,name'),
                                                    ('lang','=','ar_SY'),
                                                    ('src','=',country.name)])
            if tr:
                i += 1
                tr.write({'value': country.ar_name,
                          'res_id': country.id})

    @api.model
    def get_nationality(self):
        countries = self.env['res.country'].search([('active', '=', True),
                                                    ('nationality', '!=', False)], order="nationality")
        nationalities = []
        if countries:
            for country in countries:
                nationalities.append({'id':          country.id,
                                      'nationality': country.nationality})
        return nationalities

    @api.model
    def countries_get(self):
        countries = self.env['res.country'].search([('ar_name', '!=', ''),
                                                    '|', ('active', '=', True),
                                                         ('active', '=', False)])
        result = []
        if countries:
            for country in countries:
                result.append({'id':      country.id,
                               'ar_name': country.ar_name})
        return result


