# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from datetime import datetime,timedelta,date
import logging
_logger = logging.getLogger(__name__)


class Criteria(models.Model):
    _name = 'edu.criterion'
    _rec_name= 'name'

    name             = fields.Char('Name')
    criterion_number = fields.Integer()
    field_id         = fields.Many2one("edu.field", string="Field")
    item_ids         = fields.One2many('edu.item', 'criterion_id')
    total_items_weight = fields.Integer(compute='get_total_items_weight')
    criterion_weight   = fields.Float(compute='get_criterion_weight', store=True)

    @api.one
    def get_total_items_weight(self):
        items_count = self.env['edu.item'].search([])
        self.total_items_weight = sum(item.item_degree for item in items_count)

    @api.one
    @api.depends('item_ids', 'item_ids.item_degree')
    def get_criterion_weight(self):
        weight = sum(self.item_ids.mapped('item_degree'))
        self.criterion_weight = (weight * 100) / self.total_items_weight if weight > 0 else 0


class Items(models.Model):
    _name = 'edu.item'
    _rec_name = 'name'

    name             = fields.Char('Name')
    item_degree      = fields.Integer()
    need_approve     = fields.Boolean()
    type_approval    = fields.Binary()
    item_description = fields.Char()
    criterion_id = fields.Many2one('edu.criterion')
    item_id      = fields.Many2one("edu.item", "Item")
    type_item = fields.Selection([('visit', 'visit'),
                                  ('date', 'done date')],default='visit')

    @api.onchange('item_id')
    def onchange_item(self):
        item_id = self.item_id
        self.write({'item_description': item_id.item_description,
                    'item_degree':      item_id.item_degree,
                    'is_need_approve':  item_id.is_need_approve})


class ItemsDistribuater(models.Model):
    _name = 'comapany.pointers'

    @api.depends('parent_line_ids')
    def _total_items(self):
        for rec in self:
            rec.total_items = len(rec.parent_line_ids)

    parent_line_ids = fields.One2many('parent.item', 'pointer_id', 'items')
    total_items = fields.Integer(compute='_total_items', string="Total items")
    date_start  = fields.Date(string="Start Date")
    date_end  = fields.Date(string="End Date")
    type_evaluation = fields.Selection([('initial', 'Initial'),
                                        ('final', 'Final'), ], string='Evaluation Type', default='initial')

    @api.constrains('date_start', 'date_end')
    def check_end_date(self):
        for record in self:
            if record.date_start and record.date_end and record.date_start >= record.date_end:
                raise ValidationError("End date must be after the start date")

    @api.multi
    @api.depends('date_start','date_end','type_evaluation')
    def name_get(self):
        res = []
        for rec in self:
            name = "تقييم "
            type_evaluation = rec.type_evaluation
            if type_evaluation == 'initial':
                name += 'مبدئي'
            else:
                name += 'نهائي'

            name += ' ' + '[' + str(rec.date_start) + '/' +  str(rec.date_end) + ']'
            res.append((rec.id, name))
        return res


