# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime,timedelta,date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
class rate_wizerd(models.TransientModel):
    _name="attendance.certificate"
    
    date_from=fields.Date(string="From",required=True)
    date_to=fields.Date(string="To",required=True)
    title=fields.Many2one("mk.reports.purphose" ,"purphase",required=True)
    student_id=fields.Many2one("mk.link","student",required=True)
    episode=fields.Many2one("mk.episode","Episode",required=True)
    
    # @api.multi
    def print_report(self):
        days=[]
        date_format = "%Y-%m-%d"
        datas={}
        distance=datetime.strptime(self.date_to,date_format)-datetime.strptime(self.date_from,date_format)
        number_of_days=distance.days

        for x in range(0, number_of_days):
            next_date=datetime.strptime(self.date_from,"%Y-%m-%d")+timedelta(days=x)
            d=str(next_date)
            days.append(d[:-9])

        days.append(str(self.date_to)) 
        for rec in self :
            data=self.read()[0]
            datas={'ids':[],'form':data,'model':'attendance.certificate','days':days}

        return self.env.ref('mk_student_managment.attendance_certificate').report_action(self.ids,data=datas)

    def get_pdf(self,student_id,episode_id,purphase,date_from,date_to):
        #get episode name
        episode_name=''
        episode_obj=self.env['mk.episode']
        episode_ids=episode_obj.search([('id','=',int(episode_id))])
        if episode_ids:
            episode_name=episode_ids[0].name
        #get purphase name
        pu_obj=self.env['mk.reports.purphose']
        pu_ids=pu_obj.search([('id','=',int(purphase))])
        pu_name=''
        if pu_ids:
            pu_name=pu_ids[0].name
        #get student_name
        student_name=''
        student_obj=self.env['mk.link']
        st_ids=student_obj.search([('id','=',int(student_id))])
        if st_ids :
            student_name=st_ids[0].student_id.display_name

        data={

             'create_uid': (1, 'Administrator'),
             'episode': (int(episode_id), episode_name), 
             'title': (int(purphase), pu_name),
             'student_id': (int(student_id), student_name),
             'date_from': date_from, 
             '__last_update': '2017-08-29 07:01:35',
             'write_uid': (1, 'Administrator'), 
             'write_date': '2017-08-29 07:01:35', 
             'date_to': date_to,
             'create_date': '2017-08-29 07:01:35', 
             'id': self.id, 
        }

        days=[]
        date_format = "%Y-%m-%d"
        distance=datetime.strptime(date_to,date_format)-datetime.strptime(date_from,date_format)
        number_of_days=distance.days
        days.append(str(date_to)) 
        for x in range(0, number_of_days):
            next_date=datetime.strptime(date_from,"%Y-%m-%d")+timedelta(days=x)
            d=str(next_date)
            days.append(d[:-9])


        datas={'model':'attendance.certificate','ids': [],'form': data, 'days': days}
        pdf = self.env.ref('mk_student_managment.attendance_certificate').render_qweb_pdf(self.ids,data=datas)
        return pdf