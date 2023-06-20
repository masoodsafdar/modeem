# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class TestName(models.Model):
    _name = 'mk.test.names'
    _inherit=['mail.thread','mail.activity.mixin']

    @api.multi
    def get_study_class(self):
        study_class = self.env['mk.study.class'].search([('study_year_id', '=', self.get_year_default()),
                                                         ('is_default', '=', True)], limit=1)
        return study_class and study_class.id or False

    @api.multi
    def get_year_default(self):
        academic_year = self.env['mk.study.year'].search([('is_default', '=', True)], limit=1)
        return academic_year and academic_year.id or False

    academic_id    = fields.Many2one('mk.study.year',  string='Academic Year', default=get_year_default, required=True, ondelete='restrict', tracking=True)
    study_class_id = fields.Many2one('mk.study.class', string='Study class',   default=get_study_class,  domain=[('is_default', '=', True)], tracking=True, ondelete='restrict')
    active         = fields.Boolean("active", default=True, groups="maknon_tests.group_types_tests_archives", tracking=True)
    name           = fields.Char("Test term", required=True, tracking=True)
    branches       = fields.One2many('mk.branches.master', 'test_name', string='Branches')
    parent_test    = fields.Many2one("mk.test.names",                   string="Parent Test", tracking=True)
    test_group     = fields.Selection([('student','Students'),
                                       ('employee','Employee')],        string="Test Group", default='student', required=True, tracking=True)
    job_id         = fields.Many2many("hr.job", domain=[('educational_job','=','True')], tracking=True)
    type_test      = fields.Selection([('final',            'الخاتمين'),
                                       ('parts',            'الأجزاء'),
                                       ('contest',          'مسابقات'),
                                       ('correct_citation', 'تصحيح تلاوة'),
                                       ('indoctrination',   'تلقين'),
                                       ('vacations',        'اجازات'),], string="النوع", default='final', required=True, tracking=True)

    @api.multi
    def write(self, vals):
        if 'type_test' in vals:
            session_ids = self.env['student.test.session'].search([('test_name', '=', self.id)])
            if session_ids:
                raise ValidationError(_('عذرا ! لايمكنك تعديل النوع لارتباطه بجلسات اختبار ' ))

        return super(TestName, self).write(vals)

    @api.model
    def center_prepar_type_tests(self, center_prepration_id):
        query_string = ''' 

                  SELECT mk_test_names.id as parent_id,
                  mk_test_names.name as parent_name 

                  FROM mk_test_names left join mk_test_center_prepration_mk_test_names_rel on mk_test_center_prepration_mk_test_names_rel.mk_test_names_id = mk_test_names.id

                  WHERE mk_test_center_prepration_mk_test_names_rel.mk_test_center_prepration_id = {};
                  '''.format(int(center_prepration_id))
        self.env.cr.execute(query_string)
        center_prepar_type_tests = self.env.cr.dictfetchall()
        return center_prepar_type_tests


