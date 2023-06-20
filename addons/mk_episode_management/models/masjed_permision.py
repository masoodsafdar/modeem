# -*- coding:utf-8 -*-
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError

from datetime import timedelta, datetime, date
from ummalqura.hijri_date import HijriDate

import logging

_logger = logging.getLogger(__name__)


class MasjedPermision(models.Model):
    _name = 'mosque.permision'
    _inherit=['mail.thread','mail.activity.mixin']

    # @api.one
    @api.depends('masjed_id', 'is_valid', 'permision_date')
    def get_name_permission(self):
        mosque = self.masjed_id
        mosque_name = mosque.name
        permision_date = self.permision_date

        name = ' طلب تصريح'
        if self.is_valid:
            name = ' تصريح'

        if mosque_name:
            name += ' ' + mosque_name

        if permision_date:
            name += ' ' + permision_date

        self.name = name
        self.register_code = mosque.register_code

    @api.depends('categ_id', 'categ_id.mosque_type')
    def get_categ_type(self):
        for rec in self:
            rec.categ_type = rec.categ_id.mosque_type

    name               = fields.Char(compute=get_name_permission, default='طلب تصريح', store=True, tracking=True)
    date_request       = fields.Date('Request Date', tracking=True)
    attach_no          = fields.Char('Attachment No', tracking=True)

    masjed_id          = fields.Many2one('mk.mosque', string='Masjed', tracking=True)
    responsible_id     = fields.Many2one('hr.employee', string='Responsible', domain=[('category', '=', 'admin')], tracking=True)
    register_code      = fields.Char("كود المسجد/ المدرسة", size=20, compute=get_name_permission, store=True, tracking=True)
    permision_date     = fields.Date('تاريخ التصريح',  tracking=True)
    permision_end_date = fields.Date('تاريخ إنتهاء التصريح', compute="compute_hijri_start_date", store=True, tracking=True)
    permision_type     = fields.Selection([('pe', 'Parminante'),
                                           ('te', 'Temparorey')], string="المدة", tracking=True)
    mosque_type         = fields.Selection([('1', 'new'),
                                            ('2', 'transfer'),
                                            ('3', 'Cancel'),
                                            ('4', 'Tajmeed')], string="الإجراء", tracking=True)
    center_id           = fields.Many2one('hr.department', string='Center', tracking=True)
    city_id             = fields.Many2one('res.country.state', string='City', domain=[('type_location', '=', 'city'),('enable', '=', True)], tracking=True)
    area_id             = fields.Many2one('res.country.state', string='Area', domain=[('type_location', '=', 'area'),('enable', '=', True)], tracking=True)
    district_id         = fields.Many2one('res.country.state', string='District', domain=[('type_location', '=', 'district'),('enable', '=', True)], tracking=True)
    state               = fields.Selection([('draft', 'Draft'),
                                            ('renew', 'Temparory Permission'),
                                            ('review', 'Supervisor Review'),
                                            ('test', 'التقييم'),
                                            ('accept', 'Permenant permision'),
                                            ('new', 'Renew'),
                                            ('tajmeed', 'Tajmeed'),
                                            ('reject', 'Rejected')], string='State', default='draft', tracking=True)
    supervision_id      = fields.Many2one('hr.employee', string="Supervision", domain=[('category', '=', 'edu_supervisor')], tracking=True)
    visit_date          = fields.Date('Visit Date', tracking=True)
    student_no          = fields.Integer("Number of student", tracking=True)
    supervisor_decision = fields.Selection([('accept', 'Accept'),
                                            ('reject', 'Reject')], string='Supervisior Decision', tracking=True)
    decision_date       = fields.Date('Decision Date', tracking=True)
    note                = fields.Text('Note', tracking=True)
    eval_lines          = fields.One2many('mosque.eval.visit', 'visit_id', string="Evaluation Result")
    location_ids        = fields.One2many('mosque.eval.location.visit', 'loaction_id', string="Location Evalution")
    teacher_ids         = fields.One2many('teacher.test', 'test_id', string="Teacher Test")
    remain              = fields.Integer("Remaining Date", tracking=True)
    # teacher_ids2=fields.One2many('teacher.test','test_id2',string="Teacher Test")
    type_process        = fields.Selection([('new', 'جديد'),
                                            ('exist', 'تجديد')], string='Type', tracking=True)
    test_select         = fields.Selection([('test_slc', 'Testing')], string='Select Test', default='test_slc', tracking=True)
    categ_type          = fields.Selection([('male', 'Male'),
                                            ('female', 'Female'), ], string="نوع المسجد", compute=get_categ_type, tracking=True)
    hijri_permision_date     = fields.Char(compute="compute_hijri_start_date", store=True, tracking=True)
    hijri_permision_end_date = fields.Char(compute="compute_hijri_start_date", store=True, tracking=True)

    categ_id           = fields.Many2one('mk.mosque.category', string='الفئة', tracking=True)
    episode_value      = fields.Selection([('mo', 'صباحية'),
                                           ('ev', 'مسائية')], string="دوام الحلقات", tracking=True)
    episodes           = fields.Char('إسم الحلقات/ إسم الفصول', tracking=True)
    build_type         = fields.Many2one('mk.building.type', string='نوع المبني', tracking=True)
    check_maneg_mosque = fields.Boolean('توجد ادارة للحلقات بالمسجد/ المدرسة', tracking=True)
    check_parking_mosque = fields.Boolean('يوجد موقف بالمسجد/ المدرسة', tracking=True)
    is_valid             = fields.Boolean('إعتماد', tracking=True)
    valid_state          = fields.Selection([('valid', 'Valid'),
                                             ('not_valid', 'Not Valid')], compute='get_valid_state',store=True, string="Valid State", tracking=True)
    perm_type            = fields.Selection([('mosque_perm', 'Mosque permission'),
                                             ('school_perm', 'School permission')], compute='get_perm_type',store=True, string="Perm type", tracking=True)

    # @api.multi
    def get_valid_state(self):
        for rec in self:
            if rec.is_valid:
                rec.valid_state = 'valid'
            else:
                rec.valid_state = 'not_valid'

    @api.constrains('date_request')
    def _check_date(self):
        date_request = self.date_request
        if date_request :
            date_request_formated = datetime.strptime(date_request, "%Y-%m-%d").date()
            today = datetime.now().date()
            if date_request_formated and date_request_formated < today:
                raise ValidationError(_('لا يمكن لتاريخ الطلب أن يكون قبل تاريخ اليوم'))

    @api.depends('categ_type')
    def get_perm_type(self):
        for rec in self:
            if rec.categ_type == 'female':
                rec.perm_type = 'school_perm'
            else:
                rec.perm_type = 'mosque_perm'

    @api.model
    def set_permission_categ_type_and_perm_type(self):
        perm_ids = self.env['mosque.permision'].search([])
        for perm in perm_ids:
            perm.categ_type = perm.categ_id.mosque_type
            if perm.categ_type == 'female':
                perm.perm_type = 'school_perm'
            else:
                perm.perm_type = 'mosque_perm'

    # @api.one
    def action_valid(self):
        msg = ''
        if not self.permision_date:
            msg = ' الرجاء تحديد تاريخ التصريح'

        elif not self.permision_type:
            msg = ' الرجاء تحديد مدة التصريح'

        if msg:
            msg += ' ' + '!'
            raise ValidationError(msg)

        mosque = self.masjed_id
        mosque.permision_type = self.permision_type
        mosque.permision_date = self.permision_date
        mosque.permision_end_date = self.permision_end_date

        self.is_valid = True

    # @api.one
    def action_unvalid(self):
        self.is_valid = False

    @api.model
    def create(self, vals):
        permission = super(MasjedPermision, self).create(vals)
        vals.update({'center_department_id': permission.center_id.id})
        vals.pop('message_follower_ids')
        vals.pop('categ_id')
        permission.masjed_id.with_context(from_permission=True).write(vals)
        return permission

    # @api.multi
    def write(self, vals):
        mosque = self.masjed_id
        if mosque and not mosque.active:
            msg = ' المسجد مغلق، لا يمكن إجراء أي تغيير على بيانات التصريح' + '!'
            raise ValidationError(msg)

        res = super(MasjedPermision, self).write(vals)
        vals_masjed = {}

        # if 'categ_id' in vals:
        #     vals_masjed.update({'categ_id': vals.get('categ_id')})

        if 'episode_value' in vals:
            vals_masjed.update({'episode_value': vals.get('episode_value')})

        if 'episodes' in vals:
            vals_masjed.update({'episodes': vals.get('episodes')})

        if 'build_type' in vals:
            vals_masjed.update({'build_type': vals.get('build_type')})

        if 'check_maneg_mosque' in vals:
            vals_masjed.update({'check_maneg_mosque': vals.get('check_maneg_mosque')})

        if 'check_parking_mosque' in vals:
            vals_masjed.update({'check_parking_mosque': vals.get('check_parking_mosque')})

        if 'center_id' in vals:
            if self.env.user.has_group('mk_episode_management.update_mosque_center'):
                vals_masjed.update({'center_department_id': vals.get('center_id')})
            else:
                raise ValidationError(_('عذرا ليس لديك صلاحية تعديل مركز المسجد'))

        if 'city_id' in vals:
            vals_masjed.update({'city_id': vals.get('city_id')})

        if 'area_id' in vals:
            vals_masjed.update({'area_id': vals.get('area_id')})

        if 'district_id' in vals:
            vals_masjed.update({'district_id': vals.get('district_id')})

        if 'responsible_id' in vals:
            vals_masjed.update({'responsible_id': vals.get('responsible_id')})

        if 'permision_date' in vals:
            vals_masjed.update({'permision_date': vals.get('permision_date')})

        if 'permision_end_date' in vals:
            vals_masjed.update({'permision_end_date': vals.get('permision_end_date')})

        if 'mosque_type' in vals:
            vals_masjed.update({'mosque_type': vals.get('mosque_type')})

        if 'permision_type' in vals:
            vals_masjed.update({'permision_type': vals.get('permision_type')})

        if vals_masjed:
            self.masjed_id.with_context(from_permission=True).write(vals_masjed)
        return res

    @api.constrains('permision_date','permision_end_date')
    def check_permision_start_end_date(self):
        permision_date = self.permision_date
        masjed_id = self.masjed_id
        permissions_same_date = self.env['mosque.permision'].search([('masjed_id', '=', masjed_id.id),
                                                                     ('id', '!=', self.id),
                                                                     ('permision_end_date', '>=', permision_date)], limit=1)
        if permissions_same_date:
            raise ValidationError("هذا المسجد له تصريح لم ينتهي بعد!")

    # @api.one
    @api.depends('permision_date', 'permision_type')
    def compute_hijri_start_date(self):
        permision_date = self.permision_date
        if permision_date:
            self.hijri_permision_date = HijriDate.get_hijri_date(permision_date)
            permision_date = fields.Date.from_string(permision_date)
            if self.permision_type == 'te':
                permision_end_date = permision_date + timedelta(days=90)
            else:
                permision_end_date = permision_date + timedelta(days=1062)

            self.permision_end_date = permision_end_date
            self.hijri_permision_end_date = HijriDate.get_hijri_date(permision_end_date)
        else:
            self.hijri_permision_date = False
            self.permision_end_date = False
            self.hijri_permision_end_date = False

    @api.model
    def set_permission_date(self):
        mosq_perms = self.search([])

        nbr = len(mosq_perms)
        i = 1

        for mosq_perm in mosq_perms:
            permision_date = mosq_perm.permision_date

            if permision_date:
                mosq_perm.hijri_permision_date = HijriDate.get_hijri_date(permision_date)
                permision_date = fields.Date.from_string(permision_date)
                if mosq_perm.permision_type == 'te':
                    permision_end_date = permision_date + timedelta(days=90)
                else:
                    permision_end_date = permision_date + timedelta(days=1062)

                mosq_perm.permision_end_date = permision_end_date
                mosq_perm.hijri_permision_end_date = HijriDate.get_hijri_date(permision_end_date)

                i += 1

    #     @api.one
    #     @api.constrains('register_code', 'center_id', 'masjed_id')
    #     def check_register_code(self):
    #         msg = ''
    #         code = self.register_code
    #         department = self.center_id
    #         masjed = self.masjed_id
    #
    #         if len(code) > 3:
    #             msg = ' يجب أن لا يتجاوز كود المسجد ثلاث أرقام'
    #
    #         else:
    #             district = self.search([('id','!=',self.id),
    #                                     ('register_code','=',code),
    #                                     ('masjed_id','!=',masjed.id),
    #                                     ('center_id','=',department.id)], limit=1)
    #             if district:
    #                 msg = 'يوجد مسجد آخر بنفس الكود يتبع ل'
    #                 msg += department.name
    #                 msg += ' ' + '!'
    #
    #         if msg:
    #             msg += '!'
    #             raise ValidationError(msg)

    @api.onchange('masjed_id')
    def onchange_masjed(self):
        masjed = self.masjed_id

        responsible_id = False
        center_id = False
        city_id = False
        area_id = False
        district_id = False
        categ_id = False
        episode_value = False
        episodes = ""
        build_type = False
        check_maneg_mosque = False
        check_parking_mosque = False

        if masjed:
            responsible_id = masjed.responsible_id.id

            center_id = masjed.center_department_id.id
            city_id = masjed.city_id.id
            area_id = masjed.area_id.id
            district_id = masjed.district_id.id

            categ_id = masjed.categ_id.id
            episode_value = masjed.episode_value
            episodes = masjed.episodes
            build_type = masjed.build_type
            check_maneg_mosque = masjed.check_maneg_mosque
            check_parking_mosque = masjed.check_parking_mosque

        self.responsible_id = responsible_id

        self.center_id = center_id
        self.city_id = city_id
        self.area_id = area_id
        self.district_id = district_id

        self.categ_id = categ_id
        self.episode_value = episode_value
        self.episodes = episodes
        self.build_type = build_type
        self.check_maneg_mosque = check_maneg_mosque
        self.check_parking_mosque = check_parking_mosque

    @api.onchange('type_process')
    def onchange_type_process(self):
        if self.type_process == 'exist':
            self.state = 'accept'
            self.permision_type = 'pe'

    # @api.multi
    def draft_validate(self):
        self.write({'state': 'draft'})

    # @api.multi
    def review(self):
        ############write code of integration with supervisor ################
        self.write({'state': 'review'})

    # @api.multi
    def wait_test(self):
        self.write({'state': 'test'})

    # @api.one
    def renew_validate(self):
        self.masjed_id.write({'permision_date': self.permision_date,
                              'permision_end_date': self.permision_end_date,
                              'permision_type': 'te',
                              'state': 'accept', })

        self.write({'state': 'renew',
                    'permision_type': 'te'})

    # @api.one
    def reject_validate(self):
        self.masjed_id.mosque_type = '3'
        self.write({'state': 'reject',
                    'mosque_type': '3'})

    # @api.one
    def except_per(self):
        self.masjed_id.write({'permision_date': self.permision_date,
                              'permision_end_date': self.permision_end_date,
                              'permision_type': 'pe',
                              'state': 'accept', })

        self.write({'state': 'accept',
                    'permision_type': 'te'})

    # @api.one
    def set_draft(self):
        self.state = 'draft'

    # @api.multi
    def check_teacher(self):
        if self.permision_type == 'te':
            for teach in self.teacher_ids:
                for emp in self.env['employee.test.session'].search([]):
                    if emp.emp_id.id == teach.teacher_id.id and emp.state == 'done' and emp.degree >= emp.branch.minumim_degree:
                        teach.degree = emp.degree
                        teach.attend = 'pass'

                    if emp.emp_id.id == teach.teacher_id.id and emp.state == 'done' and emp.degree < emp.branch.minumim_degree:
                        teach.degree = emp.degree
                        teach.attend = 'fail'

                    if emp.emp_id.id != teach.teacher_id.id:
                        teach.degree = 0.0
                        teach.attend = 'absent'

    # @api.multi
    def transfer(self):
        if self.permision_type == 'te':
            self.masjed_id.write({'permision_date': self.permision_date,
                                  'permision_end_date': self.permision_end_date,
                                  'permision_type': 'pe',
                                  'mosque_type': '2',
                                  'attach_no': self.attach_no, })

            self.write({'state': 'accept',
                        'permision_type': 'pe',
                        'mosque_type': '2', })
        else:
            self.masjed_id.write({'permision_date': self.permision_date,
                                  'permision_end_date': self.permision_end_date,
                                  'permision_type': 'te',
                                  'mosque_type': '2',
                                  'attach_no': self.attach_no, })

            self.write({'state': 'renew',
                        'permision_type': 'te',
                        'mosque_type': '2', })

    # @api.multi
    def frize(self):
        self.mosque_type = '4'
        self.masjed_id.mosque_type = '4'

    # @api.one
    def renew(self):
        self.masjed_id.write({'permision_date': self.permision_date,
                              'mosque_type': '1', })
        self.mosque_type = '1'
    
    @api.model
    def _notify_for_expired_mosque_permision(self):
        expired_mosque_permision = self.env['mosque.permision'].search([('permision_end_date', '<', fields.Date.today()),
                                                                        ('responsible_id', '!=', False),
                                                                        ('state', '=', 'accept'),
                                                                        ('is_valid', '=',True)])

        for rec in expired_mosque_permision:
            reponsible_id = rec.responsible_id.user_id.partner_id
            if reponsible_id:
                notif = self.env['mail.message'].create({'message_type': "notification",
                                                        "subtype": self.env.ref("mail.mt_comment").id,
                                                        'body': "لقد انتهت مدة تصريح الحلقة",
                                                        'subject': "انتهاء مدة تصريح الحلقة",
                                                        'needaction_partner_ids': [(4, reponsible_id.id)],
                                                        'model': self._name,
                                                        'res_id': rec.id,})
                # send email to mosq supervisor
                template = self.env['mail.template'].search([('name','=','expired_mosque_notify_mail')], limit=1)
                if template:
                    b = template.sudo().send_mail(rec.id, force_send=True)

    @api.model
    def add_mosque_permisison(self, data):
        center_id = data['center_id']
        masjed_id = data['masjed_id']
        register_code = data['register_code']
        area_id = data['area_id']
        city_id = data['city_id']
        district_id = data['district_id']
        responsible_id = data['responsible_id']
        identification_id = data['identification_id']
        categ_type = data['categ_type']
        attach_id = data['attach_id']


        vals = {'center_id': center_id,
               'masjed_id': masjed_id,
               'register_code': register_code,
               'area_id': area_id,
               'city_id': city_id,
               'district_id': district_id,
               'responsible_id': responsible_id,
               'identification_id': identification_id,
               'categ_type': categ_type,
               'attach_id': attach_id,
                'state': 'draft'}
        permision_id = self.env['mosque.permision'].sudo().create(vals)
        # if permision_id:
        #     query_string = ''' INSERT INTO public.ir_attachment_mosque_permision_rel (mosque_permision_id,ir_attachment_id)
        #         		                        VALUES ({},{}) RETURNING mosque_permision_id,ir_attachment_id ; '''.format(permision_id.id, attach_id)
        #     self.env.cr.execute(query_string)
        #     return_row = self.env.cr.dictfetchall()
        return permision_id.id


    @api.model
    def cron_perm_register_code(self):

        query_1 = ''' select count(perm.id) from mosque_permision perm
                           join mk_mosque mk on mk.id = perm.masjed_id
                           where perm.register_code <> mk.register_code; '''
        self.env.cr.execute(query_1)
        count_mosq = self.env.cr.dictfetchall()

        query_2 = ''' select distinct perm.id from mosque_permision perm
                             join mk_mosque mk on mk.id = perm.masjed_id
                             where perm.register_code <> mk.register_code; '''
        self.env.cr.execute(query_2)
        mosque_permissions = self.env.cr.dictfetchall()

        permissions = [perm['id'] for perm in mosque_permissions]
        nbr_perms = len(permissions)
        failed_write = []
        nbr_wr_perms = 0
        nbr_fail_wr = 0
        i = 0
        for permission in permissions:
            i += 1
            permission_id = self.env['mosque.permision'].search([('id', '=', permission)], limit=1)
            mosq_reg_code = permission_id.masjed_id.register_code
            try:
                permission_id.register_code = mosq_reg_code
                nbr_wr_perms += 1
            except:
                failed_write.append(permission)
                nbr_fail_wr += 1


