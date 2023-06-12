#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

    
class HrDepartment(models.Model):
    _inherit = 'hr.department'
        
    name             = fields.Char('Department Name', required=True, track_visibility='onchange')
    mosque_ids       = fields.One2many('mk.mosque', 'center_department_id', string='mosques')
    level_type       = fields.Selection([('gm','General Management'),
                                         ('m','Management'),
                                         ('d','Department'),
                                         ('c','Center')], string='Level Type', required=False, track_visibility='onchange')
    latitude         = fields.Char(string='Latitude', default=0, track_visibility='onchange')
    longitude        = fields.Char(string='Longitude',default=0, track_visibility='onchange')
    signature        = fields.Binary("Signature", attachment=True, track_visibility='onchange')
    signature_name   = fields.Char("Signature", track_visibility='onchange')
    test_center_admin= fields.Char("Test center admin", track_visibility='onchange')
    city_id          = fields.Many2one('res.country.state', string='City', domain=[('type_location','=','city'),
                                                                                   ('enable','=',True)], track_visibility='onchange')
    area_id          = fields.Many2one('res.country.state', string='Area', domain=[('type_location','=','area'),
                                                                                   ('enable','=',True)], track_visibility='onchange')
    district_id      = fields.Many2one('res.country.state', string='District', domain=[('type_location','=','district'),
                                                                                       ('enable','=',True)], track_visibility='onchange')
    code             = fields.Char('Code', size=50, track_visibility='onchange')
    active           = fields.Boolean('Active', default=True, track_visibility='onchange')
    gateway_config   = fields.Many2one('mk.smsclient.config', string='gateway config', track_visibility='onchange')
    gateway_user     = fields.Char('Gateway user', size=50, track_visibility='onchange')
    gateway_password = fields.Char('Gateway password',size=50, track_visibility='onchange')
    gateway_sender   = fields.Char('Gateway sender',size=50, track_visibility='onchange')
    send_time        = fields.Float('Send time', default=0.0, digits=(16, 2), track_visibility='onchange')
    male_managers    = fields.One2many('hr.employee', 'department_id', string='assitens', domain=[('center_admin_category','=','male')])
    female_managers  = fields.One2many('hr.employee', 'department_id', string='assitens', domain=[('center_admin_category','=','female')])
    phone_number     = fields.Char('رقم المركز', track_visibility='onchange')

    _sql_constraints = [('name_uniq', 'unique (name)', "هذا السجل موجود مسبقا!"),]

    @api.model
    def get_departments(self):
        query_string = ''' 
            select id, name
            from hr_department
            where active=True order by id;
            '''
        self.env.cr.execute(query_string)
        departments = self.env.cr.dictfetchall()
        return departments

    @api.model
    def centers_district_mosque(self, district_id):
        try:
            district_id = int(district_id)
        except:
            pass

        query_string = ''' 
                    SELECT d.id, d.name
                    FROM hr_department d left join res_country_state s ON s.center_department_id=d.id
                    WHERE d.active=True and s.id={} 
                    union 
                    SELECT d.id, d.name
                    FROM hr_department d left join hr_department_res_country_state_rel r ON r.hr_department_id=d.id
                    WHERE d.active=True and r.res_country_state_id={}
                    '''.format(district_id, district_id)

        self.env.cr.execute(query_string)
        centers = self.env.cr.dictfetchall()
        return centers

    @api.model
    def get_dashboard_supervisor(self, department_id, type_mosque, mosque_id, supervisor_id):
        try:
            department_id = int(department_id)
            type_mosque = type_mosque
            mosque_id = int(mosque_id)
            supervisor_id = int(supervisor_id)
        except:
            pass

        if type_mosque not in ["male", "female"]:
            type_mosque = False

        sub_query_mosque = " "
        sub_query_edu_supervisor = " "
        sub_query_department = " "

        if mosque_id:
            sub_query_mosque = " AND m.id=%s " % (mosque_id)
            sub_query_department = " AND d.id=%s " % (department_id)

        elif supervisor_id:
            sub_query_edu_supervisor = " LEFT JOIN hr_employee_mk_mosque_rel m_edu_sup ON m.id=m_edu_sup.mk_mosque_id "
            sub_query_mosque += " AND m.center_department_id=%s AND m.gender_mosque='%s' AND m_edu_sup.hr_employee_id=%s " % (
            department_id,
            type_mosque, supervisor_id)
            sub_query_department += " AND d.id=%s " % (department_id)

        elif type_mosque:
            sub_query_mosque = " AND m.center_department_id=%s AND m.gender_mosque='%s' " % (department_id, type_mosque)
            sub_query_department = " AND d.id=%s " % (department_id)

        elif department_id:
            sub_query_mosque = " AND m.center_department_id=%s " % (department_id)
            sub_query_department = " AND d.id=%s " % (department_id)

        query_string = """SELECT COALESCE(dep.dep_id, 0) centers,
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
                                      m.active=True %s) episode_update;""" % ( sub_query_department, sub_query_department,
                                                                                sub_query_edu_supervisor, sub_query_mosque,
                                                                                sub_query_edu_supervisor, sub_query_mosque,
                                                                                sub_query_edu_supervisor, sub_query_mosque,
                                                                                sub_query_edu_supervisor, sub_query_mosque,
                                                                                sub_query_edu_supervisor, sub_query_mosque,
                                                                                sub_query_edu_supervisor, sub_query_mosque,
                                                                                sub_query_edu_supervisor, sub_query_mosque,
                                                                                sub_query_edu_supervisor, sub_query_mosque,
                                                                                sub_query_edu_supervisor, sub_query_mosque,
                                                                                sub_query_edu_supervisor, sub_query_mosque,
                                                                                sub_query_edu_supervisor, sub_query_mosque,
                                                                                sub_query_edu_supervisor, sub_query_mosque,
                                                                                sub_query_edu_supervisor, sub_query_mosque,
                                                                                sub_query_edu_supervisor, sub_query_mosque)
        self.env.cr.execute(query_string)
        counters_supervisor = self.env.cr.dictfetchall()
        return counters_supervisor

    # @api.multi
    def write(self, vals):
        user = self.env.user
        if 'active' in vals and vals.get('active') == False and user.id != self.env.ref('base.user_root').id:
            if user.id != self.env.ref('base.user_root').id:
                raise ValidationError('عذرا لا يمكنك أرشفة المركز ')
        return super(HrDepartment, self).write(vals)

    # @api.one
    def unlink(self):
        user = self.env.user
        if user.id != self.env.ref('base.user_root').id:
            raise ValidationError ('لا يمكنك حذف المركز')
        return super(HrDepartment, self).unlink()