class TestBranches(models.Model):
    _name = 'mk.branches.master'
    _inherit=['mail.thread','mail.activity.mixin']
    _order = 'trackk, order'

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = " "
            if record.trackk == 'up':
                name = record.name + " - " + "مسار من الناس إلى الفاتحة"
            else:
                name = record.name + " - " + "مسار من الفاتحة إلى الناس"
            name = name + " [" + record.from_surah.name + " - " + record.to_surah.name + " ]"
            result.append((record.id, name))
        return result

    @api.depends('parts_ids')
    def part_num_count(self):
        self.parts_num = len(self.parts_ids)

    @api.depends('test_name')
    def get_study_class_id(self):
        for rec in self:
            rec.study_class_id = rec.test_name.study_class_id.id

    @api.multi
    def unlink(self):
        for rec in self:
            session_ids = self.env['student.test.session'].search([('branch', '=', self.id)], limit=1)
            if session_ids:
                raise ValidationError(_('عفوا , لاتمتلك صلاحية حذف الفرع لارتباطه بجلسات اختبار'))

        return super(TestBranches, self).unlink()

    active             = fields.Boolean(string="Active", default=True, groups="maknon_tests.group_tests_branches_archives", tracking=True)
    test_name          = fields.Many2one("mk.test.names",      string="test term", required="1", tracking=True)
    study_class_id     = fields.Many2one("mk.study.class", string="study_class_id", compute='get_study_class_id', store=True)
    parent_branch      = fields.Many2one("mk.branches.master", string="parent branch", tracking=True)
    from_surah         = fields.Many2one("mk.surah", string="from surah",         tracking=True)
    to_surah           = fields.Many2one("mk.surah", string="to surah",           tracking=True)
    from_aya           = fields.Many2one("mk.surah.verses",    string="from aya", tracking=True)
    to_aya             = fields.Many2one("mk.surah.verses",    string="to aya",   tracking=True)   
    age_groups         = fields.Many2many("mk.grade",          string="Age groups")    
    parts_ids          = fields.Many2many("mk.parts",          string="parts")
    subject_id         = fields.Many2one("mk.memorize.method", string="subject", tracking=True)
    round_frag         = fields.Boolean("round", default=True, tracking=True)
    order              = fields.Integer("order", tracking=True)
    passing_items      = fields.Many2many("mk.passing.items",    string="passing items")
    reward_items       = fields.Many2many("mk.reward.items",     string="reward")
    evaluation_items   = fields.Many2many("mk.evaluation.items", string="evaluation")
    employee_items     = fields.Many2many("employee.items",      string="Employee Items")
    #-p
    name               = fields.Char("Branch name", required=True, tracking=True)
    trackk             = fields.Selection([('up',   'من الناس إلى الفاتحة'),
                                           ('down', 'من الفاتحة إلى الناس')], string="المسار", required=True, tracking=True)
    parts_num          = fields.Integer("Parts No", compute='part_num_count', store=True)
    age_fillter        = fields.Selection([('open',  'Open'),
                                           ('close', 'Close')], string="Age Fillter", default="open", required=True, tracking=True)
    contsets           = fields.Boolean("contests",    tracking=True)
    courses            = fields.Boolean("courses",     tracking=True)
    general            = fields.Boolean("contests",    tracking=True)
    preliminary        = fields.Boolean("preliminary", tracking=True)
    duration           = fields.Integer("Branch duration", required=True, tracking=True)
    branch_group       = fields.Selection([('student',  'Students'),                                           
                                           ('employee', 'Employee')], string="Branch Group", default='student', required=True, tracking=True)
    job_id             = fields.Many2many("hr.job", domain=[('educational_job','=','True')])
    maximum_degree     = fields.Integer("Maximum degree", required=True, tracking=True)
    minumim_degree     = fields.Integer("Minum degree",   required=True, tracking=True)
    quations_method    = fields.Selection([('lines',   'Lines Number'),
                                           ('subject', 'Subject')], default='lines', string="Quation method", tracking=True)
    qu_number_per_part = fields.Integer("Question no per part", tracking=True)
    lines_per_part     = fields.Integer("Lines per Part", tracking=True)
    select_parts       = fields.Boolean("select part", default=False, tracking=True)

    @api.constrains('qu_number_per_part')
    def _check_qu_number_per_part(self):
        if self.qu_number_per_part == 0:
            raise ValidationError(_('الرجاء تحديد عدد أسئلة الفرع'))

    @api.onchange('trackk','select_parts', 'parts_ids')
    def trackk_change(self):
        first_surah = self.env['mk.surah'].search([('order','=',1)], limit=1)
        last_surah = self.env['mk.surah'].search([('order','=',114)], limit=1)
        self.parent_branch = False
        if first_surah and last_surah:
            if self.trackk == 'down':
                self.from_surah = first_surah.id
                self.to_surah = last_surah.id

            if self.trackk == 'up':
                self.from_surah = last_surah.id
                self.to_surah = first_surah.id
        if self.select_parts:
            first_select_part = self.env['mk.parts'].search([('id', 'in', self.parts_ids.ids)], order="order asc", limit=1)
            last_select_part = self.env['mk.parts'].search([('id', 'in', self.parts_ids.ids)],   order="order desc", limit=1)
            if self.trackk == 'down':
                from_subject_page = self.env['mk.subject.page'].search([('subject_page_id', '=', self.subject_id.id),
                                                                        ('part_id', '=', first_select_part.id)],order="order asc", limit=1)
                to_subject_page = self.env['mk.subject.page'].search([('subject_page_id', '=', self.subject_id.id),
                                                                      ('part_id', 'in', last_select_part.id)],order="order desc", limit=1)

                self.from_surah = from_subject_page.from_surah.id
                self.to_surah = to_subject_page.to_surah.id

            if self.trackk == 'up':
                from_subject_page = self.env['mk.subject.page'].search([('subject_page_id', '=', self.subject_id.id),
                                                                        ('part_id', '=', last_select_part.id)], order="order asc", limit=1)
                to_subject_page = self.env['mk.subject.page'].search([('subject_page_id', '=', self.subject_id.id),
                                                                      ('part_id', '=', first_select_part.id)], order="order desc", limit=1)
                to_surah = to_subject_page.to_surah
                to_surah_verses  = self.env['mk.surah.verses'].search([('surah_id', '=',to_surah.id)], order="original_surah_order desc")
                is_in_parts = True
                for verse in  to_surah_verses:
                    if verse.part_id.id not in self.parts_ids.ids:
                        is_in_parts = False
                        break

                if is_in_parts:
                    self.to_surah = to_subject_page.to_surah.id
                else :
                    if first_select_part.id == 163:
                        self.to_surah = 231
                    else:
                        to_suraaah = self.env['mk.surah'].search([('order', '=',int(to_surah.order) + 1 )], limit=1).id
                        self.to_surah = to_suraaah

                self.from_surah = from_subject_page.from_surah.id
                # self.to_surah = to_subject_page.to_surah.id

    @api.onchange('test_name')
    def test_name_change(self):
        self.branch_group = self.test_name.test_group
        self.job_id = self.test_name.job_id

    @api.model
    def eval_items_branch(self, branch_id):
        try:
            branch_id = int(branch_id)
        except:
            pass

        query_string = ''' 
        SELECT mk_evaluation_items.name as parent_item,
        mk_evaluation_items.total as parent_total,
        mk_evaluation_items.id as parent_item_id,
        mk_discount_item.id as item_id,
        mk_discount_item.name as item_name,
        mk_discount_item.amount as item_amount,
        COALESCE(mk_discount_item.allowed_discount, 0) as allowed_discount

        FROM mk_branches_master_mk_evaluation_items_rel,
        mk_evaluation_items,
        mk_discount_item

        WHERE 
        mk_branches_master_mk_evaluation_items_rel.mk_evaluation_items_id = mk_evaluation_items.id AND
        mk_evaluation_items.id = mk_discount_item.evaluation_item 
        AND mk_branches_master_mk_evaluation_items_rel.mk_branches_master_id={};
        '''.format(branch_id)

        self.env.cr.execute(query_string)
        eval_items_branch = self.env.cr.dictfetchall()

        return eval_items_branch

    @api.model
    def get_test_branches(self, test_id, trackk):
        try:
            test_id = int(test_id)
            trackk = trackk
        except:
            pass

        query_string = ''' 
                SELECT mk_branches_master.id as branch_id, 
                mk_branches_master.name as branch_name

                FROM mk_branches_master, 
                mk_test_names

                WHERE mk_branches_master.test_name = mk_test_names.id AND
                mk_test_names.id = {} AND
                mk_branches_master.trackk = '{}'

                ORDER BY mk_branches_master.order;
                '''.format(test_id, trackk)
        self.env.cr.execute(query_string)
        test_branches = self.env.cr.dictfetchall()
        return test_branches