#-*- coding:utf-8 -*-
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class Mkepisode(models.Model):
    _inherit = "mk.episode"
    
    students_list = fields.One2many("mk.link", "episode_id", "students list", domain=[('state','=','accept')])

    # @api.multi
    def action_assign_student_from_episode(self):
        assign_episode_form = self.env.ref('mk_student_register.view_student_request_multi_form')
        vals = {
            'name': _('تنسيب لحلقة'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mk.student.internal_transfer',
            'views': [(assign_episode_form.id, 'form')],
            'view_id': assign_episode_form.id,
            'target': 'new',
            'context': {'default_episode_assign_id': self.id,
                        'default_type_order': 'assign_ep',
                        'default_program_id': self.program_id.id,
                        'default_approach_id': self.approache_id.id,
                        'episode_gender': self.women_or_men,
                        }
        }
        if not self.is_online:
            vals.update({'domain': [('is_online_student', '=', False),
                                     ('is_student_meqraa', '=', False),
                                      '|',('mosq_id', '=', self.mosque_id.id),
                                          ('mosq_id', '=', False)]})
        return vals

    # @api.multi
    def action_assign_students_course_from_episode_multi(self):
        assign_episode_form = self.env.ref('mk_student_register.view_student_request_multi_form')
        episode_id = self.env['mk.episode'].browse(self.env.context.get('active_id'))
        vals = {
            'name': _('تنسيب لحلقة'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mk.student.internal_transfer',
            'views': [(assign_episode_form.id, 'form')],
            'view_id': assign_episode_form.id,
            'target': 'new',
            'context': {'default_episode_assign_id': episode_id.id,
                        'default_type_order': 'assign_ep'}
        }
        if episode_id.is_online:
            online_student_ids = self.env['mk.student.register'].search([('is_online_student', '=', True),
                                                                         ('is_student_meqraa', '=', False),
                                                                         '|', ('mosq_id', '=', episode_id.mosque_id.id),
                                                                              ('mosq_id', '=', False)]).ids
            vals.update({'domain': [('id', 'in', online_student_ids)]})
        return vals

    # @api.multi
    def open_view_listen_lines(self):
        tree_view = self.env.ref('mk_student_managment.mk_listen_line_tree_view_episode')
        search_id = self.env.ref('mk_student_managment.mk_listenline_search_view')
        return {'name':       "تسميع الطلاب" ,
                'res_model': 'mk.listen.line',
                'res_id':     self.id,
                'views':     [(tree_view.id, 'tree'),(False, 'form')],
                'type':      'ir.actions.act_window',
                'target':    'current',
                'context': {'default_episode': self.id},
                'domain':    [('episode','=',self.id)],
                'search_view_id': search_id.id}

    # @api.multi
    def open_view_presence_lines(self):
        tree_view = self.env.ref('mk_student_managment.student_prepare_presence_tree_view_episode')
        form_view = self.env.ref('mk_student_managment.student_prepare_presence_form_view')
        search_id = self.env.ref('mk_student_managment.student_prepare_presence_search_view')
        return {'name':       "حضور الطلاب",
                'res_model': 'mk.student.prepare.presence',
                'res_id':     self.id,
                'views':     [(tree_view.id, 'tree')],
                'type':      'ir.actions.act_window',
                'target':    'current',
                'context':    {'default_episode_id': self.id},
                'domain':    [('episode_id','=',self.id)],
                'search_view_id': search_id.id}

class Mkmosque(models.Model):
    _inherit = "mk.mosque"
    
    @api.depends('episode_id.students_list','episode_id.students_list.state')
    def calculate_students(self):
        for rec in self:
            res = []
            episode_ids = self.env['mk.episode'].search([('mosque_id', '=', rec.id), 
                                                         ('state', '=', 'accept')])
            
            for episode in episode_ids:
                res = res + episode.students_list.ids
            
            rec.students_no= len(res)
            
    @api.depends('student_ids','student_ids.request_state')
    def get_student(self):
        for rec in self:
            rec.student_number = len(rec.student_ids)
    
    student_ids    = fields.One2many('mk.student.register', 'mosq_id', string="Students", domain=[('request_state','=','accept')])
    student_number = fields.Integer(compute=get_student)    
    students_no    = fields.Integer('Students no', default=0, compute=calculate_students)
    first_student  = fields.Many2one('mk.student.register', string="الطالب الأول",   ondelete='cascade')
    second_student = fields.Many2one('mk.student.register', string="الطالب الثاني", ondelete='cascade')
    third_student  = fields.Many2one('mk.student.register', string="الطالب الثالث", ondelete='cascade')
    fourth_student = fields.Many2one('mk.student.register', string="الطالب الرابع", ondelete='cascade')
    is_send_to_mosque_admin = fields.Boolean('ارسال البريد الى المدير/المديرة', default=False)

    
    @api.model
    def get_counters_supervisor(self, department_id, type_mosque, mosque_id, supervisor_id):
        sub_query_mosque = " "
        sub_query_edu_supervisor = " "
        sub_query_department = " "

        if mosque_id:
            sub_query_mosque = " AND m.id=%s " % (mosque_id)
            sub_query_department = " AND d.id=%s " % (department_id) 
            
        elif supervisor_id:
            sub_query_edu_supervisor = " LEFT JOIN hr_employee_mk_mosque_rel m_edu_sup ON m.id=m_edu_sup.mk_mosque_id "            
            sub_query_mosque += " AND m.center_department_id=%s AND m.gender_mosque='%s' AND m_edu_sup.hr_employee_id=%s " % (department_id, type_mosque, supervisor_id)                
            sub_query_department += " AND d.id=%s " % (department_id)
            
        elif type_mosque:                                    
            sub_query_mosque = " AND m.center_department_id=%s AND m.gender_mosque='%s' " % (department_id, type_mosque)
            sub_query_department = " AND d.id=%s " % (department_id) 
            
        elif department_id:                                    
            sub_query_mosque = " AND m.center_department_id=%s " % (department_id)
            sub_query_department = " AND d.id=%s " % (department_id)

        query = """SELECT COALESCE(dep.dep_id, 0) centers,
                          COALESCE(teacher.teacher_id, 0) teachers, 
                          COALESCE(supervisor.supervisor_id, 0) supervisors, 
                          COALESCE(edu_supervisor.edu_supervisor_id, 0) edu_supervisors, 
                          COALESCE(admin_emp.admin_emp_id, 0) admin_emps, 
                          COALESCE(student.student_id, 0) students, 
                          COALESCE(mosque.mosque_id, 0) masjeds, 
                          COALESCE(episode.episode_id, 0) episodes,
                          
                          COALESCE(dep_update.dep_id, 0) centers_updated, 
                          to_char(dep_update.date_update, 'YYYY-MM-DD HH24:MI') centers_updated_last,
                          
                          COALESCE(teacher_update.teacher_id, 0) teachers_updated, 
                          to_char(teacher_update.date_update, 'YYYY-MM-DD HH24:MI') teachers_updated_last,
                          
                          COALESCE(supervisor_update.supervisor_id, 0) supervisors_updated, 
                          to_char(supervisor_update.date_update, 'YYYY-MM-DD HH24:MI') supervisors_updated_last,
                          
                          COALESCE(edu_supervisor_update.edu_supervisor_id, 0) edu_supervisors_updated, 
                          to_char(edu_supervisor_update.date_update, 'YYYY-MM-DD HH24:MI') edu_supervisors_updated_last,
                          
                          COALESCE(admin_emp_update.admin_emp_id, 0) admin_emps_updated, 
                          to_char(admin_emp_update.date_update, 'YYYY-MM-DD HH24:MI') admin_emps_updated_last,

                          COALESCE(student_update.student_id, 0) students_updated, 
                          to_char(student_update.date_update, 'YYYY-MM-DD HH24:MI') students_updated_last,
                          
                          COALESCE(mosque_update.mosque_id, 0) masjeds_updated, 
                          to_char(mosque_update.date_update, 'YYYY-MM-DD HH24:MI') masjeds_updated_last,
                          
                          COALESCE(episode_update.episode_id, 0) episodes_updated, 
                          to_char(episode_update.date_update, 'YYYY-MM-DD HH24:MI') episodes_updated_last 

                   FROM (SELECT count(d.id) dep_id
                         FROM hr_department d 
                         WHERE d.active=True %s) dep,
                         
                        (SELECT count(d.id) dep_id, max(d.write_date) date_update
                         FROM hr_department d 
                         WHERE d.active=True %s) dep_update,                             

                        (SELECT count(distinct(e.id)) teacher_id
                         FROM hr_employee e 
                              LEFT JOIN mosque_relation mr ON e.id=mr.mosq_id
                              LEFT JOIN mk_mosque m ON m.id=mr.emp_id %s                                                                                          
                         WHERE e.category='teacher' AND
                               e.active=True AND
                               m.active=True %s) teacher,
                               
                        (SELECT count(distinct(e.id)) supervisor_id
                         FROM hr_employee e 
                              LEFT JOIN mosque_relation mr ON e.id=mr.mosq_id
                              LEFT JOIN mk_mosque m ON m.id=mr.emp_id  %s 
                         WHERE e.category IN ('admin','supervisor') AND
                               e.active=True AND
                               m.active=True %s) supervisor,
                               
                        (SELECT count(distinct(e.id)) edu_supervisor_id
                         FROM hr_employee e 
                              LEFT JOIN hr_employee_mk_mosque_rel mr ON e.id=mr.hr_employee_id
                              LEFT JOIN mk_mosque m ON m.id=mr.mk_mosque_id %s 
                         WHERE e.category='edu_supervisor' AND
                               e.active=True AND
                               m.active=True %s) edu_supervisor,
                               
                        (SELECT count(distinct(e.id)) admin_emp_id
                         FROM hr_employee e 
                              LEFT JOIN mosque_relation mr ON e.id=mr.mosq_id
                              LEFT JOIN mk_mosque m ON m.id=mr.emp_id %s 
                         WHERE e.category='managment' AND
                               e.active=True AND
                               m.active=True %s) admin_emp,
                               
                        (SELECT count(distinct(s.id)) student_id
                         FROM mk_student_register s
                              LEFT JOIN mk_mosque m ON s.mosq_id=m.id %s 
                         WHERE s.active=True AND
                               s.request_state <> 'reject' AND
                               m.active=True %s) student,
                               
                        (SELECT count(distinct(m.id)) mosque_id
                         FROM mk_mosque m %s 
                         WHERE m.active=True %s) mosque,
                               
                        (SELECT count(distinct(e.id)) episode_id
                         FROM mk_episode e
                              LEFT JOIN mk_mosque m ON e.mosque_id=m.id %s   
                         WHERE e.active=True AND
                               m.active=True %s) episode,
                                                             
                        (SELECT count(distinct(e.id)) teacher_id, max(e.write_date) date_update
                         FROM hr_employee e 
                              LEFT JOIN mosque_relation mr ON e.id=mr.mosq_id
                              LEFT JOIN mk_mosque m ON m.id=mr.emp_id %s 
                         WHERE e.create_date <> e.write_date AND
                               e.category='teacher' AND
                               e.active=True AND
                               m.active=True %s) teacher_update,
                               
                        (SELECT count(distinct(e.id)) supervisor_id, max(e.write_date) date_update
                         FROM hr_employee e 
                              LEFT JOIN mosque_relation mr ON e.id=mr.mosq_id
                              LEFT JOIN mk_mosque m ON m.id=mr.emp_id %s 
                         WHERE e.create_date <> e.write_date AND
                               e.category IN ('admin','supervisor') AND
                               e.active=True AND
                               m.active=True %s) supervisor_update,
                               
                        (SELECT count(distinct(e.id)) edu_supervisor_id, max(e.write_date) date_update
                         FROM hr_employee e 
                              LEFT JOIN hr_employee_mk_mosque_rel mr ON e.id=mr.hr_employee_id
                              LEFT JOIN mk_mosque m ON m.id=mr.mk_mosque_id %s 
                         WHERE e.create_date <> e.write_date AND
                               e.category='edu_supervisor' AND
                               e.active=True AND
                               m.active=True %s) edu_supervisor_update,
                               
                        (SELECT count(distinct(e.id)) admin_emp_id, max(e.write_date) date_update
                         FROM hr_employee e 
                              LEFT JOIN mosque_relation mr ON e.id=mr.mosq_id
                              LEFT JOIN mk_mosque m ON m.id=mr.emp_id %s 
                         WHERE e.create_date <> e.write_date AND
                               e.category='managment' AND
                               e.active=True AND
                               m.active=True %s) admin_emp_update,
                               
                        (SELECT count(distinct(s.id)) student_id, max(s.write_date) date_update
                         FROM mk_student_register s
                              LEFT JOIN mk_mosque m ON s.mosq_id=m.id %s 
                         WHERE s.create_date <> s.write_date AND
                               s.active=True AND
                               s.request_state <> 'reject' AND
                               m.active=True %s) student_update,
                               
                        (SELECT count(distinct(m.id)) mosque_id, max(m.write_date) date_update
                         FROM mk_mosque m %s 
                         WHERE m.create_date <> m.write_date AND
                               m.active=True %s) mosque_update,
                               
                        (SELECT count(distinct(e.id)) episode_id, max(e.write_date) date_update
                         FROM mk_episode e 
                              LEFT JOIN mk_mosque m ON e.mosque_id=m.id %s   
                         WHERE e.create_date <> e.write_date AND
                               e.active=True AND
                               m.active=True %s) episode_update;"""%(sub_query_department, sub_query_department, sub_query_edu_supervisor, sub_query_mosque,                                                                      
                                                                     sub_query_edu_supervisor, sub_query_mosque, sub_query_edu_supervisor, sub_query_mosque,                                                                      
                                                                     sub_query_edu_supervisor, sub_query_mosque, sub_query_edu_supervisor, sub_query_mosque,                                                                      
                                                                     sub_query_edu_supervisor, sub_query_mosque, sub_query_edu_supervisor, sub_query_mosque,                                                                     
                                                                     sub_query_edu_supervisor, sub_query_mosque, sub_query_edu_supervisor, sub_query_mosque,                                                                      
                                                                     sub_query_edu_supervisor, sub_query_mosque, sub_query_edu_supervisor, sub_query_mosque,                                                                      
                                                                     sub_query_edu_supervisor, sub_query_mosque, sub_query_edu_supervisor, sub_query_mosque,                                                                      
                                                                     sub_query_edu_supervisor, sub_query_mosque)

        self._cr.execute(query)
        record_update = self._cr.dictfetchall()[0]
                
        values = [record_update]
#         [{'centers':         record_update.get('nbr_dep') or 0,
#                 
#                    'masjeds':         record_update.get('nbr_mosque') or 0,
#                    'episodes':        record_update.get('nbr_episode') or 0,
#                     
#                    'supervisors':     record_update.get('nbr_supervisor') or 0,
#                    'edu_supervisors': record_update.get('nbr_edu_supervisor') or 0,
#                    'admin_emps':      record_update.get('nbr_admin_emp') or 0,
#                    'teachers':        record_update.get('nbr_teacher') or 0,
#                     
#                    'students':        record_update.get('nbr_student') or 0,
#                                         
#                    'centers_updated':              record_update.get('nbr_dep_update') or 0,
#                    'centers_updated_last':         record_update.get('dep_last_update') or False,
#                     
#                    'masjeds_updated':              record_update.get('nbr_mosque_update') or 0,
#                    'masjeds_updated_last':         record_update.get('mosque_last_update') or False,
#                    'episodes_updated':             record_update.get('nbr_episode_update') or 0,
#                    'episodes_updated_last':        record_update.get('episode_last_update') or False,
#                     
#                    'supervisors_updated':          record_update.get('nbr_supervisor_update') or 0,
#                    'supervisors_updated_last':     record_update.get('supervisor_last_update') or False,
#                    'edu_supervisors_updated':      record_update.get('nbr_edu_supervisor_update') or 0,
#                    'edu_supervisors_updated_last': record_update.get('edu_supervisor_last_update') or False,
#                    'admin_emps_updated':           record_update.get('nbr_admin_emp_update') or 0,
#                    'admin_emps_updated_last':      record_update.get('admin_emp_last_update') or False,
#                    'teachers_updated':             record_update.get('nbr_teacher_update') or 0,
#                    'teachers_updated_last':        record_update.get('teacher_last_update') or False,
#                     
#                    'students_updated':             record_update.get('nbr_student_update') or 0,
#                    'students_updated_last':        record_update.get('student_last_update') or False,}]

        return values

    @api.model
    def get_educ_supervisors(self, department_id, type_mosque):
        domain = []
        
        sub_query_mosque = " "
        
        if department_id:
            domain = [('center_department_id','=',department_id)]
            
        if type_mosque:
            domain += [('categ_id.mosque_type','=',type_mosque)]
        
        edu_supervisors = []
        edu_supervisor_ids = []
        for mosque in self.env['mk.mosque'].search(domain):
            for edu_supervisor in mosque.edu_supervisor:
                edu_supervisor_id = edu_supervisor.id

                if edu_supervisor_id in edu_supervisor_ids:
                    continue

                edu_supervisor_ids += [edu_supervisor_id]
                edu_supervisors += [{'id':   edu_supervisor_id,
                                     'name': edu_supervisor.name}]
                
        if type_mosque:                                    
            sub_query_mosque = " AND m.center_department_id=%s AND m.gender_mosque='%s' " % (department_id, type_mosque)
            
        elif department_id:                                    
            sub_query_mosque = " AND m.center_department_id=%s " % (department_id)
                
        query = """SELECT distinct(e.id) id, e.name
                   FROM hr_employee e 
                        LEFT JOIN hr_employee_mk_mosque_rel mr ON e.id=mr.hr_employee_id
                        LEFT JOIN mk_mosque m ON m.id=mr.mk_mosque_id  
                   WHERE e.category='edu_supervisor' AND
                         e.active=True AND
                         m.active=True %s """ % (sub_query_mosque)
                         
        self._cr.execute(query)
        values = self._cr.dictfetchall()

        return values

    @api.model
    def get_mosques_supervisor(self, department_id, type_mosque, supervisor_id):
        domain = []
        
        sub_query_mosque = " "
        sub_query_edu_supervisor = " "
        
        if department_id:
            domain = [('center_department_id','=',department_id)]
            
        if type_mosque:
            domain += [('categ_id.mosque_type','=',type_mosque)]
            
        if supervisor_id:
            edu_supervisor = self.env['hr.employee'].search([('id','=',supervisor_id)], limit=1)
            mosque_ids = [mosque.id for mosque in edu_supervisor.mosque_sup]
            domain += [('id','in',mosque_ids)]
        
        mosques = []
        for mosque in self.env['mk.mosque'].search(domain):
            mosques += [{'id':   mosque.id,
                         'name': mosque.name}]
        
        if supervisor_id:
            sub_query_edu_supervisor = " LEFT JOIN hr_employee_mk_mosque_rel m_edu_sup ON m.id=m_edu_sup.mk_mosque_id "            
            sub_query_mosque = " AND m.center_department_id=%s AND m.gender_mosque='%s' AND m_edu_sup.hr_employee_id=%s " % (department_id, type_mosque, supervisor_id)                
            
        elif type_mosque:                                    
            sub_query_mosque = " AND m.center_department_id=%s AND m.gender_mosque='%s' " % (department_id, type_mosque)
            
        elif department_id:                                    
            sub_query_mosque = " AND m.center_department_id=%s " % (department_id)            
            
        query="""SELECT distinct m.id id, m.name
                 FROM   mk_mosque m %s 
                 WHERE  m.active=True %s""" % (sub_query_edu_supervisor, sub_query_mosque)

        self._cr.execute(query)
        values = self._cr.dictfetchall()

        return values
            
    @api.model
    def get_mosques_detail(self, department_id, type_mosque, mosque_id, supervisor_id):
        domain = []
        if department_id:
            domain = [('center_department_id','=',department_id)]
            
        if type_mosque:
            domain += [('categ_id.mosque_type','=',type_mosque)]
            
        if mosque_id:
            domain = [('id','=',mosque_id)]
            
        elif supervisor_id:
            edu_supervisor = self.env['hr.employee'].search([('id','=',supervisor_id)], limit=1)
            mosque_ids = [mosque.id for mosque in edu_supervisor.mosque_sup]
            domain += [('id','in',mosque_ids)]
                        
        mosques = []
        for mosque in self.env['mk.mosque'].search(domain):
            supervisors = []
            admin_emps_update = []            
            teachers_update = []            
            teachers = []
            
            students = []
            episodes = []
                
            supervisors_update = []
            edu_supervisors_update = []
            admin_emps_update = []            
            teachers_update = []
            
            students_update = []
            episodes_update = []            
            
            name_mosque = mosque.name or " "
            episode_value = mosque.episode_value
    
            if episode_value == 'ev':
                name_mosque += ' ' + '[' + ' ' + 'مسائية' + ' ' + ']'
    
            elif episode_value == 'mo':
                name_mosque += ' ' + '[' + ' ' + 'صباحية' + ' ' + ']'            
            
            nbr_mosques_update = 0
            if mosque.create_date != mosque.write_date:
                nbr_mosques_update = 1     
                
            teachers = mosque.teacher_ids
            for teacher in teachers:
                if teacher.create_date != teacher.write_date:
                    teachers_update += [teacher.write_date]
                            
            supervisors = mosque.supervisors
            for supervisor in supervisors:
                if supervisor.create_date != supervisor.write_date:
                    supervisors_update += [supervisor.write_date]
                    
            edu_supervisors = mosque.edu_supervisor
            for edu_supervisor in edu_supervisors:
                if edu_supervisor.create_date != edu_supervisor.write_date:
                    edu_supervisors_update += [edu_supervisor.write_date]
                    
            admin_emps = mosque.mosq_other_emp_ids
            for admin_emp in admin_emps:
                if admin_emp.create_date != admin_emp.write_date:
                    admin_emps_update += [admin_emp.write_date]                               
            
            episodes = self.env['mk.episode'].sudo().search([('mosque_id', '=', mosque.id)])
            for episode in episodes:
                if episode.create_date != episode.write_date:
                    episodes_update += [episode.write_date]
            
            students = mosque.student_ids
            for student in students:
                if student.create_date != student.write_date:
                    students_update += [student.write_date]                           
                    
            mosques += [{'mosque_is_write':       nbr_mosques_update,
                         'mosque_name':           name_mosque,
                         
                         'all_episodes':          len(episodes),
                         'write_episodes':        len(episodes_update),
                         
                         'all_supervisors':       len(supervisors),
                         'write_supervisors':     len(supervisors_update),
                         
                         'edu_supervisors':       len(edu_supervisors),
                         'write_edu_supervisors': len(edu_supervisors_update),
                        
                         'admin_emps':            len(admin_emps),
                         'write_admin_emps':      len(admin_emps_update),                         
                         
                         'all_teachers':          len(teachers),
                         'write_teachers':        len(teachers_update),
                         
                         'all_students':          len(students),
                         'write_students':        len(students_update),}]
        
        sub_query_mosque = " "
        sub_query_edu_supervisor = " "

        if mosque_id:
            sub_query_mosque = " AND m.id=%s " % (mosque_id)
            
        elif supervisor_id:
            sub_query_edu_supervisor = " LEFT JOIN hr_employee_mk_mosque_rel m_edu_sup ON m.id=m_edu_sup.mk_mosque_id "            
            sub_query_mosque += " AND m.center_department_id=%s AND m.gender_mosque='%s' AND m_edu_sup.hr_employee_id=%s " % (department_id, type_mosque, supervisor_id)                
            
        elif type_mosque:                                    
            sub_query_mosque = " AND m.center_department_id=%s AND m.gender_mosque='%s' " % (department_id, type_mosque)
            
        elif department_id:                                    
            sub_query_mosque = " AND m.center_department_id=%s " % (department_id)
             

#         query="""SELECT distinct(m.id) id, m.name
#                          FROM mk_mosque m %s 
#                          WHERE m.active=True %s""" % (sub_query_edu_supervisor, sub_query_mosque)
                         
        query = """SELECT mosque.mosque_name mosque_name, mosque.mosque_is_write,
                          
                          COALESCE(teacher.teacher_id, 0) all_teachers, COALESCE(teacher_update.teacher_id, 0) write_teachers, 
                          to_char(teacher_update.date_update, 'YYYY-MM-DD HH24:MI') teachers_updated_last, 
                          
                          COALESCE(supervisor.supervisor_id, 0) all_supervisors, COALESCE(supervisor_update.supervisor_id, 0) write_supervisors, 
                          to_char(supervisor_update.date_update, 'YYYY-MM-DD HH24:MI') supervisors_updated_last,
                           
                          COALESCE(edu_supervisor.edu_supervisor_id, 0) edu_supervisors, COALESCE(edu_supervisor_update.edu_supervisor_id, 0) write_edu_supervisors, 
                          to_char(edu_supervisor_update.date_update, 'YYYY-MM-DD HH24:MI') edu_supervisors_updated_last,
                           
                          COALESCE(admin_emp.admin_emp_id, 0) admin_emps, COALESCE(admin_emp_update.admin_emp_id, 0) write_admin_emps, 
                          to_char(admin_emp_update.date_update, 'YYYY-MM-DD HH24:MI') admin_emps_updated_last, 

                          COALESCE(student.student_id, 0) all_students, COALESCE(student_update.student_id, 0) write_students, 
                          to_char(student_update.date_update, 'YYYY-MM-DD HH24:MI') students_updated_last,
                           
                          COALESCE(episode.episode_id, 0) all_episodes, COALESCE(episode_update.episode_id, 0) write_episodes, 
                          to_char(episode_update.date_update, 'YYYY-MM-DD HH24:MI') episodes_updated_last  

                   FROM (SELECT distinct(m.id) mosque_id, 
                   
                                case when m.episode_value='ev' then m.name||' '||'['||' '||'مسائية'||' '||']'
                                     when m.episode_value='mo' then m.name||' '||'['||' '||'صباحية'||' '||']'
                                     else m.name end as mosque_name, 
                                      
                                case when m.create_date <> m.write_date then 1 else 0 end as mosque_is_write
                                
                         FROM mk_mosque m %s 
                         WHERE m.active=True %s) mosque 
                         
                        LEFT JOIN
                        
                        (SELECT m.id mosque_id, count(distinct(e.id)) teacher_id
                         FROM hr_employee e 
                              LEFT JOIN mosque_relation mr ON e.id=mr.mosq_id
                              LEFT JOIN mk_mosque m ON m.id=mr.emp_id %s                                                                                          
                         WHERE e.category='teacher' AND
                               e.active=True AND
                               m.active=True %s                        
                         GROUP BY m.id) teacher ON teacher.mosque_id=mosque.mosque_id
                         
                        LEFT JOIN
                               
                        (SELECT m.id mosque_id, count(distinct(e.id)) supervisor_id
                         FROM hr_employee e 
                              LEFT JOIN mosque_relation mr ON e.id=mr.mosq_id
                              LEFT JOIN mk_mosque m ON m.id=mr.emp_id  %s 
                         WHERE e.category IN ('admin','supervisor') AND
                               e.active=True AND
                               m.active=True %s 
                         GROUP BY m.id) supervisor ON supervisor.mosque_id=mosque.mosque_id
                         
                        LEFT JOIN
                               
                        (SELECT m.id mosque_id, count(distinct(e.id)) edu_supervisor_id
                         FROM hr_employee e 
                              LEFT JOIN hr_employee_mk_mosque_rel mr ON e.id=mr.hr_employee_id
                              LEFT JOIN mk_mosque m ON m.id=mr.mk_mosque_id %s 
                         WHERE e.category='edu_supervisor' AND
                               e.active=True AND
                               m.active=True %s
                         GROUP BY m.id) edu_supervisor ON edu_supervisor.mosque_id=mosque.mosque_id
                         
                        LEFT JOIN
                               
                        (SELECT m.id mosque_id, count(distinct(e.id)) admin_emp_id
                         FROM hr_employee e 
                              LEFT JOIN mosque_relation mr ON e.id=mr.mosq_id
                              LEFT JOIN mk_mosque m ON m.id=mr.emp_id %s 
                         WHERE e.category='managment' AND
                               e.active=True AND
                               m.active=True %s
                         GROUP BY m.id) admin_emp ON admin_emp.mosque_id=mosque.mosque_id
                         
                        LEFT JOIN
                               
                        (SELECT m.id mosque_id, count(distinct(s.id)) student_id
                         FROM mk_student_register s
                              LEFT JOIN mk_mosque m ON s.mosq_id=m.id %s 
                         WHERE s.active=True AND
                               s.request_state <> 'reject' AND
                               m.active=True %s 
                         GROUP BY m.id) student ON student.mosque_id=mosque.mosque_id
                         
                        LEFT JOIN
                               
                        (SELECT m.id mosque_id, count(distinct(e.id)) episode_id
                         FROM mk_episode e
                              LEFT JOIN mk_mosque m ON e.mosque_id=m.id %s   
                         WHERE e.active=True AND
                               m.active=True %s
                         GROUP BY m.id) episode ON episode.mosque_id=mosque.mosque_id
                         
                        LEFT JOIN
                                                             
                        (SELECT m.id mosque_id, count(distinct(e.id)) teacher_id, max(e.write_date) date_update
                         FROM hr_employee e 
                              LEFT JOIN mosque_relation mr ON e.id=mr.mosq_id
                              LEFT JOIN mk_mosque m ON m.id=mr.emp_id %s 
                         WHERE e.create_date <> e.write_date AND
                               e.category='teacher' AND
                               e.active=True AND
                               m.active=True %s
                         GROUP BY m.id) teacher_update ON teacher_update.mosque_id=mosque.mosque_id       
                        
                        LEFT JOIN
                                                             
                        (SELECT m.id mosque_id, count(distinct(e.id)) supervisor_id, max(e.write_date) date_update
                         FROM hr_employee e 
                              LEFT JOIN mosque_relation mr ON e.id=mr.mosq_id
                              LEFT JOIN mk_mosque m ON m.id=mr.emp_id %s 
                         WHERE e.create_date <> e.write_date AND
                               e.category IN ('admin','supervisor') AND
                               e.active=True AND
                               m.active=True %s
                         GROUP BY m.id) supervisor_update ON supervisor_update.mosque_id=mosque.mosque_id
                               
                        LEFT JOIN
                                                             
                        (SELECT m.id mosque_id, count(distinct(e.id)) edu_supervisor_id, max(e.write_date) date_update
                         FROM hr_employee e 
                              LEFT JOIN hr_employee_mk_mosque_rel mr ON e.id=mr.hr_employee_id
                              LEFT JOIN mk_mosque m ON m.id=mr.mk_mosque_id %s 
                         WHERE e.create_date <> e.write_date AND
                               e.category='edu_supervisor' AND
                               e.active=True AND
                               m.active=True %s
                         GROUP BY m.id) edu_supervisor_update ON edu_supervisor_update.mosque_id=mosque.mosque_id
                               
                        LEFT JOIN
                                                             
                        (SELECT m.id mosque_id, count(distinct(e.id)) admin_emp_id, max(e.write_date) date_update
                         FROM hr_employee e 
                              LEFT JOIN mosque_relation mr ON e.id=mr.mosq_id
                              LEFT JOIN mk_mosque m ON m.id=mr.emp_id %s 
                         WHERE e.create_date <> e.write_date AND
                               e.category='managment' AND
                               e.active=True AND
                               m.active=True %s
                         GROUP BY m.id) admin_emp_update ON admin_emp_update.mosque_id=mosque.mosque_id
                               
                        LEFT JOIN
                                                             
                        (SELECT m.id mosque_id, count(distinct(s.id)) student_id, max(s.write_date) date_update
                         FROM mk_student_register s
                              LEFT JOIN mk_mosque m ON s.mosq_id=m.id %s 
                         WHERE s.create_date <> s.write_date AND
                               s.active=True AND
                               s.request_state <> 'reject' AND
                               m.active=True %s
                         GROUP BY m.id) student_update ON student_update.mosque_id=mosque.mosque_id
                               
                        LEFT JOIN
                                                             
                        (SELECT m.id mosque_id, count(distinct(e.id)) episode_id, max(e.write_date) date_update
                         FROM mk_episode e 
                              LEFT JOIN mk_mosque m ON e.mosque_id=m.id %s   
                         WHERE e.create_date <> e.write_date AND
                               e.active=True AND
                               m.active=True %s
                         GROUP BY m.id) episode_update ON episode_update.mosque_id=mosque.mosque_id;"""%(sub_query_edu_supervisor, sub_query_mosque,                                                                      
                         sub_query_edu_supervisor, sub_query_mosque, sub_query_edu_supervisor, sub_query_mosque, sub_query_edu_supervisor, sub_query_mosque, 
                         sub_query_edu_supervisor, sub_query_mosque, sub_query_edu_supervisor, sub_query_mosque, sub_query_edu_supervisor, sub_query_mosque,                                                                     
                         sub_query_edu_supervisor, sub_query_mosque, sub_query_edu_supervisor, sub_query_mosque, sub_query_edu_supervisor, sub_query_mosque, 
                         sub_query_edu_supervisor, sub_query_mosque, sub_query_edu_supervisor, sub_query_mosque, sub_query_edu_supervisor, sub_query_mosque)                         
                         
        self._cr.execute(query)
        values = self._cr.dictfetchall()
        
        return values