class PointerManagementCompany(models.Model):
    _name = 'parent.item'
    _rec_name = 'code'


    flag = fields.Boolean(compute='is_distrbiuted')
    code = fields.Char(string="code")
    item_field_id    = fields.Many2one("edu.field", string="ITEM DOMAIN")
    item_crateria_id = fields.Many2one("edu.criterion", string="ITEM CRATERIA")
    item_id   = fields.Many2one("edu.item", "Item")
    item_type = fields.Selection([('visit', 'visit'),
                                  ('date', 'done date')], default="date")
    gender    = fields.Selection([('men', 'Men'),
                                  ('women', 'Women'),
                                  ('men_women', 'Men and Women')], default="men")
    item_degree   = fields.Integer()
    is_need_approve  = fields.Boolean()
    item_description = fields.Char()
    distribuation_method = fields.Selection([('all', 'all supervisors'),
                                             ('internal', 'internal')], default="all")
    required_pointers = fields.Integer(string="required pointers number")
    done_pointers     = fields.Integer(string="done pointers")
    center_required_pointers = fields.Integer()
    centers_pointer_ids      = fields.One2many("center.item", "parent_item_id", "pointers")
    pointer_id               = fields.Many2one("comapany.pointers", "pointer")
    assigned_item_number = fields.Integer(string="assigned items")
    center_ids = fields.Many2many('hr.department', 'parent_item_department_rel', 'parent_item_id', 'department_id', string="Departments")
    select_all_centers = fields.Boolean(string='Select All Centers', default=False)
    state = fields.Selection([('new', 'New'),
                              ('center', 'Distributed to centers'),
                              ('distribuated', 'Distributed to supervisors'),
                              ('done', 'Done')], default="new")
    indicator_level = fields.Selection([('supervisory', 'Supervisory'),
                                        ('mosque', 'Mosque'),
                                        ('school', 'School'), ], string='Indicator Level', default='supervisory')

    @api.onchange('item_id')
    def onchange_item(self):
        item_id = self.item_id
        self.item_description = item_id.item_description
        self.item_degree = item_id.item_degree
        self.is_need_approve = item_id.need_approve
        self.item_type = item_id.type_item

    @api.onchange('item_field_id')
    def get_item_crateria(self):
        self.item_crateria_id = False
        items = self.env['edu.criterion'].search([('field_id', '=', self.item_field_id.id)]).ids
        return {'domain': {'item_crateria_id': [('id', 'in', items)]}}

    @api.onchange('item_crateria_id')
    def get_items(self):
        self.item_id = False
        items = self.env['edu.item'].search([('criterion_id', '=', self.item_crateria_id.id)]).ids
        return {'domain': {'item_id': [('id', 'in', items)]}}

    @api.onchange('select_all_centers')
    def onchange_select_all(self):
        departments = self.env['hr.department'].search([('code', '!=', False)])
        if self.select_all_centers:
            self.center_ids = [(6, 0, departments.ids)]
        else:
            self.center_ids = [(5, 0, 0)]

    @api.depends('centers_pointer_ids')
    def is_distrbiuted(self):
        for rec in self:
            flag = 0
            for item in rec.centers_pointer_ids:
                if item.state != 'distribuated':
                    flag = 1
            if flag == 0 and rec.centers_pointer_ids:
                rec.write({'state': 'distribuated', 'flag': True})

    @api.model
    def create(self, values):
        sequence = self.env['ir.sequence'].next_by_code('parent.item.serial')
        values['code'] = sequence
        return super(PointerManagementCompany, self).create(values)

    @api.multi
    def assgin_one(self):
        couter = 0
        if self.distribuation_method == 'all' and self.gender == 'men_women':
            couter = self.env['hr.employee'].search_count([('category', '=', 'edu_supervisor'),
                                                              ('department_id', '=', self.center_ids.ids)])
        elif self.distribuation_method == 'all' and self.gender == 'women':
            couter = self.env['hr.employee'].search_count([('gender', '=', 'female'),
                                                              ('category', '=', 'edu_supervisor'),
                                                              ('department_id', '=', self.center_ids.ids)])
        elif self.distribuation_method == 'all' and self.gender == 'men':
            couter = self.env['hr.employee'].search_count([('gender', '=', 'male'),
                                                              ('category', '=', 'edu_supervisor'),
                                                              ('department_id', '=', self.center_ids.ids)])
        if self.center_required_pointers == 0:
            raise models.ValidationError('الرجاء تحديد المؤشر المطلوب')

        #if self.center_required_pointers < couter and self.item_id.item_degree != 0:
        #   raise models.ValidationError('المؤشر المطلوب من جميع المشرفين يجب ان يساوي او يزيد عن عدد المشرفين التربويين')

        center_item_object = self.env['center.item']
        for department in self.center_ids:
            center_item_object.create({'code': self.code,
                                        'state': 'new',
                                        'item_field_id': self.item_field_id.id,
                                        'item_crateria_id': self.item_crateria_id.id,
                                        'item_id': self.item_id.id,
                                        'item_type': self.item_type,
                                        'gender': self.gender,
                                        'is_need_approve': self.is_need_approve,
                                        'item_description': self.item_description,
                                        'item_degree': self.item_degree,
                                        'distribuation_method': self.distribuation_method,
                                        'center_id': department.id,
                                        'parent_item_id': self.id,
                                        'center_required_pointers': self.center_required_pointers})
            self.write({'assigned_item_number': self.assigned_item_number + 1})
        self.write({'state': 'center'})


