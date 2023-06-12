#-*- coding:utf-8 -*-
import requests
from odoo import models, fields, api, tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

from datetime import datetime
import math

from ummalqura.hijri_date import HijriDate
from lxml import etree

import logging
_logger = logging.getLogger(__name__)


def geo_query_address(street=None, zip=None, city=None, state=None, country=None):
    if country and ',' in country and (country.endswith(' of') or country.endswith(' of the')):
        country = '{1} {0}'.format(*country.split(',', 1))
        return tools.ustr(', '.join(field for field in [street, ("%s %s" % (zip or '', city or '')).strip(), state, country] if field))

def geo_find(addr):
    if not addr:
        return None
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    try:
        result = requests.get(url, params={'sensor': 'false', 'address': addr}).json()
    except Exception as e:
        raise UserError(_('Cannot contact geolocation servers. Please make sure that your Internet connection is up and running (%s).') % e)

    if result['status'] != 'OK':
        return None

    try:
        geo = result['results'][0]['geometry']['location']
        return float(geo['lat']), float(geo['lng'])
    except (KeyError, ValueError):
        return None


class mk_courses_evalution(models.Model):
    _name = 'mk.courses.evalution'
    _inherit = ['mail.thread']
    _rec_name = 'domain'

    @api.one
    @api.depends('standard_ids','standard_ids.degree')
    def _get_total(self):
        self.degree = sum(standard.degree for standard in self.standard_ids)

    start_date   = fields.Date('Start Date', required=True, track_visibility='onchange')
    end_date     = fields.Date('End Date', track_visibility='onchange')
    domain       = fields.Char('Domain', track_visibility='onchange')
    degree       = fields.Float('Sum of Degree', compute=_get_total, track_visibility='onchange')
    standard_ids = fields.One2many('mk.course.standard', 'course_id', string="Standars")

    @api.constrains('end_date')
    def _check_start_date(self):
        if self.end_date < self.start_date:
            raise models.ValidationError('تاريخ نهاية جوانب تقويم الدورة المكثفة غير صحيح')


class mk_courses_satndard(models.Model):
    _name = 'mk.course.standard'
    _rec_name='standard'

    standard  = fields.Char('Standard')
    degree    = fields.Float('Degree')
    desc      = fields.Char('Description')
    attach    = fields.Boolean('Attachment')
    course_id = fields.Many2one('mk.courses.evalution',string="Standars")


class mk_courses_calibration_satndard(models.Model):
    _name = 'mk.course.calibration.standard'

    @api.one
    @api.depends('standard_ids','standard_ids.degree')
    def _get_total(self):
        self.degree = sum(standard.degree for standard in self.standard_ids)

    check_atta     = fields.Boolean('check',related='standard_id.attach')
    evaluation     = fields.Many2one('mk.courses.evalution',string='courses evaluations')
    degree         = fields.Float('Degree', compute=_get_total)
    due            = fields.Float('due')
    desc           = fields.Char('Description')
    attach         = fields.Binary('Attachment')
    standard_id    = fields.Many2one('mk.course.standard',string="Standars")
    calibration_id = fields.Many2one('mk.course.calibration', string='Calibration', ondelete='cascade')
    standard_ids    = fields.Many2many('mk.course.standard',string="Standars")

    @api.onchange('evaluation')
    def onchange_evaluation(self):
        courses_evals = self.env['mk.course.standard'].search([('course_id', '=', self.evaluation.id)])
        ids = [id for id in courses_evals.ids if id is not None and isinstance(id, int)]
        return {'domain': {'standard_id': [('course_id', '=', self.evaluation.id)]},
                'value': {'standard_ids': [(6, 0, tuple(set(ids)))]}}

    @api.constrains('due')
    def onchange_degree(self):
        if self.degree < self.due:
            raise models.ValidationError('الدرجة المستحقة يجب ان تكون اقل من اوتساوي درجة المعيار')


