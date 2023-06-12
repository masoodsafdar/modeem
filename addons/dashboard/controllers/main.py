# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request,Controller, route
import json

class Dashboard(http.Controller):
    
    def get_compare(self,chart):
        return request.env['dashboard.settings.chart'].search([('sequence','=',chart.sequence),('display','=',True),('display_type','=',chart.display_type),('dashboard_id','=',chart.dashboard_id.id)],order="id desc")
    
    def get_chart_data(self,chart):
        cr = request.cr
        mesure=''
        ykey=''
        model1=''
        model2=''
        filter=chart.filter
        model1=chart.chart_model_id.model.replace('.','_')
        if chart.type=='money': 
                sum_count="sum("
        else:
            sum_count="count("
            
        if chart.chart_date_field_id.ttype in ['date','datetime']:
            mesure=sum_count+chart.chart_measure_field_id.name+") as mesure"
            ykey=" date("+chart.chart_date_field_id.name+") as date "
        elif chart.chart_date_field_id.ttype =='many2one':
            mesure=sum_count+"m1."+chart.chart_measure_field_id.name+") as mesure"
            ykey="m2.name as date"
            model1+=" as m1"
            model2=chart.chart_date_field_id.relation.replace('.','_')+" as m2"
            
        group_by=""
        requete="SELECT "+mesure+', '+ykey+"  FROM "+model1
        if model2 and filter:
            group_by="m2.name"
            requete+=' ,'+model2
            requete+=" Where m1."+chart.chart_date_field_id.name+"= m2.id and m1."+filter.replace('"',"'")
        elif model2:
            group_by="m2.name"
            requete+=' ,'+model2
            requete+=" Where m1."+chart.chart_date_field_id.name+"= m2.id"
        elif filter:
            requete+=" Where "+filter.replace('"',"'")
        if not group_by:
            group_by=chart.chart_date_field_id.name
        requete+=" Group by "+group_by
        cr.execute(requete)
        return cr.dictfetchall()
            
        
    @route('/page/dashboard', type='http', auth='public')
    def get_uid(self):
        
        res=[]
        dashboard=request.env['dashboard.settings'].search([],limit=1,order='id desc')
        chart_ids=request.env['dashboard.settings.chart'].search([('display','=',True),('dashboard_id','=',dashboard.id)],order='sequence')
        for chart in chart_ids:
            result=[]
            datas=self.get_chart_data(chart)
            result=datas
            if chart.display_type=='area':
                res.append([chart.id,result,1])
            else:
                res.append([chart.id,result,2])
        return http.request.make_response(json.dumps(res,{
            'Cache-Control': 'no-cache', 
            'Content-Type': 'JSON; charset=utf-8',
            'Access-Control-Allow-Origin':  '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type, Access-Control-Allow-Headers, X-Requested-With',

            })) 
        
