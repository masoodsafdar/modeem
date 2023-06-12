#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from lxml import etree
import logging
_logger = logging.getLogger(__name__)

class MkPrograms(models.Model):
    _name = 'mk.programs'
    _inherit = ['mail.thread']
    
    """
    
    @api.multi
    def unlink(self):
        ######### for security if1 (mk_users.admin_center)
        ###if2 self.env.user.has_group('mk_users.mk_mosque_admins') or self.env.user.has_group('mk_users.mosque_users')
        for rec in self:
            if self.env.user.department_ids!=False:
                if rec.create_uid.id==1:
                    raise ValidationError(_('لايمكنك حذف هذا البرنامج, يمكنك فقط حذف البرامج المنشأة بواسطتك او واسطة احد مساجدك'))
                else:
                    if rec.env.user.id!=rec.create_uid.id:
                        hr_1=self.env['hr.employee'].search([('user_id','=',rec.create_uid.id)])
                        hr_2=self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
                        if hr_1 and hr_2:
                            if hr_1[0].department_id.id!=hr_2[0].department_id.id:
                                raise ValidationError(_('لايمكنك حذف هذا البرنامج, يمكنك فقط حذف البرامج المنشأة بواسطتك او واسطة احد مساجدك'))
            if self.env.user.mosque_ids !=False:
                if self.program_type=='open':
                    raise ValidationError(_('ليست لديك صلاحية حذف البرامج المفتوحة'))

                if self.create_uid.id==1:
                    raise ValidationError(_('لايمكنك حذف هذا البرنامج, يمكنك فقط حذف البرامج المنشأة بواسطتك او واسطة اح مساجدك'))
                else:
                    if self.env.user.id!=rec.create_uid.id:
                        raise ValidationError(_('لايمكنك حذف هذا البرنامج, يمكنك فقط حذف البرامج المنشأة بواسطتك او واسطة اح مساجدك'))

            if rec.state == "active":
                raise ValidationError(_('لا يمكنك حذف سجل تم تأكيده'))
            else:
                try:
                    super(MkPrograms, rec).unlink()
                except:
                    raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))   
    @api.multi
    def write(self,vals):
        ######### for security if1 (mk_users.admin_center)
        ###if2 self.env.user.has_group('mk_users.mk_mosque_admins') or self.env.user.has_group('mk_users.mosque_users')
        if 'program_type' not in vals:
            if self.env.user.department_ids!=False:
                if self.create_uid.id==1:
                    raise ValidationError(_('عذرا,لايمكنك تعديل او اضافة المناهج للبرامج المنشئة بطرف الجمعية'))
                else:
                    if self.env.user.id!=self.create_uid.id:
                        hr_1=self.env['hr.employee'].search([('user_id','=',self.create_uid.id)])
                        hr_2=self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
                        if hr_1 and hr_2:
                            if hr_1[0].department_id.id!=hr_2[0].department_id.id:
                                raise ValidationError(_('لايمكنك تعديل هذا البرنامج, يمكنك فقط تعديل البرامج المنشئة بواسطتك او واسطة احد مساجدك'))
            if self.env.user.mosque_ids !=False:
                if self.create_uid.id==1:
                    raise ValidationError(_('عذرا,لايمكنك تعديل او اضافة المناهج للبرامج المنشئة بطرف الجمعية'))
                else:
                    if self.env.user.id!=self.create_uid.id:
                        raise ValidationError(_('لايمكنك تعديل هذا البرنامج, يمكنك فقط تعديل البرامج المنشئة بواسطتك او واسطة احد مساجدك'))

        return super(MkPrograms, self).write(vals)    
    
    
    def default_mosque(self):
        ###### for security
        ###if self.env.user.has_group('mk_users.mosque_users') or self.env.user.has_group('mk_users.mk_mosque_admins')
        if self.env.user.has_group('hr.group_hr_user') or self.env.user.has_group('hr.group_hr_user'):
            employee=self.env['hr.employee'].search([('user_id','=',self.env.uid)])
            if employee:
                return employee.mosque_id.id
        
    def default_center(self):
        ###### for security
        ###if self.env.user.ha,default=Falses_group('mk_users.mosque_users') or self.env.user.has_group('mk_users.mk_mosque_admins')
        if self.env.user.has_group('hr.group_hr_user') or self.env.user.has_group('hr.group_hr_user'):
            employee=self.env['hr.employee'].search([('user_id','=',self.env.uid)])
            if employee:
                return employee.mosque_id.center_department_id.id
    """
    
    @api.depends('program_type')
    def logged_user(self):

        for rec in self:
            if rec.program_type=='close':
                if self.env.user.has_group('mk_program_management.group_create_close_program_association') or self.env.user.has_group('mk_program_management.select_all_programs_program_management'):
                    rec.center=False
                    rec.masjed=False
                elif self.env.user.has_group('mk_program_management.group_create_close_center_program'):
                    rec.center=True
                    rec.masjed=False
                elif self.env.user.has_group('mk_program_management.group_create_close_program_mosque'):
                    rec.center=True
                    rec.masjed=True
        for rec in self:
            if rec.program_type=='open':
                if self.env.user.has_group('mk_program_management.group_create_open_program_association')or self.env.user.has_group('mk_program_management.select_all_programs_program_management'):
                    rec.center=False
                    rec.masjed=False
                elif self.env.user.has_group('mk_program_management.group_create_open_center_program'):
                    rec.center=True
                    rec.masjed=False
                elif self.env.user.has_group('mk_program_management.group_create_open_program_mosque'):
                    rec.center=True
                    rec.masjed=True

    center = fields.Boolean(string="center",default=False,compute='logged_user')
    masjed = fields.Boolean(string="masjed",default=False,compute='logged_user')

    # @api.one
    def act_draft(self):
        self.state = 'draft'
        
    # @api.one
    def act_active(self):
        self.state = 'active'
        
    company_id           = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mk.programs'))  
    center_department_id = fields.Many2one('hr.department', string='Center', track_visibility='onchange')#,default=default_center
    
    @api.onchange('center_department_id')
    def _onchange_center_department_id(self):
        self.mosque_id = False
        
    mosque_id = fields.Many2one('mk.mosque', string='Mosque', track_visibility='onchange')
    
    @api.onchange('center_department_id')
    def get_mosques(self):
        mosque_ids = self.env['mk.mosque'].sudo().search([('center_department_id','=',self.center_department_id.id)])
        if mosque_ids:
            return {'domain':{'mosque_id':[('id','in',mosque_ids.ids)]}}
        else:
            return {'domain':{'mosque_id':[('id','in',[])]}}

    name = fields.Char('Name', track_visibility='onchange')
    #code = fields.Char('Code')
    #active = fields.Boolean('Active', default=True)
    program_approches=fields.One2many("mk.approaches","program_id","Program appreoches")
    state = fields.Selection([('draft',  'Draft'),
                              ('active', 'Active')], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='onchange')

    active   = fields.Boolean('Active', default=True , track_visibility='onchange')
    memorize = fields.Boolean('Memorize', track_visibility='onchange')
    mail     = fields.Boolean('Mail',     track_visibility='onchange')
    femail   = fields.Boolean('Femail',   track_visibility='onchange')

    program_gender = fields.Selection([('men', 'Male'),
                                       ('women', 'Female')], 'الجنس', compute='_get_gender', store=True, track_visibility='onchange')
    gender = fields.Selection([('male', 'Male'),
                                       ('female', 'Female')], 'الجنس', compute='_get_gender', store=True)
    recruitment_ids    = fields.Many2many('hr.recruitment.degree', string='Qualfication')
    specialization_ids = fields.Many2many('mk.specializations',    string='Specialization')
    experience_years   = fields.Float('Experience Years', track_visibility='onchange')

    minimum_audit = fields.Boolean('Minimum Audit', track_visibility='onchange')
    maximum_audit = fields.Boolean('Maximum Audit', track_visibility='onchange')
    reading       = fields.Boolean('Reading',       track_visibility='onchange')
    is_previous_program = fields.Boolean('Previous Program?',              track_visibility='onchange')
    program_id          = fields.Many2one('mk.programs', string='Program', track_visibility='onchange')
    
    is_required         = fields.Boolean('Required for All Mosques',       track_visibility='onchange')
    #is_share = fields.Boolean('Can Be Share')
    #is_change = fields.Boolean('Can Be Change')
    program_type=fields.Selection([('open','open'),
                                   ('close','close')], string="program type")
    program_purpose = fields.Selection([('memorize_quran',    'Memorize all Quran'),
	                                    ('memorize_part',     'Memorize Specific Parts'),
	                                    #('memorize_surah', 'Memorize Specific Surah'),
	                                    ('mastering_reading', 'Mastering Reading Only')], string='Program Purpose', required=False)

    _sql_constraints = [('name_uniq', 'unique (name)', "البرنامج موجود مسبقا !!"),]
    
    """@api.model    
    def fields_view_get(self, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(MkPrograms, self).fields_view_get(view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='company_id']")
        company_ids = []
        company_recs= self.env['mk.study.year'].search([])
        company_ids = [x.company_id.id for x in company_recs]
        domain = "[('id', 'in', " + str(company_ids) + ")]"
	for node in nodes:
		node.set('domain', domain)
        res['arch'] = etree.tostring(doc)
        return res 
    """

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(MkPrograms, self).fields_view_get(view_id=view_id,view_type=view_type, toolbar=toolbar, submenu=submenu)
        # menu avtive ?
        # grouo ?
        context=self._context
        doc = etree.XML(res['arch'])
        # closed --- open
        # create --group/type 
        #open program create view 
        
        if context.get('default_program_type')=='open' and not self.env.user.has_group('mk_program_management.group_create_open_program_association') and not self.env.user.has_group('mk_program_management.group_create_open_center_program') and not self.env.user.has_group('mk_program_management.group_create_open_program_mosque'):
            for node_tree in doc.xpath("//tree"):   
                node_tree.set("create", 'false')
            for node_tree in doc.xpath("//form"):   
                node_tree.set("create", 'false')

        #open program  edit view:
        if context.get('default_program_type')=='open' and not self.env.user.has_group('mk_program_management.group_edit_level_program') :
            for node_tree in doc.xpath("//tree"):   
                node_tree.set("edit", 'false')
            for node_tree in doc.xpath("//form"):   
                node_tree.set("edit", 'false')
        
        #open program delete  view:
        if context.get('default_program_type')=='open' and not self.env.user.has_group('mk_program_management.group_delete_program'):
            for node_tree in doc.xpath("//tree"):   
                node_tree.set("delete", 'false')
            for node_tree in doc.xpath("//form"):   
                node_tree.set("delete", 'false')

        #close program create view:
        if context.get('default_program_type')=='close' and not self.env.user.has_group('mk_program_management.group_create_close_program_association') and not self.env.user.has_group('mk_program_management.group_create_close_center_program') and not self.env.user.has_group('mk_program_management.group_create_close_program_mosque'):
            for node_tree in doc.xpath("//tree"):   
                node_tree.set("create", 'false')
            for node_tree in doc.xpath("//form"):   
                node_tree.set("create", 'false')
 
        #close program  edit view:
        if context.get('default_program_type')=='close' and not self.env.user.has_group('mk_program_management.group_edit_level_program_close') :
            for node_tree in doc.xpath("//tree"):   
                node_tree.set("edit", 'false')
            for node_tree in doc.xpath("//form"):   
                node_tree.set("create", 'false')
        #open program delete  view:
        if context.get('default_program_type')=='close' and not self.env.user.has_group('mk_program_management.group_delete_program_close'):
            for node_tree in doc.xpath("//tree"):   
                node_tree.set("delete", 'false')
            for node_tree in doc.xpath("//form"):   
                node_tree.set("delete", 'false')

        res['arch'] = etree.tostring(doc)
        return res

    @api.depends('mail','femail')
    def _get_gender(self):
        for rec in self:
            if rec.mail and rec.femail:
                rec.program_gender = False
                rec.gender = False
            elif rec.mail:
                rec.program_gender = 'men'
                rec.gender = 'male'
            elif rec.femail:
                rec.program_gender = 'women'
                rec.gender = 'female'
            else:
                rec.program_gender = False
                rec.gender = False

    @api.model
    def set_programs_gender_cron_fct(self):
        programs_ids = self.env['mk.programs'].search([])
        for program in programs_ids:
            if program.mail and program.femail:
                program.program_gender = False
            elif program.mail:
                program.program_gender = 'male'
            elif program.femail:
                program.program_gender = 'female'
            else:
                program.program_gender = False

