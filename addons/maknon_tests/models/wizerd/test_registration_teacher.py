from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class TestRegisterTeacher(models.TransientModel):    
    _name="test.register.teacher"

    @api.multi
    def get_study_class(self):
        study_class = self.env['mk.study.class'].search([('study_year_id', '=', self.get_year_default()),
                                                         ('is_default', '=', True)], limit=1)
        return study_class and study_class.id or False

    @api.multi
    def get_year_default(self):
        academic_year = self.env['mk.study.year'].search([('is_default', '=', True)], limit=1)
        return academic_year and academic_year.id or False

    academic_id    = fields.Many2one('mk.study.year',         string='Academic Year', default=get_year_default, required=True,                      ondelete='restrict')
    study_class_id = fields.Many2one('mk.study.class',        string='Study class',   default=get_study_class,  domain=[('is_default', '=', True)], ondelete='restrict')
    #center_id=fields.Many2one("mk.test.center.prepration",string="Test center")
    center_tests     = fields.Many2many("mk.test.names",      string="tests")  
    test_name        = fields.Many2one("mk.test.names",       string="Test Name")
    trackk           = fields.Selection([('up',   'من الناس إلى الفاتحة'),
                                         ('down', 'من الفاتحة إلى الناس')], string="المسار")
    branch           = fields.Many2one("mk.branches.master",  string="Branch")
    branch_duration  = fields.Integer(related='branch.duration', string="branch duration")
    avalible_minutes = fields.Integer("remaining minutes")
    counter          = fields.Integer("remaining minutes", compute='get_remaining')
    hide             = fields.Integer("remaining minutes", compute='all_st')
    total_minutes    = fields.Integer("total minutes")
    teacher          = fields.Many2one("hr.employee",  string="Teacher")
    avalible_teacher = fields.Many2many("hr.employee", string="available")
    reg_teacher_ids  = fields.One2many("test.register.teacher.line", "register_id", string="Teachers")
    masjed           = fields.Many2one("mk.mosque",  string="Masjed")
    #episode          = fields.Many2one("mk.episode", string="Episode")
    teacher_ids      = fields.Many2many("hr.employee",   string="المعلم")
    set_b            = fields.Boolean("add more teacher", default=True)
    test_session_id  = fields.Many2one("center.time.table",         string="TestCenterTimetable")
    
#     @api.onchange('masjed')
#     def on_masjed(self):
#         self.episode = False    

    @api.onchange('test_session_id')
    def onchange_test_time(self):
        self.center_tests = () 
        center_tests = self.test_session_id.center_id.test_names.ids
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
        
        for teacher in self.teacher_ids:
            flag, massege = self.env['test.register.teacher.line'].action_teacher_validate(branch, academic_id, study_class_id, teacher.id, test_name, avalible_minutes, wi_counter)
            result.append((0, 0, {'teacher_id':       teacher.id,
                                  'avalible_minutes': self.avalible_minutes,
                                  'center_tests':     self.test_session_id.center_id.test_names.ids,
                                  
                                  'test_name':        test_name_id,
                                  'trackk':           trackk,
                                  'branch':           branch_id,
                                  
                                  'flag':             flag,
                                  'massege':          massege}))

        self.teacher_ids = False
        self.reg_teacher_ids = result
        self.set_b = False
        
        self.branch = False
        self.trackk = False
        self.test_name = False

        return {"type": "ir.actions.do_nothing",}

    @api.depends('reg_teacher_ids')
    def get_remaining(self):
        self.counter=0
        for rec in self.reg_teacher_ids:
            if rec.flag==True and rec.test_name:
                self.counter=self.counter+1

    @api.depends('reg_teacher_ids')
    def all_st(self):
        self.hide=len(self.reg_teacher_ids)

    @api.multi
    def ok(self):
        test_session = self.test_session_id
        test_session_id = test_session.id
        date_test = test_session.date
        for reg_teacher in self.reg_teacher_ids:
            if reg_teacher.flag==True and reg_teacher.teacher_id and reg_teacher.branch and reg_teacher.test_name:
                self.env['employee.test.session'].create({'emp_id':          reg_teacher.teacher_id.id,
                                                          'test_name':       reg_teacher.test_name.id,
                                                          'test_session_id': test_session_id,
                                                          'branch':          reg_teacher.branch.id,
                                                          'date':            date_test,
                                                          #'center_name': self.test_time.center_id.center_id.display_name,
                                                          #'masjed_name': reg_teacher.teacher_id.sudo().mosq_id.name
                                                          })