class PointerManagementcenter(models.Model):
    _name = 'center.item'
    _rec_name = 'item_id'

    total_supervisors = fields.Integer(compute='_total_supervisors', string="supervisors")
    state = fields.Selection([('new', 'New'),
                              ('distribuated', 'Distributed to supervisors'),
                              ('done', 'Done')], default="new")
    code = fields.Char(string="code")
    item_field_id    = fields.Many2one("edu.field", string="ITEM DOMAIN")
    item_crateria_id = fields.Many2one("edu.criterion", string="ITEM CRATERIA")
    flag      = fields.Boolean(compute='is_done', string="flag")
    item_id   = fields.Many2one("edu.item", "Item")
    item_type = fields.Selection([('visit', 'visit'),
                                  ('date', 'done date')], default="date")
    is_need_approve  = fields.Boolean()
    item_description = fields.Char()
    item_degree   = fields.Integer()
    gender  = fields.Selection([('men', 'Men'),
                                ('women', 'Women'),
                                ('men_women', 'Men and Women')], default="men")
    distribuation_method = fields.Selection([('all', 'all supervisors'),
                                             ('internal', 'internal')], default="all")
    done_pointers   = fields.Integer(string="done pointers")
    center_id       = fields.Many2one("hr.department", string="department")
    parent_item_id           = fields.Many2one("parent.item", "parent")
    supervisors_pointer_ids  = fields.One2many("supervisor.item", "center_parent_id", "pointers")
    assigned_item_number     = fields.Integer(string="assigned items")
    center_required_pointers = fields.Integer(string="center_required_pointers")
    line_ids  = fields.One2many('supervisor.pointer', 'item_center_id')
    sup_count = fields.Integer(compute="supervisors_count")

    @api.depends('line_ids')
    def _total_supervisors(self):
        for rec in self:
            rec.total_supervisors = len(rec.line_ids.ids)

    @api.depends('done_pointers')
    def is_done(self):
        for rec in self:
            if rec.done_pointers != 0:
                if rec.done_pointers == rec.assigned_item_number:
                    rec.write({'state': ' done'})
                    rec.parent_item_id.write({'done_pointers': rec.parent_item_id.done_pointers + 1})
                    if rec.parent_item_id.done_pointers != 0:
                        if rec.parent_item_id.done_pointers == rec.parent_item_id.assigned_item_number:
                            rec.parent_item_id.write({'state': 'done'})
                    rec.flag = True

    def supervisors_count(self):
        a = 0
        if self.distribuation_method == 'all' and self.gender == 'women':
            a = self.env['hr.employee'].search_count([('gender', '=', 'female'),
                                                      ('category', '=', 'edu_supervisor'),
                                                      ('department_id', '=', self.center_id.id)])
        elif self.distribuation_method == 'all' and self.gender == 'men':
            a = self.env['hr.employee'].search_count([('gender', '=', 'male'),
                                                      ('category', '=', 'edu_supervisor'),
                                                      ('department_id', '=', self.center_id.id)])
        elif self.distribuation_method == 'all' and self.gender == 'men_women':
            a = self.env['hr.employee'].search_count([('category', '=', 'edu_supervisor'),
                                                      ('department_id', '=', self.center_id.id)])
        self.sup_count = a

    @api.multi
    def sup_assign(self):
        if self.total_supervisors < self.sup_count:
            raise models.ValidationError('يجب إسناد هذا البند على جميع المشرفين في المركز')
        if self.distribuation_method == 'all':
            for rec in self.lines:
                if rec.required_pointer <= 0 and self.center_required_pointers != 0:
                    raise models.ValidationError('يجب إسناد هذا البند على جميع المشرفين في المركز')

        sum_pointers = 0

        for record in self.line_ids:
            for line in record:
                sum_pointers += line.required_pointer
        if self.center_required_pointers != sum_pointers:
            raise models.ValidationError(
                'مجموع المؤشرات المسندة للمشرفين التربويين  يجب ان يساوي المؤشر المطلوب من المركز')

        sup_item_object = self.env['supervisor.item']
        for supervisor in self.line_ids:
            sup_item_object.create({
                'code': self.parent_item_id.id,
                'state': 'new',
                'field_id': self.item_field_id.id,
                # 'evaluation_type': self.item_field_id.type_evaluation,
                'item_crateria_id': self.item_crateria_id.id,
                'item_id': self.item_id.id,
                'is_need_approve': self.is_need_approve,
                'item_type': self.item_type,
                'gender': self.gender,
                'item_description': self.item_description,
                'item_degree': self.item_degree,
                'supervisor_id': supervisor.supervisor_id.id,
                'sup_required_pointer': supervisor.required_pointer,
                'center_parent_id': self.id,
                'center_id': self.center_id.id
            })
        self.write({'state': 'distribuated'})
        self.parent_item_id.write({'state': 'distribuated'})