class masjed_teacher_test(models.Model):
    _name = 'teacher.test'

    teacher_id = fields.Many2one('hr.employee', string='Teacher')
    degree = fields.Float("Degree")
    attend = fields.Selection([('pass', 'Pass'),
                               ('fail', 'Fail'),
                               ('absent', 'Absent')], string='Attendance', )
    test_id = fields.Many2one('mosque.permision', string='Teacher')


class masjed_eval_visit(models.Model):
    _name = 'mosque.eval.visit'

    item_id = fields.Char('Item')
    degree = fields.Integer('Evalution Degree')
    visit_id = fields.Many2one('mosque.permision', string="visit")
    degree_sup = fields.Integer('supervision Degree')
    evaluation = fields.Selection([('excellent', 'excellent'),
                                   ('verygood', 'very good'),
                                   ('good', 'good')], string='Evaluation', )


class masjed_eval_visit_location(models.Model):
    _name = 'mosque.eval.location.visit'

    item_id = fields.Char('Item')
    degree = fields.Integer('Evalution Degree')
    degree_sup = fields.Integer('supervision Degree')
    yes_no = fields.Selection([('yes', 'Yes'),
                               ('no', 'No')], string='Yes/No', )
    loaction_id = fields.Many2one('mosque.permision', string="Location Info")
    check = fields.Boolean('check')


