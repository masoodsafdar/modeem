from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class TeacherTestSubscriptionrWizard(models.TransientModel):
    _name = 'teacher.test.subscription'

    @api.model
    def _defautl_study_class_id(self):
        default_study_class=self.env['mk.study.class'].search([('is_default','=',True)], limit=1)
        return default_study_class.id

    employee_id                = fields.Many2one('hr.employee',     string='الموظف')
    mosque_id                  = fields.Many2one('mk.mosque',       string='المسجد')
    episode_id                 = fields.Many2one('mk.episode',      string='الحلقة')
    study_class_id             = fields.Many2one('mk.study.class',  string='الفصل الدراسي', default=_defautl_study_class_id, readonly=True)
    study_year_id              = fields.Many2one(related='study_class_id.study_year_id',  string='Study Year')
    test_name_id               = fields.Many2one('mk.test.names',   string='نوع الاختبار')

    trackk                     = fields.Selection([('up',   'من الناس إلى الفاتحة'),
                                                   ('down', 'من الفاتحة إلى الناس')], string="المسار")
    branch_id                     = fields.Many2one("mk.branches.master", string="الفرع")
    test_center_id             = fields.Many2one('mak.test.center', string='مركز الاختبار')
    test_center_preparation_id = fields.Many2one('mk.test.center.prepration', string='اعدادات مركز الاختبار')
    test_period_id             = fields.Many2one('test.period', string='الفترة')
    day                        = fields.Selection([('Friday',    'Friday'),
                                                   ('Saturday',  'Saturday'),
                                                   ('Sunday',    'Sunday'),
                                                   ('Monday',    'Monday'),
                                                   ('Tuesday',   'Tuesday'),
                                                   ('Wednesday', 'Wednesday'),
                                                   ('Thursday',  'Thursday')], string="اليوم", help="Days available at center")
    avalible_teacher = fields.Many2many("hr.employee", string="available")
    total_minutes    = fields.Integer("total minutes")

    center_time_table_id       = fields.Many2one('center.time.table', string='جدول الاختبار')
    counter                    = fields.Integer("remaining minutes", compute='get_remaining')
    student_id                 = fields.One2many("select.students", "wi2", string="students")
    avalible_minutes           = fields.Integer(related="center_time_table_id.avalible_minutes",string="remaining minutes")
    employee_link_id           = fields.Many2one("mk.link",   string="student list")

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        domain =[]
        employee_id = self.employee_id
        category = employee_id.category2

        if category == 'center_admin':
            domain += ['|', ('center_department_id', '=', employee_id.department_id.id),
                            ('center_department_id', 'in', employee_id.department_ids.ids)]
        elif category == 'edu_supervisor':
            domain += [('id', 'in', employee_id.mosque_sup.ids)]
        elif category in ['admin', 'teacher', 'supervisor','others', 'bus_sup']:
            domain += [('id', 'in', employee_id.mosqtech_ids.ids)]
        return {'domain': {'mosque_id': domain}}

    @api.onchange('test_name_id','study_class_id')
    def onchange_test_name_id(self):
        employee_id = self.employee_id
        domain = [('study_class_id','=',self.study_class_id.id),
                  ('test_group','=','employee'),
                  ('gender','=',employee_id.gender),
                  ('test_names', 'in', [self.test_name_id.id])]
        category = employee_id.category2
        if category in ['center_admin', 'admin', 'teacher']:
            domain += ['|',('center_id', '=', employee_id.department_id.id),
                           ('center_id', '=', employee_id.department_ids.ids)]
        else:
            domain += [('center_id', '=', employee_id.department_id.id)]
        return {'domain': {'test_center_id': domain}}

    @api.depends('student_id')
    def get_remaining(self):
        self.counter = 0
        for rec in self.student_id:
            if rec.flag == True and rec.test_name:
                self.counter = self.counter + 1

    @api.multi
    def set_branch(self):
        # create student+link for student
        employee_id = self.employee_id
        identification_id = employee_id.identification_id
        employee_name = employee_id.name
        episode_id = self.episode_id
        mosque_id = episode_id.mosque_id
        student = self.env['mk.student.register'].search([('identity_no', '=', identification_id),
                                                          ('category', '!=', False)], limit=1)
        if not student:
            vals = {'identity_no': identification_id,
                    'category': employee_id.category2,
                    'name': employee_name,
                    'second_name': employee_name,
                    'mosq_id': mosque_id.id,
                    'birthdate': employee_id.birthday,
                    'mobile': employee_id.mobile_phone.strip()}
            student = self.env['mk.student.register'].create(vals)
        employee_link = self.env['mk.link'].search([('episode_id', '=', episode_id.id),
                                                    ('student_id', '=', student.id)], limit=1)
        if not employee_link:
            employee_link = self.env['mk.link'].create({'student_id': student.id,
                                                    'episode_id': episode_id.id,
                                                    'mosq_id': mosque_id.id,
                                                    'state': 'accept'})

        self.employee_link_id = employee_link.id

        # verificatio
        result = []
        test_name = self.test_name_id
        test_name_id = test_name and test_name.id or False

        branch = self.branch_id
        branch_id = branch and branch.id or False

        trackk = self.trackk

        academic_id = self.study_year_id.id
        study_class_id = self.study_class_id.id

        avalible_minutes = self.avalible_minutes
        wi_counter = self.counter
        test_time = self.center_time_table_id

        employee_link_id = self.employee_link_id
        flag, massege = self.env['select.students'].action_student_validate(branch, trackk, academic_id,
                                                                            study_class_id, employee_link_id.id, test_name, avalible_minutes, wi_counter, test_time)
        result.append((0, 0, {'student_id': employee_link_id.id,
                              'avalible_minutes': self.avalible_minutes,
                              'center_tests': self.center_time_table_id.center_id.test_names.ids,

                              'test_name': test_name_id,
                              'trackk': trackk,
                              'branch': branch_id,

                              'flag': flag,
                              'massege': massege}))

        self.student_id = result

        return {"type": "ir.actions.do_nothing", }

    def teacher_test_subscription(self):
        test_center = self.center_time_table_id.center_id
        current_date = datetime.now().date()
        registration_end__date = datetime.strptime(test_center.registeration_end_date, '%Y-%m-%d').date()
        if current_date <= registration_end__date:
            for student in self.student_id:
                if student.flag == True and student.student_id and student.test_name and student.branch:
                    vals = {'student_id':  student.student_id.id,
                             'test_name':   student.test_name.id,
                             'test_time':   self.center_time_table_id.id,
                             'branch':      student.branch.id,
                             'center_name': self.center_time_table_id.center_id.center_id.display_name,
                             'masjed_name': student.student_id.sudo().mosq_id.display_name,
                             'mosque_id':   student.student_id.sudo().mosq_id.id,
                            'category': self.employee_id.category2}
                    if test_center.committee_assign_type == 'supervisor_assign':
                        student_mosque = student.student_id.mosq_id
                        commitee_member = self.env['committe.member'].search([('center_id', '=', test_center.id),
                                                                              ('member_id.category', '=', 'edu_supervisor'),
                                                                              ('member_id.mosque_sup', 'in',[student_mosque.id])], limit=1)
                        vals.update({'committe_id': commitee_member.committe_id.id,
                                     'user_id':     commitee_member.member_id.user_id.id})
                    self.env['student.test.session'].create(vals)
        else:
            raise ValidationError(_('عذرا لايمكنك تسجيل الطلاب بعد تاريخ نهاية التسجيل في الاختبارات'))