class PointerManagementcenter(models.Model):
    _name = 'supervisor.pointer'

    @api.onchange('supervisor_id')
    def item_change(self):
        item_center_id = self.item_center_id
        if item_center_id.gender=='women':
            return {'domain':{'supervisor':[('gender','=','female'),
                                            ('category','=','edu_supervisor'),
                                            ('department_id','=',item_center_id.center_id.id)]}}
        else:
            if item_center_id.gender=='men':
                return {'domain':{'supervisor':[('gender','=','male'),
                                                ('category','=','edu_supervisor'),
                                                ('department_id','=',item_center_id.center_id.id)]}}
            else:
                return {'domain':{'supervisor':[('category','=','edu_supervisor'),
                                                ('department_id','=',item_center_id.center_id.id)]}}

    supervisor_id    = fields.Many2one("hr.employee", domain="[('category', '=', 'edu_supervisor')]")
    required_pointer = fields.Integer(required=True)
    item_center_id   = fields.Many2one('center.item','center')
    don_pointer      = fields.Integer()


class PointerManagementsupervisors(models.Model):
    _name = 'supervisor.item'
    _rec_name = 'item_id'

    state = fields.Selection([('new', 'New'),
                              ('done', 'Done')], string="الحالة", default="new")
    code = fields.Many2one('parent.item', string="code")
    item_crateria_id = fields.Many2one("edu.criterion", string="ITEM CRATERIA")
    criterion_weight = fields.Float(compute="_get_crateria_done_degree")
    center_id = fields.Many2one("hr.department")
    supervisor_id = fields.Many2one("hr.employee", domain="[('category2','=','edu_supervisor')]")
    supervisor_decision = fields.Selection(string='Supervisior Decision', selection=[('accept', 'Accept'),
                                                                                     ('reject', 'Reject')])
    masjed_id = fields.Many2one("mk.mosque", "mosque")
    superv_mosqus_ids = fields.Many2many("mk.mosque", compute='get_superv_mosqus_ids', store=True)
    mosq_category = fields.Selection([('a', 'أ'),
                                      ('b', 'ب'),
                                      ('c', 'ج'),
                                      ('quran_complex', 'مجمع قراني'),
                                      ('edu_complex', 'مجمع تعليمي'),
                                      ('mosque', 'مسجد')], string='الفئة')
    field_id = fields.Many2one("edu.field", string="المجال")
    evaluation_type = fields.Selection([('initial', 'Initial'),
                                        ('final', 'Final')], string='Evaluation Type')
    evaluation_status = fields.Selection([('verified', 'Verified'),
                                          ('not_verified', 'Not Verified'),
                                          ('in_progress', 'In Progress')], string='Evaluation Status', )
    supervisor_notes = fields.Text(string='Supervisor Notes')
    mosque_notes = fields.Text(string='Mosque/School Notes')
    study_class_id = fields.Many2one('mk.study.class', string='الفصل الدراسي', compute="get_study_class",track_visibility='onchange')
    #achievement_percentage = fields.Float(string='Achievement Percentage')
    evaluation_method = fields.Selection([('multiple_choice', 'Multiple Choice'),
                                          ('grade_input', 'Grade Input')], string='Evaluation Method', invisible=1)
    item_type = fields.Selection([('visit', 'visit'),
                                  ('date', 'done date')], default='date')
    gender = fields.Selection([('men', 'Men'),
                               ('women', 'Women'),
                               ('men_women', 'Men and Women')], default="men")
    item_id = fields.Many2one("edu.item", "Item")
    item_degree = fields.Integer(related='item_id.item_degree', store=True)
    done_pointers = fields.Integer(string="done pointers")
    done_date = fields.Date(string="done date")
    sup_required_pointer = fields.Integer()
    is_need_approve = fields.Boolean()
    item_description = fields.Char()
    visit_ids = fields.One2many('visits.managment', 'supervisor_item_id', 'visits')

    @api.one
    def _get_crateria_done_degree(self):
        items_count = self.env['edu.item'].search([])
        item_count = self.env['edu.item'].search([('criterion_id', '=', self.item_crateria_id.id)])
        item_deserved = self.env['supervisor.item'].search(
            [('supervisor_id', '=', self.supervisor_id.id), ('item_crateria_id', '=', self.item_crateria_id.id)])
        weight = sum(item.item_degree for item in item_count)

        total_items_weight = sum(item.item_degree for item in items_count)
        total_deserved = sum(deserved.deserved_degree for deserved in item_deserved)
        criterion_assigned_weight = sum(item.item_degree for item in item_deserved)

        if weight <= 0:
            self.criterion_weight = 0
            self.crateria_done_degree = 0.0
        else:
            self.criterion_weight = (weight * 100) / total_items_weight
            self.crateria_done_degree = float(self.criterion_weight * total_deserved) / float(criterion_assigned_weight)

        '''
        for rec in self:
            items=self.env['supervisor.item'].search([('supervisor','=',rec.supervisor.id),('item_crateria','=',rec.item_crateria.id)])
            total_weights=0
            total_deserved=0
            if items:

                for item in items:
                    total_weights=total_weights+item.item_degree
                    total_deserved=total_deserved+item.deserved_degree
            if total_weights >0: 
                rec.criterion_weight=total_weights         
                rec.crateria_done_degree=float(rec.criterion_weight*total_deserved)/float(total_weights)
            else:
                rec.crateria_done_degree=0.0

        '''
        # items_weights=self.search([('criterion.id','=',self.item_crateria.id)])
        # for rec in items_weights:
        #     if

        # sum_required_pointes=sum(item.item_degree for item in items_weights)
        # for rec in self:
        #     x=rec.filtered(
        #         lambda item: item.item_crateria==rec.item_crateria)
        #     rec=x.mapped(lambda r:r.item+rec.item)

        # criteria=self.env['edu.criterion'].search([('id','=',self.item_crateria.id)])
        # #sum=0.0
        # for rec in criteria:
        #     for item in rec.items:
        #         if self.item_crateria.id==self.item_crateria.id:
        #             if item.id==self.item.id:
        #                 x=sum(item.item_degree)
        # list=[]
        # items_weights=self.env['edu.item'].search([('criterion.id','=',self.item_crateria.id)])
        # for cre in items_weights:
        #     list.append(cre.id)
        #     #if self.item_crateria.id==cre.id:
        #         if len(items_weights)>1:
        #     weights=sum(item.item_degree for item in items_weights)
        # '''
        # items_weights=self.env['edu.item'].search([('criterion','=',self.item_crateria)])

        # sum_required_pointes=sum(item.item_degree for item in items_weights)

        # self.crateria_done_degree=(self.criterion_weight*self.item_done_percent)/sum_required_pointes
        # '''

    @api.one
    def _get_deserved_degree(self):
        if self.sup_required_pointer <= 0:
            self.deserved_degree = 0

        else:
            self.deserved_degree = (self.done_pointers * self.item_degree) / self.sup_required_pointer

    @api.one
    def _get_item_done_degree(self):
        if self.done_pointers <= 0:
            self.item_done_degree = 0
        else:
            self.item_done_degree = (self.done_pointers * self.sup_required_pointer) / 100

    @api.one
    @api.depends('done_pointers', 'sup_required_pointer')
    def _get_item_done_percent(self):
        self.item_done_percent = (self.done_pointers * 100) / self.sup_required_pointer if self.sup_required_pointer > 0 else 0


    actual_date = fields.Date()
    center_parent_id = fields.Many2one("center.item", "center parent")
    note = fields.Text(string="Notes")
    deserved_degree = fields.Float(compute="_get_deserved_degree")
    item_done_degree = fields.Integer(compute="_get_item_done_degree")
    item_done_percent = fields.Integer(compute="_get_item_done_percent", store=True)
    crateria_done_degree = fields.Integer(compute="_get_crateria_done_degree")
    # mosque.permision
    mosque_permision_id = fields.Integer()
    mosque_permision_ids = fields.One2many('mosque.permision', 'supervisor_id', string='mosque_permision')
    permision_requests = fields.Boolean(default=False)
    eval_line_ids = fields.One2many('mosque.eval.visit', 'visit_id', string="Evaluation Result")
    location_ids = fields.One2many('mosque.eval.location.visit', 'loaction_id', string="Location Evalution")
    student_no = fields.Integer()
    visit_date = fields.Date('Visit Date')

    @api.multi
    def get_year_default(self):
        academic_year = self.env['mk.study.year'].search([('is_default', '=', True)], limit=1)
        return academic_year and academic_year.id or False

    def get_study_class(self):
        self.study_class_id = self.env['mk.study.class'].search([('study_year_id', '=', self.get_year_default()),
                                                                 ('is_default', '=', True)], limit=1)

    @api.depends('supervisor_id')
    def get_superv_mosqus_ids(self):
        self.superv_mosqus_ids = self.supervisor_id.mosque_sup.ids

    @api.onchange('masjed_id')
    def get_mosq_category(self):
        return {'value': {'mosq_category': self.masjed_id.mosq_category}}

    @api.onchange('done_pointers')
    def _done_pointers(self):
        if self.done_pointers > self.sup_required_pointer:
            raise models.ValidationError('المؤشر المتحقق يجب الايزيد عن قيمة المؤشر المطلوب')

    @api.multi
    def done(self):
        self.write({'state': 'done'})
        if self.item_type=='visit':
            draft_visits = self.visit_ids.filtered(lambda v: v.state == 'draft')
            print('draft_visits     : ', draft_visits)
            if not draft_visits and len(self.visit_ids)!=0:
                self.write({'state':'done',
                            'actual_date':datetime.today()})
                self.center_parent_id.parent_item_id.update({'state':'done'})
            else:
                raise UserError(_("خطة الزيارات"))
        else:
            if self.item_type=='date':
                self.write({'state':'done','actual_date':datetime.today()})
                self.center_parent_id.parent_item_id.update({'state':'done'})
        self.center_parent_id.done_pointers=self.center_parent_id.done_pointers+self.done_pointers
        self.center_parent_id.parent_item_id.done_pointers=self.center_parent_id.parent_item_id.done_pointers+self.done_pointers
        is_don =self.search([('center_parent_id','=',self.center_parent_id.id),('state','=','new')])
        if not  is_don:
            self.center_parent_id.update({'state':'done'})
            self.center_parent_id.parent_item_id.update({'state':'done'})


