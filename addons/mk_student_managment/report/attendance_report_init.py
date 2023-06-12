# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class student_attendance(models.AbstractModel):
    _name = 'report.mk_student_managment.student_attendance_report_temp'
       
    def cheack_student_state(self, data, date):
        student = data['form']['student_id'][0]
        episode = data['form']['episode'][0]
        self.env.cr.execute("""
                SELECT mk_student_attendace.state as state, mk_episode_attendace.date as day
                
                FROM public.mk_episode_attendace, public.mk_student_attendace
                
                WHERE mk_student_attendace.episode_attendace_id = mk_episode_attendace.id and
                mk_episode_attendace.date=%s and
                mk_episode_attendace.episode=%s and
                mk_student_attendace.student=%s;
            
            """, (date, episode, student))
            
        res = self.env.cr.dictfetchall()
        
        return res

    @api.model
    def get_report_values(self, docids, data=None):        
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        
        atttendance_report = self.env['ir.actions.report']._get_report_from_name('mk_student_managme.student_attendance_report_temp')

        return {'doc_ids':   self.ids,
                'doc_model': atttendance_report.model,

                'student':   data['form']['student'],
                'episode':   data['form']['episode'],
                'period':    data['form']['period'],
                
                'date_from': data['form']['date_from'],
                'date_to':   data['form']['date_to'],
                
                'lines':   data['form']['lines']}

    def get_lines(self, data):
        # this function return list of dicts [{'date':,'state'}]
        records = []
        days = data['days']
        
        for day in days:
            attend_record = self.cheack_student_state(data, day)
            if len(attend_record) > 0:
                records.append(attend_record[0])
                
            else:
                records.append({'state': 'attended', 
                                'day':   day})
                
        return records
        #[{'day':x,'date':y},{'day':x,'date':y},{'day':x,'date':y}]
