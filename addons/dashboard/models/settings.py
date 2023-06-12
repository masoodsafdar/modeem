#!/usr/bin/env python
#coding: utf8 
from odoo import models, fields, api

class DashboardSettings(models.Model):
    _name = 'dashboard.settings'
    
    
    def get_default_chart_model(self):
        return self.search([],limit=1,order='id desc').chart_model_id.id
    def get_default_chart_measure_field(self):
        return self.search([],limit=1,order='id desc').chart_measure_field_id.id
    def get_default_chart_date_field(self):
        return self.search([],limit=1,order='id desc').chart_date_field_id.id
    
    def get_default_lines(self):
        return self.search([],limit=1,order='id desc').line_ids.ids
    
    def get_default_chart(self):
        return self.search([],limit=1,order='id desc').chart_ids.ids
    
    name=fields.Char('Name',default="Setting")
    provider_latitude=fields.Char('latitude')
    provider_longitude=fields.Char('ongitude')
    map=fields.Char('ongitude')
    line_ids=fields.One2many('dashboard.settings.line','dashboard_id','Fields',default=get_default_lines)
    chart_ids=fields.One2many('dashboard.settings.chart','dashboard_id','Charts',default=get_default_chart)
    

class DashboardSettingsLine(models.Model):
    _name = 'dashboard.settings.line'
    
    name=fields.Char('Name')
    model_id = fields.Many2one('ir.model','Model')
    field_id = fields.Many2one('ir.model.fields','Field')
    group_id = fields.Many2one('ir.model.fields','Group By')
    color=fields.Selection([('red','Red'),('green','Green'),('primary','Primary'),('yellow','Yellow')],string='Color')
    icon=fields.Char('Icon')
    filter=fields.Char('Filter')
    type=fields.Selection([('money','Money'),('qty','Quantity')],string='Type')
    dashboard_id = fields.Many2one('dashboard.settings','Setting')
    display=fields.Boolean('Show/hide',default=True)
    groupby=fields.Boolean('Group by',default=False)
    

class DashboardSettingschart(models.Model):
    _name = 'dashboard.settings.chart'
    
    name=fields.Char('Name')
    sequence=fields.Integer('Sequence',default=1)
    display_type=fields.Selection([('area','Area'),('bar','Bar')],string='Display Type')
    chart_model_id = fields.Many2one('ir.model','Chart Model')
    chart_measure_field_id = fields.Many2one('ir.model.fields','Chart measure Field')
    chart_date_field_id = fields.Many2one('ir.model.fields','Chart date Field')
    filter=fields.Char('Filter')
    type=fields.Selection([('money','Money'),('qty','Quantity')],string='Type')
    dashboard_id = fields.Many2one('dashboard.settings','Setting')
    display=fields.Boolean('Show/hide',default=True)
    
    @api.onchange('display_type','chart_model_id')
    def _onchange_price(self):
        domain=[]
        if self.chart_model_id:
            domain.append(('model_id','=',self.chart_model_id.id)) 
        if self.display_type:
            if self.display_type=='area':
                domain+=[(('ttype','in',['date','datetime']))]
            else :
                domain+=[(('ttype','in',['date','datetime','many2one']))]
        return {
            'domain': {
                'chart_date_field_id': domain,
            }
        }


