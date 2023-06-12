from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class TestRegister(models.TransientModel):    
    _name="test.register"

    academic_id    = fields.Many2one('mk.study.year',  string='Academic Year', required=True, ondelete='restrict')
    study_class_id = fields.Many2one('mk.study.class', string='Study class', ondelete='restrict')
    test_time      = fields.Many2one("center.time.table", string="Test Time")
    # center_id=fields.Many2one("mk.test.center.prepration",string="Test center")
    center_tests     = fields.Many2many("mk.test.names", string="tests")  
    test_name        = fields.Many2one("mk.test.names",      string="Test Name")
    trackk           = fields.Selection([('up',   'من الناس إلى الفاتحة'),
                                         ('down', 'من الفاتحة إلى الناس')], string="المسار")
    branch           = fields.Many2one("mk.branches.master", string="Branch")
    #student_id=fields.Many2one("mk.link",string="student")
    branch_duration  = fields.Integer(related='branch.duration', string="branch duration")
    avalible_minutes = fields.Integer("remaining minutes")
    counter          = fields.Integer("remaining minutes", compute='get_remaining')
    hide             = fields.Integer("remaining minutes", compute='all_st')
    total_minutes    = fields.Integer("total minutes")
    teacher          = fields.Many2one("hr.employee",  string="Teacher")
    avalible_teacher = fields.Many2many("hr.employee", string="available")
    student_id       = fields.One2many("select.students", "wi", string="students")
    masjed           = fields.Many2one("mk.mosque",  string="Masjed")
    episode          = fields.Many2one("mk.episode", string="Episode")
    students_list    = fields.Many2many("mk.link",   string="student list")
    set_b            = fields.Boolean("add more student", default=True)
    employee_id      = fields.Many2one('hr.employee',     string='الموظف')
    employee_link_id = fields.Many2one("mk.link",   string="student list")

    @api.onchange('masjed', 'episode', 'study_class_id')
    def on_change_students_list(self):
        self.students_list = False
        episode_id = self.episode
        masjed_id = self.masjed
        domain = [('mosq_id','=',masjed_id.id)]
        if self.study_class_id.is_default:
            domain += [('episode_id.study_class_id.is_default', '=', True),
                       ('episode_id.state', '=', 'accept'),
                       ('episode_id.active', '=', True),
                       ('state', '=', 'accept')]
        else:
            domain += [('episode_id.study_class_id', '=', self.study_class_id.id),
                       ('episode_id.state', 'in', ['accept', 'done']),
                       ('state', 'in', ['accept', 'done']),
                       '|',('episode_id.active', '=', True),
                           ('episode_id.active', '=', False)]
        if episode_id:
            domain += [('episode_id','=',episode_id.id)]
        return {'domain': {'students_list': domain}}

    @api.onchange('masjed')
    def on_masjed(self):
        self.episode = False
        self.employee_id = False
        masjed = self.masjed

        domain = ['|',('mosque_sup', 'in', [masjed.id]),
                            '|',('mosqtech_ids', 'in', [masjed.id]),
                                    '&',('category', '=', 'center_admin'),
                                         '|', ('department_id', '=', masjed.center_department_id.id),
                                                ('department_ids', 'in', [masjed.center_department_id.id])]
        return {'domain': {'employee_id': domain}}

    @api.onchange('test_time')
    def onchange_test_time(self):
        self.center_tests = () 
        center_tests = self.test_time.center_id.test_names.ids
        if center_tests:
            self.center_tests = center_tests
        
    @api.onchange('trackk')
    def onchange_trackk(self):
        self.branch = False        

    @api.multi
    def show(self):
        self.set_b=True
        return {"type": "ir.actions.do_nothing",}

    @api.multi
    def hide1(self):
        self.set_b=False
        return {"type": "ir.actions.do_nothing",}

    @api.multi
    def set_branch(self):
        result=[]
        test_name = self.test_name
        test_name_id = test_name and test_name.id or False
        
        branch = self.branch
        branch_id = branch and branch.id or False
        
        trackk = self.trackk
        
        academic_id = self.academic_id.id
        study_class_id = self.study_class_id.id
        
        avalible_minutes = self.avalible_minutes
        wi_counter = self.counter
        test_time = self.test_time
        for student in self.students_list:
            flag, massege = self.env['select.students'].action_student_validate(branch, trackk, academic_id, study_class_id, student.id, test_name, avalible_minutes, wi_counter,test_time)
            result.append((0, 0, {'student_id':       student.id,
                                  'avalible_minutes': self.avalible_minutes,
                                  'center_tests':     self.test_time.center_id.test_names.ids,
                                  
                                  'academic_id':      academic_id,
                                  'test_name':        test_name_id,
                                  'study_class_id':   study_class_id,
                                  'trackk':           trackk,
                                  'branch':           branch_id,
                                  
                                  'flag':             flag,
                                  'massege':          massege}))

        self.students_list = False
        self.student_id = result
        self.set_b = False
        
        self.branch = False
        self.trackk = False
        self.test_name = False

        return {"type": "ir.actions.do_nothing",}

    @api.depends('student_id')
    def get_remaining(self):
        self.counter=0
        for rec in self.student_id:
            if rec.flag==True and rec.test_name:
                self.counter=self.counter+1

    @api.depends('student_id')
    def all_st(self):
        self.hide=len(self.student_id)

    @api.multi
    def ok(self):
        test_center = self.test_time.center_id
        study_class_id = self.study_class_id
        current_date = datetime.now().date()
        registration_end__date = datetime.strptime(test_center.registeration_end_date, '%Y-%m-%d').date()
        if study_class_id.is_default and current_date > registration_end__date:
            raise ValidationError(_('عذرا لايمكنك تسجيل الطلاب بعد تاريخ نهاية التسجيل في الاختبارات'))
        else:
            for student in self.student_id:
                if student.flag == True and student.student_id and student.test_name and student.branch:
                    vals = {'student_id':  student.student_id.id,
                             'test_name':   student.test_name.id,
                             'test_time':   self.test_time.id,
                             'branch':      student.branch.id,
                             'center_name': self.test_time.center_id.center_id.display_name,
                             'masjed_name': student.student_id.sudo().mosq_id.display_name,
                             'mosque_id':   student.student_id.sudo().mosq_id.id,
                            'category': student.student_id.student_id.category,
                            'attachment_id': student.attachment_id.id }
                    if test_center.committee_assign_type == 'supervisor_assign':
                        student_mosque = student.student_id.mosq_id
                        commitee_member = self.env['committe.member'].search([('center_id', '=', test_center.id),
                                                                              ('member_id.category', '=', 'edu_supervisor'),
                                                                              ('member_id.mosque_sup', 'in',[student_mosque.id])], limit=1)
                        vals.update({'committe_id': commitee_member.committe_id.id,
                                     'user_id':     commitee_member.member_id.user_id.id})
                    self.env['student.test.session'].create(vals)

    @api.multi
    def set_employee_branch(self):
        employee_id = self.employee_id
        identification_id = employee_id.identification_id
        employee_name = employee_id.name


        mosque_id = self.masjed

        # verification
        result = []
        test_name = self.test_name
        test_name_id = test_name and test_name.id or False

        branch = self.branch
        branch_id = branch and branch.id or False

        trackk = self.trackk

        academic_id = self.academic_id.id
        study_class_id = self.study_class_id.id

        avalible_minutes = self.avalible_minutes
        wi_counter = self.counter
        test_time = self.test_time
        flag, massege = self.env['select.students'].action_employee_validate(branch, trackk, academic_id, study_class_id, employee_id, test_name, avalible_minutes, wi_counter, test_time)
        result.append((0, 0, {'employee_id': employee_id.id,
                              'avalible_minutes': self.avalible_minutes,
                              'center_tests': self.test_time.center_id.test_names.ids,
                              'academic_id': academic_id,
                              'test_name': test_name_id,
                              'trackk': trackk,
                              'branch': branch_id,
                              'flag': flag,
                              'massege': massege}))

        self.student_id = result

        return {"type": "ir.actions.do_nothing", }

    def teacher_ok(self):
        test_center = self.test_time.center_id
        current_date = datetime.now().date()
        study_class_id = self.study_class_id
        registration_end__date = datetime.strptime(test_center.registeration_end_date, '%Y-%m-%d').date()
        if study_class_id.is_default and current_date > registration_end__date:
            raise ValidationError(_('عذرا لايمكنك تسجيل الطلاب بعد تاريخ نهاية التسجيل في الاختبارات'))
        else:
            mosq_id = self.masjed
            for employee in self.employee_id:
                if employee :
                    vals = {'employee_id':  employee.id,
                             'test_name':   self.test_name.id,
                             'test_time':   self.test_time.id,
                             'branch':      self.branch.id,
                             'center_name': self.test_time.center_id.center_id.display_name,
                             'masjed_name': mosq_id.display_name,
                             'mosque_id':   mosq_id.id,
                            'category': self.employee_id.category2}

                    if test_center.committee_assign_type == 'supervisor_assign':
                        employee_mosques = employee.employee_id.mosqtech_ids
                        for employee_mosque in employee_mosques:
                            commitee_member = self.env['committe.member'].search([('center_id', '=', test_center.id),
                                                                              ('member_id.category', '=', 'edu_supervisor'),
                                                                              ('member_id.mosque_sup', 'in',[employee_mosque.id])], limit=1)
                            if commitee_member:
                                vals.update({'committe_id': commitee_member.committe_id.id,
                                             'user_id':     commitee_member.member_id.user_id.id})
                                break
                    self.env['student.test.session'].create(vals)