class masjed_eval(models.Model):
    _name = 'mosque.eval'
    _rec_name = 'start_date'

    start_date = fields.Date('Evaluation start Date')
    end_date = fields.Date('Evaluation end Date')
    eval_degree = fields.Integer('Evalution Degree')
    eval_ids = fields.One2many('mosque.eval.line', 'eval_id', string="Evaluation")


class masjed_eval_line(models.Model):
    _name = 'mosque.eval.line'
    _rec_name = 'item'

    item = fields.Char('Item')
    eval_calculate = fields.Selection([('degree', 'Degree'),
                                       ('yes/no', 'Yes/No')], string='Evalution Cal')
    evaluation = fields.Selection([('excellent', 'excellent'),
                                   ('verygood', 'very good'),
                                   ('good', 'good')], string='Evaluation', )
    degree = fields.Integer('Degree')
    eval_id = fields.Many2one('mosque.eval', string='evaluation')


class masjed_eval_location(models.Model):
    _name = 'mosque.eval.location'
    _rec_name = 'start_date'

    start_date = fields.Date('Evaluation start Date')
    end_date = fields.Date('Evaluation end Date')
    item_ids = fields.One2many('mosque.location.line', 'line_id', string="Items")


class masjed_eval_line_location(models.Model):
    _name = 'mosque.location.line'
    _rec_name = 'item'

    item = fields.Char('Item')
    item_type = fields.Selection([('men', 'Men'),
                                  ('women', 'Women'),
                                  ('both', 'Both')], string='Item Type', )
    item_important = fields.Selection([('required', 'Required'),
                                       ('not_required', 'Not Required')], string='Item Important', )
    line_id = fields.Many2one('mosque.eval.location', string='Item')
    eval_calculate = fields.Selection([('degree', 'Degree'),
                                       ('yes/no', 'Yes/No')], string='Evalution Cal', )
    degree = fields.Integer('Evalution Degree')
    yes_no = fields.Selection([('yes', 'Yes'),
                               ('no', 'No')], string='Yes/No')


