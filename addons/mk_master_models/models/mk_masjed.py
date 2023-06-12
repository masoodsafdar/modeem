#-*- coding:utf-8 -*-
from odoo import models, fields, api, tools, _
from datetime import datetime
import math
import xmlrpc.client as xmlrpclib
from odoo.exceptions import UserError, ValidationError
import os.path
import sys
# Add the directory containing the configuration file to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..', 'conf_files')))
# from conf import ERP_DB, ERP_HOST, ERP_USER, ERP_PASSWORD


import logging
_logger = logging.getLogger(__name__)

    
class Mkmosque(models.Model):
    _name = 'mk.mosque'
    _inherit = ['mail.thread']

    @api.depends('write_date')
    def get_mosq_subscription_url(self):
        for rec in self:
            rec.mosq_subscription_url= "http://edu.maknon.org.sa/showmosques/" + str(rec.id)

    @api.depends('episode_id')
    def get_teachers(self):
        for rec in self:
            teacher_ids=self.env['hr.employee'].sudo().search([('mosqtech_ids', '=', rec.id), 
                                                               ('category','=','teacher')])
            #rec.teacher_ids=teacher_ids
            rec.teachers_number=len(teacher_ids)     
            
    @api.depends('episode_id')
    def get_episode(self):
        for rec in self:
            episode_ids = self.env['mk.episode'].sudo().search([('mosque_id', '=', rec.id),
                                                                ('state', 'in', ['draft','accept'])])
            rec.episodes_number = len(episode_ids)     
            
    @api.depends('episode_id')
    def get_others_emp(self):
        for rec in self:
            #rec.teacher_ids=teacher_ids
            rec.others_emp_number=len(rec.mosq_other_emp_ids)

    # @api.multi
    def _compute_students(self):
        for rec in self:
            student_ids=self.env['mk.student.register'].sudo().search([('mosq_id', '=', rec.id)])
            rec.student_numbers = len(student_ids)
    
    # @api.one
    @api.depends('categ_id')
    def get_gender_mosque(self):
        self.gender_mosque = self.categ_id.mosque_type
        
    # @api.multi
    @api.depends('name','episode_value')
    def name_get(self):
        res = []
        for rec in self:
            name_mosque = rec.name or " "
            if rec.is_complexe and rec.complex_name:
                name_mosque += '/' + rec.complex_name
            episode_value = rec.episode_value

            if rec.district_id:
                name_mosque += ' - ' + rec.district_id.name

            if episode_value == 'ev':
                name_mosque += ' ' + '[' + ' ' + 'مسائية' + ' ' + ']'

            elif episode_value == 'mo':
                name_mosque += ' ' + '[' + ' ' + 'صباحية' + ' ' + ']'

            res.append((rec.id, name_mosque))

        return res

    name                    = fields.Char('Name', required=True, track_visibility='onchange')
    image                   = fields.Binary("Image",              attachment=True)
    image_medium            = fields.Binary("Medium-sized image", attachment=True)
    image_small             = fields.Binary("Small-sized image",  attachment=True)
    responsible_id          = fields.Many2one('hr.employee', string='Responsible', domain=[('category','=','admin')], track_visibility='onchange')
    one_way_money           = fields.Integer('one way money', track_visibility='onchange')
    double_way_money        = fields.Integer('Double way money', track_visibility='onchange')
    build_type              = fields.Many2one('mk.building.type', string='build type', track_visibility='onchange')
    mosq_subscription_url   = fields.Char(string='رابط تسجيل الطلاب في المسجد', compute=get_mosq_subscription_url, store=True, track_visibility='onchange')
    permision_date          = fields.Date('تاريخ التصريح',        track_visibility='onchange')
    permision_end_date      = fields.Date('Permisiion  End Date', track_visibility='onchange')
    responsible_end_date    = fields.Date('تاريخ التصريح للمشرف', track_visibility='onchange')
    responsible_type        = fields.Selection([('1', 'تجديد'),
                                                ('2', 'تحويل'),
                                                ('3', 'إلغاء'),
                                                ('4', 'تجميد')], string="نتيجة التصريح للمشرف", track_visibility='onchange')
    permision_type          = fields.Selection([('pe', 'دائم'),
                                                ('te', 'مؤقت')], string="نوع التصريح", track_visibility='onchange')
    mosque_type             = fields.Selection([('1', 'تجديد'),
                                                ('2', 'تحويل'),
                                                ('3', 'إلغاء'),
                                                ('4', 'تجميد')], string="نتيجة التصريح", track_visibility='onchange')
    teacher_ids             = fields.Many2many("hr.employee", "mosque_relation", "emp_id", "mosq_id", string="Teachers", domain=[('category','=','teacher')])
    episodes                = fields.Char('Episodes', track_visibility='onchange')
    episode_value           = fields.Selection([('mo', 'Early'),
                                                ('ev', 'Late')], string="دوام الحلقات", track_visibility='onchange')
    teachers_number         = fields.Integer('Teachers no', default=0, compute=get_teachers)
    mosq_other_emp_ids      = fields.Many2many("hr.employee", "mosque_relation", "emp_id", "mosq_id", string="others supervisors", domain=[('category','=','managment')])
    others_emp_number       = fields.Integer('other num', default=0, compute=get_others_emp)
    city_id                 = fields.Many2one('res.country.state', string='City',     required=True, domain=[('type_location','=','city'), 
                                                                                                               ('enable','=',True)], track_visibility='onchange')
    area_id                 = fields.Many2one('res.country.state', string='Area',     required=True, domain=[('type_location','=','area'), 
                                                                                                               ('enable','=',True)], track_visibility='onchange')
    district_id             = fields.Many2one('res.country.state', string='District', required=True, domain=[('type_location','=','district'),
                                                                                                             ('enable','=',True)], track_visibility='onchange')
    episode_id              = fields.One2many('mk.episode', 'mosque_id',string='Episode', domain=[('state','=','accept')])
    latitude                = fields.Char('Latitude',  track_visibility='onchange')
    longitude               = fields.Char('Longitude', track_visibility='onchange')
    episodes_number         = fields.Integer(compute=get_episode, string="episode numbers")
    # student_number          = fields.Integer(string="Students numbers", compute='_compute_students')
    student_numbers          = fields.Integer(string="Students numbers", compute='_compute_students')
    respons_moques_ids      = fields.One2many('responsible.mosque', 'response_id', string='Responsible',)
    state                   = fields.Selection([('draft',     'Draft'),
                                                ('permision', 'طلب تصريح'),
                                                ('accept',    'Accepted'),
                                                ('reject',    'Rejected'),], default='draft', string='State', track_visibility='onchange')
    supervisors             = fields.Many2many("hr.employee", "mosque_relation", "emp_id", "mosq_id", string="supervisors", domain=[('category','in',['admin','supervisor'])])    
    categ_id                = fields.Many2one('mk.mosque.category', string='Category', required=True, track_visibility='onchange')
    is_complexe             = fields.Boolean(related='categ_id.is_complexe')
    complex_name            = fields.Char('Complexe', track_visibility='onchange')
    register_code           = fields.Char('Register Code', readonly=True,     track_visibility='onchange')
    check_maneg_mosque      = fields.Boolean('Find mange episodes in mosque', track_visibility='onchange')
    check_parking_mosque    = fields.Boolean('Find parking in mosque',        track_visibility='onchange')
    link_ids                = fields.One2many("event.link", 'link_id',    string="Link")
    managment_id            = fields.Many2many("hr.employee", "mosque_relation", "emp_id", "mosq_id", string='أداري \أداريين المسجد', domain=[('category2','=','managment')])
    center_department_id    = fields.Many2one('hr.department', string='المركز', readonly=True, track_visibility='onchange')
    attach_no               = fields.Char("Attachment No", track_visibility='onchange')
    res_identity            = fields.Char(related='responsible_id.identification_id', string="رقم الهوية", track_visibility='onchange')
    edu_supervisor          = fields.Many2many('hr.employee',        string='Educational supervisor', domain=[('category','=','edu_supervisor')])
    gateway_config          = fields.Many2one('mk.smsclient.config', string='gateway config', required=False, track_visibility='onchange')
    gateway_user            = fields.Char('Gateway user',     size=50, track_visibility='onchange')
    gateway_password        = fields.Char('Gateway password', size=50, track_visibility='onchange')
    gateway_sender          = fields.Char('Gateway sender',   size=50, track_visibility='onchange')
    send_time               = fields.Float('Send time',       default=0.0, digits=(16, 2), track_visibility='onchange')
    phone                   = fields.Char('هاتف المسجد',             track_visibility='onchange')
    fax                     = fields.Char('فاكس المسجد',             track_visibility='onchange')
    email                   = fields.Char('البريد اﻹلكتروني للمسجد', track_visibility='onchange')
    mosque_addres           = fields.Char('عنوان المسجد',            track_visibility='onchange')
    mosque_secondary_addres = fields.Char('العنوان الثانوي للمسجد',  track_visibility='onchange')
    mosque_link             = fields.Char('رابط المسجد',             track_visibility='onchange')
    mosque_logo             = fields.Binary(attachment=True, string="شعار المسجد ( 380 * 200 مفرغ )")
    mosque_logo_two         = fields.Binary(attachment=True, string="شعار المسجد ( 110 * 84 مفرغ )")
    mosque_info             = fields.Text('معلومات عن المسجد', track_visibility='onchange')
    page_theme              = fields.Selection([('dark_green',  'اخضر غامق'),
                                                ('light_green', 'اخضر فاتح'), 
                                                ('light_blue',  'ازرق فاتح'), 
                                                ('dark_blue',   'ازرق غامق'),
                                                ('red',         'احمر'), 
                                                ('pink',        'وردي'), 
                                                ('light_gray',  'رمادي فاتح'), 
                                                ('dark_gray',   'رمادي غامق'),
                                                ('orange',      'برتقالي'), 
                                                ('yellow',      'اصفر'), 
                                                ('bege',        'بيجي')], string='الثيم الخاص بالصفحة', track_visibility='onchange')    
    first_student_image     = fields.Binary("الصورة  ( 200 * 200)", attachment=True)
    second_student_image    = fields.Binary("الصورة  ( 200 * 200)", attachment=True)
    third_student_image     = fields.Binary("الصورة  ( 200 * 200)", attachment=True)
    fourth_student_image    = fields.Binary("الصورة  ( 200 * 200)", attachment=True)
        
    is_specific_eval        = fields.Boolean('قياس وتقييم خاص', track_visibility='onchange')
    #Small Review
    lessons_minimum_audit   = fields.Float('Lessons Minimum Audit',   track_visibility='onchange')
    quantity_minimum_audit  = fields.Float('Quantity Minimum Audit',  track_visibility='onchange')
    deduct_qty_small_review = fields.Float('مقدار الخصم',             track_visibility='onchange')
    memorize_minimum_audit  = fields.Float('Memorize Minimum Audit',  track_visibility='onchange')
    deduct_memor_sml_review = fields.Float('مقدار الخصم',             track_visibility='onchange')
    mastering_minimum_audit = fields.Float('Mastering Minimum Audit', track_visibility='onchange')
    deduct_tjwd_sml_review  = fields.Float('مقدار الخصم',             track_visibility='onchange')
    #Big Review
    lessons_maximum_audit    = fields.Float('Lessons Maximum Audit',  track_visibility='onchange')
    quantity_maximum_audit  = fields.Float('Quantity Maximum Audit',  track_visibility='onchange')
    deduct_qty_big_review   = fields.Float('مقدار الخصم',             track_visibility='onchange')
    memorize_maximum_audit  = fields.Float('Memorize Maximum Audit',  track_visibility='onchange')
    deduct_memor_big_review = fields.Float('مقدار الخصم',             track_visibility='onchange')
    mastering_maximum_audit = fields.Float('Mastering Maximum Audit', track_visibility='onchange')
    deduct_tjwd_big_review  = fields.Float('مقدار الخصم',             track_visibility='onchange')
    #Tlawa
    lessons_reading         = fields.Float('Lessons Reading',   track_visibility='onchange')
    quantity_reading        = fields.Float('Quantity Reading',  track_visibility='onchange')
    deduct_qty_reading      = fields.Float('مقدار الخصم',       track_visibility='onchange')
    memorize_reading        = fields.Float('Memorize Reading',  track_visibility='onchange')
    deduct_memor_reading    = fields.Float('مقدار الخصم',       track_visibility='onchange')
    mastering_reading       = fields.Float('Mastering Reading', track_visibility='onchange')
    deduct_tjwd_reading     = fields.Float('مقدار الخصم',       track_visibility='onchange')
    #Memorize
    lessons_memorize        = fields.Float('Lessons Memorize',   track_visibility='onchange')
    quantity_memorize       = fields.Float('Quantity Memorize',  track_visibility='onchange')
    deduct_qty_memorize     = fields.Float('مقدار الخصم',        track_visibility='onchange')
    memorize_degree         = fields.Float('Memorize Degree',    track_visibility='onchange')
    deduct_memor_memorize   = fields.Float('مقدار الخصم',        track_visibility='onchange')
    mastering_memorize      = fields.Float('Mastering Memorize', track_visibility='onchange')
    deduct_tjwd_memorize    = fields.Float('مقدار الخصم',        track_visibility='onchange')
    #Attendance
    preparation_degree         = fields.Float('Prepartion Degree',        track_visibility='onchange')
    late_deduct             = fields.Float('Late Deduct',                 track_visibility='onchange')
    excused_absence_deduct     = fields.Float('Excused Absence Deduct',   track_visibility='onchange')
    no_excused_absence_deduct = fields.Float('No Excused Absence Deduct', track_visibility='onchange')
    behavior_degree         = fields.Float('Behavior Degree',             track_visibility='onchange')
    #Test
    test_degree             = fields.Float('Test Degree',  track_visibility='onchange')
    nbr_question_test       = fields.Integer('عدد الأسئلة', track_visibility='onchange')
    qty_question_test       = fields.Selection([('qty001','آية'),
                                                ('qty025','ربع صفحة'),
                                                ('qty050','نصف صفحة'),
                                                ('qty075','ثلاثة ارباع صفحة'),
                                                ('qty100','صفحة واحدة'),
                                                ('qty125','صفحة وربع'),
                                                ('qty150','صفحة ونصف'),
                                                ('qty175','صفحة وثلاثة ارباع'),
                                                ('qty200','صفحتان'),], string='مقدار السؤال', track_visibility='onchange')
    deduction_test          = fields.Float('مقدار الخصم', track_visibility='onchange')
    #Exam
    exam_degree             = fields.Float('درجة الإختبار', track_visibility='onchange')
    nbr_question_exam       = fields.Integer('عدد الأسئلة', track_visibility='onchange')
    qty_question_exam       = fields.Selection([('qty001','آية'),
                                                ('qty025','ربع صفحة'),
                                                ('qty050','نصف صفحة'),
                                                ('qty075','ثلاثة ارباع صفحة'),
                                                ('qty100','صفحة واحدة'),
                                                ('qty125','صفحة وربع'),
                                                ('qty150','صفحة ونصف'),
                                                ('qty175','صفحة وثلاثة ارباع'),
                                                ('qty200','صفحتان'),], string='مقدار السؤال', track_visibility='onchange')
    deduction_exam          = fields.Float('مقدار الخصم', track_visibility='onchange')
       
    gender_mosque           = fields.Selection([('male','Male'),
                                                ('female','Female')], string="Mosque gender", compute=get_gender_mosque, store=True)
    mosq_category           = fields.Selection([('a', 'أ'),
                                                ('b', 'ب'),
                                                ('c','ج'),
                                                ('quran_complex','مجمع قراني'),
                                                ('edu_complex','مجمع تعليمي'),
                                                ('mosque','مسجد')], string='الفئة')
    close_date              = fields.Date('Close Date')
    reject_reason           = fields.Text('Reject Reason', track_visibility='onchange')

    is_synchronized_admin   = fields.Boolean('التحيين',default=False)
    mosq_type               = fields.Many2one('hr.department.category', string='الفئة في الاداري', invisible=True, track_visibility='onchange')
    code                    = fields.Char('Unified Code', readonly=True,     track_visibility='onchange')
    is_synchro_edu_admin  = fields.Boolean('الموائمة', default=False)
    has_permission        = fields.Boolean('يوجد تصريح' ,default=False)
    permission_status     = fields.Selection([('draft', 'مبدئي'),
                                              ('renew', 'تصريح مؤقت'),
                                              ('review', 'زيارة مشرف تربوي'),
                                              ('test', 'التقييم'),
                                              ('accept', 'تصريح دائم'),
                                              ('new', 'تجديد'),
                                              ('tajmeed', 'تجميد'),
                                              ('reject', 'مرفوض')], string='حالة التصريح', track_visibility='onchange')

    # @api.model
    # def create_from_portal(self, values):
    #     # sequence = self.env['ir.sequence'].next_by_code('mk.mosque.serial')
    #     # values['register_code'] = sequence
    #     _logger.debug("######################## Enter create_from_portal", values)
    #     tools.image_resize_images(values)
    #
    #     center_department_id = values.get('center_department_id', False)
    #     department_id = self.env['hr.department'].browse(center_department_id)
    #
    #     district_id = values.get('district_id', False)
    #     if not department_id:
    #         if district_id:
    #             district = self.env['res.country.state'].browse(district_id)
    #             department_id = district.center_department_id
    #
    #     db = ERP_DB
    #     user = ERP_USER
    #     password = ERP_PASSWORD
    #
    #     common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(ERP_HOST))
    #     models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(ERP_HOST))
    #     uid = common.authenticate(db, user, password, {})
    #
    #     categ_id = self.env['mk.mosque.category'].search([('id', '=', int(values.get('categ_id')) )] , limit=1)
    #     build_type_id = self.env['mk.building.type'].search([('id', '=', int(values.get('build_type')) )] , limit=1)
    #     district_id = self.env['res.country.state'].search([('type_location','=','district'),
    #                                                            ('enable','=',True),
    #                                                            ('id', '=', district_id )], limit=1)
    #
    #     values_dept = {"name": values.get('name'),
    #                    "episodes": values.get('episodes'),
    #                    # "register_code": values.get('register_code'),
    #                    "responsible_department": department_id.department_code,
    #                    "episode_value": values.get('episode_value'),
    #                    "mosque_category_id": categ_id.code,
    #                    "build_type_id": build_type_id.code,
    #                    "district_id": district_id.district_code,
    #                    "is_maneg_mosque": values.get('check_maneg_mosque'),
    #                    "is_parking_mosque": values.get('check_parking_mosque'),
    #                    "latitude": values.get('latitude'),
    #                    "longitude": values.get('longitude')}
    #     mosq_details = {}
    #     res = models.execute_kw(db, uid, password, 'hr.department', 'create_mosque', [values_dept])
    #     _logger.debug("######################## res" )
    #     if res:
    #         _logger.debug("######################## res" + str( res['mosque_id']))
    #         mosq_details.update({'mosque_id':     res['mosque_id'],
    #                              'register_code': res['register_code']})
    #     return mosq_details


    @api.model
    def delete_mosque(self, vals):
        return 1

    # @api.one
    def unlink(self):
        if self.active == True:
            if self.state == "accept":
                raise ValidationError(_('لا يمكنك حذف سجل تم تأكيده'))
            else:
                raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))
        else:
            return super(Mkmosque, self).unlink()
    # shaimaa solve recursion error
    # @api.multi
    # def write(self, values):
    #     user = self.env.user
    #     for rec in self:
    #         if user.id != self.env.ref('base.user_root').id:
    #             if rec.is_synchro_edu_admin:
    #                 if 'categ_id' in values and values.get('categ_id') != rec.categ_id.id:
    #                     raise ValidationError('عذرا لا يمكنك تعديل فئة المسجد/لمدرسة بعد الاعتماد و المراجعة من قبل التعليمي')
    #                 if 'mosq_type' in values and values.get('mosq_type') != rec.mosq_type.id:
    #                     raise ValidationError('عذرا لا يمكنك تعديل نوع الحلقة بعد الاعتماد و المراجعة من قبل التعليمي')
    #                 if 'name' in values:
    #                     raise ValidationError('عذرا لا يمكنك تعديل إسم المسجد/لمدرسة بعد الاعتماد و المراجعة من قبل التعليمي')
    #                 if 'complex_name' in values :
    #                     raise ValidationError('عذرا لا يمكنك تعديل إسم المجمع بعد الاعتماد و المراجعة من قبل التعليمي')
    #                 if 'district_id' in values and values.get('district_id') != rec.district_id.id:
    #                     raise ValidationError('عذرا لا يمكنك تعديل حي المسجد بعد الاعتماد و المراجعة من قبل التعليمي')
    #                 if 'center_department_id' in values and values.get('center_department_id') != rec.center_department_id.id:
    #                     raise ValidationError('عذرا لا يمكنك تعديل المركز بعد الاعتماد و المراجعة من قبل التعليمي')
    #
    #             if not user.has_group('mk_episode_management.group_mosque_name_edit'):
    #                 if 'name' in values:
    #                     raise ValidationError('عذرا لا يمكنك تعديل إسم المسجد/لمدرسة ')
    #                 if 'complex_name' in values :
    #                     raise ValidationError('عذرا لا يمكنك تعديل إسم المجمع ')
    #                 if 'categ_id' in values:
    #                     raise ValidationError('عذرا لا يمكنك تعديل فئة المسجد/لمدرسة')
    #             if not (self.env.context.get('from_permission')) and ('center_department_id' in values or 'mosq_type' in values or 'district_id' in values):
    #                 raise ValidationError('عذرا لا يمكنك تعديل بيانات المسجد')
    #         tools.image_resize_images(values)
    #         if 'active' in values:
    #             for rec in self:
    #                 rec.close_date = fields.Datetime.now()
    #     return super(Mkmosque, self).write(values)

    @api.constrains('register_code')
    def _check_register_code(self):
        mosque = self.env['mk.mosque'].search([('register_code', '=', self.register_code),
                                               ('id', '!=', self.id)], limit=1)
        if mosque:
            raise ValidationError(_('يوجد مسجد/مدرسة أخرى بنفس الكود'))

    # @api.multi
    def draft_validate(self):
        self.write({'state':'draft'})
        
    # @api.multi
    def reject_validate(self):
        view = self.env.ref('mk_master_models.mosq_reject_wizard_form')
        return {
            'name': _('Reject Reason'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mosq.reject.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
        }

    # @api.multi
    def accept_validate(self):
        self.write({'state':'accept'})

    # @api.multi
    def send_permision(self):
        eval_rec=self.env['mosque.eval'].search([])
        eval_location=self.env['mosque.eval.location'].search([])
        emp_rec=self.env['hr.employee'].search([('category2','=','teacher')])
        list1=[]
        list2=[]
        list3=[]
        
        for rec in eval_rec:
            for  eval_val in rec.eval_ids:
                list2.append((0,0,{'item_id':eval_val.item,'degree':eval_val.degree}))
                
        for rec in eval_location:
            for  item in rec.item_ids:
                if item.eval_calculate=='yes/no':
                    list1.append((0,0,{'item_id':item.item,'yes_no':item.yes_no}))
                else:
                    list1.append((0,0,{'item_id':item.item,'degree':item.degree,'check':True}))

        for teacher in emp_rec:
            for mosq in teacher.mosqtech_ids:
                if mosq.id==self.id:
                    list3.append((0,0,{'teacher_id':teacher.id}))         
 
        self.env['mosque.permision'].create({'masjed_id':self.id,
                                            'city_id':self.city_id.id,
                                            'area_id':self.area_id.id,
                                            'district_id':self.district_id.id,
                                            'state':'draft',
                                            'eval_lines':list2,
                                            'location_ids':list1,
                                            'code':self.register_code,
                                            'teacher_ids':list3})
        
        self.env['mosque.supervisor.request'].create({'center_id':self.center_department_id.id,
                                                      'mosque_id':self.id,
                                                      'employee_id':self.responsible_id.id,
                                                      'date_request':datetime.today().strftime('%m-%d-%Y'),
                                                      'identification_id':self.responsible_id.identification_id})
        self.write({'state':'permision'})
    
    @api.model
    def permision_schedular(self):
        mail = self.env['mail.message']
        msoq_rec = self.env['mosque.permision'].search(['|',('permision_type','=','pe'),
                                                            ('permision_type','=','te')])
        
        for rec in msoq_rec :
            if rec.permision_end_date:
                current_date = datetime.today()
                current_date = str(datetime.now().date())
                time = int((datetime.strptime(current_date, "%Y-%m-%d")-datetime.strptime(rec.permision_end_date, "%Y-%m-%d")).days)
                diff_date = math.fabs(time-1)
                time2 = int((datetime.strptime(current_date, "%Y-%m-%d")-datetime.strptime(rec.permision_end_date, "%Y-%m-%d")).days/ 30)
                diff_date2 = math.fabs(time2-1)
                rec.write({'remain':diff_date2})
                if diff_date == 60:
                    message = {'message_type': 'notification',
                               'subject': "انتهاء تصريح مسجد",
                               'body': "تبقي شهرين علي انتهاء تصريح المسجد %s" %rec.masjed_id.name,
                               'partner_ids':[(6, 0, [rec.masjed_id.center_department_id.manager_id.user_id.partner_id.id])]}
                    mail.create(message)

    # @api.one
    def set_draft(self):
        self.state = 'draft'

    #    shaimaa to solve recursion error
    # @api.multi
    # def open_episods(self):
    #     tree_view = self.env.ref('mk_episode_management.mk_episode_tree_view')
    #     #res_id=self.env['mk.episode'].search([('parent_episode','=',self.id),('selected_period','=','esha')])
    #     return {'name':       "/"+self.name+" / "+"الحلقات"+"/" ,
    #             'res_model': 'mk.episode',
    #             'res_id':    'mk.episode',
    #             'views':     [(tree_view.id, 'tree'),(False, 'form')],
    #             'type':      'ir.actions.act_window',
    #             'target':    'current',
    #             'domain':    [('mosque_id','=',self.id),
    #                           ('state', 'in', ['draft', 'accept'])]}

    # @api.multi
    def open_teacher(self):
        #tree_view = self.env.ref('mk_episode_management.mk_episode_form_view')
        #res_id=self.env['mk.episode'].search([('parent_episode','=',self.id),('selected_period','=','esha')])
        return {'name':"/"+self.name+" / "+"المعلمين"+"/" ,
                'res_model': 'hr.employee',
                'res_id': 'hr.employee',
                'views': [(False, 'kanban'),(False, 'tree'),(False, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain':[('mosqtech_ids','in',[self.id]),('category','=','teacher')]}

    # @api.multi
    def open_super(self):
        #tree_view = self.env.ref('mk_episode_management.mk_episode_form_view')
        #res_id=self.env['mk.episode'].search([('parent_episode','=',self.id),('selected_period','=','esha')])
        return {'name':"/"+self.name+" / "+"االمشرفين"+"/" ,
                'res_model': 'hr.employee',
                'res_id': 'hr.employee',
                'views': [(False, 'kanban'),(False, 'tree'),(False, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain':[('mosqtech_ids','in',[self.id]),('category','in',['supervisor','admin'])]}

    # @api.multi
    def open_other(self):
        return {'name':"/"+self.name+" / "+"الاداريين"+"/" ,
                'res_model': 'hr.employee',
                'res_id': 'hr.employee',
                'views': [(False, 'kanban'),(False, 'tree'),(False, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain':[('mosqtech_ids','in',[self.id]),('category','=','managment')]}

    @api.onchange('motivate_responsable')
    def onchange_motivate_responsable(self):
        if self.motivate_responsable:
            self.mobile = self.motivate_responsable.mobile_phone

    # @api.multi
    def open_student(self):
        #tree_view = self.env.ref('mk_episode_management.mk_episode_form_view')
        #res_id=self.env['mk.episode'].search([('parent_episode','=',self.id),('selected_period','=','esha')])
        return {'name':"/"+self.name+" / "+"الطلاب"+"/" ,
                'res_model': 'mk.student.register',
                'res_id': 'mk.student.register',
                'views': [(False, 'kanban'),(False, 'tree'),(False, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain':[('mosq_id','in',[self.id])]}

    @api.model
    def get_masjed_count(self):
        count = 0
        number_accepted_mosques = self.env['mk.mosque'].search([('state', '=', 'accept'),
                                                                '|',('active', '=', True),
                                                                    ('active', '=', False)])
        if number_accepted_mosques:
            count = len(number_accepted_mosques)
        return count

    @api.model
    def get_masjed(self,register_code):

        mosques = self.env['mk.mosque'].search([('register_code', '=', register_code),
                                                '|', ('active', '=', True),
                                                     ('active', '=', False)])
        mosques_list = []
        if mosques :
            for mosque in mosques:
                mosques_list.append({'id': mosque.id,
                                     'name': mosque.name,
                                     'latitude': mosque.latitude,
                                     'longitude': mosque.longitude})
        return mosques_list

    @api.model
    def get_district_mosque(self, district_id, mosque_type):
        try:
            district_id = int(district_id)
        except:
            pass
        mosque_type = mosque_type
        mosques = self.env['mk.mosque'].search([('district_id', '=', district_id),
                                                ('categ_id.mosque_type', '=', mosque_type),
                                                '|', ('active', '=', True),
                                                     ('active', '=', False)])
        mosq_list = []
        if mosques:
            for mosq in mosques:
                mosq_list.append({'id':       mosq.id,
                                  'name':     mosq.name,
                                  'type':     mosque_type,
                                  'lat':      mosq.latitude,
                                  'long':     mosq.longitude})
        return mosq_list

    @api.model
    def get_mosque(self, responsible_id, categ_type):
        try:
            responsible_id = int(responsible_id)
            categ_type = str(categ_type)
        except:
            pass

        mosques = self.env['mk.mosque'].search([('responsible_id', '=', responsible_id),
                                                ('categ_id.mosque_type', '=', categ_type),
                                                '|', ('active', '=', True),
                                                     ('active', '=', False)])
        mosque_list = []
        if mosques:
            for mosq in mosques:
                mosque_list.append({'id': mosq.id,
                                    'name': mosq.name})
        return mosque_list

    @api.model
    def get_response(self, center_id):
        try:
            center_id = int(center_id)
        except:
            pass

        item_list = []
        mosques = self.env['mk.mosque'].search([('center_department_id', '=', center_id)])
        if mosques:
            for mosq in mosques:
                responsible = mosq.responsible_id
                if responsible:
                    item_list.append({'responsible':  responsible.id,
                                       'name':        responsible.name})
        return item_list

    @api.model
    def get_mosque_details(self, mosque_id):
        try:
            mosque_id = int(mosque_id)
        except:
            pass

        mosque_details = []
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        mosque = self.env['mk.mosque'].search([('id', '=', mosque_id),
                                               '|', ('active', '=', True),
                                                    ('active', '=', False)], limit=1)
        if mosque:
            mosque_details.append({'name':                    mosque.name,
                                   'display_name':            mosque.display_name,
                                   'mosque_info':             mosque.mosque_info,
                                   'responsible_id':          mosque.responsible_id.id,
                                   'categ_id':                mosque.categ_id.id,
                                   'gender_mosque':           mosque.gender_mosque,
                                   'email':                   mosque.email,
                                   'area_id':                 mosque.area_id.id,
                                   'first_student_image':     '%s/web/binary/image/?model=%s&field=first_student_image&id=%s' % (base_url,'mk.mosque',mosque.id),
                                   'first_student':           mosque.first_student.display_name,
                                   'second_student_image':    '%s/web/binary/image/?model=%s&field=second_student_image&id=%s' % (base_url,'mk.mosque',mosque.id),
                                   'second_student':          mosque.second_student.display_name,
                                   'third_student_image':     '%s/web/binary/image/?model=%s&field=third_student_image&id=%s' % (base_url,'mk.mosque',mosque.id),
                                   'third_student':           mosque.third_student.display_name,
                                   'fourth_student_image':    '%s/web/binary/image/?model=%s&field=fourth_student_image&id=%s' % (base_url,'mk.mosque',mosque.id),
                                   'fourth_student':          mosque.fourth_student.display_name,
                                   'mosque_logo_two':         '%s/web/binary/image/?model=%s&field=mosque_logo_two&id=%s' % (base_url,'mk.mosque',mosque.id) ,
                                   'mosque_addres':           mosque.mosque_addres,
                                   'mosque_secondary_addres': mosque.mosque_secondary_addres,
                                   'page_theme':              mosque.page_theme})
        return mosque_details

    @api.model
    def filter_mosque(self, district_id):
        try:
            district_id = int(district_id)
        except:
            pass

        query_1 = '''
                  select m.id as mosque_id,
                  COALESCE (m.display_name, m.name) as mosque_name,
                  m.latitude as lat,
                  m.longitude as long,
                  m.episode_value as shift
                  from mk_mosque m left join mk_mosque_category c on m.categ_id=c.id
                  where m.active=True
                  and m.district_id={}

                  and m.state='accept'

                  and c.mosque_type='male';
                  '''.format(district_id)

        query_2 = '''
                  select m.id as mosque_id,
                  COALESCE (m.display_name, m.name) as mosque_name,
                  m.latitude as lat,
                  m.longitude as long,
                  m.episode_value as shift,
                  m.district_id
                  from mk_mosque m left join mk_mosque_category c on m.categ_id=c.id
                  where m.active=True
                  and m.district_id={}

                  and m.state='accept'

                  and c.mosque_type='female';
                  '''.format(district_id)

        self.env.cr.execute(query_1)
        male = self.env.cr.dictfetchall()

        self.env.cr.execute(query_2)
        female = self.env.cr.dictfetchall()

        data = {'male': male, 'female': female}
        return data

    @api.model
    def general_counters(self, mosque_id):
        try:
            mosque_id = int(mosque_id)
        except:
            pass

        query_string_none = ''' 
           select mosques.nbr_mosque, 
           episodes.nbr_episode, 
           supervisors.nbr_supervisor, 
           teachers.nbr_teacher, 
           students.nbr_student,
           final_exams.nbr_final_exam,
           normal_exams.nbr_normal_exam
           from
           (select count(*) nbr_mosque
           from mk_mosque
           where active=True
           and state='accept')mosques,

           (select count(*) nbr_episode
           from mk_episode_master
           where active=True
           and state='active')episodes,

           (select count(*) nbr_supervisor
           from hr_employee
           where active=True
           and state='accept'
           and category in ('supervisor','managment'))supervisors,

           (select count(*) nbr_teacher
           from hr_employee
           where active=True
           and state='accept'
           and category='teacher')teachers,

           (select count(*) nbr_student
           from mk_student_register
           where active=True
           and request_state='accept')students,

           (select count(studnt_id) nbr_final_exam
           from student_test_session
           where state='done' and
           type_test='final')final_exams,


           (select count(studnt_id) nbr_normal_exam
           from student_test_session
           where state='done' and
           type_test='parts' and
           studnt_id not in
           (select count(studnt_id)
           from student_test_session
           where state='done' and
           type_test='final'))normal_exams;
           '''
        query_string = ''' 
           select episodes.nbr_episode, 
           supervisors.nbr_supervisor, 
           teachers.nbr_teacher, 
           students.nbr_student,
           final_exams.nbr_final_exam,
           normal_exams.nbr_normal_exam
           from

           (select count(*) nbr_episode
           from mk_episode_master
           where active=True
           and state='active'
           and mosque_id={m})episodes,

           (select count(hr_employee.id) nbr_supervisor
           from hr_employee left join hr_employee_mk_mosque_rel on hr_employee.id = hr_employee_mk_mosque_rel.hr_employee_id
           where active=True
           and state='accept'
           and category in ('supervisor','managment')
           and mk_mosque_id={m})supervisors,

           (select count(hr_employee.id) nbr_teacher
           from hr_employee left join hr_employee_mk_mosque_rel on hr_employee.id = hr_employee_mk_mosque_rel.hr_employee_id
           where active=True
           and state='accept'
           and category='teacher'
           and mk_mosque_id={m})teachers,

           (select count(*) nbr_student
           from mk_student_register
           where active=True
           and request_state='accept'
           and mosq_id={m})students,

           (select count(studnt_id) nbr_final_exam
           from student_test_session
           where state='done' and
           type_test='final'and
           mosque_id={m})final_exams,

           (select count(studnt_id) nbr_normal_exam
           from student_test_session
           where state='done' and
           type_test='parts' and
           mosque_id={m} and
           studnt_id not in
           (select count(studnt_id)
           from student_test_session
           where state='done' and
           type_test='final'))normal_exams;
           '''.format(m=mosque_id)

        if not mosque_id:
            self.env.cr.execute(query_string_none)
        else:
            self.env.cr.execute(query_string)

        general_counters = self.env.cr.dictfetchall()

        return general_counters

    @api.model
    def get_dashboard_mosques_center(self, center_id):
        try:
            center_id = int(center_id)
        except:
            pass

        query_string = ''' 
               select id, name
               from mk_mosque
               where active=True and center_department_id={} order by id;
               '''.format(center_id)
        self.env.cr.execute(query_string)
        mosques_center = self.env.cr.dictfetchall()
        return mosques_center

    @api.model
    def get_dashboard_mosques_supervisor(self, department_id, type_mosque, supervisor_id):
        try:
            department_id = int(department_id)
            supervisor_id = int(supervisor_id)
            type_mosque = type_mosque
        except:
            pass

        if type_mosque not in ['male', 'female']:
            type_mosque = False

        sub_query_mosque = " "
        sub_query_edu_supervisor = " "

        if supervisor_id:
            sub_query_edu_supervisor = " LEFT JOIN hr_employee_mk_mosque_rel m_edu_sup ON m.id=m_edu_sup.mk_mosque_id "
            sub_query_mosque = " AND m.center_department_id=%s AND m.gender_mosque='%s' AND m_edu_sup.hr_employee_id=%s " % (
            department_id, type_mosque, supervisor_id)

        elif type_mosque:
            sub_query_mosque = " AND m.center_department_id=%s AND m.gender_mosque='%s' " % (department_id, type_mosque)

        elif department_id:
            sub_query_mosque = " AND m.center_department_id=%s " % (department_id)

        query_string = """SELECT distinct m.id id, m.name
                                FROM   mk_mosque m %s 
                                WHERE  m.active=True %s""" % (sub_query_edu_supervisor, sub_query_mosque)
        self.env.cr.execute(query_string)

        mosqs_supervisor = self.env.cr.dictfetchall()
        return mosqs_supervisor

    @api.model
    def get_dashboard_mosques_detail(self, department_id, type_mosque, mosque_id, supervisor_id):
        try:
            department_id = int(department_id)
            mosque_id = int(mosque_id)
            supervisor_id = int(supervisor_id)
            type_mosque = type_mosque
        except:
            pass

        if type_mosque not in ['male', 'female']:
            type_mosque = False

        sub_query_mosque = " "
        sub_query_edu_supervisor = " "

        if mosque_id:
            sub_query_mosque = " AND m.id=%s " % (mosque_id)

        elif supervisor_id:
            sub_query_edu_supervisor = " LEFT JOIN hr_employee_mk_mosque_rel m_edu_sup ON m.id=m_edu_sup.mk_mosque_id "
            sub_query_mosque += " AND m.center_department_id=%s AND m.gender_mosque='%s' AND m_edu_sup.hr_employee_id=%s " % (
            department_id, type_mosque, supervisor_id)

        elif type_mosque:
            sub_query_mosque = " AND m.center_department_id=%s AND m.gender_mosque='%s' " % (department_id, type_mosque)

        elif department_id:
            sub_query_mosque = " AND m.center_department_id=%s " % (department_id)

        ev = "evening"
        mo = "morning"

        query_string = """SELECT mosque.mosque_name mosque_name, mosque.mosque_is_write,

                          COALESCE(teacher.teacher_id, 0) all_teachers, COALESCE(teacher_update.teacher_id, 0) write_teachers, 
                          to_char(teacher_update.date_update, 'YYYY-MM-DD HH24:MI') teachers_updated_last, 

                          COALESCE(supervisor.supervisor_id, 0) all_supervisors, COALESCE(supervisor_update.supervisor_id, 0) write_supervisors, 
                          to_char(supervisor_update.date_update, 'YYYY-MM-DD HH24:MI') supervisors_updated_last,

                          COALESCE(edu_supervisor.edu_supervisor_id, 0) edu_supervisors, 
                          COALESCE(edu_supervisor_update.edu_supervisor_id, 0) write_edu_supervisors, 
                          to_char(edu_supervisor_update.date_update, 'YYYY-MM-DD HH24:MI') edu_supervisors_updated_last,

                          COALESCE(admin_emp.admin_emp_id, 0) admin_emps, COALESCE(admin_emp_update.admin_emp_id, 0) write_admin_emps, 
                          to_char(admin_emp_update.date_update, 'YYYY-MM-DD HH24:MI') admin_emps_updated_last, 

                          COALESCE(student.student_id, 0) all_students, COALESCE(student_update.student_id, 0) write_students, 
                          to_char(student_update.date_update, 'YYYY-MM-DD HH24:MI') students_updated_last,

                          COALESCE(episode.episode_id, 0) all_episodes, COALESCE(episode_update.episode_id, 0) write_episodes, 
                          to_char(episode_update.date_update, 'YYYY-MM-DD HH24:MI') episodes_updated_last  

                   FROM (SELECT distinct(m.id) mosque_id, 

                                case when m.episode_value='ev' then m.name||' '||'['||' '||'%s'||' '||']'
                                     when m.episode_value='mo' then m.name||' '||'['||' '||'%s'||' '||']'
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
                         GROUP BY m.id) episode_update ON episode_update.mosque_id=mosque.mosque_id;""" % ( ev, mo, sub_query_edu_supervisor, sub_query_mosque,
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

        mosques_detail = self.env.cr.dictfetchall()
        return mosques_detail

    @api.model
    def masjed_update(self, data):
        register_code = data['register_code']
        masjed_id = data['masjed_id']
        latitude = data['latitude']
        longitude = data['longitude']

        update = 1
        mosque_id = self.env['mk.mosque'].sudo().search([('id', '=', masjed_id),
                                                         ('register_code', '=', register_code)], limit=1)

        updated_mosq = mosque_id.sudo().write({'latitude': latitude,
                                               'longitude': longitude})
        if updated_mosq:
            update = 0
        return update

    @api.model
    def student_mosque_odoo(self, mosque_id, student_id):
        try:
            mosque_id = int(mosque_id)
            student_id = int(student_id)
        except:
            pass

        student_mosque = 1
        query_string = '''
                 INSERT INTO
                      public.mk_mosque_mk_student_register_rel
                      (mk_student_register_id,mk_mosque_id)
                       VALUES
                        ({},{}) RETURNING mk_student_register_id,mk_mosque_id;
                     '''.format(student_id, mosque_id)
        self.env.cr.execute(query_string)
        return_row = self.env.cr.dictfetchall()
        if return_row :
            student_mosque = 0
        return student_mosque

    @api.model
    def add_mosque_request(self, data):
        name = data['name'].encode('utf-8')
        episodes = data['episodes'].encode('utf-8')
        episode_value = data['episode_value']
        categ_id = data['categ_id']
        build_type = data['build_type']
        check_maneg_mosque = data['check_maneg_mosque']
        check_parking_mosque = data['check_parking_mosque']
        area_id = data['area_id']
        city_id = data['city_id']
        district_id = data['district_id']
        latitude = data['latitude']
        longitude = data['longitude']
        center_department_id = data['center_department_id']
        vals = { 'name': str(name),
                 'episodes' : episodes,
                 'episode_value': episode_value,
                 'categ_id': categ_id,
                 'build_type': build_type,
                 'check_maneg_mosque': check_maneg_mosque,
                 'check_parking_mosque': check_parking_mosque,
                 'area_id': area_id,
                 'city_id': city_id,
                 'district_id': district_id,
                 'latitude': latitude,
                 'longitude': longitude,
                 'center_department_id': center_department_id}

        mosque_id = self.env['mk.mosque'].create(vals)
        return mosque_id.id

    @api.model
    def cron_mosque_register_code(self):
        query = ''' select distinct register_code from mk_mosque'''
        self.env.cr.execute(query)
        codes = self.env.cr.dictfetchall()

        reg_codes = [code['register_code'] for code in codes ]

        for rec in reg_codes:
            len_mosques = self.env['mk.mosque'].search_count([('register_code', '=', rec),
                                                                '|',('active','=',True),
                                                                    ('active','=',False)])
            lennn = len_mosques
            while lennn >= 2:
                mosques = self.env['mk.mosque'].search([('register_code', '=', rec),
                                                        '|', ('active', '=', True),
                                                             ('active', '=', False)], limit=2)
                if len(mosques) == 2:
                    sequence = self.env['ir.sequence'].get('mk.mosque.serial')
                    write_mosq = self.env['mk.mosque'].search([('id', '=', mosques[1].id),
                                                                '|', ('active', '=', True),
                                                                     ('active', '=', False)], limit =1)

                    write_mosq.write({'register_code':sequence})
                    lennn = lennn - 1

        mosque_without_reg_code = self.env['mk.mosque'].search([('register_code','=',False),
                                                                '|',('active','=',True),
                                                                    ('active','=',False)])
        if mosque_without_reg_code:
            for mosq in mosque_without_reg_code:
                sequence = self.env['ir.sequence'].get('mk.mosque.serial')
                mosq.write({'register_code': sequence})

    @api.model
    def get_mosque_with_online_episodes(self):
        query_string = '''
                    select distinct(mosq.id) , mosq.display_name
                            from mk_mosque mosq
                            join mk_episode ep on ep.mosque_id = mosq.id
                            join mk_study_class class on ep.study_class_id = class.id
                            where ep.is_online = True 
                                and ep.active = true
                                and mosq.active = true
                                and class.is_default = True
                                and mosq.state='accept';'''
        self.env.cr.execute(query_string)
        mosques = self.env.cr.dictfetchall()
        return mosques

class responsible_mosque(models.Model):
    _name = 'responsible.mosque'
    
    # @api.multi
    @api.depends('name','second_name', 'third_name', 'fourth_name')
    def _display_name(self):
        
        for rec in self:
            second=''
            third=''
            first=''
            fourth=''
            
            if rec.name:
                first=rec.name.encode('utf-8','ignore')
                
            if rec.second_name:
                second=(rec.second_name).encode('utf-8','ignore')

            if rec.third_name:
                third=(rec.third_name).encode('utf-8','ignore')

            if first and second and third:
                rec.display_name=first+' '+second+' '+ third
                
            if rec.fourth_name:
                fourth= (rec.fourth_name).encode('utf-8','ignore')

            rec.display_name=first+' '+second+' '+ third+' '+fourth    
    
    display_name   = fields.Char(compute="_display_name", string="Name",store=True)
    response_id    = fields.Many2one('mk.mosque', string='Responsiple')
    mosque_id      = fields.Many2one('mk.mosque', string='Mosque')
    register_code  = fields.Char('Code', size=12)
    name           = fields.Char('First Name', required=True,)
    second_name    = fields.Char('Second Name', required=True,)
    third_name     = fields.Char('Third Name', required=True,)
    fourth_name    = fields.Char('Fourth Name',)
    no_identity    = fields.Boolean('No Identity',)
    identity_no    = fields.Integer('Identity No',)
    passport_no    = fields.Char('Passport No', size=15,)
    email          = fields.Char('Email')
    mobile         = fields.Char('Mobile',size=12)
    country_id     = fields.Many2one('res.country', string='Country',)
    gender         = fields.Selection([('male', 'Male'), 
                                       ('female', 'Female'),], "Gender", default="male")
    job_id         = fields.Many2one('hr.job', string='Job', domain=[('active', '=', True)])
    marital_status = fields.Selection([('single', 'Single'), 
                                       ('married', 'Married'), 
                                       ('widower','Widower'),
                                       ('divorced','Divorced')], string='Marital status')
    grade_id       = fields.Many2one('mk.grade', string='Grade', domain=[('active', '=', True)])
    iqama_expire   = fields.Date(string='Iqama Expire')    

    @api.model
    def create(self,values):
        if 'code' not in values:
            sequence=self.env['ir.sequence'].get('mk.mosque.responsiable.serial')
            values['register_code']=sequence

        return super(responsible_mosque, self).create(values)

    # @api.multi
    def unlink(self):
        try:
            super(responsible_mosque, self).unlink()
        except:
            raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))


class mosque_category(models.Model):
    _name = 'mk.mosque.category'
    _inherit = ['mail.thread']
    _rec_name = 'display_name'
    
    name         = fields.Char(string="Category name", track_visibility='onchange')
    mosque_type  = fields.Selection([('male', 'Male'),
                                     ('female', 'Female')], string="Type", track_visibility='onchange')
    order_categ  = fields.Integer("الترتيب",          track_visibility='onchange')
    active       = fields.Boolean(string="Active", track_visibility='onchange')
    display_name = fields.Char(compute="_display_name", string="Name", store=True)
    is_complexe  = fields.Boolean(string="Is complexe", track_visibility='onchange')
    code         = fields.Char(string="Code", track_visibility='onchange', copy=False)


    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'The code must be unique !'),
    ]

    _order = "order_categ"


    # @api.multi
    def unlink(self):
        try:
            super(mosque_category, self).unlink()
        except:
            raise UserError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))

    @api.depends('mosque_type')
    def _display_name(self):
        for record in self:
            if record.mosque_type=='male':
                name = record.name+' '+'['+' '+'رجالي'+' '+']'
                record.display_name=name
            if record.mosque_type=='female':
                name = record.name+' '+'['+' '+'نسائي'+' '+']'
                record.display_name=name

    @api.model
    def get_mosque_category(self):
        mosque_categories = self.env['mk.mosque.category'].search(['|', ('active', '=', True),
                                                                        ('active', '=', False)])
        item_list = []
        if mosque_categories:
            for cat in mosque_categories:
                item_list.append({'id': cat.id,
                                  'name': cat.name})
        return item_list

    @api.model
    def create(self, vals):
        if 'code' not in vals:
            vals['code'] = self.env['ir.sequence'].next_by_code('mosque.category')
        return super(mosque_category, self).create(vals)

    # @api.multi
    def write(self, vals):
        return super(mosque_category, self).write(vals)


class mk_news_link(models.Model):
    _name = 'event.link'

    title   = fields.Char(string='title',)
    link_id = fields.Many2one("mk.mosque","Link")


class DepartmentCategory(models.Model):
    _name = "hr.department.category"
    _inherit = ['mail.thread']


    name = fields.Char(string='Name', translate=True)
    code = fields.Char('Code', copy=False)
    active = fields.Boolean('Active', default=True)

    @api.constrains('code')
    def _check_code(self):
        if self.code:
            dept_categ = self.env['hr.department.category'].search([('code', '=', self.code),
                                                                    ('id', '!=', self.id)], limit=1)

            if dept_categ:
                raise ValidationError(_("Code must be unique"))