class selectstudent(models.TransientModel):
    _name = "select.students"
    _rec_name = 'student_id'

    student_id       = fields.Many2one("mk.link",string="student")
    employee_id       = fields.Many2one("hr.employee",string="Employee")
    massege          = fields.Text(string=" ", default='الرجاء تعبئة البيانات كامله')
    flag             = fields.Boolean(string="agree",        default=False)
    wi               = fields.Many2one("test.register",      string="wiz")
    wi2               = fields.Many2one("teacher.test.subscription",      string="wiz2")
    trackk			 = fields.Selection([('up',   'من الناس إلى الفاتحة'),
      									 ('down', 'من الفاتحة إلى الناس')],   string="المسار", required=True)
    branch           = fields.Many2one("mk.branches.master", string="Branch")
    test_name        = fields.Many2one("mk.test.names",      string="Test Name")
    avalible_minutes = fields.Integer("remaining minutes")
    branch_duration  = fields.Integer(related='branch.duration', string="branch duration")
    center_tests     = fields.Many2many("mk.test.names", string="tests")
    academic_id      = fields.Many2one('mk.study.year',  string='Academic Year', required=True, ondelete='restrict')
    study_class_id   = fields.Many2one('mk.study.class', string='Study class',  ondelete='restrict')
    attachment_id   = fields.Many2one('ir.attachment' , string='المرفقات')
    type_test        = fields.Selection(related='test_name.type_test')

    @api.model
    def action_employee_validate(self, branch, trackk, academic_id, study_class_id, employee_id, test_name,
                                 avalible_minutes,wi_counter, test_time):
        flag = False
        massege = " "
        if branch:
            if test_name.parent_test:
                is_pass_parent_test, flag, massege = self.is_employee_pass_parent_test(academic_id, study_class_id, employee_id,
                                                                              test_name)

                is_pass_test_before = True
                if is_pass_parent_test:
                    is_pass_test_before, flag, massege = self.is_employee_pass_test_before(employee_id, branch)

                is_it_his_normal_track = False
                if not is_pass_test_before:
                    is_it_his_normal_track, flag, massege = self.is_employee_it_his_normal_track(employee_id, trackk, branch)

                is_it_pass_next_tests = False
                if is_it_his_normal_track:
                    is_it_pass_next_tests, flag, massege = self.is_employee_it_pass_next_tests(employee_id, academic_id,
                                                                                      study_class_id, test_name, branch)

                is_there_is_available_seats = False
                if is_it_pass_next_tests:
                    if branch.parent_branch:
                        is_pass_parent_branch, flag, massege = self.is_employee_pass_parent_branch(employee_id, branch, academic_id,
                                                                                          study_class_id)
                        if is_pass_parent_branch:
                            is_there_is_available_seats, flag, massege = self.is_there_is_available_seats()
                    else:
                        is_there_is_available_seats, flag, massege = self.is_there_is_available_seats()

                is_student_information_validate = False
                if is_there_is_available_seats:
                    is_student_information_validate, flag, massege = self.is_employee_information_validate(employee_id)

                if is_student_information_validate:
                    is_auto_assign_committee_test, flag, massege = self.is_employee_auto_assign_committee_test(test_time, employee_id)

            else:
                # is_pass_test_before, flag, massege = self.is_pass_test_before(student_id, branch)
                is_pass_test_before = True
                is_it_his_normal_track, flag, massege = self.is_employee_it_his_normal_track(employee_id, trackk, branch)

                # is_it_his_normal_track = False
                # if not is_pass_test_before:
                if is_it_his_normal_track:
                    is_pass_test_before, flag, massege = self.is_employee_pass_test_before(employee_id, branch)
                    # is_it_his_normal_track, flag, massege = self.is_it_his_normal_track(student_id, trackk, branch)

                is_it_pass_next_tests = False
                if not is_pass_test_before:
                    is_it_pass_next_tests, flag, massege = self.is_employee_it_pass_next_tests(employee_id, academic_id,
                                                                                      study_class_id, test_name, branch)

                is_there_is_available_seats = False
                if is_it_pass_next_tests:
                    if branch.parent_branch:
                        is_pass_parent_branch, flag, massege = self.is_employee_pass_parent_branch(employee_id, branch, academic_id,
                                                                                          study_class_id)

                        if is_pass_parent_branch:
                            is_there_is_available_seats, flag, massege = self.is_there_is_available_seats(avalible_minutes,
                                                                                                          branch,
                                                                                                          wi_counter)
                    else:
                        is_there_is_available_seats, flag, massege = self.is_there_is_available_seats(avalible_minutes,
                                                                                                      branch, wi_counter)

                is_student_information_validate = False
                if is_there_is_available_seats:
                    is_student_information_validate, flag, massege = self.is_employee_information_validate(employee_id)

                if is_student_information_validate:
                    is_auto_assign_committee_test, flag, massege = self.is_employee_auto_assign_committee_test(test_time, employee_id)
        else:
            flag = False
            massege = 'الرجاء تعبئة البيانات كامله'

        return flag, massege
    @api.onchange('trackk')
    def onchange_trackk(self):
    	self.branch = False

    @api.onchange('test_name')
    def test_change(self):
        self.branch = False
        if self.test_name == False:
            self.flag = False
            self.massege = 'الرجاء تعبئة البيانات كامله'

    @api.model
    def action_student_validate(self, branch, trackk, academic_id, study_class_id, student_id, test_name, avalible_minutes, wi_counter,test_time):
        flag = False
        massege = " "
        if branch:
            if test_name.parent_test:
                is_pass_parent_test, flag, massege = self.is_pass_parent_test(academic_id, study_class_id, student_id, test_name)

                is_pass_test_before = True
                if is_pass_parent_test:
                    is_pass_test_before, flag, massege = self.is_pass_test_before(student_id, branch)

                is_it_his_normal_track = False
                if not is_pass_test_before:
                    is_it_his_normal_track, flag, massege = self.is_it_his_normal_track(student_id, trackk, branch)

                is_it_pass_next_tests = False
                if is_it_his_normal_track:
                    is_it_pass_next_tests, flag, massege = self.is_it_pass_next_tests(student_id, academic_id, study_class_id, test_name, branch)

                is_there_is_available_seats = False
                if is_it_pass_next_tests:
                    if branch.parent_branch:
                        is_pass_parent_branch, flag, massege = self.is_pass_parent_branch(student_id, branch, academic_id, study_class_id)
                        if is_pass_parent_branch:
                            is_there_is_available_seats, flag, massege = self.is_there_is_available_seats()
                    else:
                        is_there_is_available_seats, flag, massege = self.is_there_is_available_seats()

                is_student_information_validate = False
                if is_there_is_available_seats:
                    is_student_information_validate, flag, massege = self.is_student_information_validate(student_id)

                if is_student_information_validate:
                    is_auto_assign_committee_test, flag, massege = self.is_auto_assign_committee_test(test_time,student_id)

            else:
                # is_pass_test_before, flag, massege = self.is_pass_test_before(student_id, branch)
                is_pass_test_before = True
                is_it_his_normal_track, flag, massege = self.is_it_his_normal_track(student_id, trackk, branch)

                # is_it_his_normal_track = False
                # if not is_pass_test_before:
                if is_it_his_normal_track:
                    is_pass_test_before, flag, massege = self.is_pass_test_before(student_id, branch)
                    # is_it_his_normal_track, flag, massege = self.is_it_his_normal_track(student_id, trackk, branch)

                is_it_pass_next_tests = False
                if not is_pass_test_before:
                    is_it_pass_next_tests, flag, massege = self.is_it_pass_next_tests(student_id, academic_id, study_class_id, test_name, branch)

                is_there_is_available_seats = False
                if is_it_pass_next_tests:
                    if branch.parent_branch:
                        is_pass_parent_branch, flag, massege = self.is_pass_parent_branch(student_id, branch, academic_id, study_class_id)

                        if is_pass_parent_branch:
                            is_there_is_available_seats, flag, massege = self.is_there_is_available_seats(avalible_minutes, branch, wi_counter)
                    else:
                        is_there_is_available_seats, flag, massege = self.is_there_is_available_seats(avalible_minutes, branch, wi_counter)

                is_student_information_validate = False
                if is_there_is_available_seats:
                    is_student_information_validate, flag, massege = self.is_student_information_validate(student_id)

                if is_student_information_validate:
                    is_auto_assign_committee_test, flag, massege = self.is_auto_assign_committee_test(test_time,student_id)
        else:
            flag = False
            massege = 'الرجاء تعبئة البيانات كامله'

        return flag, massege

    @api.onchange('branch')
    def student_validate(self):
        branch = self.branch
        trackk = self.trackk
        academic_id = self.academic_id.id
        study_class_id = self.study_class_id.id
        student_id = self.student_id.id

        test_name = self.test_name

        flag, massege = self.action_student_validate(branch, trackk, academic_id, study_class_id, student_id, test_name, self.avalible_minutes, self.wi.counter, self.wi.test_time)

        self.flag = flag
        self.massege = massege

    def is_student_information_validate(self,student_id):
        link = self.env['mk.link'].sudo().search([('id', '=', student_id)])
        if link :
            if not link.student_id.mobile and link.student_id.category == False:
                flag = False
                massege = 'الرجاء إضافة رقم جوال الطالب'
                return False, flag, massege
            elif (not link.student_id.identity_no and not link.student_id.no_identity) or (not link.student_id.passport_no and link.student_id.no_identity) and link.student_id.category == False:
                flag = False
                massege = 'الرجاء إضافة رقم هوية الطالب'
                return False, flag, massege
            elif not link.student_id.birthdate and link.student_id.category == False:
                flag = False
                massege = 'الرجاء إضافة تاريخ ميلاد الطالب'
                return False, flag, massege
            else:
                flag = True
                massege = " "
                return True, flag, massege

    def is_employee_information_validate(self,employee_id):
        if not employee_id.mobile_phone and employee_id.category == False:
            flag = False
            massege = 'الرجاء إضافة رقم جوال الموظف'
            return False, flag, massege
        elif not employee_id.identification_id and employee_id.category == False:
            flag = False
            massege = 'الرجاء إضافة رقم هوية الموظف'
            return False, flag, massege
        elif not employee_id.birthday and employee_id.category == False:
            flag = False
            massege = 'الرجاء إضافة تاريخ ميلاد الموظف'
            return False, flag, massege
        else:
            flag = True
            massege = " "
            return True, flag, massege

    def is_employee_auto_assign_committee_test(self,test_time,employee_id):
        test_center = test_time.center_id
        if test_center.committee_assign_type == 'supervisor_assign':
            student_mosques = employee_id.mosqtech_ids
            for student_mosque in student_mosques:
                commitee_members = self.env['committe.member'].search([('center_id', '=', test_center.id),
                                                                       ('member_id.category','=','edu_supervisor'),
                                                                       ('member_id.mosque_sup','in',[student_mosque.id])], limit=1)
                if commitee_members:
                    flag = True
                    massege = " "
                    return True, flag, massege
            else:
                flag = False
                massege = 'لا توجد لجنة إختبار خاصة بالمشرف التربوي لمسجد ' + ' ' + str(student_mosque.name) + ' ' + 'في مركز الاختبار' + ' ' + str(test_center.name)
                return False, flag, massege
        else:
            flag = True
            massege = " "
            return True, flag, massege
    def is_auto_assign_committee_test(self,test_time,student_id):
        test_center = test_time.center_id
        if test_center.committee_assign_type == 'supervisor_assign':
            link = self.env['mk.link'].search([('id', '=', student_id)])
            student_mosque = link.student_id.mosq_id
            commitee_members = self.env['committe.member'].search([('center_id', '=', test_center.id),
                                                                   ('member_id.category','=','edu_supervisor'),
                                                                   ('member_id.mosque_sup','in',[student_mosque.id])], limit=1)
            if commitee_members:
                flag = True
                massege = " "
                return True, flag, massege
            else:
                flag = False
                massege = 'لا توجد لجنة إختبار خاصة بالمشرف التربوي لمسجد ' + ' ' + str(student_mosque.name) + ' ' + 'في مركز الاختبار' + ' ' + str(test_center.name)
                return False, flag, massege
        else:
            flag = True
            massege = " "
            return True, flag, massege

    def is_pass_parent_test(self, academic_id, study_class_id, student_id, test_name):
        link = self.env['mk.link'].sudo().search([('id', '=', student_id)])

        parent_test = test_name.parent_test
        parent_test_id = parent_test.id

        domain = [('student_id','=',link.student_id.id),
                  ('academic_id','=',academic_id),
                  ('study_class_id','=',study_class_id),
                  ('state','=','done'),
                  ('is_pass','=',True)]

        up_branche = self.env['mk.branches.master'].sudo().search([('test_name','=',parent_test_id),
                                                                    ('trackk','=','up')], order='order desc', limit=1)
        if up_branche:
            is_test_up = self.env['student.test.session'].sudo().search(domain+[('branch','=',up_branche.id)], limit=1)

            if is_test_up:
                flag = True
                massege = " "
                return True, flag, massege
            else:
                flag = False
                massege = 'عفوا الطالب لم يكمل اختبار فروع ' + str(parent_test.name) + 'للفصل' + str(parent_test.study_class_id.name) +' وهو  متطلب'
                return False, flag, massege

        down_branche = self.env['mk.branches.master'].sudo().search([('test_name','=',parent_test_id),
                                                                     ('trackk','=','down')], order='order desc', limit=1)
        if down_branche:
            is_test_down = self.env['student.test.session'].sudo().search(domain+[('branch','=',down_branche.id)], limit=1)

            if is_test_down:
                flag = True
                massege = " "
                return True, flag, massege

            else:
                flag = False
                massege = 'عفوا الطالب لم يكمل اختبار فروع ' + str(parent_test.name) + 'للفصل' + str(parent_test.study_class_id.name) +' وهو  متطلب'
                return False, flag, massege

    def is_there_is_available_seats(self, avalible_minutes, branch, wi_counter):
        if avalible_minutes - (branch.duration * wi_counter + 1) < 0 :
            flag = False
            massege = "لاتوجد مقاعد شاغرة امتلئت السعة الاستيعابية للفترة"
            return False, flag, massege

        else:
            flag = True
            massege = " "
            return True, flag, massege

    def is_pass_test_before(self, student_id, branch):
        link = self.env['mk.link'].search([('id','=',student_id)], limit=1)
        order_branch = branch.order
        branch_type = branch.test_name.type_test
        if branch_type == 'correct_citation':
            std_test = self.env['student.test.session'].search([('student_id.student_id', '=', link.student_id.id),
                                                                ('test_name.type_test', '=', 'correct_citation'),
                                                                '|', ('state', 'not in', ['cancel', 'absent', 'done']),
                                                                '&', ('state', '=', 'done'),
                                                                ('is_pass', '=', True)], order="id desc", limit=1)
            if std_test:
                is_pass = std_test.is_pass
                state = std_test.state
                std_branch = std_test.branch
                name_std_branch = std_branch.name

                name_study_year = std_test.academic_id.name
                name_study_class = std_test.study_class_id.name

                if is_pass and state == 'done':
                    massege = 'لا يمكن تسجيل الطالب في هذا الفرع لأنه اجتاز' + ' ' + name_std_branch + ' ' + 'بنجاح خلال' + ' ' + name_study_class
                else:
                    massege = 'لا يمكن تسجيل الطالب في هذا الفرع لأنه تم تسجيله في ' + ' ' + name_std_branch + ' ' + 'خلال' + ' ' + name_study_class
                flag = False
                return True, flag, massege

        else:
            std_test = self.env['student.test.session'].search([('student_id.student_id','=',link.student_id.id),
                                                                ('branch.order','>=',order_branch),
                                                                ('branch.test_name.type_test', 'not in', ['correct_citation', 'vacations']),
                                                                '|',('state','not in', ['cancel','absent','done']),
                                                                    '&',('state','=','done'),
                                                                        ('is_pass','=',True)], order="id desc", limit=1)
            if std_test:
                is_pass = std_test.is_pass
                state = std_test.state
                std_branch = std_test.branch
                name_std_branch = std_branch.name

                name_study_year = std_test.academic_id.name
                name_study_class = std_test.study_class_id.name

                if std_branch.order == order_branch:
                    if is_pass and state == 'done':
                        massege = 'الطالب نجح في هذا الفرع مسبقا خلال' + ' ' + name_study_class
                    else:
                        massege = 'تم تسجيل الطالب في هذا  الفرع مسبقاً خلال' + ' ' + name_study_class
                else:
                    if is_pass and state == 'done':
                        massege = 'لا يمكن تسجيل الطالب في هذا الفرع لأنه اجتاز إختبار' + ' ' + name_std_branch + ' ' + 'بنجاح خلال' + ' ' + name_study_class
                    else:
                        massege = 'لا يمكن تسجيل الطالب في هذا الفرع لأنه تم تسجيله في إختبار' + ' ' + name_std_branch + ' ' + 'خلال' + ' ' + name_study_class

                flag = False
                return True, flag, massege

        flag = True
        massege = " "
        return False, flag, massege

    def is_employee_pass_test_before(self, employee_id, branch):
        order_branch = branch.order
        branch_type = branch.test_name.type_test
        if branch_type == 'correct_citation':
            std_test = self.env['student.test.session'].search([('employee_id', '=', employee_id.id),
                                                                ('test_name.type_test', '=', 'correct_citation'),
                                                                '|', ('state', 'not in', ['cancel', 'absent', 'done']),
                                                                '&', ('state', '=', 'done'),
                                                                ('is_pass', '=', True)], order="id desc", limit=1)
            if std_test:
                is_pass = std_test.is_pass
                state = std_test.state
                std_branch = std_test.branch
                name_std_branch = std_branch.name

                name_study_year = std_test.academic_id.name
                name_study_class = std_test.study_class_id.name

                if is_pass and state == 'done':
                    massege = 'لا يمكن تسجيل الموظف في هذا الفرع لأنه اجتاز' + ' ' + name_std_branch + ' ' + 'بنجاح خلال' + ' ' + name_study_class
                else:
                    massege = 'لا يمكن تسجيل الموظف في هذا الفرع لأنه تم تسجيله في ' + ' ' + name_std_branch + ' ' + 'خلال' + ' ' + name_study_class
                flag = False
                return True, flag, massege

        else:
            std_test = self.env['student.test.session'].search([('employee_id', '=', employee_id.id),
                                                                ('branch.order', '>=', order_branch),
                                                                (
                                                                'branch.test_name.type_test', '!=', 'correct_citation'),
                                                                '|', ('state', 'not in', ['cancel', 'absent', 'done']),
                                                                '&', ('state', '=', 'done'),
                                                                ('is_pass', '=', True)], order="id desc", limit=1)
            if std_test:
                is_pass = std_test.is_pass
                state = std_test.state
                std_branch = std_test.branch
                name_std_branch = std_branch.name

                name_study_year = std_test.academic_id.name
                name_study_class = std_test.study_class_id.name

                if std_branch.order == order_branch:
                    if is_pass and state == 'done':
                        massege = 'الموظف نجح في هذا الفرع مسبقا خلال' + ' ' + name_study_class
                    else:
                        massege = 'تم تسجيل الموظف في هذا  الفرع مسبقاً خلال' + ' ' + name_study_class
                else:
                    if is_pass and state == 'done':
                        massege = 'لا يمكن تسجيل الموظف في هذا الفرع لأنه اجتاز إختبار' + ' ' + name_std_branch + ' ' + 'بنجاح خلال' + ' ' + name_study_class
                    else:
                        massege = 'لا يمكن تسجيل الموظف في هذا الفرع لأنه تم تسجيله في إختبار' + ' ' + name_std_branch + ' ' + 'خلال' + ' ' + name_study_class

                flag = False
                return True, flag, massege

        flag = True
        massege = " "
        return False, flag, massege

    def is_it_his_normal_track(self, student_id, trackk, branch):
        link = self.env['mk.link'].search([('id', '=', student_id)], limit=1)
        branch_type = branch.test_name.type_test
        if branch_type not in ['final', 'correct_citation', 'vacations']:
            std_test = self.env['student.test.session'].search([('student_id.student_id', '=', link.student_id.id),
                                                                ('branch.trackk', '!=', trackk),
                                                                '|', ('state', 'not in', ['cancel', 'absent', 'done']),
                                                                '&', ('state', '=', 'done'),
                                                                ('is_pass', '=', True)], order="id desc", limit=1)
            if std_test:
                if std_test.branch.test_name.type_test == 'parts':
                    masar = ""
                    if std_test.branch.trackk == 'up':
                        masar = "من الناس إلى الفاتحة"
                    else:
                        masar = "من الفاتحة إلى الناس"

                    flag = False
                    massege = 'مسار الطالب ' + ' [ ' + masar + ' ] ' + 'غير مسموح له بتغيير المسار'
                    return False, flag, massege
                else:
                    flag = True
                    massege = " "
                    return True, flag, massege

        flag = True
        massege = " "
        return True, flag, massege

    def is_employee_it_his_normal_track(self, employee_id, trackk, branch):
        branch_type = branch.test_name.type_test
        if branch_type not in ['final', 'correct_citation']:
            std_test = self.env['student.test.session'].search([('employee_id', '=', employee_id.id),
                                                                ('branch.trackk', '!=', trackk),
                                                                '|', ('state', 'not in', ['cancel', 'absent', 'done']),
                                                                '&', ('state', '=', 'done'),
                                                                ('is_pass', '=', True)], order="id desc", limit=1)
            if std_test:
                if std_test.branch.test_name.type_test == 'parts':
                    masar = ""
                    if std_test.branch.trackk == 'up':
                        masar = "من الناس إلى الفاتحة"
                    else:
                        masar = "من الفاتحة إلى الناس"

                    flag = False
                    massege = 'مسار الموظف ' + ' [ ' + masar + ' ] ' + 'غير مسموح له بتغيير المسار'
                    return False, flag, massege
                else:
                    flag = True
                    massege = " "
                    return True, flag, massege

        flag = True
        massege = " "
        return True, flag, massege
    def is_it_pass_next_tests(self, student_id, academic_id, study_class_id, test_name, branch):
        std_test = self.env['student.test.session'].search([('student_id','=',student_id),
                                                            ('academic_id','=',academic_id),
                                                            ('study_class_id','=',study_class_id),
                                                            ('state','=','done'),
                                                            ('is_pass','=',True),
                                                            ('test_name','=',test_name.id),
                                                            ('branch_order','>',branch.order)], limit=1)
        if std_test:
            passed_branches = []
            info = str(std_test[0].branch.name)
            passed_branches.append(info)
            flag = False
            massege = 'الطالب نجح في الفروع ' + str(passed_branches) + 'وهي فروع شاملة لهذا الفرع'
            return False, flag, massege
        else:
            flag = True
            massege = " "
            return True, flag, massege

    def is_employee_it_pass_next_tests(self, employee_id, academic_id, study_class_id, test_name, branch):
        std_test = self.env['student.test.session'].search([('employee_id', '=', employee_id.id),
                                                            ('academic_id', '=', academic_id),
                                                            ('study_class_id', '=', study_class_id),
                                                            ('state', '=', 'done'),
                                                            ('is_pass', '=', True),
                                                            ('test_name', '=', test_name.id),
                                                            ('branch_order', '>', branch.order)], limit=1)
        if std_test:
            passed_branches = []
            info = str(std_test[0].branch.name)
            passed_branches.append(info)
            flag = False
            massege = 'الموظف نجح في الفروع ' + str(passed_branches) + 'وهي فروع شاملة لهذا الفرع'
            return False, flag, massege
        else:
            flag = True
            massege = " "
            return True, flag, massege
    def is_pass_parent_branch(self, student_id, branch, academic_id, study_class_id):
        is_test_branch = self.env['student.test.session'].search([('student_id','=',student_id),
                                                                  ('branch','=',branch.parent_branch.id),
                                                                  ('is_pass','=',True),
                                                                  ('academic_id','=',academic_id),
                                                                  ('study_class_id','=',study_class_id)])
        if is_test_branch:
            flag = True
            massege = " "
            return True, flag, massege

        else:
            flag = False
            massege = 'الطالب لم يختبر الفرع ' + ' ( ' + branch.parent_branch.name + ' ) ' + 'وهو فرع متطلب'
            return False, flag, massege

    def is_employee_pass_parent_branch(self, employee_id, branch, academic_id, study_class_id):
        is_test_branch = self.env['student.test.session'].search([('employee_id', '=', employee_id.id),
                                                                  ('branch', '=', branch.parent_branch.id),
                                                                  ('is_pass', '=', True),
                                                                  ('academic_id', '=', academic_id),
                                                                  ('study_class_id', '=', study_class_id)])
        if is_test_branch:
            flag = True
            massege = " "
            return True, flag, massege

        else:
            flag = False
            massege = 'الموظف لم يختبر الفرع ' + ' ( ' + branch.parent_branch.name + ' ) ' + 'وهو فرع متطلب'
            return False, flag, massege

    def is_employee_pass_parent_test(self, academic_id, study_class_id, employee_id, test_name):

        parent_test = test_name.parent_test
        parent_test_id = parent_test.id

        domain = [('employee_id', '=', employee_id.id),
                  ('academic_id', '=', academic_id),
                  ('study_class_id', '=', study_class_id),
                  ('state', '=', 'done'),
                  ('is_pass', '=', True)]

        up_branche = self.env['mk.branches.master'].sudo().search([('test_name', '=', parent_test_id),
                                                                   ('trackk', '=', 'up')], order='order desc', limit=1)
        if up_branche:
            is_test_up = self.env['student.test.session'].sudo().search(domain + [('branch', '=', up_branche.id)],
                                                                        limit=1)

            if is_test_up:
                flag = True
                massege = " "
                return True, flag, massege
            else:
                flag = False
                massege = 'عفوا الموظف لم يكمل اختبار فروع ' + str(parent_test.name) + 'للفصل' + str(
                    parent_test.study_class_id.name) + ' وهو  متطلب'
                return False, flag, massege

        down_branche = self.env['mk.branches.master'].sudo().search([('test_name', '=', parent_test_id),
                                                                     ('trackk', '=', 'down')], order='order desc',
                                                                    limit=1)
        if down_branche:
            is_test_down = self.env['student.test.session'].sudo().search(domain + [('branch', '=', down_branche.id)],
                                                                          limit=1)

            if is_test_down:
                flag = True
                massege = " "
                return True, flag, massege

            else:
                flag = False
                massege = 'عفوا الموظف لم يكمل اختبار فروع ' + str(parent_test.name) + 'للفصل' + str(
                    parent_test.study_class_id.name) + ' وهو  متطلب'
                return False, flag, massege