class masjed_supervisor(models.Model):
    _name = 'mosque.supervisor'
    _rec_name = 'attach_no'

    @api.model
    def get_sequence(self):
        seq = self.env['ir.sequence'].next_by_code('mosque.supervisor.serial')
        sequence_no = seq + '/' + str(date.today().strftime("%m/%Y"))
        return sequence_no

    start_date = fields.Date('Evaluation start Date')
    end_date = fields.Date('Evaluation end Date')
    attach_no = fields.Char('Attachment No', default=get_sequence, readonly=True)
    attachment_ids = fields.Many2many('ir.attachment', string="Attachment")
    line_ids = fields.One2many('mosque.supervisor.line', 'line_id', string="Supervisor")
    state = fields.Selection([('draft', 'في انتظار الرفع'),
                              ('waiting', 'في انتظار الرد'),
                              ('done', 'تم الرد'), ], default="draft", string="status")

    # @api.one
    def action_waiting(self):
        self.state = 'waiting'

    # @api.one
    def action_done(self):
        for line in self.line_ids:
            state = line.state
            if state == 'accept':
                line.mosque_id.responsible_id = line.employee_id.id
            elif not state:
                msg = 'الرجاء تحديد الحالة بالنسبة لمسجد ' + line.mosque_id.name + ' و المشرف ' + line.employee_id.name
                raise ValidationError(msg)

        self.state = 'done'

    # @api.multi
    def send_notify(self):
        mail = self.env['mail.message']
        obj_general_sending = self.env['mk.general_sending']
        for rec in self:
            for supervisor in rec.line_ids:
                message = {'message_type': 'notification',
                           'subject': "قرار وزاري بخصوص التكليف",
                           'body': "لقد تم %s" % supervisor.state,
                           'partner_ids': [(6, 0, [supervisor.employee_id.user_id.partner_id.id])]}
                a = obj_general_sending.send_sms(supervisor.employee_id.work_phone, "لقد تم%s" % supervisor.state)
        mail.create(message)

    # @api.multi
    def get_supervisior(self):
        line_ids = []
        obj_re = self.env['mosque.supervisor.request'].search([])
        for rec in obj_re:
            if rec.date_request >= self.start_date and rec.date_request <= self.end_date:
                for mosq in rec.mosque_ids:
                    line_ids.append((0, 0, {'center_id': rec.center_id.id,
                                            'mosque_id': mosq.id,
                                            'employee_id': rec.employee_id.id}))
        self.line_ids = line_ids


