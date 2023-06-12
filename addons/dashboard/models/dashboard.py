#!/usr/bin/env python
#coding: utf8 

from odoo import models, fields, api
import datetime



class Dashboard(models.Model):
    _name = 'dashboard.dashboard'
    
    def has_active(self,model):
        for field in model.field_id:
            if field.name=='active':
                return True
        return False
    def _compute_field_list(self):
        dashboard=self.env['dashboard.settings'].search([],limit=1,order='id desc')
        lists = dashboard.line_ids
        last_slices_list=[]
        for list in lists:
            if list.display:
                action = self.env['ir.actions.act_window'].search([('res_model','=',list.model_id.model),('view_type','=','form')],limit=1)
                
                if list.type=='money': 
                    sum_count="sum( "
                else:
                    sum_count="count( "
                model1=list.model_id.model.replace('.','_')
                model2=''
                group=''
                m1=""
                groupjoin=''
                action_where=''
                if list.groupby:
                    mesure=sum_count+"m1."+list.field_id.name+") as field"
                    group="m2.name as group, m2.id as id"
                    model1+=" as m1"
                    model2=list.group_id.relation.replace('.','_')+" as m2"
                    m1="m1."
                    groupjoin=" and "+m1+list.group_id.name+"= m2.id"
                else:
                    mesure=sum_count+list.field_id.name+") as field"
                    
                requete_action="Select "+m1+"id as id "   
                requete="SELECT "+mesure
                if group:
                    requete+=", "+group+" FROM "+model1+", "+model2
                    requete_action+=" FROM "+model1+", "+model2
                else:
                    requete+=" FROM "+model1
                    requete_action+=" FROM "+model1
                    
                if self.has_active(list.model_id) and list.filter: 
                    requete+=" Where "+m1+"active=true And "+m1+list.filter+groupjoin
                    action_where=" Where "+m1+"active=true And "+m1+list.filter+groupjoin
                elif self.has_active(list.model_id):
                    requete+=" Where "+m1+"active=true "+groupjoin
                    action_where=" Where "+m1+"active=true "+groupjoin
                elif list.filter:
                    requete+=" Where "+list.filter+groupjoin
                    action_where=" Where "+list.filter+groupjoin
                else:
                    requete+=" Where "+groupjoin.replace('and','')
                    action_where=" Where "+groupjoin.replace('and','')
                if list.groupby:
                    requete+=" Group by m2.name, m2.id"
                
                self.env.cr.execute(requete.replace('"',"'"))
                result = self.env.cr.dictfetchall()
                fields=[]
                if list.groupby:
                    
                    for res in result:
                        requete_action_ids=requete_action+" Where m2.id ="+str(res['id'])+groupjoin
                        self.env.cr.execute(requete_action_ids.replace('"',"'"))
                        result_ids = self.env.cr.dictfetchall()
                        
                        res_ids=[]
                        for resu in result_ids:
                            res_ids.append(resu['id'])
                        last_slices_list.append([res['field'],list.name+" "+res['group'] or list.field_id.field_description+res['group'],list.color,list.icon,action.id,res_ids])
                else:
                    requete_action+=action_where
                    self.env.cr.execute(requete_action.replace('"',"'"))
                    result_ids = self.env.cr.dictfetchall()
                    res_ids=[]
                    for res in result_ids:
                        res_ids.append(res['id'])
                    last_slices_list.append([result[0]['field'],list.name or list.field_id.field_description,list.color,list.icon,action.id,res_ids])
        return last_slices_list
    
        
    def _get_default_chart(self):
        chart_list=[]
        dashboard=self.env['dashboard.settings'].search([],limit=1,order='id desc')
        chart_ids=self.env['dashboard.settings.chart'].search([('dashboard_id','=',dashboard.id)],order='sequence')
        for list in chart_ids:
            if list.display :
                if list.display_type=='area':
                    chart_list.append([list.id,list.name,1])
                else:
                    chart_list.append([list.id,list.name,2])
        return chart_list
    
    
    name = fields.Char('Name')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', store=True, string="Currency")
    field_list = fields.Selection('_compute_field_list',string='Slices names')
    chart_list=fields.Selection('_get_default_chart',string='Charts')
    
    @api.multi
    def action_setting(self):
        
        action = self.env.ref('dashboard.action_dashboard_config').read()[0]

        setting = self.env['dashboard.settings'].search([],limit=1,order='id desc').id
        action['views'] = [(self.env.ref('dashboard.dashboard_config_settings').id, 'form')]
        action['res_id'] = setting
        return action
    
    
    
    @api.multi
    def view_details(self):
        action = self.env['ir.actions.act_window'].search([('id','=',self.env.context['action_id'],)],limit=1)
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_mode': 'tree,kanban,form',
            'target': action.target,
            'domain':[('id','in',self.env.context['active_ids'])],
            'context': {},
            'res_model': action.res_model,
        }
        return result