class visitsManagment(models.Model):
    _name = 'visits.managment'

    visit_id   = fields.Many2one('edu.visit', string='نوع الزيارة')
    visit_date = fields.Date()
    supervisor_id = fields.Many2one('hr.employee')
    item_id       = fields.Many2one('edu.item')
    notes     = fields.Char()
    masjed_id = fields.Many2one("mk.mosque", "mosque")
    state     = fields.Selection([('draft', 'لم تتم الزيارة'),
                                  ('done', 'تمت الزيارة')], default='draft')
    supervisor_item_id = fields.Many2one("supervisor.item", "item_id")
    women_men          = fields.Selection([('men', 'Men'),
                                            ('women', 'Women'),
                                            ('men_women', 'Men and Women')], default="men")

    @api.onchange('supervisor_item_id')
    def item_cchange(self):
        mosq = self.env['hr.employee'].search([('id', '=', self.supervisor_item_id.supervisor_id.id)]).mosque_sup
        return {'value': {'item_id':     self.supervisor_item_id.item_id.id,
                          'masjed_id':   self.supervisor_item_id.masjed_id.id},
                'domain': {'masjed_id': [('id', 'in', mosq.ids)]}}

    @api.onchange('masjed_id')
    def get_supervisior(self):
        self.supervisor_id = self.env['mk.mosque'].search([('id', '=', self.masjed_id.id)]).responsible_id.id

    @api.multi
    def accept(self):
        self.write({'state': 'done'})
        flag=0
        for visit in self.supervisor_item_id.visit_ids:
           if visit.state=='draft':
               flag=1
        if flag==0 and self.supervisor_item_id.visit_ids:
           self.supervisor_item_id.write({'state':'done'})
           self.supervisor_item_id.item_id.write({'done_pointers':self.supervisor_item_id.center_parent_id.done_pointers+1})

    @api.model
    def create(self, vals):
        visit_type = self.env['edu.visit'].search([('id', '=', vals['visit_id'])])
        if visit_type:
            if visit_type[0].is_suddenly != True:
                hr = self.env['hr.employee'].search([('id', '=', vals['supervisor_id'])])
                if hr:
                    mail = self.env['mail.message']
                    if hr[0].user_id.partner_id:
                        valus = {
                            'message_type': 'notification',
                            'subject': 'زيارة جديدة',
                            'body': 'لديك بند زيارة الي' + ' ' + 'مسجد' +
                                    self.env['mk.mosque'].search([('id', '=', vals['masjed_id'])])[0].name,
                            'partner_ids': [(6, 0, [hr[0].user_id.partner_id.id])]}

                        mail.create(valus)
        return super(visitsManagment, self).create(vals)

###########################################################

class MasjedPermision(models.Model):
    _inherit = 'mosque.permision'

    supervisor_id = fields.Many2one('supervisor.item', string='Suprervisor item', track_visibility='onchange')

class mosque_domain(models.Model):
    _inherit = 'mk.mosque'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        post = []

        if 'default_sup' in self._context:
            sup_ids=self.env['supervisor.item'].resolve_2many_commands('visits' ,self._context.get('default_sup'))
            args.append(('id', 'not in',
                             [isinstance(d['masjed_id'], tuple) and d['masjed_id'][0] or d['masjed_id']
                              for d in sup_ids]))
        return super(mosque_domain,self).name_search(name, args=args, operator=operator, limit=limit)

class supervisors_domain(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        post = []
        if 'default_supervisor' in self._context:
            line_ids = self.env['center.item'].resolve_2many_commands('lines' ,self._context.get('default_supervisor'))
            args.append(('id', 'not in',
                             [isinstance(d['supervisor'], tuple) and d['supervisor'][0] or d['supervisor']
                              for d in line_ids]))
        return super(supervisors_domain,self).name_search(name, args=args, operator=operator, limit=limit)