class mk_courses_request(models.Model):
    _name = 'mk.course.request'
    _inherit = ['mail.thread']
    _rec_name = 'course'

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            if rec.course_request_type == 'quran_day':
                type_course = "يوم قراني"
            if rec.course_request_type == 'intensive_course':
                type_course = "دورة مكثفة"
            if rec.course_request_type == 'ramadan_course':
                type_course = "دورة رمضانية"
            if rec.course_name and type_course:
                name = rec.course_name + " [ " + type_course + " ]"
                result.append((rec.id, name))
        return result

    @api.depends('start_date','end_date','day_ids')
    def on_change_start_date(self):
        for rec in self:
            start_date = rec.start_date
            end_date = rec.end_date

            if start_date and end_date:
                d1 = datetime.strptime(start_date, "%Y-%m-%d")
                d2 = datetime.strptime(end_date, "%Y-%m-%d")

                week = abs((d2-d1).days)/7
                week_day = math.ceil(week)
                total_day = len(rec.day_ids)

                rec.no_day = total_day*week_day
                rec.no_day_copy = rec.no_day

    @api.one
    @api.constrains('start_date','end_date','day_ids')
    def _check_dates(self):
        course = self.course
        start_date = self.start_date
        if start_date and start_date < course.start_date:
            raise models.ValidationError('الدروة المكثفة لم تبدا ')

        end_date = self.end_date
        if end_date and end_date > course.end_date:
            raise models.ValidationError('التاريخ المدخل خارج نطاق التاريخ المحدد للدورة ')

    @api.depends('mosque_id')
    def _defautl_admin(self):
        for rec in self:
            emp_obj=self.env['res.users'].search([('id','=',self.env.uid)]).mosque_ids
            if emp_obj:
                for mosq in emp_obj:
                    rec.admin_id=mosq.responsible_id.id
            else:
                rec.admin_id=rec.mosque_id.responsible_id.id    \

    @api.depends('mosque_id')
    def compute_mosq_department(self):
        for rec in self:
            mosque_id = rec.mosque_id
            if mosque_id:
                rec.department_id=rec.mosque_id.center_department_id.id

    @api.model
    def mosq_department_cron_fct(self):
        mosq_request = self.env['mk.course.request'].search([])
        i = 0
        j = 0
        for request in mosq_request:
            i += 1
            try:
                request.write({'department_id': request.mosque_id.center_department_id.id})
            except:
                j += 1
                pass


    @api.depends('no_hours','no_day')
    def _get_total_hour(self):
        for rec in self:
            rec.total_hours = rec.no_hours * rec.no_day


    @api.model
    def default_user(self):
        employee=self.env['hr.employee'].search([('user_id','=',self.env.uid)]).user_id
        return employee

    @api.depends('mosque_id', 'course_request_type')
    def _defautl_note(self):
        mosque_type = self.mosque_id.categ_id.mosque_type
        note_obj = self.env['mk.contral.condition'].search([('check_courses', '=', True),
                                                            ('categ_type', '=', 'male')], limit=1)
        if mosque_type == 'female':
            if self.course_request_type == 'quran_day' :
                note_obj = self.env['mk.contral.condition'].search([('check_courses', '=', True),
                                                                    ('categ_type', '=', 'female'),
                                                                    ('course_request_type','=','quran_day')], limit=1)
            elif self.course_request_type == 'ramadan_course':
                note_obj = self.env['mk.contral.condition'].search([('check_courses', '=', True),
                                                                    ('categ_type', '=', 'female'),
                                                                    ('course_request_type', '=', 'ramadan_course')], limit=1)
            else:
                note_obj = self.env['mk.contral.condition'].search([('check_courses', '=', True),
                                                                    ('categ_type', '=', 'female'),
                                                                    ('course_request_type','=','intensive_course')], limit=1)
        if mosque_type == 'male':

            if self.course_request_type == 'ramadan_course':
                note_obj = self.env['mk.contral.condition'].search([('check_courses', '=', True),
                                                                    ('categ_type', '=', 'male'),
                                                                    ('course_request_type', '=', 'ramadan_course')], limit=1)
            else:
                note_obj = self.env['mk.contral.condition'].search([('check_courses', '=', True),
                                                                    ('categ_type', '=', 'female'),
                                                                    ('course_request_type','=','intensive_course')], limit=1)
        if note_obj:
            self.note = note_obj.note

    # def _defautl_note2(self):
    #     note_obj=self.env['mk.contral.condition'].search([('check_courses','=',True)])
    #     for rec in note_obj:
    #         note2 = rec.note2
    #         return  note2

    @api.model
    def _defautl_department(self):
        employee=self.env['res.users'].search([('id','=',self.env.uid)]).department_id.id
        return employee

    @api.model
    def _defautl_masjed(self):
        emp_obj=self.env['res.users'].search([('id','=',self.env.uid)]).mosque_ids
        for mosq in emp_obj:
            return mosq.id

    @api.depends('start_date','end_date')
    def compute_hijri_start_date(self):
        for rec in self:
            if rec.start_date:
                rec.hijri_start_date = HijriDate.get_hijri_date(rec.start_date)

            if rec.end_date:
                rec.hijri_end_date = HijriDate.get_hijri_date(rec.end_date)

                rec.hijri_end_geo = HijriDate.get_georing_date(rec.hijri_end_date)

    @api.model
    def get_hijri_today(self,date):
        if date:
            return HijriDate.get_hijri_date(date)


    @api.model
    def get_year_default(self):
        year = self.env['mk.study.year'].search([('is_default','=',True)], limit=1)
        return year and year.id or False

    @api.onchange('academic_id')
    def on_change_academic_id(self):
        ids = (self.env['mk.study.class'].search([('study_year_id', '=', self.academic_id.id)])).ids
        return {'domain': {'study_class_id': [('id', 'in', ids)]}}

    @api.depends('write_date')
    def get_subscription_url(self):
        for rec in self:
            rec.course_request_url= "http://edu.maknon.org.sa/showintensive_course/" + str(rec.id)

    mosque_location_id = fields.Integer(string='mosque location id', track_visibility='onchange')
    user_id            = fields.Many2one('res.users', string="user",default=default_user, track_visibility='onchange')
    department_id      = fields.Many2one('hr.department',string="Department",compute="compute_mosq_department", store=True, track_visibility='onchange')
    employee_id2       = fields.Many2one('res.users', string="employee", track_visibility='onchange')
    mosque_id          = fields.Many2one('mk.mosque',default=_defautl_masjed, track_visibility='onchange')
    gender_mosque      = fields.Selection([('male','رجالي'),
                                           ('female','نسائي')], related="mosque_id.gender_mosque", string='Mosque gender', store=True, track_visibility='onchange')
    mosque_location    = fields.Many2one('mk.mosque',string="أسم المسجد/المدرسة", track_visibility='onchange')
    mosque_location_cc = fields.Char(string="أسم المسجد/المدرسة", track_visibility='onchange')
    state_id           = fields.Many2one('res.country.state', string='الحي', domain=[('type_location','=','district'),
                                                                                     ('enable','=',True)], track_visibility='onchange')
    location           = fields.Selection(string="Location", selection=[('internal', 'Internal'),
															            ('external', 'External'),
															            ('female_episodes', 'حلقات نسائية في مسجد/جامع'),
                                                                        ('remotly', 'Remotly')],default='internal', track_visibility='onchange')
    external_mosq_name = fields.Char('اسم المسجد/الجامع')
    academic_id        = fields.Many2one('mk.study.year',  string='العام الدراسي', default=get_year_default, track_visibility='onchange')
    study_class_id     = fields.Many2one('mk.study.class', string='الفصل الدراسي', track_visibility='onchange')
    course             = fields.Many2one('mk.types.courses', string='Course', track_visibility='onchange')
    course_name        = fields.Char("course Name", required=True, track_visibility='onchange')
    employee_id        = fields.Many2one("hr.employee", string="Employee", required=True, track_visibility='onchange')
    mobile             = fields.Char('Mobile', track_visibility='onchange')
    mobile_company     = fields.Char('Mobile company', track_visibility='onchange')
    admin_id           = fields.Many2one('hr.employee',string="Mosque Admin",compute="_defautl_admin", store=True, track_visibility='onchange')
    mobile_admin       = fields.Char('Mobile admin', track_visibility='onchange')
    yes                = fields.Selection(string="هل سبق اقامة دورة في المسجد/المدرسة", selection=[('نعم', 'Yes'), ('ﻻ', 'No')], track_visibility='onchange')
    yes_ep             = fields.Selection(string="هل يوجد أدارة حلقات بالمسجد/المدرسة‬",selection=[('نعم', 'Yes'), ('ﻻ', 'No')], track_visibility='onchange')
    #no=fields.Boolean('No')
    #no_ep=fields.Boolean('No')
    emp_ids            = fields.One2many('mk.course.emp', 'request_id', string="Employee")
    epsoide_ids        = fields.Many2many('mk.episode', string="Episode", domain=lambda self:[('mosque_id', '=', self.mosque_location_id)])
    #
    start_date         = fields.Date(string='Start Date', track_visibility='onchange')
    end_date           = fields.Date(string='End Date', track_visibility='onchange')
    day_ids            = fields.Many2many('mk.work.days', string="Days")
    subh               = fields.Boolean('Subah', track_visibility='onchange')
    zaher              = fields.Boolean('Zaher', track_visibility='onchange')
    asor               = fields.Boolean('Asor', track_visibility='onchange')
    mogreb             = fields.Boolean('mogreb', track_visibility='onchange')
    esha               = fields.Boolean('Esha', track_visibility='onchange')
    no_day             = fields.Integer(string="No Of Days", compute="on_change_start_date", track_visibility='onchange')
    no_day_copy        = fields.Integer(string="No Of Days", track_visibility='onchange')
    #branch_ids=fields.Many2many('test.branch.line', string="Branches"
        #,domain=[('branch_type','=','ic')]# )
    no_hours           = fields.Integer("No Of Hours", track_visibility='onchange')
    no_teacher         = fields.Integer("No Of Teachers", track_visibility='onchange')
    no_student         = fields.Integer("No Of Student", required=True, track_visibility='onchange')
    no_supervisor      = fields.Integer("No Of supervisor", track_visibility='onchange')
    cost               = fields.Float("Cost", track_visibility='onchange')
    commit             = fields.Boolean('Commit', track_visibility='onchange')
    student_ids        = fields.One2many('mk.course.student', 'request_st_id', string="Students")
    state              = fields.Selection(string="State", selection=[('draft', 'Draft'),
                                                                     ('send','Send'),
                                                                     ('accept', 'Accept'),
                                                                     ('reject', 'Reject'),
                                                                     ('closed', 'Closed')], default='draft', track_visibility='onchange')
    #google_map_mosque = fields.Char(string="Map")
    note               = fields.Text(string="Note", compute=_defautl_note, store=True)
    # note2              = fields.Text(default=_defautl_note2, string="Note", track_visibility='onchange')
    partner_latitude   = fields.Char(string="Longitude", track_visibility='onchange')
    partner_longitude  = fields.Char(string="Latitude", track_visibility='onchange')
    no_seats           = fields.Integer('Number of vacant seats', track_visibility='onchange')
    total_hours        = fields.Integer('إجمالي الساعات',compute="_get_total_hour", track_visibility='onchange')
    # location = fields.Char(string="Coordonnées géographiques", compute="tt_return_location")
    locate_desc        = fields.Text(string="وصف الموقع", track_visibility='onchange')
    #check=fields.Char('check',default=check)
    flag               = fields.Boolean('flage', track_visibility='onchange')
    flag2              = fields.Boolean('flage', track_visibility='onchange')
    emp_sec            = fields.Char("مشرف البرنامج", track_visibility='onchange')
    hijri_start_date   = fields.Char(compute="compute_hijri_start_date",store=True, track_visibility='onchange')
    hijri_end_date     = fields.Char(compute="compute_hijri_start_date",store=True, track_visibility='onchange')
    company_id         = fields.Many2one('res.company', string="Company", default=lambda self: self.env['res.company']._company_default_get('mk.course.request') , track_visibility='onchange')
    active             = fields.Boolean('نشط', default=True, track_visibility='onchange')
    course_request_code= fields.Char('Course request code', size=12, readonly=True, track_visibility='onchange')

    course_episode_nbr       = fields.Integer('Course Episodes', track_visibility='onchange')
    course_students_nbr      = fields.Integer('Course Students', track_visibility='onchange')
    course_teachers_nbr      = fields.Integer('Course Teachers', track_visibility='onchange')
    course_administrators_nbr = fields.Integer('Course Administrators', track_visibility='onchange')
    close_total_hours        = fields.Integer('Total hours', track_visibility='onchange')
    parts_female_total_nbr   = fields.Integer('Parts female total nbr', track_visibility='onchange')
    parts_female_total_done_nbr = fields.Integer('Parts female total done nbr', track_visibility='onchange')
    parts_nbr                = fields.Integer('Parts nbr', track_visibility='onchange')
    students_finals_nbr      = fields.Integer('Students finals', track_visibility='onchange')
    students_final_tests_nbr = fields.Integer('Students in final tests', track_visibility='onchange')
    students_parts_tests_nbr = fields.Integer('Students in parts tests', track_visibility='onchange')
    course_request_type      = fields.Selection(string="Course request type", selection=[('quran_day', 'Quran day'),
                                                                                         ('intensive_course', 'Intensive course'),
                                                                                         ('ramadan_course', 'Ramadan course')], default='intensive_course', required=True, track_visibility='onchange')
    image                    = fields.Binary("Image",              attachment=True)
    image_medium             = fields.Binary("Medium-sized image", attachment=True)
    image_small              = fields.Binary("Small-sized image",  attachment=True)
    course_request_url       = fields.Char(string='Course link', compute=get_subscription_url, store=True, track_visibility='onchange')
    branches_ids             = fields.Many2many("mk.parts.names", string="فروع الحفظ و المراجعة")
    nbr_student_courses  = fields.Integer('student_courses', compute='get_student_courses', store=True, track_visibility='onchange')

    def set_request_to_send(self):
        self.state="send"

    @api.depends('student_ids', 'student_ids.request_st_id')
    def get_student_courses(self):
        for rec in self:
            students = self.env['mk.course.student'].search([('request_st_id','=',rec.id)])
            rec.nbr_student_courses = len(students)

    @api.multi
    def close_course_data_wizard(self):
        return {
            'name': _('ييانات اقفال الدورة'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'close.course.data',
            'target': 'new',
            'context': {'mosque_id':                            self.mosque_id.id,
                        'default_gender_mosque':                self.gender_mosque,
                        'default_course_episode_nbr':           self.course_episode_nbr,
                        'default_course_students_nbr':          self.course_students_nbr,
                        'default_course_teachers_nbr':          self.course_teachers_nbr,
                        'default_course_administrators_nbr':    self.course_administrators_nbr,
                        'default_close_total_hours':            self.close_total_hours,
                        'default_parts_nbr':                    self.parts_nbr,
                        'default_parts_female_total_nbr':       self.parts_female_total_nbr,
                        'default_parts_female_total_done_nbr':  self.parts_female_total_done_nbr,
                        'default_students_finals_nbr':          self.students_finals_nbr,
                        'default_students_final_tests_nbr':     self.students_final_tests_nbr,
                        'default_students_parts_tests_nbr':     self.students_parts_tests_nbr,
                        'default_course_administrators_nbr':    self.course_administrators_nbr}
        }

    @api.multi
    def action_student_course_subscription(self):
        return {
            'name': _('تسجيل الطلاب في الدورة'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'student.course.subscription',
            'target': 'new',
            'context': {'default_course_id': self.id}
        }

    @api.multi
    def action_reset_accept(self):
        self.write({'state':'accept'})

    @api.model
    def archive_cron_fct(self):
        active_requests = self.env['mk.course.request'].search([('active', '=', True)])
        for request in active_requests:
            request.active = False

    @api.constrains('no_day_copy')
    def check_no_day_copy(self):
        no_day_copy = self.no_day_copy
        minimum_no_day = self.course.minimum_no_day
        if no_day_copy < minimum_no_day:
            raise ValidationError('عدد أيام الدورة غير متوافق مع الشروط ! يجب أن لا تقل عن الحد الأدنى للأيام المحدد في نوع البرنامج')

    @api.constrains('no_student', 'mosque_id')
    def check_no_student(self):
        gender_mosque = self.mosque_id.gender_mosque
        if gender_mosque == 'male' and self.no_student < 50:
            raise ValidationError('عدد الطلاب يجب أن لا يقل عن 50')
        if gender_mosque == 'female' and self.no_student < 30:
            raise ValidationError('عدد الطلاب يجب أن لا يقل عن 30')

    @api.constrains('commit')
    def check_commit(self):
        commit = self.commit
        if not commit:
            raise ValidationError("الرجاء الموافقة على شزوط الدورات المكثفة !")

    @api.model
    def create(self, vals):
        del vals["mosque_location"]
        sequence = self.env['ir.sequence'].next_by_code('mk.intensive.course.request.serial')
        vals['course_request_code'] = sequence
        tools.image_resize_images(vals)

        new_record = super(mk_courses_request, self).create(vals)
        #self.mosque_location=False
        self.clear_caches()
        return new_record

    @api.multi
    def write(self,vals):
        self.ensure_one()
        employee = self.env['hr.employee'].search([('user_id','=',self.env.uid)])
        self.clear_caches()

        # if self.state == 'accept' and (employee.category2 != 'center_admin' and self.env.uid != 1):
        #     raise ValidationError("عذرا! لايمكنك التعديل علي هذة الدورة بعد الموافقة")
        #if 'course_request_code' not in vals:
        if not self.course_request_code:
            sequence = self.env['ir.sequence'].next_by_code('mk.intensive.course.request.serial')
            vals['course_request_code'] = sequence
        tools.image_resize_images(vals)
        return super(mk_courses_request, self).write(vals)

    @api.multi
    def unlink(self):
        user = self.env.user
        if user.id != self.env.ref('base.user_root').id:
            raise ValidationError ('لا يمكنك حذف طلب الدورة')
        return super(mk_courses_request, self).unlink()

    @api.onchange('mosque_location')
    def on_change_mosque(self):
        self.clear_caches()
        if self.mosque_location:
            self.mosque_location_cc = self.mosque_location.name
            msq_location_id = self.mosque_location.id
            self.mosque_location_id = self.mosque_location.id
            self.mosque_location = False
            self.flag=True
            return {'domain':{'epsoide_ids':[('mosque_id', '=', msq_location_id)]}}

    @api.onchange('study_class_id')
    def on_change_study_class_id(self):
        self.course = False

    @api.onchange('mosque_id')
    def on_change_mosque_id(self):
        if self.mosque_id:
            self.clear_caches()
            self.admin_id = self.mosque_id.sudo().responsible_id.id
            self.mobile_admin = self.mosque_id.sudo().responsible_id.mobile_phone
            self.partner_latitude = self.mosque_id.latitude
            self.partner_longitude = self.mosque_id.longitude
            self.state_id = self.mosque_id.district_id.id

    @api.onchange('employee_id')
    def on_change_employee_id(self):
        if self.employee_id:
            self.mobile = self.employee_id.mobile_phone
            self.emp_sec = self.employee_id.name
            self.flag2 = True

    @api.onchange('location')
    def on_change_location(self):
        self.partner_latitude = False
        self.partner_longitude = False

    @api.onchange('center_id')
    def get_mosques(self):
        mosque_ids=self.env['mk.mosque'].search([('center_department_id','=',self.center_id.id)]).ids
        return {'domain':{'mosque_id':[('id','in',mosque_ids)]}}

    @api.one
    def reject(self):
        self.write({'state':'reject'})

    def send_email_accept_intensive_course_request(self):
        try:
            template = self.env['ir.model.data'].sudo().get_object('mk_intensive_courses','mail_accept_intensive_course_request_template')
            if template:
                template.send_mail(self.id, force_send=True)

        except:
            pass

    @api.one
    def accept(self):
        self.write({'state':'accept'})
        self.send_email_accept_intensive_course_request()

    def send(self):
        self.ensure_one()
        self.write({'state': 'send'})
        view = self.env.ref('mk_intensive_courses.message_wizard_form')
        wiz = self.env['message.wizard'].create({'message': ("طلبكم قيد المراجعة وخلال خمسة أيام عمل يأتي الرد")})
        return {
            'name': _('ارسال الطلب'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
        }

    @api.one
    def draft(self):
        self.write({'state':'draft'})

    @api.multi
    def geo_localize(self):
        # We need country names in English below
        for partner in self.with_context(lang='ar_SY'):
            result = geo_find(geo_query_address(city=partner.mosque_id.city_id.name,
                                                state=partner.mosque_id.district_id.name,
                                                country=partner.mosque_id.city_id.country_id.name))

            if result is None:
                result = geo_find(geo_query_address(city=partner.mosque_id.city_id.name,
                                                    state=partner.mosque_id.district_id.name,
                                                    country=partner.mosque_id.city_id.country_id.name))

            if result:
                partner.write({'partner_latitude': result[0],
                               'partner_longitude': result[1],
                               'date_localization': fields.Date.context_today(partner)})
        return True

    @api.onchange('epsoide_ids')
    def on_change_epsoide_ids(self):
        list1=[]
        ls=[]
        if self.epsoide_ids:
            for epsoide in  self.epsoide_ids:
                ls.append((0, 0, {'emp_id' :epsoide.teacher_id.id,
                                  'category_id':'teacher',}))
                self.emp_ids=ls
                for student in epsoide.students_list:
                    list1.append(student.student_id.id)
                    self.student_ids=[(0,0,{'student_id':rec}) for rec in list1]

    @api.depends('student_ids','no_student')
    def calc_student_seats(self):
        self.no_seats = self.no_student - len(self.student_ids)

    @api.model
    def get_courses_count(self):
        count = 0
        accepted_courses = self.env['mk.course.request'].search([('state', '=', 'accept'),
                                                                                                 '|', ('active', '=', True),
                                                                                                      ('active', '=', False)])
        if accepted_courses:
            count = len(accepted_courses)
        return count

    @api.model
    def get_intensive_course_details(self, course_id):
        course_details = []
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        course = self.env['mk.course.request'].search([('id', '=', int(course_id)),
                                                                    '|', ('active', '=', True),
                                                                         ('active', '=', False)], limit=1)
        if course:
            if course.course_request_type == 'quran_day':
                course_type = 'يوم قراني'
            if course.course_request_type == 'ramadan_course':
                course_type = 'دورة رمضانية'
            else:
                course_type = 'دورة مكثفة'
            course_details.append({'course_name':          course.course_name,
                                    'course_request_code': course.course_request_code,
                                    'course_request_type': course_type,
                                    'start_date':          course.start_date,
                                    'end_date':            course.end_date,
                                    'state':               course.state,
                                    'branches_ids':        course.branches_ids.ids,
                                    'mosque_id':           course.mosque_id.id,
                                    'mosque_name':         course.mosque_id.display_name,
                                    'study_class_id':      course.study_class_id.id,
                                    'emp_sec':             course.emp_sec,
                                    'admin_id':            course.admin_id.id,
                                    'admin_name':            course.admin_id.name,
                                    'course_episode_nbr':  course.course_episode_nbr,
                                    'no_student':          course.no_student,
                                    'no_day':              course.no_day,
                                   'logo'   :              '%s/web/binary/image/?model=%s&field=image&id=%s' % (base_url,'mk.course.request',course.id)})

        return course_details

    @api.model
    def get_intensive_course_branches(self, course_id):
        try:
            course_id = int(course_id)
        except:
            pass
        branches = []
        course = self.env['mk.course.request'].search([('id', '=', course_id),
                                                        '|', ('active', '=', True),
                                                             ('active', '=', False)], limit=1)
        if course:
            branch_ids = course.branches_ids
            for branch in branch_ids:
                branches.append({'branch_id':   branch.id,
                                 'branch_name': branch.display_name,})
        return branches

    @api.multi
    def open_view_student_courses(self):
        tree_view = self.env.ref('mk_intensive_courses.mk_student_course_tree_view')
        search_id = self.env.ref('mk_intensive_courses.mk_student_course_view_search')
        return {'name':       "/"+"المسجلين"+"/" ,
                 'res_model': 'mk.course.student',
                'res_id':    'mk.course.student',
                'views':     [(tree_view.id, 'tree'),(False, 'form')],
                'type':      'ir.actions.act_window',
                'target':    'current',
                'domain':    [('request_st_id','=',self.id)],
                'search_view_id': search_id.id}

    @api.multi
    def update_course_request_data(self):
        form_id = self.env.ref('mk_intensive_courses.course_request_update_wizard_form_view')
        vals = {
            'name': _('تعديل البيانات'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'course.request.update.wizard',
            'views': [(form_id.id, 'form')],
            'view_id': form_id.id,
            'context': {'default_study_class_id': self.study_class_id.id,
                        'default_academic_id': self.academic_id.id,
                        'default_location': self.location,
                        'default_external_mosq_name': self.external_mosq_name,
                        'default_course_id': self.id
                        },
            'target': 'new',
        }
        return vals

    @api.model
    def update_episodes_linked_with_updated_course_requests(self):
        course_requests = self.env['mk.course.request'].search([('study_class_id', '=', 108)])
        i = 0
        total = len(course_requests)
        for course in course_requests:
            i += 1
            mosque = course.mosque_id
            episode_season_ids = set()
            course_requests = mosque and mosque.course_request_ids or []
            for course_request in course_requests:
                if course_request.study_class_id.id != 108:
                    continue
                episode_season_ids.add(course_request.id)
            episodes = self.env['mk.episode'].search([('study_class_id', '=', 108),
                                                      ('mosque_id', '=', mosque.id)])
            for episode in episodes:
                episode.episode_specific_ids = list(episode_season_ids)

    @api.multi
    def print_close_certificate(self):
        if self.course_request_type == 'quran_day':
            res = self.env.ref('mk_intensive_courses.close_quran_day_course_data_id').report_action(self)
        else:
            res = self.env.ref('mk_intensive_courses.close_course_data_id').report_action(self)
        return res


class Mosque(models.Model):
    _inherit = 'mk.mosque'

    course_request_ids = fields.One2many('mk.course.request', 'mosque_id', string='Courses', domain=[('state','=','accept')])


class Episode(models.Model):
    _inherit = 'mk.episode'

    @api.one
    @api.depends('mosque_id','mosque_id.course_request_ids','study_class_id')
    def get_episode_ids(self):
        mosque = self.mosque_id
        study_class_id = self.study_class_id.id
        episode_season_ids = set()
        course_requests = mosque and mosque.course_request_ids or []
        for course_request in course_requests:
            if course_request.study_class_id.id != study_class_id:
                continue

            episode_season_ids.add(course_request.id)
        self.episode_specific_ids = list(episode_season_ids)

    episode_specific_ids = fields.Many2many('mk.course.request', string='نطاق الدورات الموسمية', compute=get_episode_ids, store=True)
    episode_season_id    = fields.Many2one('mk.course.request',  string='الدورات الموسمية')

    @api.model
    def data_set_domain_ep_season(self):
        eps = self.search([])
        nbr = len(eps)
        i = 1
        j = 1
        for ep in eps:
            mosque = ep.mosque_id
            episode_season_ids = set()
            course_requests = mosque and mosque.course_request_ids or []
            for course_request in course_requests:
                episode_season_ids.add(course_request.id)

            ep.episode_specific_ids = list(episode_season_ids)
            vals = {}
            semester = ep.study_class_id
            if not semester:
                semester = ep.parent_episode.study_class_id

            if not ep.start_date:
                vals.update({'start_date': semester.start_date})

            if not ep.end_date:
                vals.update({'end_date': semester.end_date})

            if not ep.episode_season:
                vals.update({'episode_season': 'normal'})

            ep.write(vals)
            if j == 50:
                j = 0

            i += 1
            j += 1


class mk_courses_emp(models.Model):
    _name = 'mk.course.emp'

    @api.onchange('category_id')
    def on_change_category_id(self):
        if self.category_id:
            return {'domain':{'emp_id':[('category', '=', self.category_id)]}}

    emp_type           = fields.Selection([('internal', 'Internal'),
                                           ('external', 'External')], string="Employee Type")
    emp_id             = fields.Many2one('hr.employee',       string="Employee")
    request_id         = fields.Many2one('mk.course.request', string="Request")
    category_id        = fields.Selection([('teacher', 'teacher'),
                                           ('admin','Admin')], string="Category")
    mosque_location_id = fields.Integer(string='mosque location id')


class Update_courses_student(models.TransientModel):
    _name = 'mk.course.student.update'

    branch_id      = fields.Many2one("mk.parts.names", string="الفرع")
    student_course = fields.Many2one('mk.course.student')

    @api.one
    def action_update_branch(self):
        self.student_course.write({'branch_id': self.branch_id.id})


class mk_courses_student(models.Model):
    _name = 'mk.course.student'
    _inherit = ['mail.thread']
    _rec_name = 'student_id'

    student_id         = fields.Many2one('mk.student.register', string="Student", required=1, ondelete='cascade', track_visibility='onchange')
    no_identity        = fields.Boolean('No Identity', compute='get_student_details', store=True, track_visibility='onchange')
    identity_no        = fields.Char('Identity No',    compute='get_student_details', store=True, track_visibility='onchange')
    passport_no        = fields.Char('Passport No',    compute='get_student_details', store=True, track_visibility='onchange')
    mobile             = fields.Char('Mobile',         compute='get_student_details', store=True, track_visibility='onchange')
    email              = fields.Char('Email',          compute='get_student_details', store=True, track_visibility='onchange')
    nationality        = fields.Char('الجنسية' ,       compute='get_student_details', store=True, track_visibility='onchange')
    birthdate          = fields.Date('Birthdate',      compute='get_student_details', store=True, track_visibility='onchange')
    gender             = fields.Selection([('male', 'Male'),
                                           ('female', 'Female')], string="Gender",  default="male",  compute='get_student_details', store=True, track_visibility='onchange')
    attende            = fields.Boolean('attendance')
    request_st_id      = fields.Many2one('mk.course.request',   string="Course request", required=1)
    mosque_id          = fields.Many2one(related='request_st_id.mosque_id', store=True)
    mosque_location_id = fields.Integer('mosque location id')
    branch_id          = fields.Many2one("mk.parts.names" ,string="الفرع")
    branch_path_type   = fields.Selection([('momorize', 'Momorize'),
                                           ('review','Reveiw'),
                                           ('correct_recitation','Correct recitation')], string="Branch Path")

    def action_change_branch(self):
        course_request = self.env['mk.course.request'].browse(self.env.context.get('active_id'))
        branch = self.branch_id
        student_branch_update_form = self.env.ref('mk_intensive_courses.branch_form_wizard')
        action_vals = {
            'name': _('تعديل الفرع'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mk.course.student.update',
            'views': [(student_branch_update_form.id, 'form')],
            'view_id': student_branch_update_form.id,
            'target': 'new',
            'context': {'default_branch_id': branch.id,
                        'default_student_course': self.id,
                        'course_request_branch_ids': course_request.branches_ids.ids},
        }
        return action_vals

    def action_delete_course_subscription(self):
        self.unlink()

    @api.model
    def student_course_subscription(self, data):

        identity_no = data['identity_no']
        no_identity = data['no_identity']
        if not no_identity:
            data['passport_no'] = False

        passport_no = data['passport_no']
        nationality = data['nationality']

        if 'branch_path_type' in data:
            branch_path_type = data['branch_path_type']
        else:
            branch_path_type = False

        course_request = data['course_request']
        branch_id = data['branch_id']

        course_student = False
        course_id = self.env['mk.course.request'].search([('id', '=',course_request)], limit=1)

        existing_student = False
        domain = ['|', ('active', '=', True),('active', '=', False)]
        if not no_identity:
            existing_students = self.env['mk.student.register'].search([('identity_no', '=', identity_no),
                                                                       ('no_identity', '!=', True)]  + domain, limit=2)
            if len(existing_students) == 2:
                raise models.ValidationError('عذرا ! الطالب مكرر في النظام')

            if existing_students:
                existing_student = existing_students[0]
        else:
            if len(passport_no) != 10:
                raise models.ValidationError('عذرا ! رقم جواز السفر خاطئ')
            existing_students = self.env['mk.student.register'].search([('passport_no', '=', passport_no),
                                                                       ('no_identity', '=', True)]  + domain, limit=2)

            if len(existing_students) == 2:
                raise models.ValidationError('عذرا ! الطالب مكرر في النظام')

            total = 0
            i = 0
            while i < len(passport_no):
                temp = int(passport_no[i]) * 2
                temp = str(temp).ljust(2, '0')
                # adding a "0" digit to the number in case the number is less than 10
                # to prevent index error in the next line
                # example: 3 * 2 = 6 => 60  ,  8 * 2 = 16 => 16
                total += int(temp[0]) + int(temp[1])
                i += 1
                total += int(passport_no[i])
                i += 1

            # check if the validation is correct
            if total % 10 == 0:
                if passport_no[0] == '1':
                    raise models.ValidationError('عذرا ! الرقم المستخدم رقم هوية')

                if passport_no[0] == '2':
                    raise models.ValidationError('عذرا ! الرقم المستخدم رقم إقامة')

            if existing_students:
                existing_student = existing_students[0]

        data['country_id'] = int(nationality)
        data.pop('nationality')

        if existing_student:
            student = existing_student
            if not student.active:
                student.active = True
            if student.mosq_id == False:
                student.mosq_id = course_id.mosque_id.id
            student.write(data)
        else:
            data['mosq_id'] = course_id.mosque_id.id
            data['district_id'] = course_id.mosque_id.district_id.id
            student = self.env['mk.student.register'].create(data)


        existing_suscription = self.env['mk.course.student'].search([('student_id', '=', student.id),
                                                                     ('request_st_id', '=', int(course_request))], limit=1)

        if not existing_suscription:
            course_student = self.env['mk.course.student'].create({'student_id':     student.id,
                                                                   'request_st_id':  course_request,
                                                                   'branch_id':      branch_id and int(branch_id),
                                                                   'branch_path_type': branch_path_type})

        vals = {'registration_code': student and student.registeration_code or False,
                'course_student':    course_student and course_student.id}

        return str(vals)

    @api.depends('student_id')
    def get_student_details(self):
        for rec in self:
            student = rec.student_id
            rec.no_identity = student.no_identity
            rec.identity_no = student.identity_no
            rec.passport_no = student.passport_no
            rec.mobile = student.mobile
            rec.email = student.email
            rec.nationality = student.nationality
            rec.birthdate = student.birthdate
            rec.gender = student.gender


class mk_student_register(models.Model):
    _inherit = 'mk.student.register'

    student_course_ids = fields.One2many('mk.course.student', 'student_id', string="البرامج المكثفة")


class MkParts(models.Model):
    _name = 'mk.parts.names'
    _inherit = ['mail.thread']
    _order = 'order'

    name  = fields.Char('Name',     track_visibility='onchange')
    order = fields.Integer('Order', track_visibility='onchange')