#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from datetime import datetime, timedelta
from lxml import etree

import logging
_logger = logging.getLogger(__name__)


class MkTestCenterConfig(models.Model):
    _name = 'mk.test.center.prepration'
    _inherit=['mail.thread','mail.activity.mixin']

    #_rec_name = 'center_id'
    
    @api.one
    @api.depends('place_options','center_id','center_id.display_name','internal_place','internal_place.name')
    def get_name_center_prep(self):        
        name = str(self.center_id.display_name) + ' ' + ' ( '
        place_options = self.place_options
        
        if place_options == 'at':
            name += 'مقر المركز' + ' ) '
            
        elif place_options == 'out':
            name += 'خارج المركز' + ' ) '
            
        elif place_options == 'in':
            name += str(self.sudo().internal_place.display_name) + ' ) '
            
        elif place_options == 'company':
            name += 'الجمعية' + ' ) '
            
        elif place_options == 'c_female':
            name += 'مكتب الإشراف النسائي' + ' ) '
            
        elif place_options == 'portal':
            name += 'لجنة متحركة' + ' ) '
        
        self.name = name

    @api.model
    def center_prep_name_cron_fct(self):
        test_center_preparation_internal = self.env['mk.test.center.prepration'].search([('center_id.study_class_id.is_default', '=', True),
                                                                                         ('place_options', '=', 'in')])
        for center in test_center_preparation_internal:
            name = str(center.center_id.display_name) + ' ' + ' ( '
            name += str(center.sudo().internal_place.display_name) + ' ) '
            center.name = name

    @api.one
    @api.depends('main_center')
    def cheack_user_logged_in(self):
        visible_for_user = True        

        if self.env.user.has_group('maknon_tests.read_tests_centers') and not self.env.user.has_group('maknon_tests.group_Student_tests_full'):
            if self.sudo().center_id.main_company:
                visible_for_user = False
                
            elif self.sudo().center_id.center_id.id in [self.env.user.department_id.id] or self.sudo().center_id.center_id.id in self.env.user.department_ids.ids: 
                visible_for_user=True
                
            elif self.create_date:
                visible_for_user=False
                
        self.visible_for_user = visible_for_user
                            
    @api.depends('place_options','internal_place')
    def get_place(self):
        for rec in self:
            place_options = rec.place_options
            if place_options=='at':
                rec.place_description=str(rec.sudo().center_id.center_id.area_id.name)+' , '+str(rec.sudo().center_id.center_id.city_id.name)+' , '+str(rec.sudo().center_id.center_id.district_id.name)
                
                if rec.sudo().center_id.center_id.latitude:
                    rec.latitude=rec.sudo().center_id.center_id.latitude
                    
                if rec.sudo().center_id.center_id.longitude:
                    rec.longtitude=rec.sudo().center_id.center_id.longitude
                    
            elif place_options=='in' and rec.internal_place:                
                rec.place_description = str(rec.sudo().internal_place.area_id.name)+' , '+str(rec.sudo().internal_place.city_id.name)+' , '+str(rec.sudo().internal_place.district_id.name)
                rec.longtitude = rec.sudo().internal_place.latitude
                rec.latitude = rec.sudo().internal_place.longitude
                
            elif place_options == 'company':
                rec.longtitude = False
                rec.latitude = False                
                company_id = self.env['res.company'].sudo().search([('id','=',1)], limit=1)
                if company_id:
                    rec.place_description = str(company_id[0].street)+" , "+str(company_id[0].street2)+" , "+str(company_id[0].city)
                    
            elif place_options in ['c_female','portal']:
                rec.place_description=False                    
                rec.longtitude=False
                rec.latitude=False
                
    @api.onchange('center_group')
    def center_group_ONC(self):
        if self.center_group:
            test_ids=self.env['mk.test.names'].search([('test_group','=',self.center_group),
                                                       ('study_class_id','=',self.study_class_id.id),
                                                       ('academic_id','=',self.academic_id.id)])
            return {'domain':{'test_names':[('id', 'in',test_ids.ids)]}} 
        
    @api.depends('center_id')
    def get_info(self):
        for rec in self:
            center_obje=self.env['mak.test.center'].sudo().search([('id','=',rec.center_id.id)])
            if center_obje:
                info_text="* العام الدراسي  :"+str(center_obje[0].academic_id.name)+"\n"+'* الفصل الدراسي :'+" "+str(center_obje[0].study_class_id.name)+"\n"+"* المركز الرئيسي : "+str(center_obje[0].center_id.name)+" "+"\n"
                info_text=info_text+" "+"* مراكز الاشراف  :"+" "
                for ce in center_obje[0].department_ids:
                    info_text=info_text+ce.name+"  -  "
                info_text=info_text+"\n"+"* انواع الاختبارات  :"+" "
                
                for test in center_obje[0].test_names:
                    info_text=info_text+str(test.name)+" - "
                rec.center_info=info_text                      

    @api.depends('committee_test_ids')
    def committee_numbers(self):
        self.committe_number = len(self.committee_test_ids)
        
    @api.one
    @api.depends('center_id','place_options')
    def get_mosques(self):
        mosques = [] 
        
        place_options = self.place_options
        center = self.center_id
        
        if place_options == 'in'  and center:
            mosques = self.env['mk.mosque'].search([('center_department_id','=',center.center_id.id),
                                                    ('categ_id.mosque_type','=',center.gender)])
            
            mosques = [mosque.id for mosque in mosques]
            
        self.mosque_ids = [(6,0,mosques)]
    
    name                     = fields.Char("Name", store=True, compute='get_name_center_prep')          
    visible_for_user         = fields.Boolean(string="show",   default=True, compute='cheack_user_logged_in')
    active                   = fields.Boolean(string="active", default=True, groups='maknon_tests.tests_centers_archive', tracking=True)
    place_options            = fields.Selection([('company',  'مقر الجمعية'),
                                                 ('in',       'داخل المركز'),
                                                 ('out',      'خارج المركز'),
                                                 ('at',       'في مقر المركز'),
                                                 ('c_female', 'مكتب الإشراف النسائي'),
                                                 ('portal',   'لجنة متحركة')], string="exam place", tracking=True)
    # outside place
    latitude                 = fields.Char("latitude")
    longtitude               = fields.Char("longtitude")
    place_description        = fields.Char("place discribtion", compute='get_place')
    out_disc                 = fields.Char("place discribtion", tracking=True) # in place
    mosque_ids               = fields.Many2many('mk.mosque', compute=get_mosques, store=True)
    internal_place           = fields.Many2one("mk.mosque", string="select mosque", tracking=True)
    main_center              = fields.Char('Test Center')
    academic_id              = fields.Many2one('mk.study.year',  string='Academic Year', required=True,                      ondelete='restrict', tracking=True)
    study_class_id           = fields.Many2one('mk.study.class', string='Study class',   domain=[('is_default', '=', True)], ondelete='restrict', tracking=True)
    center_group             = fields.Selection([('student',  'Student'),
                                                 ('employee', 'Employee')], string="center exam group", tracking=True)
    center_code              = fields.Char(string="code", tracking=True)
    company_id               = fields.Many2one('res.company',     string='Company', default=lambda self: self.env['res.company']._company_default_get('mk.test.center.config'))
    center_id                = fields.Many2one('mak.test.center', string='Test Center', tracking=True)
    center_info              = fields.Text(string="center information", compute='get_info')
    website_registeration    = fields.Boolean('Registeration by Website',    tracking=True)
    is_auto_assign_committee = fields.Boolean('إسناد تلقائي للجنة الإختبار ', tracking=True)
    committee_assign_type    = fields.Selection([('all_committee_assign', 'All committee assign'),
                                                 ('supervisor_assign', 'Supervisor assign'),
                                                 ('manual_assign', 'Manual assign')], string="Committee assign type",default="all_committee_assign", required="1", tracking=True)
    #Committee Test Lines
    registeration_start_date = fields.Date('Registeration Start Date', tracking=True)
    registeration_end_date   = fields.Date('Registeration End Date',   tracking=True)
    exam_start_date          = fields.Date('Exam Start Date',          tracking=True)
    exam_end_date            = fields.Date('Exam End Date', tracking=True)
    periods_ids              = fields.Many2many("test.period", string="Available Periods")
    friday                   = fields.Boolean('Friday',    tracking=True)
    saturday                 = fields.Boolean('Saturday',  tracking=True)
    sunday                   = fields.Boolean('Sunday',    tracking=True)
    monday                   = fields.Boolean('Monday',    tracking=True)
    tuesday                  = fields.Boolean('Tuesday',   tracking=True)
    wednesday                = fields.Boolean('Wednesday', tracking=True)
    thursday                 = fields.Boolean('Thursday',  tracking=True)
    department_ids           = fields.Many2many("hr.department", string="Departments")
    test_names               = fields.Many2many("mk.test.names", string="Tests Names")
    all_branches             = fields.Boolean(string="ALL branches", default=True, tracking=True)
    branches_ids             = fields.Many2many("mk.branches.master", string="Branches")
    committee_test_ids       = fields.One2many('committee.tests', 'commitee_id', string='Committee test')
    timetable_ids            = fields.One2many("center.time.table", "center_id","TimeTable")
    flag                     = fields.Boolean(string="flag", default=False, tracking=True)
    committe_number          = fields.Integer(string="members number", compute='committee_numbers')
    
    @api.onchange('center_id')
    def onchange_center_id(self):
        center = self.center_id
        if center:
            self.department_ids = center.department_ids
            self.test_names = center.test_names
            self.all_branches = center.all_branches
            self.branches_ids = center.branches_ids
            self.registeration_start_date = center.registeration_start_date
            self.registeration_end_date = center.registeration_end_date
            self.exam_start_date = center.exam_start_date
            self.exam_end_date = center.exam_end_date
            self.academic_id = center.academic_id
            self.study_class_id = center.study_class_id
            self.main_center = center.center_id.name
            
        else:
            self.department_ids=False
            self.test_names=False
            self.all_branches=False
            self.branches_ids=False
            self.registeration_start_date=False
            self.registeration_end_date=False
            self.exam_start_date=False
            self.exam_end_date=False
            self.academic_id=False
            self.study_class_id=False
            self.main_center=False   
            
        self.internal_place = False

    @api.constrains('registeration_start_date', 'registeration_end_date', 'exam_start_date', 'exam_end_date',
                    'study_class_id.start_date', 'study_class_id.end_date')
    def _check_date(self):
        study_class_start_date = self.study_class_id.start_date
        study_class_end_date = self.study_class_id.end_date

        if self.registeration_start_date < study_class_start_date:
            raise ValidationError(_('عفوا , تاريخ بداية التسجيل لايمكن ان يكون سابق لتاريخ بداية الفصل'))

        elif self.exam_end_date > study_class_end_date:
            raise ValidationError(_('عفوا , تاريخ نهاية الاختبارات لايمكن ان يكون بعد تاريخ نهاية الفصل'))

        elif (self.registeration_start_date > self.exam_start_date):
            raise ValidationError(_('عفوا ,, تاريخ بداية الاختبارات لايمكن ان يكون سابق لتاريخ التسجيل'))

        elif (self.registeration_end_date < self.registeration_start_date):
            raise ValidationError(_('عفوا , تاريخ نهاية التسجيل لايمكن ان يكون سابق لتاريخ بداية التسجيل'))

        elif (self.registeration_end_date > self.exam_end_date):
            raise ValidationError(_('عفوا , لايمكن ان يستمر التسجيل لما بعد نهاية الاختبارات'))

        elif (self.exam_end_date > study_class_end_date):
            raise ValidationError(_('عفوا , تاريخ نهاية الاختبارات لايمكن ان يستمر لما بعد نهاية الفصل'))

    @api.multi
    def genrate_time_table(self):
        # get all avilable days betwen start date and end date
        #create timetable record per available period
        if len(self.committee_test_ids) == 0:
            raise ValidationError(_('عذرا , يجب تحديد لجان الاختبار اولا'))
        
        saturday = self.saturday
        monday = self.monday
        thursday = self.thursday
        wednesday = self.wednesday
        tuesday = self.tuesday
        friday = self.friday
        sunday = self.sunday
        
        if not (saturday or monday or thursday or wednesday or tuesday or friday or sunday):
            raise ValidationError(_('عذرا , يجب تحديد ايام الاختبارات'))
            
        if len(self.periods_ids) == 0:
            raise ValidationError(_('عذرا , يجب تحديد الفترات المتاحة'))                

        available_periods=[]
        if saturday:
            available_periods.append("Saturday")
            
        if monday:
            available_periods.append("Monday")
            
        if thursday:
            available_periods.append("Thursday")
            
        if tuesday:
            available_periods.append("Tuesday") 
            
        if friday:
            available_periods.append("Friday")
            
        if sunday:            
            available_periods.append("Sunday")
            
        if wednesday:
            available_periods.append("Wednesday")

        days = []
        weekdays = {}
        date_format = "%Y-%m-%d"

        exam_end_date = self.exam_end_date
        exam_start_date = self.exam_start_date

        distance = datetime.strptime(exam_end_date, date_format) - datetime.strptime(exam_start_date, date_format)
        number_of_days = distance.days

        for x in range(0, number_of_days):
            next_date = datetime.strptime(exam_start_date,"%Y-%m-%d")+timedelta(days=x)
            weekday = (datetime.date(next_date)).strftime("%A")
            d = str(next_date)
            if weekday in available_periods:
                days.append(d[:-9])
                weekdays[d[:-9]] = weekday
                #weekdays.append({d[:-9]:weekday})
        days.append(str(exam_end_date))
        last_day = (datetime.strptime(exam_end_date, "%Y-%m-%d")).strftime("%A")
        #(datetime.date(self.exam_end_date))
        weekdays[str(exam_end_date)] = last_day
        #weekdays.append(last_day)
        center_name = self.center_id.display_name
        test_center_prepa_id = self.id
        timetable_ob = self.env['center.time.table']
        
        type_center = 'student'
        if self.center_group == 'employee':
            type_center = 'teacher'
            
        for day in days:
            for period in self.periods_ids:
                timetable_ob.create({'center_name':    center_name,
                                     'center_id':      test_center_prepa_id,
                                     'academic_id':    self.center_id.academic_id.id,
                                     'study_class_id': self.center_id.study_class_id.id,
                                     'day':            weekdays[day] ,
                                     'date':           day,
                                     'period_id':      period.id,
                                     'type_center':    type_center})
        self.flag = True

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(MkTestCenterConfig, self).fields_view_get(view_id=view_id,view_type=view_type, toolbar=toolbar, submenu=submenu)

        doc = etree.XML(res['arch'])
        context=self._context
        if self.env.user.has_group('maknon_tests.read_tests_centers') and not self.env.user.has_group('maknon_tests.group_Student_tests_full'):
            domain_center="[('test_group','=',center_group),"
            dept_ids=[]
            dept_ids.append(self.env.user.department_id.id)
            dept_ids=dept_ids+self.env.user.department_ids.ids

            domain_center=domain_center+"('center_id','in',"+str(dept_ids)+")]"
            for node in doc.xpath("//field[@name='center_id']"):

                node.set('domain',domain_center)

        res['arch'] = etree.tostring(doc)
        return res
        # Monday  Tuesday, Wednesday, Thursday, Friday, Saturday. Sunday 

    @api.one
    def write(self, vals):
        if 'active' in vals:
            visible_for_user = self.visible_for_user
            if vals['active'] == False and not visible_for_user:
                raise ValidationError(_('عذرا ! لايمكنك ارشفة جدول اختبار تابع لمركز مستهدف'))
            
            elif vals['active'] == True and not visible_for_user:
                raise ValidationError(_('عذرا لايمكنك الغاء ارشفة جدول اختبار تابع لمركز مستهدف '))

        return super(MkTestCenterConfig, self).write(vals)
    
    @api.one
    def unlink(self):
        if not self.visible_for_user:
            raise ValidationError(_('عفوا ,لايمكنك حذف جدول تابع لمركز اختبار مستهدف'))

        return super(MkTestCenterConfig, self).unlink()

    @api.model
    def test_centers(self, gender, episode_id, user_id):
        gender = gender
        episode_id = int(episode_id)
        user_id = int(user_id)

        query = '''
        SELECT test_center.id,
        test_center.name

        FROM
        (SELECT distinct mk_test_center_prepration.id,
        mk_test_center_prepration.name

        FROM mk_test_center_prepration
        LEFT JOIN center_time_table ON center_time_table.center_id=mk_test_center_prepration.id
        LEFT JOIN mak_test_center ON mk_test_center_prepration.center_id=mak_test_center.id
        LEFT JOIN hr_department ON mak_test_center.center_id=hr_department.id '''

        if episode_id > 0:
            query += ''' left join mk_mosque on mk_mosque.center_department_id=hr_department.id
                        left join mk_episode on mk_episode.mosque_id=mk_mosque.id'''

        query += ''' WHERE center_time_table.active = True AND
        center_time_table.type_center='student' AND
        center_time_table.date >= current_date AND
        mak_test_center.gender = '{}'  AND'''.format(gender)

        if episode_id > 0:
            query += ''' mk_episode.id={}) test_center order by test_center.name;'''.format(episode_id)
        else:
            query += ''' 
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

            SELECT distinct mk_test_center_prepration.id,
            mk_test_center_prepration.name

            FROM mk_test_center_prepration
            LEFT JOIN center_time_table ON center_time_table.center_id=mk_test_center_prepration.id
            LEFT JOIN mak_test_center ON mk_test_center_prepration.center_id=mak_test_center.id
            LEFT JOIN hr_department ON mak_test_center.center_id=hr_department.id 

            WHERE center_time_table.active = True AND
            center_time_table.type_center='student' AND
            center_time_table.date >= current_date AND
            mak_test_center.gender = '{}'  AND
            mak_test_center.main_company=True) test_center

            order by test_center.name;'''.format(user_id, user_id, user_id, gender)

        self.env.cr.execute(query)
        test_centers = self.env.cr.dictfetchall()
        return test_centers