class masjed_supervisor_line(models.Model):
    _name = 'mosque.supervisor.line'

    # @api.one
    @api.depends('employee_id')
    def get_id_supervisor(self):
        employee = self.employee_id
        self.id_supervisor = employee and employee.identification_id or ''

    center_id = fields.Many2one('hr.department', string='Center')
    mosque_id = fields.Many2one('mk.mosque', string='Mosque')
    employee_id = fields.Many2one('hr.employee', string='supervisor', required=True)
    id_supervisor = fields.Char('رقم الهوية', compute=get_id_supervisor, store=True)
    line_id = fields.Many2one('mosque.supervisor', string='supervisor')
    state = fields.Selection([('accept', 'Accepted'),
                              ('reject', 'Rejected'),
                              ('block', 'Blocked')], string='State')
    attachment_ids = fields.Many2many('ir.attachment', string="Attachment")

    @api.onchange('center_id')
    def center_id_on_change(self):
        return {'domain': {'mosque_id': [('center_department_id', '=', self.center_id.id)]}}

    @api.onchange('mosque_id')
    def onchange_mosque_id(self):
        employee_id = False
        mosque = self.mosque_id

        domain_supervisor = []

        if mosque:
            employee = mosque.responsible_id
            domain_employee = [('category', '=', 'admin'),
                               ('state', 'in', ('draft', 'accept')),
                               ('mosqtech_ids', 'in', [mosque.id])]
            if employee:
                employee_id = employee.id
                domain_supervisor = [employee_id]
                domain_employee += [('id', '!=', employee_id)]

            employees = self.env['hr.employee'].search(domain_employee)
            domain_supervisor += [employee.id for employee in employees]

        self.employee_id = employee_id

        return {'domain': {'employee_id': [('id', 'in', domain_supervisor)]}}


