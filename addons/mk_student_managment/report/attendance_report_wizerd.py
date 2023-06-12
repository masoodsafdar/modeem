# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)


class rate_wizerd(models.TransientModel):
    _name = "attendance.certificate"
    
    date_from  = fields.Date(string="From", required=True)
    date_to    = fields.Date(string="To",   required=True)
    title      = fields.Many2one("mk.report.purphose" , string="purphase",required=False)
    student_id = fields.Many2one("mk.link",             string="student", required=True)
    episode    = fields.Many2one("mk.episode",          string="Episode", required=True)
    
    # @api.multi
    def print_report(self):
        datas = self.get_data_report(self.student_id.id, self.date_from, self.date_to)
        return self.env.ref('mk_student_managment.attendance_certificate').report_action(self.ids, data=datas)
        
    def get_data_report(self, link_id, date_from, date_to):
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()

        plan = self.env['mk.student.prepare'].search([('link_id','=',link_id)], limit=1)

        if not plan:
            return {'model': 'attendance.certificate',
                    'ids':   [],
                    'form':  {'date_from': date_from, 
                              'date_to':   date_to,
                 
                              'student':   "",
                              'episode':   "",
                              'period':    "",
                 
                              'lines':     []}}
        
        plan_id = plan.id
        listen_plan_lines = self.env['mk.listen.line'].search([('preparation_id','=',plan_id),
                                                               ('type_follow','=','listen'),
                                                               ('state','!=','draft')])
        records = []
        val_state = {'absent':        'غائب',
                     'absent_excuse': 'غائب بعذر',
                     'excuse':        'إستأذن'}
        
        val_epriod = {'subh':   'الصبح',
                      'zuhr':   'الظهر',
                      'aasr':   'العصر',
                      'magrib': 'المغرب',
                      'esha':   'العشاء'}

        for listen_plan_line in listen_plan_lines:
            mistake_lines = listen_plan_line.mistake_line_ids
            if mistake_lines:

                for indiscipline in mistake_lines[0].indiscipline_ids:
                    type_indiscipline = indiscipline.type_indiscipline
                    if type_indiscipline not in ['absent','absent_excuse','excuse']:
                        continue
                    
                    # date_indiscipline = indiscipline.date_indiscipline
                    date_indiscipline = datetime.strptime(indiscipline.date_indiscipline, '%Y-%m-%d').date()

                    if date_indiscipline <= date_to and date_indiscipline >= date_from:                                            
                        records += [{'date':   date_indiscipline,
                                     'status': val_state.get(type_indiscipline),}]

            # date_listen = listen_plan_line.actual_date
            date_listen = datetime.strptime(listen_plan_line.actual_date, '%Y-%m-%d').date()

            if listen_plan_line.state == 'done' and date_listen <= date_to and date_listen >= date_from:
                records += [{'date':   date_listen,
                             'status': 'اكتمل'}]

        link = plan.link_id
        episode = link.episode_id

        form = {'date_from': date_from, 
                'date_to':   date_to,                                
                 
                'student':   link.student_id.display_name,
                'episode':   episode.parent_episode.name,
                'period':    val_epriod.get(episode.selected_period, ''),
                 
                'lines':     records}

        datas = {'model': 'attendance.certificate',
                 'ids':   [],
                 'form':  form}

        return datas        
    
    def get_pdf(self, link_id, date_from, date_to):
        return self.env.ref('mk_student_managment.attendance_certificate').render_qweb_pdf(self.ids, data=self.get_data_report(link_id, date_from, date_to))

    def get_pdf2(self, student_id, date_from, date_to):
        #get episode name
        episode_name = ''
        episode_obj = self.env['mk.episode']
#         episode_ids = episode_obj.search([('id','=',int(episode_id))])
#         if episode_ids:
#             episode_name = episode_ids[0].name
            
        #get purphase name
        pu_obj = self.env['mk.report.purphose']
        #pu_ids = pu_obj.search([('id','=',int(purphase))])
        pu_name = ''
        #if pu_ids:
            #pu_name = pu_ids[0].name
            
        #get student_name
        student_name = ''
        student_obj = self.env['mk.link']
        st_ids = student_obj.search([('id','=',int(student_id))])
        if st_ids:
            student_name = st_ids[0].student_id.display_name


        days = []
        date_format = "%Y-%m-%d"
        distance = datetime.strptime(date_to, date_format) - datetime.strptime(date_from, date_format)
        number_of_days = distance.days
        days.append({'date':(str(date_to)),'status':'done'}) 
        
        for x in range(0, number_of_days):
            next_date = datetime.strptime(date_from,"%Y-%m-%d")+timedelta(days=x)
            d = str(next_date)
            days.append({'date':(d[:-9]),'status':'done'})
            
        data = {'__last_update': '2017-08-29 07:01:35',
              
                'write_date':    '2017-08-29 07:01:35',
                'write_uid':     (1, 'Administrator'), 
              
                'create_date':   '2017-08-29 07:01:35',
                'create_uid':    (1, 'Administrator'), 
              
                'id':            self.id,
                'title':         (3, pu_name),
                              
                'episode':       episode_name,               
                'student':       student_name,
                'period':        'period',
                
                'date_from':     date_from, 
                'date_to':       date_to,
                'lines':  days}            

        datas = {'model': 'attendance.certificate',
                 'ids':   [],
                 'form':  data,}

        pdf = self.env.ref('mk_student_managment.attendance_certificate').render_qweb_pdf(self.ids, data=datas)
        return pdf
    