class CommitteeTest(models.Model):
    _name = 'committee.tests'
    _inherit=['mail.thread','mail.activity.mixin']

    name                 = fields.Char(string="Name", tracking=True)
    members_ids          = fields.One2many("committe.member","committe_id", "members list")
    commitee_id          = fields.Many2one('mk.test.center.prepration', string='Committee_id', tracking=True)
    active               = fields.Boolean(string="active", default=True, tracking=True)
    examiner_employee_id = fields.Many2one('hr.employee', string='Examinner')

    @api.multi
    def re(self):
        commite=self.env['committee.tests'].search([])
        if commite:
            for c in commite:
                c.write({'name':c.examiner_employee_id.name})
                self.env['committe.member'].create({'committe_id':c.id,
                                                    'center_id':c.commitee_id.id,
                                                    'member_id':c.examiner_employee_id.id})


class committeMembers(models.Model):
    _name='committe.member'
    _inherit=['mail.thread','mail.activity.mixin']

    member_id   = fields.Many2one("hr.employee", "Member", tracking=True)
    outsource   = fields.Boolean(string="outsource",       tracking=True)
    committe_id = fields.Many2one("committee.tests","commitee_id")
    center_id   = fields.Many2one('mk.test.center.prepration', string='Test Center')

    main_member = fields.Boolean(string="main member", default=False, tracking=True)


    @api.constrains('member_id')
    def check_committe_user(self):
        if self.member_id:
            user = self.member_id.user_id
            if not user:
                raise ValidationError(_("You cannot set committe member whithout user"))

    @api.onchange('center_id')
    def onchange_get_teacher_domain(self):
        if self.center_id.center_id.sudo().main_company:
            hr_employee = self.env['hr.employee'].sudo().search([('state','=','accept'),
                                                                 ('gender','=',self.center_id.center_id.gender),
                                                                 ('department_id','in',self.center_id.center_id.sudo().department_ids.ids)])
        else:
            hr_employee = self.env['hr.employee'].sudo().search([('state','=','accept'),
                                                                 ('gender','=',self.center_id.center_id.gender),
                                                                 '|',('department_id','=',self.center_id.center_id.sudo().center_id.id),
                                                                     ('department_id','in',self.center_id.center_id.sudo().department_ids.ids)])
        if hr_employee:
            return {'domain':{'member_id':[('id', 'in',hr_employee.ids)]}}
        else:
            return {'domain':{'member_id':[('id', 'in',[])]}}

    @api.onchange('outsource')
    def onchange_outsource(self):
        hr_employee=[]
        if self.outsource==True:
            hr_employee=self.env['hr.employee'].sudo().search([('state','=','accept'),
                                                               ('outsource','=',True),
                                                               ('gender','=',self.center_id.center_id.gender)])
        else:
            if self.center_id.center_id.main_company==True:
                hr_employee=self.env['hr.employee'].sudo().search([('state','=','accept'),
                                                                   ('gender','=',self.center_id.center_id.gender)])
            else:    
                hr_employee=self.env['hr.employee'].sudo().search([('state','=','accept'),
                                                                   ('gender','=',self.center_id.center_id.gender),
                                                                   ('department_id','=',self.center_id.center_id.sudo().center_id.id)])
            
        if hr_employee:
            return {'domain':{'member_id':[('id', 'in',hr_employee.ids)]}}
        else:
            return {'domain':{'member_id':[('id', 'in',[])]}}

    @api.multi
    def set_as_main_member(self):
        members=self.env['committe.member'].search([('committe_id','=',self.committe_id.id)])
        if members:
            for member in members:
                member.write({'main_member':False})
        self.write({'main_member':True})
        #here 

        # update exist sessions
        if self.center_id.sudo().center_group=='student':
            #test_center_group = self.env.ref('maknon_tests.session_exiaminer')
            #test_center_group.sudo().write({'users': [(4, self.member_id.user_id.id)]})
            self.member_id.user_id.sudo().write({'gender':self.center_id.center_id.sudo().gender})
            committe_sessions=self.env['student.test.session'].sudo().search([('committe_id','=',self.committe_id.id),
                                                                              ('state','=','draft')])
            if committe_sessions:
                for session in committe_sessions:
                    session.sudo().write({'user_id':self.member_id.user_id.id})
        else:
            #test_center_group = self.env.ref('maknon_tests.emp_session_exiaminer')
            #test_center_group.sudo().write({'users': [(4, self.member_id.user_id.id)]})
            committe_sessions=self.env['employee.test.session'].sudo().search([('committe_id','=',self.committe_id.id),
                                                                               ('state','=','draft')])
            if committe_sessions:
                for session in committe_sessions:
                    session.sudo().write({'user_id':self.member_id.user_id.id})