class masjed_supervisor_request(models.Model):
    _name = 'mosque.supervisor.request'
    _inherit=['mail.thread','mail.activity.mixin']

    # @api.one
    @api.depends('employee_id', 'is_valid', 'date_request')
    def get_name_request(self):
        date_request = self.date_request
        employee = self.employee_id

        name = ' طلب تكليف'
        if self.is_valid:
            name = ' تكليف'

        if employee:
            name += ' ' + self.employee_id.name

        if date_request:
            name += ' ' + date_request

        self.name = name

    # @api.one
    @api.depends('employee_id')
    def get_nbr_attach(self):
        employee = self.employee_id
        attach_no = ''
        if employee:
            supervisor_attach = self.env['mosque.supervisor.line'].search([('employee_id', '=', employee.id),
                                                                           ('state', '=', 'accept')], limit=1)
            if supervisor_attach:
                attach_no = supervisor_attach.line_id.name
        self.attach_no = attach_no
        
    # @api.one
    @api.depends('employee_id')
    def get_identification_id(self):
        employee = self.employee_id
        self.identification_id = employee and employee.identification_id or ''         


    name                    = fields.Char(compute=get_name_request, default='طلب تكليف', store=True, tracking=True)
    center_id               = fields.Many2one('hr.department', string='Center', tracking=True)
    employee_id             = fields.Many2one('hr.employee', string='supervisor', domain=[('category', '=', 'admin')], tracking=True)
    identification_id       = fields.Char(compute='get_identification_id', store=True, tracking=True)
    mosque_admin_id         = fields.Many2one('hr.employee', string='supervisor', domain=[('category', '=', 'supervisor')], tracking=True)
    admin_identification_id = fields.Char(related='mosque_admin_id.identification_id', store=True, tracking=True)
    mosque_ids              = fields.Many2many('mk.mosque', string='Mosque')
    mosque_id               = fields.Many2one('mk.mosque', string='المسجد', tracking=True)
    date_request            = fields.Date('Request Date', tracking=True)
    hijri_date_request      = fields.Char(compute="compute_dates", store=True, tracking=True)
    permision_end_date      = fields.Date('End Date', compute="compute_dates", store=True, tracking=True)
    hijri_end_date          = fields.Char(compute="compute_dates", store=True, tracking=True)
    permision_type          = fields.Selection([('pe', 'Parminante'),
                                                ('te', 'Temparorey')], string= "المدة", tracking=True)
    state                   = fields.Selection([('draft', 'مبدئي'),
                                                ('waiting', 'في انتظار الرد'),
                                                ('accept', 'Accepted'),
                                                ('reject', 'Rejected'),
                                                ('done', 'منتهي'),
                                                ('block', 'موقف')], string="الحالة", default='draft', tracking=True)
    attachment_ids          = fields.Many2many('ir.attachment', string="Attachment")
    attach_no               = fields.Char('Attach No', compute=get_nbr_attach, store=True, tracking=True)
    super_type              = fields.Selection([('1', 'new'),
                                                ('2', 'transfer'),
                                                ('3', 'Cancel'),
                                                ('4', 'Tajmeed')], string="Option", tracking=True)
    categ_type              = fields.Selection([('male', 'Male'),
                                                ('female', 'Female')], string="Type", required=True, tracking=True)
    type_request                = fields.Selection([('supervisor_request', 'Supervisor request'),
                                                    ('admin_request', 'Admin request')], default='supervisor_request' ,string="Permission requests", required=True, tracking=True)
    is_valid                = fields.Boolean('إعتماد',               tracking=True)
    active                  = fields.Boolean('Active', default=True, tracking=True)
    auto_renowell           = fields.Boolean('Auto renowell', tracking=True)

    # @api.multi
    def toggle_auto_renowell(self):
        """ Inverse the value of the field ``auto_renowell`` on the records in ``self``. """
        for record in self:
            record.auto_renowell = not record.auto_renowell

    @api.model
    def auto_renowell_mosque_supervisor_request_cron_fct(self):
        current_date = datetime.now().date()
        ended_mosque_supervisor_request_ids = self.env['mosque.supervisor.request'].search([('permision_end_date', '<', current_date),
                                                                                            ('auto_renowell', '=', True),
                                                                                            ('state', '=', 'accept')])
        total = len(ended_mosque_supervisor_request_ids)
        i = 0
        fail = 0
        archive = 0
        failed = []
        archived = []
        for supervisor_request in ended_mosque_supervisor_request_ids:
            i += 1
            vals = { 'center_id':   supervisor_request.center_id.id,
                    'categ_type':   supervisor_request.categ_type,
                    'mosque_id':    supervisor_request.mosque_id.id,
                    'employee_id':  supervisor_request.employee_id.id,
                    'date_request': datetime.now().date(),
                    'type_request': supervisor_request.type_request,
                    'attachment_ids':[(6,0, supervisor_request.attachment_ids.ids )]}
            if supervisor_request.mosque_id.active == True:
                supervisor_request.state = 'done'
                supervisor_request.active = False
                try:
                    self.env['mosque.supervisor.request'].create(vals)
                except:
                    failed.append(supervisor_request.id)
                    fail += 1
            else:
                archived.append(supervisor_request.id)
                archive += 1

    # @api.model
    # def default_get(self, fields):
    #     defaults = super(masjed_supervisor_request, self).default_get(fields)
    #     active_mosque_id = self.env.context.get('default_mosque_id')
    #     if active_mosque_id:
    #         active_mosque = self.env['mk.mosque'].search([('id', '=', active_mosque_id)])
    #         defaults.update({'categ_type': active_mosque.gender_mosque,
    #                          'center_id': active_mosque.center_department_id.id,})
    #     return defaults

    # @api.one
    def action_waiting(self):
        self.state = 'waiting'

    # @api.one
    def action_blocked(self):
        self.state = 'block'

    # @api.one
    def action_done(self):
        self.state = 'done'
        type_request = self.type_request
        if type_request == 'admin_request' and self.mosque_id.mosque_admin_id:
            self.mosque_id.mosque_admin_id = False
        if type_request == 'supervisor_request' and self.mosque_id.responsible_id:
            self.mosque_id.responsible_id = False

    # @api.one
    def action_draft(self):
        if datetime.strptime(self.permision_end_date,"%Y-%m-%d") < datetime.strptime(str(fields.Date.today()),"%Y-%m-%d"):
            raise ValidationError(_("هذا التكليف منتهي لا يمكن تحويله إلى مبدئي "))
        else:
            self.state="draft"
    # @api.one
    def action_accept(self):
        mosque_id = self.mosque_id
        type_request = self.type_request
        mosq_sup_requests = self.env['mosque.supervisor.request'].search([('mosque_id', '=', mosque_id.id),
                                                                           ('id', '!=', self.id),
                                                                          ('type_request', '=', type_request),
                                                                           ('state', '=', 'accept')], limit=1)
        if mosq_sup_requests:
            raise ValidationError(_("يوجد تكليف مقبول لهذا المسجد/المدرسة لا يمكنك قبول أكثر من تكليف"))
        else:
            self.state = 'accept'
            mosque_id.responsible_end_date = self.date_request
            mosque_id.attach_no = self.attach_no
            if type_request == 'admin_request' and not mosque_id.mosque_admin_id:
                mosque_id.mosque_admin_id = self.mosque_admin_id
            if type_request == 'supervisor_request' and not mosque_id.responsible_id:
                mosque_id.responsible_id = self.employee_id

    # @api.one
    def action_reject(self):
        self.state = 'reject'

    # @api.onchange('categ_type', 'center_id')
    # def onchange_categ_type(self):
    #     categ_type = self.categ_type
    #     center = self.center_id
    #     center_id = center.id
    #     mosque_ids = []
    #     if center_id:
    #         # self.employee_id = center.manager_id.id
    #         if categ_type:
    #             mosques = self.env['mk.mosque'].search([('center_department_id', '=', center_id),
    #                                                     ('categ_id.mosque_type', '=', categ_type)])
    #             mosque_ids = [mosque.id for mosque in mosques]

    #     self.mosque_id = False


    #     return {'domain': {'mosque_ids': [('id', 'in', mosque_ids)],
    #                        'mosque_id': [('id', 'in', mosque_ids)]}, }

    # @api.onchange('mosque_id')
    # def onchange_mosque_id(self):
    #     type_request = self.type_request
    #     employee_id = False
    #     mosque_admin_id = False
    #     mosque = self.mosque_id

    #     domain_supervisor = []

    #     if mosque:
    #         if type_request == 'supervisor_request':
    #             employee = mosque.responsible_id
    #             domain_employee = [('category', '=', 'admin'),
    #                                ('state', 'in', ('draft', 'accept')),
    #                                ('mosqtech_ids', 'in', [mosque.id])]
    #             if employee:
    #                 employee_id = employee.id
    #                 domain_supervisor = [employee_id]
    #                 domain_employee += [('id', '!=', employee_id)]

    #             employees = self.env['hr.employee'].search(domain_employee)
    #             domain_supervisor += [employee.id for employee in employees]

    #         elif type_request == 'admin_request':
    #             mosque_admin = mosque.mosque_admin_id
    #             domain_employee = [('category', '=', 'supervisor'),
    #                                ('state', 'in', ('draft', 'accept')),
    #                                ('mosqtech_ids', 'in', [mosque.id])]
    #             if mosque_admin:
    #                 mosque_admin_id = mosque_admin.id
    #                 domain_supervisor = [mosque_admin_id]
    #                 domain_employee += [('id', '!=', mosque_admin_id)]

    #             employees = self.env['hr.employee'].search(domain_employee)
    #             domain_supervisor += [employee.id for employee in employees]

    #     self.employee_id = employee_id
    #     self.mosque_admin_id = mosque_admin_id

    #     return {'domain': {'employee_id': [('id', 'in', domain_supervisor)],
    #                        'mosque_admin_id': [('id', 'in', domain_supervisor)]}}

    # @api.one
    def action_valid(self):
        msg = ''
        if not self.date_request:
            msg = ' الرجاء تحديد تاريخ التكليف'

        elif not self.permision_type:
            msg = ' الرجاء تحديد مدة التكليف'

        elif self.permision_end_date and datetime.strptime(self.permision_end_date,"%Y-%m-%d") < datetime.strptime(str(fields.Date.today()),"%Y-%m-%d"):
            msg = 'لا يمكن اعتماد تكليف بعد نهاية تاريخه'

        if msg:
            msg += ' ' + '!'
            raise ValidationError(msg)
        self.is_valid = True

    # @api.one
    def action_unvalid(self):
        self.is_valid = False

    # @api.one
    @api.depends('date_request', 'permision_type')
    def compute_dates(self):
        date_request = self.date_request
        if date_request:
            self.hijri_date_request = HijriDate.get_hijri_date(date_request)
            date_request = fields.Date.from_string(date_request)
            if self.permision_type == 'te':
                permision_end_date = date_request + timedelta(days=90)
            else:
                permision_end_date = date_request + timedelta(days=365)

            self.permision_end_date = permision_end_date
            self.hijri_end_date = HijriDate.get_hijri_date(permision_end_date)
        else:
            self.hijri_date_request = False
            self.permision_end_date = False
            self.hijri_end_date = False

    @api.model
    def set_mosque(self):
        supervisor_requests = self.search([])

        nbr = len(supervisor_requests)
        i = 1

        for supervisor_request in supervisor_requests:
            mosques = supervisor_request.mosque_ids
            if mosques:
                supervisor_request.mosque_id = mosques[0].id
                i += 1

    @api.model
    def set_permission_date(self):
        supervisor_requests = self.search([])

        nbr = len(supervisor_requests)
        i = 1

        for supervisor_request in supervisor_requests:
            date_request = supervisor_request.date_request
            if date_request:
                supervisor_request.hijri_date_request = HijriDate.get_hijri_date(date_request)
                date_request = fields.Date.from_string(date_request)
                if supervisor_request.permision_type == 'te':
                    permision_end_date = date_request + timedelta(days=90)
                else:
                    permision_end_date = date_request + timedelta(days=365)

                supervisor_request.permision_end_date = permision_end_date
                supervisor_request.hijri_end_date = HijriDate.get_hijri_date(permision_end_date)

                i += 1

    # @api.one
    def write(self, vals):
        mosque = self.mosque_id
        if mosque and not mosque.active:
            msg = ' المسجد مغلق، لا يمكن إجراء أي تغيير على بيانات التكليف' + '!'
            raise ValidationError(msg)

        return super(masjed_supervisor_request, self).write(vals)
    
    @api.model
    def _notify_for_expired_mosque_supervisor_request(self):
        expired_supervisor_requests = self.env['mosque.supervisor.request'].search([('permision_end_date', '<', fields.Date.today()),
                                                                                    ('employee_id', '!=', False),
                                                                                    ('state', '=', 'accept'),
                                                                                    ('is_valid', '=',True)])
        for rec in expired_supervisor_requests:
            responsible = rec.employee_id.user_id.partner_id
            if responsible:
                notif = self.env['mail.message'].create({'message_type': "notification",
                                                        "subtype": self.env.ref("mail.mt_comment").id,
                                                        'body': "لقد انتهت مدة تكليف مشرف المسجد",
                                                        'subject': "انتهاء تكليف مشرف",
                                                        'needaction_partner_ids': [(4, responsible.id)],
                                                        'model': self._name,
                                                        'res_id': rec.id,
                                                        })
                # send email to mosq supervisor
                template = self.env['mail.template'].search([('name','=','expired_supervisor_requests_mail')], limit=1)
                if template:
                    b = template.sudo().send_mail(rec.id, force_send=True)

    @api.model
    def get_status(self, responsible_id):
        try:
            responsible_id = int(responsible_id)
        except:
            pass

        supervisor_requests = self.env['mosque.supervisor.request'].search([('employee_id', '=', responsible_id),
                                                                             '|', ('active', '=', True),
                                                                                  ('active', '=', False)])
        result = []
        if supervisor_requests:
            for request in supervisor_requests:
                result.append({'state': request.state})
        return result

    @api.model
    def add_request_permisison(self, data):
        masjed_id = data['masjed_id']
        attach_id = data['attach_id']

        vals = {'center_id':        int(data['center_id']),
               'employee_id':       int(data['employee_id']),
               'identification_id': data['identification_id'],
               'categ_type':        data['categ_type'],
               'mosque_id':         masjed_id,
                'state':            'draft'}
        request_id = self.env['mosque.supervisor.request'].create(vals)
        if request_id:
            try:
                query_string2 = ''' INSERT INTO public.mk_mosque_mosque_supervisor_request_rel (mosque_supervisor_request_id,mk_mosque_id)
                                                VALUES ({},{})
                                                RETURNING mosque_supervisor_request_id,mk_mosque_id ; '''.format(request_id.id, masjed_id)
                self.env.cr.execute(query_string2)
                return_row2 = self.env.cr.dictfetchall()

                if len(return_row2) > 0:
                    query_string3 = ''' INSERT INTO public.ir_attachment_mosque_supervisor_request_rel (mosque_supervisor_request_id,ir_attachment_id)
                                                        VALUES ({},{})
                                                        RETURNING mosque_supervisor_request_id,ir_attachment_id ; '''.format(request_id.id, attach_id)
                    self.env.cr.execute(query_string3)
                    return_row3 = self.env.cr.dictfetchall()
            except:
                pass
        return request_id.id

    @api.constrains('date_request','permision_end_date')
    def check_request_start_end_date(self):
        date_request = self.date_request
        mosque_id = self.mosque_id
        type_request = self.type_request
        mosq_sup_requests_same_date = self.env['mosque.supervisor.request'].search([('mosque_id', '=', mosque_id.id),
                                                                               ('type_request', '=',type_request),
                                                                               ('id', '!=', self.id),
                                                                               ('state', '!=', 'block'),
                                                                               ('permision_end_date', '>=',date_request)], limit=1)

        if mosq_sup_requests_same_date:
            raise ValidationError("هذا المسجد له تكليف لم ينتهي بعد!")

    def _get_latest_date(self, requests):
        latest_request = self.env['mosque.supervisor.request'].search([('id', 'in', requests.ids)], order="permision_end_date desc", limit=1)
        return latest_request

    @api.model
    def cron_fix_requests_no_employee(self):
        requests_no_employee = self.env['mosque.supervisor.request'].search(['|','&',('employee_id', '=', False),
                                                                                      ('type_request', '=', 'supervisor_request'),
                                                                                  '&',('mosque_admin_id', '=', False),
                                                                                      ('type_request', '=', 'admin_request')])
        total = len(requests_no_employee)
        requests_no_employee.unlink()

    @api.model
    def cron_fix_supervisor_requests_pb(self):
        mosques = self.env['mk.mosque'].search([])
        total = len(mosques)
        i = 0
        mosq_multi_req_diff_sup = []
        for mosque in mosques:
            i += 1
            requests = self.env['mosque.supervisor.request'].search([('mosque_id', '=', mosque.id),
                                                                     ('type_request', '=', 'supervisor_request'),
                                                                     ('state','=' ,'accept')])
            if requests:
                if len(requests) == 1:
                    continue
                supervisors_list = [req.employee_id.id for req in requests]
                supervisors = list(set(supervisors_list))
                if  len(supervisors) > 1:
                    mosq_multi_req_diff_sup.append(mosque.id)
                else:
                    latest_request = self._get_latest_date(requests)
                    for request in requests:
                        if request.id == latest_request.id:
                            continue
                        request.state = 'done'
                    mosque.responsible_id = latest_request.employee_id.id
                    latest_request.is_valid = True

    @api.model
    def cron_fix_admin_requests_pb(self):
        mosques = self.env['mk.mosque'].search([])
        total = len(mosques)
        i = 0
        mosq_multi_req_diff_sup = []
        for mosque in mosques:
            i += 1
            requests = self.env['mosque.supervisor.request'].search([('mosque_id', '=', mosque.id),
                                                                     ('type_request', '=', 'admin_request'),
                                                                     ('state','=' ,'accept')])
            if requests:
                if len(requests) == 1:
                    continue
                supervisors_list = [req.mosque_admin_id.id for req in requests]
                supervisors = list(set(supervisors_list))
                if  len(supervisors) > 1:
                    mosq_multi_req_diff_sup.append(mosque.id)
                else:
                    latest_request = self._get_latest_date(requests)
                    for request in requests:
                        if request.id == latest_request.id:
                            continue
                        request.state = 'done'
                    mosque.mosque_admin_id = latest_request.mosque_admin_id.id
                    latest_request.is_valid = True

