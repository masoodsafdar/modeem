#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class TestCenterTimetable(models.Model):
    _name = 'center.time.table'
    _inherit=['mail.thread','mail.activity.mixin']
    
    @api.multi
    def name_get(self):        
        result = []
        arabic_days = {'Friday':    'الجمعة',
                       'Saturday':  'السبت',
                       'Sunday':    'الأحد',
                       'Monday':    'الاثنين',
                       'Tuesday':   'الثلاثاء',
                       'Wednesday': 'الاربعاء',
                       'Thursday':  'الخميس',
                       'False':     ' '}
        
        for record in self:
            result.append((record.id, "%s  %s / %s" % (arabic_days[record.day], record.date,record.period_id.name)))

        return result    

    @api.one
    @api.depends('center_id')
    def get_commite_no(self):
        self.committee_no = len(self.center_id.committee_test_ids)    
            
    @api.one
    @api.depends('total_minutes','used_minites')
    def get_available_minutes(self):
        self.avalible_minutes = max((self.total_minutes - self.used_minites), 0)

    @api.one
    @api.depends('center_id')
    def cheack_user_logged_in(self):
        visible_for_user = True

        if self.env.user.has_group('maknon_tests.read_tests_time_tables') and not self.env.user.has_group('maknon_tests.group_Student_tests_full'):
            center = self.sudo().center_id.center_id

            if center.main_company:
                visible_for_user = False
                
            elif center.center_id.id in [self.env.user.department_id.id] or center.center_id.id in self.env.user.department_ids.ids: 
                visible_for_user = True
                
            elif self.create_date:
                visible_for_user = False
        
        self.visible_for_user = visible_for_user
    
    @api.one
    @api.depends('center_id')
    def get_gender(self):
        self.gender = self.center_id.center_id.gender

    @api.one
    @api.depends('center_id')
    def get_total_minutes(self):
        self.total_minutes = (self.total_hours*60) * len(self.center_id.committee_test_ids)
            
    @api.one
    @api.depends('total_minutes','list_of_examiners')
    def get_used_minutes(self):
        used_min = 0
        for lin in self.list_of_examiners:
            if lin.state != 'cancel':
                used_min = used_min + (lin.branch.duration)
                
        self.used_minites = used_min    

    center_name       = fields.Char("center name")
    center_id         = fields.Many2one("mk.test.center.prepration", string="Test center", tracking=True)
    date              = fields.Date("Date", help="Date within center tests duration",      tracking=True)
    day               = fields.Selection([('Friday',    'Friday'),
                                          ('Saturday',  'Saturday'),
                                          ('Sunday',    'Sunday'),
                                          ('Monday',    'Monday'),
                                          ('Tuesday',   'Tuesday'),
                                          ('Wednesday', 'Wednesday'),
                                          ('Thursday',  'Thursday')], string="Day",    help="Days available at center",                      tracking=True)
    period_id         = fields.Many2one("test.period",                string="period", help="select period from avalible periods at center", tracking=True)
    total_hours       = fields.Integer("total hours",  related='period_id.total_hours')
    full              = fields.Boolean("full", readonly=True)    
    active            = fields.Boolean("active", default=True, tracking=True)
    gender            = fields.Selection([('male','رجالي'),
                                          ('female','نسائي')], string="center gender", compute='get_gender')
    total_minutes     = fields.Integer("capacity/minutes",  compute='get_total_minutes')
    used_minites      = fields.Integer("remaining minutes", compute='get_used_minutes')
    avalible_minutes  = fields.Integer("remaining minutes", compute='get_available_minutes')
    committee_no      = fields.Integer("committee No.",     compute='get_commite_no')
    visible_for_user  = fields.Boolean("show",              compute='cheack_user_logged_in', default=True)    
    list_of_examiners = fields.One2many("student.test.session",  "test_time",       string="List of Examiners")
    teacher_test_ids  = fields.One2many("employee.test.session", "test_session_id", string="قائمة الممتحنين")
    type_center       = fields.Selection([('student', 'Student'),
                                          ('teacher', 'Teacher')], string="Type", default='student', tracking=True)
    study_class_id    = fields.Many2one('mk.study.class',          string="Study class",              compute='get_study_class_id', store=True)
    academic_id       = fields.Many2one('mk.study.year',  string='Academic Year', ondelete='restrict', compute='get_study_class_id', store=True)


    @api.one
    @api.depends('center_id')
    def get_study_class_id(self):
        self.study_class_id = self.center_id.study_class_id.id
        self.academic_id = self.center_id.academic_id.id

    @api.one
    def write(self, vals):
        if 'active' in vals:
            if vals['active'] == False and self.visible_for_user == False:
                raise ValidationError(_('عذرا ! لايمكنك ارشفة '+' '+str(self.sudo().center_id.center_id.display_name)))
            
            elif vals['active'] == True and self.visible_for_user == False:
                raise ValidationError(_('عذرا لايمكنك الغاء ارشفة '+' '+str(self.sudo().center_id.center_id.display_name)))

        return super(TestCenterTimetable, self).write(vals)    
    
    @api.one
    def unlink(self):
        if not self.visible_for_user:
            raise ValidationError(_('عفوا , لاتمتلك صلاحية حذف مركز مستهدف'))

        return super(TestCenterTimetable, self).unlink()

    @api.model
    def calendar_center(self, gender, center_id, episode_id, period_id, user_id):
        gender = gender
        try:
            center_id = int(center_id)
            episode_id = int(episode_id)
            period_id = int(period_id)
            user_id = int(user_id)
        except:
            pass

        query = ''' SELECT Distinct center_time_table.id id,
                    mk_test_center_prepration.name as center_name, 
                    mk_test_center_prepration.id as center_id,
                    mk_test_center_prepration.place_options, 
                    center_time_table.date,
                    center_time_table.day,
                    test_period.name

                    FROM center_time_table
                    left join test_period on center_time_table.period_id=test_period.id
                    left join mk_test_center_prepration on center_time_table.center_id=mk_test_center_prepration.id
                    left join mak_test_center on mk_test_center_prepration.center_id=mak_test_center.id
                    left join hr_department on mak_test_center.center_id=hr_department.id '''

        if episode_id > 0 and not center_id:
            query += '''left join mk_mosque on mk_mosque.center_department_id=hr_department.id
                        left join mk_episode on mk_episode.mosque_id=mk_mosque.id '''

        query += '''WHERE center_time_table.active = True AND
                            center_time_table.date >= current_date AND
                            center_time_table.type_center='student' AND
                            mak_test_center.gender = '{}' '''.format(gender)

        if period_id > 0:
            query += " AND center_time_table.period_id = {} ".format(period_id)

        if center_id > 0:
            query += " AND mk_test_center_prepration.id = {} ".format(center_id)

        elif episode_id > 0:
            query += " AND mk_episode.id = {} ".format(episode_id)
        else:
            query += '''
                 AND mk_test_center_prepration.id IN (SELECT test_center.id

                FROM
                (SELECT distinct mk_test_center_prepration.id

                FROM mk_test_center_prepration
                LEFT JOIN center_time_table ON center_time_table.center_id=mk_test_center_prepration.id
                LEFT JOIN mak_test_center ON mk_test_center_prepration.center_id=mak_test_center.id
                LEFT JOIN hr_department ON mak_test_center.center_id=hr_department.id 

                WHERE center_time_table.active = True AND
                center_time_table.type_center='student' AND
                center_time_table.date >= current_date AND
                mak_test_center.gender = '{}' AND
                hr_department.id IN (SELECT res_users.department_id 
                FROM res_users 
                WHERE res_users.id={}

                UNION

                SELECT hr_department_res_users_rel.hr_department_id 
                FROM hr_department_res_users_rel 
                WHERE res_users_id={}

                UNION

                SELECT hr_department.id
                FROM hr_department
                LEFT JOIN mk_mosque ON mk_mosque.center_department_id=hr_department.id
                LEFT JOIN mk_mosque_res_users_rel ON mk_mosque_res_users_rel.mk_mosque_id=mk_mosque.id
                WHERE mk_mosque_res_users_rel.res_users_id={})

                UNION

                SELECT distinct mk_test_center_prepration.id

                FROM mk_test_center_prepration
                LEFT JOIN center_time_table ON center_time_table.center_id=mk_test_center_prepration.id
                LEFT JOIN mak_test_center ON mk_test_center_prepration.center_id=mak_test_center.id
                LEFT JOIN hr_department ON mak_test_center.center_id=hr_department.id 

                WHERE center_time_table.active = True AND
                center_time_table.type_center='student' AND
                center_time_table.date >= current_date AND
                mak_test_center.gender = '{}'  AND
                mak_test_center.main_company=True) test_center)'''.format(gender, user_id, user_id, user_id, gender)

        self.env.cr.execute(query)
        calendar_center = self.env.cr.dictfetchall()
        return calendar_center

    @api.model
    def center_prepa_timetable(self, center_id, date):
        try:
            center_id = int(center_id)
            date = date
        except:
            pass

        query_string = ''' 
        SELECT DISTINCT test_period.name, center_time_table.id

        FROM center_time_table left join test_period on center_time_table.period_id = test_period.id

        WHERE center_time_table.center_id = {}
        AND center_time_table.date = '{}';
        '''.format(center_id,date)

        self.env.cr.execute(query_string)
        center_prepa_timetable = self.env.cr.dictfetchall()
        return center_prepa_timetable

    @api.model
    def test_calendar(self, gender):

        query_string = ''' 

        SELECT center_time_table.id id,
        mak_test_center.name as center_name, 
        mk_test_center_prepration.id as center_id,
        mk_test_center_prepration.place_options, 
        center_time_table.date,
        test_period.name

        FROM center_time_table
        left join test_period on center_time_table.period_id=test_period.id
        left join mk_test_center_prepration on 
        center_time_table.center_id=mk_test_center_prepration.id
        left join mak_test_center on 
        mk_test_center_prepration.center_id=mak_test_center.id

        WHERE center_time_table.active = True AND
        center_time_table.date >= current_date AND
        mak_test_center.gender = '{}';
        '''.format(gender)

        self.env.cr.execute(query_string)
        test_calendar = self.env.cr.dictfetchall()
        return test_calendar