class SelectTeacher(models.TransientModel):
    _name = "test.register.teacher.line"
    _rec_name = 'teacher_id'

    @api.multi
    def get_year_default(self):
        academic_year = self.env['mk.study.year'].search([('is_default', '=', True)], limit=1)
        return academic_year and academic_year.id or False

    @api.multi
    def get_study_class(self):
        study_class = self.env['mk.study.class'].search([('study_year_id', '=', self.get_year_default()),
                                                         ('is_default', '=', True)], limit=1)
        return study_class and study_class.id or False
    
    teacher_id       = fields.Many2one("hr.employee",string="Teacher")
    massege          = fields.Text(string=" ", default='الرجاء تعبئة البيانات كامله')
    flag             = fields.Boolean(string="agree",        default=False)
    register_id      = fields.Many2one("test.register.teacher",      string="wizard")
    trackk			 = fields.Selection([('up',   'من الناس إلى الفاتحة'),
      									 ('down', 'من الفاتحة إلى الناس')], string="المسار", required=True)
    branch           = fields.Many2one("mk.branches.master", string="Branch")
    test_name        = fields.Many2one("mk.test.names",      string="Test Name")
    avalible_minutes = fields.Integer("remaining minutes")
    branch_duration  = fields.Integer(related='branch.duration', string="branch duration")
    center_tests     = fields.Many2many("mk.test.names", string="tests")
    academic_id      = fields.Many2one('mk.study.year',  string='Academic Year', default=get_year_default, required=True,                      ondelete='restrict')
    study_class_id   = fields.Many2one('mk.study.class', string='Study class',   default=get_study_class,  domain=[('is_default', '=', True)], ondelete='restrict')
    
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
    def action_teacher_validate(self, branch, academic_id, study_class_id, teacher_id, test_name, avalible_minutes, wi_counter):
        flag = False
        massege = " "
        if branch:
            if self.test_name.parent_test:
                is_pass_parent_test, flag, massege = self.is_pass_parent_test(academic_id, study_class_id, teacher_id, test_name)
                
                is_pass_test_before = True
                if is_pass_parent_test:
                    is_pass_test_before, flag, massege = self.is_pass_test_before(teacher_id, branch, academic_id, study_class_id)
                
                is_it_his_normal_track = False
                if not is_pass_test_before:
                    is_it_his_normal_track, flag, massege = self.is_it_his_normal_track(teacher_id, academic_id, study_class_id, branch)
                    
                is_it_pass_next_tests = False
                if is_it_his_normal_track:
                    is_it_pass_next_tests, flag, massege = self.is_it_pass_next_tests(teacher_id, academic_id, study_class_id, test_name, branch)
                    
                if is_it_pass_next_tests:
                    if branch.parent_branch:
                        is_pass_parent_branch, flag, massege = self.is_pass_parent_branch(teacher_id, branch, academic_id, study_class_id)
                        if is_pass_parent_branch:
                            is_there_is_available_seats, flag, massege = self.is_there_is_available_seats()
                    else:
                        is_there_is_available_seats, flag, massege = self.is_there_is_available_seats()

            else:
                is_pass_test_before, flag, massege = self.is_pass_test_before(teacher_id, branch, academic_id, study_class_id)

                is_it_his_normal_track = False
                if not is_pass_test_before:
                    is_it_his_normal_track, flag, massege = self.is_it_his_normal_track(teacher_id, academic_id, study_class_id, branch)
                
                is_it_pass_next_tests = False
                if is_it_his_normal_track:
                    is_it_pass_next_tests, flag, massege = self.is_it_pass_next_tests(teacher_id, academic_id, study_class_id, test_name, branch)
                    
                if is_it_pass_next_tests:
                    if branch.parent_branch:
                        is_pass_parent_branch, flag, massege = self.is_pass_parent_branch(teacher_id, branch, academic_id, study_class_id)
                        
                        if is_pass_parent_branch:
                            is_there_is_available_seats, flag, massege = self.is_there_is_available_seats(avalible_minutes, branch, wi_counter)
                    else:
                        is_there_is_available_seats, flag, massege = self.is_there_is_available_seats(avalible_minutes, branch, wi_counter)
        else:
            flag = False
            massege = 'الرجاء تعبئة البيانات كامله'    
            
        return flag, massege
    
    @api.onchange('branch')
    def teacher_validate(self):
        branch = self.branch
        academic_id = self.academic_id.id
        study_class_id = self.study_class_id.id
        teacher_id = self.teacher_id.id
        
        test_name = self.test_name
                
        flag, massege = self.action_teacher_validate(branch, academic_id, study_class_id, teacher_id, test_name, self.avalible_minutes, self.register_id.counter)
        self.flag = flag
        self.massege = massege
            
    def is_pass_parent_test(self, academic_id, study_class_id, teacher_id, test_name):
        parent_test = test_name.parent_test
        parent_test_id = parent_test.id
        
        domain = [('teacher','=',teacher_id),
                  ('academic_id','=',academic_id),
                  ('study_class_id','=',study_class_id),
                  ('state','=','done'),
                  ('is_pass','=',True)]
        
        up_branche = self.env['mk.branches.master'].sudo().search([('test_name','=',parent_test_id),
                                                                    ('trackk','=','up')], order='order desc', limit=1)
        if up_branche:
            is_test_up = self.env['employee.test.session'].sudo().search(domain+[('branch','=',up_branche.id)], limit=1)
            
            if is_test_up:
                flag = True
                massege = " "
                return True, flag, massege
            
        down_branche = self.env['mk.branches.master'].sudo().search([('test_name','=',parent_test_id),
                                                                     ('trackk','=','down')], order='order desc', limit=1)        
        if down_branche:
            is_test_down = self.env['employee.test.session'].sudo().search(domain+[('branch','=',down_branche.id)], limit=1)
            
            if is_test_down:
                flag = True
                massege = " "
                return True, flag, massege

            else:            
                flag = False
                massege = 'عفوا المعلم لم يكمل اختبار فروع ' + str(parent_test.name) + ' وهو  متطلب'
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

    def is_pass_test_before(self, teacher_id, branch, academic_id, study_class_id):
        std_test = self.env['employee.test.session'].search([('teacher','=',teacher_id),
                                                            ('branch','=',branch.id),
                                                            #('academic_id','=',academic_id),
                                                            #('study_class_id','=',study_class_id)
                                                            ], limit=1)
        if std_test:
            if std_test.state == 'done':
                if std_test.degree < branch.minumim_degree:
                    flag = True
                    massege = " "
                    return False, flag, massege
                else:
                    massege = 'المعلم نجح في هذا الفرع مسبقا'
                    flag = False
                    return True, flag, massege
            else:
                massege = 'تم تسجيل المعلم في هذا الفرع سابقا'
                flag = False
                return True, flag, massege

        else:
            flag = True
            massege = " "
            return False, flag, massege
        
    def is_it_his_normal_track(self, teacher_id, academic_id, study_class_id, branch):
        std_test = self.env['employee.test.session'].search([('teacher','=',teacher_id),
                                                            #('academic_id','=',academic_id),
                                                            #('study_class_id','=',study_class_id),
                                                            ('state','=','done'),
                                                            #('is_pass','=',True)
                                                            ], order="date desc", limit=1)#done_date desc", limit=1)
        if std_test:
            if std_test.branch.trackk != branch.trackk:
                masar = ""
                if std_test.branch.trackk == 'up':
                    masar = "من الناس إلى الفاتحة"
                else:
                    masar = "من الفاتحة إلى الناس"
                    
                flag = False
                massege = 'مسار المعلم ' + ' [ ' + masar + ' ] ' + 'غير مسموح له بتغيير المسار'
                return False, flag, massege
            
            else:
                flag = True
                massege = " "
                return True, flag, massege
        else:
            flag = True
            massege = " "
            return True, flag, massege

    def is_it_pass_next_tests(self, teacher_id, academic_id, study_class_id, test_name, branch):
        std_test = self.env['employee.test.session'].search([('teacher','=',teacher_id),
                                                            #('academic_id','=',academic_id),
                                                            #('study_class_id','=',study_class_id),
                                                            ('state','=','done'),
                                                            #('is_pass','=',True),
                                                            ('test_name','=',test_name.id),
                                                            #('branch_order','>',branch.order)
                                                            ], limit=1)
        if std_test:
            passed_branches = []
            info = str(std_test[0].branch.name)
            passed_branches.append(info)
            flag = False
            massege = 'المعلم نجح في الفروع ' + str(passed_branches) + 'وهي فروع شاملة لهذا الفرع'
            return False, flag, massege
        else:
            flag = True
            massege = " "
            return True, flag, massege
        
    def is_pass_parent_branch(self, teacher_id, branch, academic_id, study_class_id):
        is_test_branch = self.env['employee.test.session'].search([('teacher','=',teacher_id),
                                                                  ('branch','=',branch.parent_branch.id),
                                                                  #('is_pass','=',True),
                                                                  #('academic_id','=',academic_id),
                                                                  #('study_class_id','=',study_class_id)
                                                                  ])
        if is_test_branch:
            flag = True
            massege = " "
            return True, flag, massege
        
        else:
            flag = False
            massege = 'المعلم لم يختبر الفرع ' + ' ( ' + branch.parent_branch.name + ' ) ' + 'وهو فرع متطلب'
            return False, flag, massege