class pem_wizard(models.TransientModel):
    _name = 'perm.wizard'

    employee_id = fields.Many2many('hr.employee', 'employee_sup_wiz_rel', 'emp_id', 'wiz_id', string='Employee')
    active_id = fields.Many2one('mosque.supervisor', string="supervisor")

    @api.onchange('active_id')
    def onchange_active(self):
        list1 = []

        for rec in self.active_id.line_ids:
            list1.append(rec.employee_id.id)

        return {'domain': {'employee_id': [('id', 'in', list1)]}}

    # @api.multi
    def yes(self):
        for record in self.active_id.line_ids:
            sup_rec = self.env['mosque.supervisor.request'].search([('employee_id', '=', record.employee_id.id)])
            if record.employee_id.id in self.employee_id.ids:
                record.state = 'accept'
            else:
                record.state = 'reject'

            for sup_id in sup_rec:
                sup_id.state = record.state
                sup_id.attachment_ids = self.active_id.attachment_ids
                sup_id.attach_no = self.active_id.attach_no

                if sup_id.state == "accept":
                    sup_id.employee_id.write({'mosqtech_ids': sup_id.mosque_ids.ids})
                    for mosq in sup_id.mosque_ids:
                        mosq.responsible_end_date = sup_id.permision_end_date
                        mosq.responsible_type = sup_id.super_type