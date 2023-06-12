# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from random import randint
from odoo.tools.translate import _
from odoo.exceptions import ValidationError, UserError
from odoo.osv import osv
from odoo.http import request

import logging

import time

_logger = logging.getLogger(__name__)


def get_state_translation_value(model_name=None, field_name=None, field_value=None):
    translated_state = dict(request.env[model_name].sudo().fields_get(allfields=[field_name])[field_name]['selection'])[field_value]
    return translated_state


class StudentPrepare(models.Model):
    _name = 'mk.student.prepare'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Prepration Students'
    _rec_name = 'link_id'

    #region prepare fields
    link_id             = fields.Many2one('mk.link', string='Student Link', ondelete='set null', index=True, track_visibility='onchange')
    student_register_id = fields.Many2one('mk.student.register', string='Student Link', ondelete='set null', compute='get_student_register', store=True, track_visibility='onchange')
    stage_pre_id = fields.Many2one('mk.episode', string='Episode', ondelete='set null', track_visibility='onchange')
    name = fields.Many2one('hr.employee', string='Teacher', required=True, track_visibility='onchange')
    program_id = fields.Many2one('mk.programs', string='Program', ondelete='restrict', track_visibility='onchange')
    general_behavior_type = fields.Selection([('excellent', 'ممتاز'),
                                              ('very_good', 'جيد جداً'),
                                              ('good', 'جيد'),
                                              ('accepted', 'مقبول'),
                                              ('weak', 'ضعيف'), ], default='accepted', string='السلوك العام')

    academic_id = fields.Many2one('mk.study.year', string='العام الدراسي', related='stage_pre_id.academic_id',copy=False, store=True)
    study_class_id = fields.Many2one('mk.study.class', string='الفصل الدراسي', related='stage_pre_id.study_class_id', copy=False, store=True)
    prepare_date = fields.Date('Prepration Date', default=fields.Date.today(), track_visibility='onchange')
    active = fields.Boolean('Active', track_visibility='onchange', default=True)

    check_memory = fields.Boolean('Check Program', compute='get_check', store=True, track_visibility='onchange')
    check_minimum = fields.Boolean('Check Minimum', compute='get_check', store=True, track_visibility='onchange')
    check_max = fields.Boolean('Check Minimum', compute='get_check', store=True, track_visibility='onchange')
    check_read = fields.Boolean('Check Reading', compute='get_check', store=True, track_visibility='onchange')

    std_save_ids    = fields.One2many('mk.listen.line', 'preparation_id', string='Save', domain=[('type_follow', '=', 'listen')], copy=False)
    smal_review_ids = fields.One2many('mk.listen.line', 'preparation_id', string='Smal Review ', domain=[('type_follow', '=', 'review_small')], copy=False)
    big_review_ids  = fields.One2many('mk.listen.line', 'preparation_id', string='Big Review', domain=[('type_follow', '=', 'review_big')], copy=False)
    recitation_ids  = fields.One2many('mk.listen.line', 'preparation_id', string='التلاوة', domain=[('type_follow', '=', 'tlawa')], copy=False)
    listen_ids      = fields.One2many('mk.listen.line', 'preparation_id', string='Listen lines', copy=False)

    history_ids  = fields.One2many('mk.student.prepare.history', 'preparation_id', string='History', copy=False)
    behavior_ids = fields.One2many('mk.student.prepare.behavior', 'preparation_id', string='سلوكيات الطالب', copy=False)
    presence_ids = fields.One2many('mk.student.prepare.presence', 'preparation_id', string='حضور الطالب', copy=False)

    nbr_lines   = fields.Integer('عدد الأسطر', compute='get_nbr_lines', store=True, copy=False)
    nbr_pages   = fields.Float('عدد الأوجه الإجمالي',   compute='get_nbr_lines', store=True, copy=False)
    nbr_listen_pages        = fields.Float(' أوجه التسميع',         compute='get_nbr_lines', store=True, copy=False)
    nbr_read_pages          = fields.Float(' أوجه التلاوة',          compute='get_nbr_lines', store=True, copy=False)
    nbr_small_review_pages  = fields.Float(' أوجه المراجعة الصغرى', compute='get_nbr_lines', store=True, copy=False)
    nbr_big_review_pages    = fields.Float(' أوجه المراجعة الكبرى', compute='get_nbr_lines', store=True, copy=False)
    is_meqraa_student       = fields.Boolean('Meqraa Student', default=False, track_visibility='onchange')
    #endregion

    #region old fields
    period_id    = fields.Many2one('mk.periods', string='Period', ondelete='restrict', track_visibility='onchange', copy=False)
    test_ids     = fields.One2many('mk.test.line', 'line_id', string='Line Test', copy=False)

    subh   = fields.Boolean('Subh', track_visibility='onchange')
    zuhr   = fields.Boolean('Zuhr', track_visibility='onchange')
    aasr   = fields.Boolean('Aasr', track_visibility='onchange')
    magrib = fields.Boolean('Magrib', track_visibility='onchange')
    esha   = fields.Boolean('Esha', track_visibility='onchange')
    period_subh   = fields.Char('Subh', track_visibility='onchange')
    period_zuhr   = fields.Char('Zuhr', track_visibility='onchange')
    period_aasr   = fields.Char('Aasr', track_visibility='onchange')
    period_magrib = fields.Char('Magrib', track_visibility='onchange')
    period_esha   = fields.Char('Esha', track_visibility='onchange')
    archived = fields.Boolean('Archived', track_visibility='onchange')
    is_delete_request = fields.Boolean('delete request', default=False)
    #endregion

    # @api.multi
    def write(self, vals):
        if 'active' in vals and vals.get('active') == False:
            cr = self.env.cr
            query1 = ('''update mk_student_prepare set active=false where id ='{}';''').format(self.id)
            cr.execute(query1)

            query2 = ('''update  mk_listen_line
                          set active=false where id in (select ml.id 
                                                       from mk_student_prepare as mp 
                                                       join  mk_listen_line as ml on  mp.id = ml.preparation_id 
                                                       where mp.id = '{}');''').format(self.id)
            cr.execute(query2)

            query3 = ('''update  mk_details_mistake set active=false where id in (select md.id
                                                                                  from  mk_student_prepare as mp  
                                                                                  join  mk_listen_line ml on mp.id = ml.preparation_id  
                                                                                  join  mk_details_mistake md on ml.id  = md.mistake_id 
                                                                                  where mp.id = '{}');''').format(self.id)
            cr.execute(query3)

            query4 = ('''update  mk_student_plan_line_indiscipline set active=false where id in (select mi.id
                                                                                                  from  mk_student_prepare as mp  join 
                                                                                                  mk_listen_line ml on mp.id = ml.preparation_id join 
                                                                                                  mk_details_mistake md on ml.id  = md.mistake_id join 
                                                                                                  mk_student_plan_line_indiscipline mi on md.id = mi.eval_id 
                                                                                                  where mp.id = '{}');''').format(self.id)
            cr.execute(query4)
        return super(StudentPrepare, self).write(vals)

    # @api.multi
    def action_update_student_prepare(self):
        preparation_id = self.env['mk.student.prepare'].browse(self.env.context.get('active_id'))
        student_id = preparation_id.link_id.student_id

        if student_id.is_student_meqraa:
            student_prepare_update_form = self.env.ref('mk_student_managment.view_meqraa_student_prepare_update_form')
        else:
            student_prepare_update_form = self.env.ref('mk_student_managment.view_student_prepare_update_form')
        action_vals = {
            'name': _('تعديل المنهج'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mk.student.prepare.update',
            'views': [(student_prepare_update_form.id, 'form')],
            'view_id': student_prepare_update_form.id,
            'target': 'new',
            'context': {'default_preparation_id': preparation_id.id,
                        'default_program_type':   preparation_id.link_id.program_type,
                        'default_program_id':     preparation_id.link_id.program_id.id,
                        'default_approache_id':   preparation_id.link_id.approache.id,
                        'episode_gender':         preparation_id.link_id.episode_id.women_or_men,
                        'default_type_order':     'assign'}
        }
        return action_vals

    #region compute fcts
    @api.depends('listen_ids.nbr_lines', 'listen_ids.nbr_pages')
    def get_nbr_lines(self):
        for rec in self:
            total_nbr_lines = 0
            nbr_listen_lines = 0
            nbr_read_lines = 0
            nbr_small_review_lines = 0
            nbr_big_review_lines = 0
            lines_ids = rec.listen_ids
            for line in lines_ids:
                nbr_lines = line.nbr_lines
                type_follow = line.type_follow
                total_nbr_lines += nbr_lines
                if type_follow == 'tlawa':
                    nbr_read_lines += nbr_lines
                elif type_follow == 'review_small':
                    nbr_small_review_lines += nbr_lines
                elif type_follow == 'review_big':
                    nbr_big_review_lines += nbr_lines
                else:
                    nbr_listen_lines += nbr_lines

            rec.nbr_lines = total_nbr_lines
            rec.nbr_pages = total_nbr_lines / 15

            rec.nbr_listen_pages = nbr_listen_lines / 15
            rec.nbr_read_pages = nbr_read_lines / 15
            rec.nbr_small_review_pages = nbr_small_review_lines / 15
            rec.nbr_big_review_pages = nbr_big_review_lines / 15

    @api.depends('link_id')
    def get_student_register(self):
        for rec in self:
            link_id = rec.link_id
            if link_id:
                rec.student_register_id = link_id.student_id

    @api.depends('link_id', 'link_id.is_memorize', 'link_id.is_min_review', 'link_id.is_big_review', 'link_id.is_tlawa')
    def get_check(self):
        for rec in self:
            link = rec.link_id
            rec.check_memory= link.is_memorize
            rec.check_minimum= link.is_min_review
            rec.check_max= link.is_big_review
            rec.check_read= link.is_tlawa

        # self.sudo().write({'check_memory':   link.is_memorize,
        #                     'check_minimum': link.is_min_review,
        #                     'check_max':     link.is_big_review,
        #                     'check_read':    link.is_tlawa})
    #endregion

    #region api
    @api.model
    def set_general_behavior_type(self, general_behavior_type, link_id):
        _logger.info('\n\n _____ set_general_behavior_type : %s ', link_id)
        link_id = int(link_id)

        preparation_id = self.sudo().search([('link_id', '=', link_id)], limit=1)
        if preparation_id:
            try:
                preparation_id.sudo().write({'general_behavior_type': general_behavior_type})
                return 1
            except:
                return 2
        _logger.info('\n\n _____ set_general_behavior_type END')
        return 0

    @api.model
    def add_behavior(self, plan_id, behavior_id, send_to_parent, send_to_teacher):
        _logger.info('\n\n\n ____________  add_behavior : %s', plan_id)
        student_bahavior = self.env['mk.student.prepare.behavior'].create({'preparation_id': plan_id,
                                                                          'behavior_id': behavior_id,
                                                                          'date_behavior': datetime.strptime(fields.Date.today(), '%Y-%m-%d').date(),
                                                                          'send_to_parent': send_to_parent if send_to_parent else False,
                                                                          'send_to_teacher': send_to_teacher if send_to_teacher else False})
        _logger.info('\n\n\n ____________  add_behavior END')
        return student_bahavior and student_bahavior.id or 0
    #endregion

    #region old api
    @api.model
    def student_prepare(self, std_id, ep_id):
        return []
        try:
            std_id = int(std_id)
            ep_id = int(ep_id)
        except:
            pass

        preparation_id = self.env['mk.student.prepare'].search([('link_id', '=', std_id),
                                                                ('stage_pre_id', '=', ep_id)], limit=1)
        lines_list = []
        if preparation_id:
            if preparation_id.check_memory:
                listen_listen_line = self.env['mk.listen.line'].search([('preparation_id', '=', preparation_id.id),
                                                                        ('type_follow', '=', 'listen'),
                                                                        ('state', '!=', 'done')], limit=1)

                if listen_listen_line:
                    lines_list.append({'student_name': listen_listen_line.student_id.student_id.display_name,
                                       'type_follow': listen_listen_line.type_follow,
                                       'from_sura_name': listen_listen_line.from_surah.name,
                                       'from_aya': listen_listen_line.from_aya.original_surah_order,
                                       'to_sura_name': listen_listen_line.to_surah.name,
                                       'to_aya': listen_listen_line.to_aya.original_surah_order,
                                       'state': listen_listen_line.state,
                                       'delay': int(listen_listen_line.delay),
                                       'prep_id': listen_listen_line.id,
                                       'mistake': listen_listen_line.mistake,
                                       'degree': listen_listen_line.degree})
            if preparation_id.check_minimum:
                review_small_listen_line = self.env['mk.listen.line'].search(
                    [('preparation_id', '=', preparation_id.id),
                     ('type_follow', '=', 'review_small'),
                     ('state', '!=', 'done')], limit=1)


                if review_small_listen_line:
                    lines_list.append({'student_name': review_small_listen_line.student_id.student_id.display_name,
                                       'type_follow': review_small_listen_line.type_follow,
                                       'from_sura_name': review_small_listen_line.from_surah.name,
                                       'from_aya': review_small_listen_line.from_aya.original_surah_order,
                                       'to_sura_name': review_small_listen_line.to_surah.name,
                                       'to_aya': review_small_listen_line.to_aya.original_surah_order,
                                       'state': review_small_listen_line.state,
                                       'delay': int(review_small_listen_line.delay),
                                       'prep_id': review_small_listen_line.id,
                                       'mistake': review_small_listen_line.mistake,
                                       'degree': review_small_listen_line.degree})
            if preparation_id.check_max:
                review_big_listen_line = self.env['mk.listen.line'].search([('preparation_id', '=', preparation_id.id),
                                                                            ('type_follow', '=', 'review_big'),
                                                                            ('state', '!=', 'done')], limit=1)


                if review_big_listen_line:
                    lines_list.append({'student_name': review_big_listen_line.student_id.student_id.display_name,
                                       'type_follow': review_big_listen_line.type_follow,
                                       'from_sura_name': review_big_listen_line.from_surah.name,
                                       'from_aya': review_big_listen_line.from_aya.original_surah_order,
                                       'to_sura_name': review_big_listen_line.to_surah.name,
                                       'to_aya': review_big_listen_line.to_aya.original_surah_order,
                                       'state': review_big_listen_line.state,
                                       'delay': int(review_big_listen_line.delay),
                                       'prep_id': review_big_listen_line.id,
                                       'mistake': review_big_listen_line.mistake,
                                       'degree': review_big_listen_line.degree})
            if preparation_id.check_read:
                tlawa_listen_line = self.env['mk.listen.line'].search([('preparation_id', '=', preparation_id.id),
                                                                       ('type_follow', '=', 'tlawa'),
                                                                       ('state', '!=', 'done')], limit=1)


                if tlawa_listen_line:
                    lines_list.append({'student_name': tlawa_listen_line.student_id.student_id.display_name,
                                       'type_follow': tlawa_listen_line.type_follow,
                                       'from_sura_name': tlawa_listen_line.from_surah.name,
                                       'from_aya': tlawa_listen_line.from_aya.original_surah_order,
                                       'to_sura_name': tlawa_listen_line.to_surah.name,
                                       'to_aya': tlawa_listen_line.to_aya.original_surah_order,
                                       'state': tlawa_listen_line.state,
                                       'delay': int(tlawa_listen_line.delay),
                                       'prep_id': tlawa_listen_line.id,
                                       'mistake': tlawa_listen_line.mistake,
                                       'degree': tlawa_listen_line.degree})

        return lines_list

    @api.model
    def plans_student_settings(self, student_plan_id):
        return str([])
        try:
            student_plan_id = int(student_plan_id)
        except:
            pass

        student_preparation = self.env['mk.student.prepare'].sudo().search([('id', '=', student_plan_id)], limit=1)

        plan_m = []
        plan_r = []
        plan_t = []

        for history in student_preparation.history_ids:
            type_subject = history.type_subject
            new_plan = {'id': history.id,
                        'type_subject': type_subject,
                        'surah_from_id': history.surah_from_id.id,
                        'aya_from_id': history.aya_from_id.id,
                        # 'start_point_id': history.start_point_id.id,
                        'direction': history.direction,
                        'qty_id': history.qty_id.id}

            if type_subject == "m":
                plan_m = [new_plan]

            elif type_subject == "r":
                plan_r = [new_plan]

            elif type_subject == "t":
                plan_t = [new_plan]

            new_plan = {}

        plans_student_settings = plan_m + plan_r + plan_t

        return str(plans_student_settings)

    @api.model
    def get_student_course(self, student_id):
        return []
        try:
            student_id = int(student_id)
        except:
            pass

        lines_list = []
        student_prepare = self.env['mk.student.prepare'].search([('link_id', '=', student_id)], limit=1)
        if student_prepare:
            if student_prepare.check_memory:
                listen_listen_line = self.env['mk.listen.line'].search([('preparation_id', '=', student_prepare.id),
                                                                        ('type_follow', '=', 'listen'),
                                                                        ('state', '!=', 'done')], limit=1)

                if listen_listen_line:
                    lines_list.append({'id': listen_listen_line.id,
                                       'student_id': listen_listen_line.student_id.id,
                                       'from_surah': listen_listen_line.from_surah.name,
                                       'to_surah': listen_listen_line.to_surah.name,
                                       'from_aya': listen_listen_line.from_aya.original_surah_order,
                                       'to_aya': listen_listen_line.to_aya.original_surah_order,
                                       'state': listen_listen_line.state,
                                       'type_follow': listen_listen_line.type_follow})
            if student_prepare.check_minimum:
                review_small_listen_line = self.env['mk.listen.line'].search(
                    [('preparation_id', '=', student_prepare.id),
                     ('type_follow', '=', 'review_small'),
                     ('state', '!=', 'done')], limit=1)

                if review_small_listen_line:
                    lines_list.append({'id': review_small_listen_line.id,
                                       'student_id': review_small_listen_line.student_id.id,
                                       'from_surah': review_small_listen_line.from_surah.name,
                                       'to_surah': review_small_listen_line.to_surah.name,
                                       'from_aya': review_small_listen_line.from_aya.original_surah_order,
                                       'to_aya': review_small_listen_line.to_aya.original_surah_order,
                                       'state': review_small_listen_line.state,
                                       'type_follow': review_small_listen_line.type_follow})
            if student_prepare.check_max:
                review_big_listen_line = self.env['mk.listen.line'].search([('preparation_id', '=', student_prepare.id),
                                                                            ('type_follow', '=', 'review_big'),
                                                                            ('state', '!=', 'done')], limit=1)

                if review_big_listen_line:
                    lines_list.append({'id': review_big_listen_line.id,
                                       'student_id': review_big_listen_line.student_id.id,
                                       'from_surah': review_big_listen_line.from_surah.name,
                                       'to_surah': review_big_listen_line.to_surah.name,
                                       'from_aya': review_big_listen_line.from_aya.original_surah_order,
                                       'to_aya': review_big_listen_line.to_aya.original_surah_order,
                                       'state': review_big_listen_line.state,
                                       'type_follow': review_big_listen_line.type_follow})
            if student_prepare.check_read:
                tlawa_listen_line = self.env['mk.listen.line'].search([('preparation_id', '=', student_prepare.id),
                                                                       ('type_follow', '=', 'tlawa'),
                                                                       ('state', '!=', 'done')], limit=1)

                if tlawa_listen_line:
                    lines_list.append({'id': tlawa_listen_line.id,
                                       'student_id': tlawa_listen_line.student_id.id,
                                       'from_surah': tlawa_listen_line.from_surah.name,
                                       'to_surah': tlawa_listen_line.to_surah.name,
                                       'from_aya': tlawa_listen_line.from_aya.original_surah_order,
                                       'to_aya': tlawa_listen_line.to_aya.original_surah_order,
                                       'state': tlawa_listen_line.state,
                                       'type_follow': tlawa_listen_line.type_follow})
        return lines_list
    #endregion

    #region cron fcts
    @api.model
    def cron_delete_listen_line_ep_summer_43(self):
        prepare_ids = self.env['mk.student.prepare'].search([('academic_id', '=', 20),
                                                             ('study_class_id', '=', 108),
                                                             ('stage_pre_id.is_episode_meqraa', '=', False)],
                                                            order="id asc")
        total = len(prepare_ids)
        i = 0
        j = 0
        empty_prep = 0
        for prep in prepare_ids:
            i += 1
            listen_lines_ids = self.env['mk.listen.line'].search([('preparation_id', '=', prep.id)])
            if not listen_lines_ids:
                empty_prep += 1
            else:
                listen_lines_ids.unlink()
                j += 1

    @api.model
    def cron_delete_student_prepare_without_listen_line(self, id_from):
        cr = self.env.cr
        start_date = fields.Datetime.now()
        prepare_ids = self.env['mk.student.prepare'].search([('listen_ids', '=', False),
                                                             ('id', '>', id_from),
                                                             '|', ('active', '=', True),
                                                             ('active', '=', False)], order="id asc", limit=1000)
        # i = 0
        # for prep in prepare_ids:
        #     i += 1
        #     behaviors = self.env['mk.student.prepare.behavior'].search([('preparation_id', '=', prep.id),
        #                                                                '|', ('active', '=', True),
        #                                                                     ('active', '=', False)])
        # if behaviors:
        #     for behav in behaviors:
        #        behav.unlink()

        # list_prepare = [ prep for prep in prepare_ids.ids]

        # query1 = '''delete from mk_student_prepare_behavior where preparation_id in %s;'''
        # cr.execute(query1, [tuple(list_prepare)])

        # query2 = '''delete from mk_student_prepare_history where preparation_id in %s;'''
        # cr.execute(query2, [tuple(list_prepare)])

        # i = 0
        # for prep in prepare_ids:
        #     i += 1
        #     history = self.env['mk.student.prepare.history'].search([('preparation_id', '=', prep.id),
        #                                                                '|', ('active', '=', True),
        #                                                                     ('active', '=', False)])
        #     if history:
        #         for hist in history:
        #             hist.unlink()

        # query = '''delete from mk_student_prepare where id in %s;'''
        # cr.execute(query,[tuple(list_prepare)])

        i = 0
        j = 0
        for prep in prepare_ids:
            try:
                prep.sudo().unlink()
                i += 1
            except:
                j += 1

        end_date = fields.Datetime.now()

    @api.model
    def cron_delete_student_prepare_with_no_episode(self):
        cr = self.env.cr
        start_date = fields.Datetime.now()
        prepare_ids = self.env['mk.student.prepare'].search([('stage_pre_id', '=', False),
                                                             '|', ('active', '=', True),
                                                             ('active', '=', False)], order="id asc", limit=(2000))

        # query1 = '''select id from mk_student_prepare where stage_pre_id is null limit 1000; '''
        # cr.execute(query1)
        # student_prepare = cr.dictfetchall()
        # list_prepare = [prep['id'] for prep in student_prepare]
        # nbr_prepare = len(list_prepare)

        # query1 = '''delete from mk_student_prepare_behavior where preparation_id in %s;'''
        # cr.execute(query1, [tuple(list_prepare)])

        # i = 0
        # for prep in prepare_ids:
        # i += 1
        # behaviors = self.env['mk.student.prepare.behavior'].search([('preparation_id', '=', prep.id),
        #                                                           '|', ('active', '=', True),
        #                                                                ('active', '=', False)])
        # if behaviors:
        #    for behav in behaviors:
        #       behav.sudo().unlink()

        # query2 = '''delete from mk_student_prepare_history where preparation_id in %s;'''
        # cr.execute(query2, [tuple(list_prepare)])

        # i = 0
        # for prep in prepare_ids:
        #    i += 1
        #    history = self.env['mk.student.prepare.history'].search([('preparation_id', '=', prep.id),
        #                                                                '|', ('active', '=', True),
        #                                                                     ('active', '=', False)])
        #    if history:
        #        for hist in history:
        #            hist.sudo().unlink()

        # query = '''delete from mk_student_prepare where id in %s;'''
        # cr.execute(query, [tuple(list_prepare)])

        i = 0
        j = 0
        for prep in prepare_ids:
            try:
                prep.sudo().unlink()
                i += 1
            except:
                j += 1

        end_date = fields.Datetime.now()

    @api.model
    def action_archive_old_prepera(self):
        cr = self.env.cr

        query1 = ('''UPDATE mk_student_prepare SET active=False WHERE create_date < '2021-12-03 23:00:00';''')
        cr.execute(query1)

        query2 = ('''UPDATE mk_listen_line SET active=False WHERE create_date < '2021-12-03 23:00:00';''')
        cr.execute(query2)

        query3 = ('''UPDATE mk_student_prepare_history SET active=False WHERE create_date < '2021-12-03 23:00:00';''')
        cr.execute(query3)

        query4 = ('''UPDATE mk_student_prepare_behavior SET active=False WHERE create_date < '2021-12-03 23:00:00';''')
        cr.execute(query4)
    #endregion


class ListenLine(models.Model):
    _name = 'mk.listen.line'
    _order = 'actual_date desc ,id desc'
    _description = 'MK Listen Lin'
    _rec_name = 'preparation_id'

    # region line fields
    preparation_id = fields.Many2one('mk.student.prepare', string='Link std_save_ids', ondelete='cascade', index=True)
    center_department_id = fields.Many2one('hr.department', string='المركز')
    mosque_id            = fields.Many2one("mk.mosque", string='المسجد')
    episode    = fields.Many2one("mk.episode", string='الحلقة')
    student_id = fields.Many2one('mk.link', string="Student", index=True)
    student_register_id = fields.Many2one("mk.student.register", string='Student Register')

    study_year_id  = fields.Many2one("mk.study.year",  string='العام الدراسي')
    study_class_id = fields.Many2one("mk.study.class", string='الفصل الدراسي')
    actual_date    = fields.Date('Actual Date', default=fields.Date.today())

    from_surah  = fields.Many2one('mk.surah',        string='From Sura', ondelete='restrict')
    from_aya    = fields.Many2one('mk.surah.verses', string='From Aya',  ondelete='restrict')
    to_surah    = fields.Many2one('mk.surah',        string='To Sura',   ondelete='restrict')
    to_aya      = fields.Many2one('mk.surah.verses', string='To Aya',    ondelete='restrict')
    nbr_lines   = fields.Integer('عدد الأسطر',        compute='get_nbr_lines', store=True)
    nbr_pages   = fields.Float('عدد الأوجه الإجمالي', compute='get_nbr_lines', store=True)
    type_follow = fields.Selection([('listen', 'Listening'),
                                    ('review_small', 'Smll Review'),
                                    ('review_big', 'Big Review'),
                                    ('tlawa', 'التلاوة')], default='listen', string='Type of Follow', required=True, index=True)

    total_mstk_qty   = fields.Integer('أخطاء الحفظ',   store=True)
    total_mstk_read  = fields.Integer('أخطاء التجويد', store=True)
    approache_id     = fields.Many2one("mk.approaches", string='Approache')
    degree           = fields.Float('Degree', compute='amount_mistake', default=100)

    active = fields.Boolean('Active', related='preparation_id.active', default=True, store=True)
    state  = fields.Selection([('draft', 'Draft'),
                              ('absent', 'Absent'),
                              ('done', 'Done')], 'Status', default='done', index=True)
    is_meqraa_student = fields.Boolean('Meqraa Student', default=False)
    is_from_mobile = fields.Boolean()
    #endregion

    #region old fields
    order      = fields.Integer('Order')
    is_test    = fields.Boolean('is test')

    date  = fields.Date('Date')
    day   = fields.Selection([('0', 'Monday'),
                            ('1', 'Tuseday'),
                            ('2', 'Wednsday'),
                            ('3', 'Thursday'),
                            ('4', 'Friday'),
                            ('5', 'Saturday'),
                            ('6', 'Sunday')], 'Day')
    actual_day  = fields.Selection([('0', 'Monday'),
                                     ('1', 'Tuseday'),
                                     ('2', 'Wednsday'),
                                     ('3', 'Thursday'),
                                     ('4', 'Friday'),
                                     ('5', 'Saturday'),
                                     ('6', 'Sunday')], 'Actual Day')
    program_id  = fields.Many2one('mk.programs',              string='Program', ondelete='restrict')
    subject_id  = fields.Many2one('mk.subject.configuration', string='Subject')
    day_subject = fields.Char('Day Subject')
    check  = fields.Boolean('Matching', default=True)
    delay  = fields.Boolean('Delay')
    is_absent_excuse = fields.Boolean('غائب بعذر')
    is_not_read      = fields.Boolean('لم يسمع')
    permission_id    = fields.Many2one('mk.student_absence', string='Permission', ondelete='restrict')

    subh   = fields.Boolean('Subh')
    zuhr   = fields.Boolean('Zuhr')
    aasr   = fields.Boolean('Aasr')
    magrib = fields.Boolean('Magrib')
    esha   = fields.Boolean('Esha')

    mistake_line_ids = fields.One2many('mk.details.mistake', 'mistake_id', string='Mistake')
    mistake          = fields.Integer('Mistaks', compute='amount_mistake', store=True)
    #endregion

    #region Onchange
    @api.onchange('episode')
    def onchange_episode(self):
        episode = self.episode
        link_ids = episode.link_ids.filtered(lambda l: l.state == 'accept')
        students = [link.student_id.id for link in link_ids]
        return {'value': {'study_class_id': episode.study_class_id.id,
                          'student_register_id': False},
                'domain': {'student_register_id': [('id', 'in', students)]}}

    @api.onchange('student_register_id')
    def onchange_episode(self):
        student = self.student_register_id
        link_ids = student.link_ids.filtered(lambda l: l.state == 'accept')
        if not self.env.context.get('active_model') == 'mk.mosque':
            episodes = [link.episode_id.id for link in link_ids]
            return {'domain': {'episode': [('id', 'in', episodes)]}}

    @api.onchange('mosque_id')
    def onchange_mosque(self):
        episodes = self.env['mk.episode'].search([('mosque_id','=',self.mosque_id.id),
                                                  ('state','in',['accept','draft']),
                                                  ('study_class_id.is_default', '=', True)])
        return {'domain': {'episode': [('id', 'in', episodes.ids)]}}

    @api.onchange('from_surah')
    def onchange_from_surah(self):
        self.from_aya = False

    @api.onchange('to_surah')
    def onchange_to_surah(self):
        self.to_aya = False
    #endregion

    @api.constrains('actual_date')
    def check_actual_date(self):
        for record in self:
            if record.actual_date and record.actual_date > fields.Date.today():
                raise ValidationError(_('الرجاء التحقق من التاريخ الفعلي المحدد! لا يمكن أن يكون أكبر من تاريخ اليوم'))

    @api.model
    def create(self, vals):
        if not vals.get('student_id', False):
            student_link = self.env['mk.link'].search([('episode_id', '=', vals.get('episode')),
                                                       ('student_id', '=', vals.get('student_register_id'))], limit=1)
            vals['student_id'] = student_link.id
            vals['preparation_id'] = student_link.preparation_id.id
            vals['mosque_id'] = student_link.mosq_id.id
            vals['center_department_id'] = student_link.mosq_id.center_department_id.id
            vals['approache_id'] = student_link.approache.id
            vals['study_year_id'] = student_link.academic_id.id
            vals['study_class_id'] = student_link.study_class_id.id
        return super(ListenLine, self).create(vals)

    #region Get api
    @api.model
    def order_students(self, episode_id, flter):
        _logger.info('\n\n\n ____________  order_students : %s', episode_id)
        students = []
        episode_id = int(episode_id)
        actual_date = datetime.strptime(fields.Date.today(), '%Y-%m-%d').date()
        links = self.env['mk.link'].search([('episode_id', '=', episode_id),
                                             ('state', '=', 'accept')])
        presences = self.env['mk.student.prepare.presence'].search([('episode_id', '=', episode_id),
                                                                    ('presence_date', '=', actual_date)])
        test_sessions = self.env['student.test.session'].search([('episode_id', '=', episode_id),
                                                                 ('state', '!=', 'cancel')])
        for link in links:
            vals = {}
            link_id = link.id

            presence = presences.filtered(lambda p: p.link_id == link)
            state = 'تحضير الطالب'
            if presence:
                presence = presence[0]
                state = get_state_translation_value('mk.student.prepare.presence', 'status', presence.status)

            age = 0
            # dob = link.student_id.birthdate
            # if dob:
            #     d1 = datetime.strptime(dob, "%Y-%m-%d").date()
            #     d2 = date.today()
            #     age = relativedelta(d2, d1).years
            preparation = link.preparation_id
            general_behavior = preparation.general_behavior_type
            general_behavior_type = False
            if general_behavior:
                general_behavior_type = get_state_translation_value('mk.student.prepare', 'general_behavior_type', general_behavior)

            vals = {'id':                    link_id,
                    'student_id':            link.student_id.id,
                    'plan_id':               preparation.id,
                    'general_behavior_type': general_behavior_type,
                    'name':  link.student_id.display_name,
                    'rate':  0,
                    'age':   age,
                    'state': state}

            test_session = test_sessions.filtered(lambda t: t.student_id == link)
            if test_session:
                test_session = test_session[0]
                vals.update({'test_register': True,
                            'session_id':     test_session.id,
                            'type_exam_id':   test_session.test_name.id,
                            'track':          test_session.branch.trackk,
                            'branch_id':      test_session.branch.id,
                            'period_id':      test_session.test_time.id})
            else:
                vals.update({'test_register': False,
                             'session_id':    False,
                             'type_exam_id':  False,
                             'track':         False,
                             'branch_id':     False,
                             'period_id':     False})
            students += [vals]
        students = sorted(students, key=lambda k: k[flter])
        return str(students)

    @api.model
    def student_behaviors(self, link_id):
        behaviors = self.env['mk.student.prepare.behavior'].search([('preparation_id.link_id', '=', link_id)])
        if not behaviors:
            return []

        plan = behaviors[0].preparation_id

        teacher_name = plan.name.name

        episode = plan.stage_pre_id
        episode_id = episode.id
        episode_name = episode.name
        period_id = episode.period_id.id

        mosque_name = episode.mosque_id.name

        student = plan.link_id.student_id
        student_id = student.id
        student_name = student.display_name

        records = []

        for behavior in behaviors:
            records += [{'id':           behavior.id,
                         'date':         behavior.date_behavior,

                         'teacher_name': teacher_name,
                         'masjed_name':  mosque_name,

                         'episode_id':   episode_id,
                         'episode_name': episode_name,
                         'period': period_id,

                         'student_id':   student_id,
                         'student_name': student_name,

                         'comment_name': behavior.behavior_id.name,
                         'punishment_name': '',
                         'punish_date': False, }]

        return records

    @api.model
    def educational_plan(self, episode_id, student_id):
        _logger.info('\n\n\n ____________  educational_plan : %s', student_id)
        episode_id = int(episode_id)
        student_id = int(student_id)

        line_link = self.env['mk.link'].search([('episode_id', '=', episode_id),
                                                ('student_id', '=', student_id)], limit=1)
        lines = self.env['mk.listen.line'].search([('student_id', '=', line_link.id)], order='order')

        memorize_lines = []
        s_review_lines = []
        big_review_lines = []
        tlawa_lines = []

        if line_link.is_memorize:
            for line in lines.filtered(lambda l: l.type_follow == 'listen'):
                memorize_lines.append({"prep_id":         line.id,
                                       "actual_date":     line.actual_date ,
                                       "from_sura_name":  line.from_surah.name,
                                       "from_aya":        line.from_aya.original_surah_order,
                                       "to_sura_name":    line.to_surah.name,
                                       "to_aya":          line.to_aya.original_surah_order,
                                       "total_mstk_qty":  line.total_mstk_qty,
                                       "total_mstk_read": line.total_mstk_read})

        if line_link.is_min_review:
            for line in lines.filtered(lambda l: l.type_follow == 'review_small'):
                s_review_lines.append({"prep_id":         line.id,
                                       "actual_date":     line.actual_date,
                                       "from_sura_name":  line.from_surah.name,
                                       "from_aya":        line.from_aya.original_surah_order,
                                       "to_sura_name":    line.to_surah.name,
                                       "to_aya":          line.to_aya.original_surah_order,
                                       "total_mstk_qty":  line.total_mstk_qty,
                                       "total_mstk_read": line.total_mstk_read})

        if line_link.is_big_review:
            for line in lines.filtered(lambda l: l.type_follow == 'review_big'):
                big_review_lines.append({"prep_id":         line.id,
                                         "actual_date":     line.actual_date,
                                         "from_sura_name":  line.from_surah.name,
                                         "from_aya":        line.from_aya.original_surah_order,
                                         "to_sura_name":    line.to_surah.name,
                                         "to_aya":          line.to_aya.original_surah_order,
                                         "total_mstk_qty":  line.total_mstk_qty,
                                         "total_mstk_read": line.total_mstk_read})

        if line_link.is_tlawa:
            for line in lines.filtered(lambda l: l.type_follow == 'tlawa'):
                tlawa_lines.append({"prep_id":         line.id,
                                    "actual_date":     line.actual_date,
                                    "from_sura_name":  line.from_surah.name,
                                    "from_aya":        line.from_aya.original_surah_order,
                                    "to_sura_name":    line.to_surah.name,
                                    "to_aya":          line.to_aya.original_surah_order,
                                    "total_mstk_qty":  line.total_mstk_qty,
                                    "total_mstk_read": line.total_mstk_read})

        educational_plan = {'plan_listen':       memorize_lines,
                            'plan_review_small': s_review_lines,
                            'plan_review_big':   big_review_lines,
                            'plan_tlawa':        tlawa_lines}
        return educational_plan

    @api.model
    def teacher_plain_lines(self, episode_id, student_id):
        _logger.info('\n\n\n ____________  teacher_plain_lines : %s', student_id)
        episode_id = int(episode_id)
        student_id = int(student_id)
        tlawa = {}
        listen = {}
        reviewsmall = {}
        reviewbig = {}

        link = self.env['mk.link'].search([('episode_id', '=', episode_id),
                                           ('student_id', '=', student_id),
                                           ('state', '=', 'accept')], limit=1)
        preparation_id = link.preparation_id.id
        default_vals = {'degree': None,
                         'from_aya': 1,
                         'from_sura_name': "الفاتحة",
                         'mistake': 0,
                         'prep_id': preparation_id,
                         'to_aya': None,
                         'to_sura_name': None}
        done_listen_lines = self.env['mk.listen.line'].search([('preparation_id', '=', preparation_id)], order='id desc')

        if link.is_memorize:
            item_line = False
            done_listen_line = done_listen_lines.filtered(lambda l: l.type_follow == 'listen')
            for item in done_listen_line:
                item_line = item
                break
            if item_line:
                listen = self.check_line_state(item_line)
            else:
                listen = default_vals

        if link.is_min_review:
            item_line = False
            done_review_small_line = done_listen_lines.filtered(lambda l: l.type_follow == 'review_small')
            for item in done_review_small_line:
                item_line = item
                break
            if item_line:
                reviewsmall = self.check_line_state(item_line)
            else:
                reviewsmall = default_vals

        if link.is_big_review:
            item_line = False
            done_review_big_line = done_listen_lines.filtered(lambda l: l.type_follow == 'review_big')
            for item in done_review_big_line:
                item_line = item
                break
            if item_line:
                reviewbig = self.check_line_state(item_line)
            else:
                reviewbig = default_vals

        if link.is_tlawa:
            item_line = False
            done_tlawa_line = done_listen_lines.filtered(lambda l: l.type_follow == 'tlawa')
            for item in done_tlawa_line:
                item_line = item
                break
            if item_line:
                tlawa = self.check_line_state(item_line)
            else:
                tlawa = default_vals

        data = {'tlawa':       tlawa,
                'listen':      listen,
                'reviewsmall': reviewsmall,
                'reviewbig':   reviewbig }
        return data

    @api.model
    def check_line_state(self, line):
        to_aya_order = line.to_aya.original_accumalative_order
        next_aya = self.env['mk.surah.verses'].search([('original_accumalative_order', '=', to_aya_order+1)], limit=1)
        if next_aya:
            from_surah = next_aya.surah_id.name
            from_aya = next_aya.original_surah_order
        else:
            from_surah = "الفاتحة"
            from_aya = 1

        vals = {'degree':         100,
                'from_aya':       from_aya,
                'from_sura_name': from_surah,
                'mistake':        0,
                'prep_id':        line.preparation_id.id,
                'to_aya':         None,
                'to_sura_name':   None}
        return vals

    @api.model
    def student_plan_lines_mobile(self, link_id):
        plan = self.env['mk.student.prepare'].search([('link_id', '=', link_id)], limit=1)

        if not plan:
            return []

        plan_id = plan.id
        listen_plan_lines = self.env['mk.listen.line'].search([('preparation_id', '=', plan_id),
                                                               ('type_follow', '=', 'listen'),
                                                               ('actual_date', '!=', False)])
        min_rev_plan_lines = self.env['mk.listen.line'].search([('preparation_id', '=', plan_id),
                                                                ('type_follow', '=', 'review_small'),
                                                                ('actual_date', '!=', False)])
        max_rev_plan_lines = self.env['mk.listen.line'].search([('preparation_id', '=', plan_id),
                                                                ('type_follow', '=', 'review_big'),
                                                                ('actual_date', '!=', False)])
        tlawa_plan_lines = self.env['mk.listen.line'].search([('preparation_id', '=', plan_id),
                                                              ('type_follow', '=', 'tlawa'),
                                                              ('actual_date', '!=', False)])

        listen_records = []
        min_rev_records = []
        max_rev_records = []
        tlawa_records = []

        for listen_plan_line in listen_plan_lines:
            listen_records += [self.get_student_plan_lines_mobile(listen_plan_line)]

        for min_rev_plan_line in min_rev_plan_lines:
            min_rev_records += [self.get_student_plan_lines_mobile(min_rev_plan_line)]

        for max_rev_plan_line in max_rev_plan_lines:
            max_rev_records += [self.get_student_plan_lines_mobile(max_rev_plan_line)]

        for tlawa_plan_line in tlawa_plan_lines:
            tlawa_records += [self.get_student_plan_lines_mobile(tlawa_plan_line)]

        return [{'listen': listen_records},
                {'reviewsmall': min_rev_records},
                {'reviewbig': max_rev_records},
                {'tlawa': tlawa_records}]

    @api.model
    def get_student_plan_lines_mobile(self, plan_line):
        mistake_lines = []

        for mistake_line in plan_line.mistake_line_ids:
            aya = mistake_line.aya_id
            if not aya:
                continue

            mistake_lines += [{'nbr_mstk_qty': mistake_line.nbr_mstk_qty,
                               'nbr_mstk_qlty': mistake_line.number_mistake,
                               'nbr_mstk_read': mistake_line.nbr_mstk_read,

                               'surah_id': mistake_line.surah_id.id,
                               'surah_id_name': mistake_line.surah_id.name,

                               'aya_id': aya.id,
                               'aya_name': aya.original_surah_order}]

        return {'mistakes': mistake_lines,

                'actual_date': plan_line.actual_date,

                'from_sura_name': plan_line.from_surah.name,
                'from_aya': plan_line.from_aya.original_surah_order,

                'to_sura_name': plan_line.to_surah.name,
                'to_aya': plan_line.to_aya.original_surah_order}
    #endregion

    # region offline api
    @api.model
    def teacher_offline_check_students(self, data):
        _logger.info('\n\n\n ____________  teacher_offline_check_students : %s', data)
        episode_id = data ['episode_id']
        app_link_ids = data ['links']
        current_link_ids = self.env['mk.link'].search([('episode_id', '=', episode_id),
                                                       ('state', '=', 'accept')]).ids
        deleted_links = []
        new_links = []
        update = False
        set_app_link_ids = set(app_link_ids)
        set_current_link_ids = set(current_link_ids)

        if set_app_link_ids != set_current_link_ids:
            update = True
            items = set_app_link_ids.intersection(set_current_link_ids)
            deleted_links = list(set_app_link_ids - items)
            new_link_ids = list(set_current_link_ids - items)

            for link in self.env['mk.link'].browse(new_link_ids):
                student = link.student_id
                age = 0
                # dob = link.student_id.birthdate
                # if dob:
                #     d1 = datetime.strptime(dob, "%Y-%m-%d").date()
                #     d2 = date.today()
                #     age = relativedelta(d2, d1).years
                # test_session = self.env['student.test.session'].sudo().search([('student_id', '=', link_id),
                #                                                                ('state', '!=', 'cancel')],limit=1)
                new_links.append({'id':                    link.id,
                                  'student_id':            student.id,
                                  'plan_id':               link.preparation_id.id,
                                  'general_behavior_type': False,
                                  'name':                  student.display_name,
                                  'rate':          0,
                                  'age':           age,
                                  'test_register': False,
                                  'session_id':    False,

                                  'type_exam_id':  False,
                                  'track':         False,
                                  'branch_id':     False,
                                  'period_id':     False,
                                  'state':         'تحضير الطالب'})
                sorted(new_links, key=lambda k: k['age'])
        result = {'update':        update,
                  'deleted_links': deleted_links,
                  'new_links':     new_links}
        _logger.info('\n\n\n ____________  teacher_offline_check_students END')
        return result

    @api.model
    def teacher_offline_add_listen_line(self, data):
        _logger.info('\n\n\n ____________  teacher_offline_add_listen_line : %s', data)
        all_listen_lines = []
        link_objs = {}
        aya_objs = {}
        for item in data:
            link_id = int(item['link_id'])
            type_follow = item['type_follow']
            from_surah_id = int(item['from_surah'])
            from_aya_order = int(item['from_aya'])
            to_surah_id = int(item['to_surah'])
            to_aya_order = int(item['to_aya'])
            listen_date = item['actual_date']
            listen_lines = {}

            student_link = link_objs.get(link_id, False)
            if not student_link:
                student_link = self.env['mk.link'].search([('id', '=', link_id)], limit=1)
                episode = student_link.episode_id
                if episode.state == 'done':
                    stdnt_link = self.env['mk.link'].search([('student_id', '=', student_link.student_id.id),
                                                               ('state', '=', 'accept'),
                                                               ('study_class_id.is_default', '=', True)], limit=1)
                    if stdnt_link:
                        student_link = stdnt_link

                link_objs.update({link_id: student_link})

            preparation = student_link.preparation_id

            from_aya = aya_objs.get((from_surah_id,from_aya_order), False)
            if not from_aya:
                from_aya = self.env['mk.surah.verses'].search([('surah_id', '=', from_surah_id),
                                                               ('original_surah_order', '=', from_aya_order)], limit=1)
                aya_objs.update({(from_surah_id,from_aya_order): from_aya})

            to_aya = aya_objs.get((to_surah_id,to_aya_order), False)
            if not to_aya:
                to_aya = self.env['mk.surah.verses'].search([('surah_id', '=', to_surah_id),
                                                             ('original_surah_order', '=', to_aya_order)], limit=1)
                aya_objs.update({(to_surah_id,to_aya_order): to_aya})
            preparation_id = preparation.id
            student_id = student_link.student_id.id
            mosq_id = student_link.mosq_id.id
            episode_id = student_link.episode_id.id
            academic_id = student_link.academic_id.id
            study_class_id = student_link.study_class_id.id
            center_department_id = student_link.mosq_id.center_department_id.id

            vals = {'preparation_id':      preparation_id,
                    'type_follow':         type_follow,
                    'student_id':          student_link.id,
                    'student_register_id': student_id,
                    'mosque_id':           mosq_id,
                    'center_department_id':center_department_id,
                    'episode':             episode_id,
                    'approache_id':        student_link.approache.id,
                    'study_year_id':       academic_id,
                    'study_class_id':      study_class_id,
                    'actual_date':         listen_date,
                    'from_surah':          from_surah_id,
                    'from_aya':            from_aya.id,
                    'to_surah':            to_surah_id,
                    'to_aya':              to_aya.id,
                    'is_from_mobile':      True,
                    'total_mstk_qty':      int(item['total_mstk_qty']),
                    'total_mstk_read':     int(item['total_mstk_read']),
                    'state': 'done'}

            listen_line = self.env['mk.listen.line'].create(vals)

            listen_lines.update({'line_id': listen_line.id})
            existing_presence = self.env['mk.student.prepare.presence'].search([('preparation_id', '=', preparation_id),
                                                                                ('presence_date', '=', listen_date)], limit=1)
            if not existing_presence:
                self.env['mk.student.prepare.presence'].create({'preparation_id':      preparation_id,
                                                                'presence_date':       listen_date,
                                                                'status':             'present',
                                                                'link_id':             student_link.id,
                                                                'episode_id':          episode_id,
                                                                'mosque_id':           mosq_id,
                                                                'center_department_id':center_department_id,
                                                                'student_register_id': student_id,
                                                                'study_year_id':       academic_id,
                                                                'study_class_id':      study_class_id,
                                                                'is_from_mobile' :     True})
            # new_start_point = self.check_line_state(listen_line)
            # if new_start_point:
            listen_lines.update({'new_start_point': {'degree':        listen_line.degree,
                                                    'from_aya':       to_aya_order,
                                                    'from_sura_name': to_aya.surah_id.name,
                                                    'mistake':        listen_line.mistake,
                                                    'prep_id':        listen_line.preparation_id.id,
                                                    'to_aya':         None,
                                                    'to_sura_name':   None}})

            all_listen_lines.append(listen_lines)
        _logger.info('\n\n\n ____________ teacher_offline_add_listen_line END')
        return str(all_listen_lines)

    @api.model
    def teacher_offline_set_attendance(self, data):
        _logger.info('\n\n\n ____________ teacher_offline_set_attendance : %s', data)
        prep_objs = {}
        for item in data:
            preparation_id = int(item['plan_id'])
            state = item['state']
            date = item['date']
            preparation = prep_objs.get(preparation_id, False)
            if not preparation:
                preparation = self.env['mk.student.prepare'].search([('id', '=', preparation_id),
                                                                     ('stage_pre_id.state', '=', 'accept'),
                                                                    '|', ('active', '=', True),
                                                                         ('active', '=', False)], limit=1)

                if not preparation:
                    prepare = self.env['mk.student.prepare'].search([('link_id.student_id', '=', preparation.student_register_id.id),
                                                                     ('link_id.state', '=', 'accept'),
                                                                     ('study_class_id.is_default', '=', True),
                                                                     '|', ('active', '=', True),
                                                                          ('active', '=', False)], limit=1)
                    preparation = prepare
                if not preparation:
                    continue
                prep_objs.update({preparation_id: preparation})

            existing_presence = self.env['mk.student.prepare.presence'].search([('preparation_id', '=', preparation.id),
                                                                                ('presence_date', '=', date)], limit=1)
            if existing_presence:
                existing_presence.write({'status': state})
            else:
                link = preparation.link_id
                presence = self.env['mk.student.prepare.presence'].sudo().create({'preparation_id': preparation.id,
                                                                                  'presence_date':  date,
                                                                                  'status':         state,
                                                                                  'link_id':        link.id,
                                                                                  'episode_id':     link.episode_id.id,
                                                                                  'mosque_id':      link.mosq_id.id,
                                                                                  'center_department_id':link.mosq_id.center_department_id.id,
                                                                                  'student_register_id': link.student_id.id,
                                                                                  'study_year_id':       link.academic_id.id,
                                                                                  'study_class_id':      link.study_class_id.id,
                                                                                  'is_from_mobile':      True})
        _logger.info('\n\n\n ____________ teacher_offline_set_attendance END')
        return True
    #endregion

    #region online api
    @api.model
    def attendance_students(self, plan_id, state):
        preparation_id = int(plan_id)
        preparation = self.env['mk.student.prepare'].sudo().search([('id', '=', preparation_id)], limit=1)

        episode = preparation.stage_pre_id
        if episode.state == 'done':
            prepare = self.env['mk.student.prepare'].search([('link_id.student_id', '=', preparation.student_register_id.id),
                                                                 ('link_id.state', '=', 'accept'),
                                                                 ('study_class_id.is_default', '=', True)], limit=1)
            if prepare:
                preparation = prepare

        actual_date = datetime.strptime(fields.Date.today(), '%Y-%m-%d').date()
        existing_presence = self.env['mk.student.prepare.presence'].sudo().search([('preparation_id', '=', preparation.id),
                                                                                   ('presence_date', '=', actual_date)], limit=1)
        if existing_presence:
            existing_presence.write({'status': state})
        else:
            link = preparation.link_id
            presence = self.env['mk.student.prepare.presence'].sudo().create({'preparation_id':      preparation.id,
                                                                              'presence_date':       actual_date,
                                                                              'status':              state,
                                                                              'link_id':             link.id,
                                                                              'episode_id':          link.episode_id.id,
                                                                              'mosque_id':           link.mosq_id.id,
                                                                              'center_department_id':link.mosq_id.center_department_id.id,
                                                                              'student_register_id': link.student_id.id,
                                                                              'study_year_id':       link.academic_id.id,
                                                                              'study_class_id':      link.study_class_id.id,
                                                                              'is_from_mobile':       True})
        return True

    @api.model
    def teacher_add_listen_line(self, data):
        link_id = int(data['link_id'])
        type_follow = data['type_follow']
        from_surah_id = data['from_surah']
        from_aya_id = data['from_aya']
        to_surah_id = data['to_surah']
        to_aya_id = data['to_aya']
        listen_lines = {}
        actual_date = datetime.strptime(fields.Date.today(), '%Y-%m-%d').date()
        student_link = self.env['mk.link'].search([('id', '=', link_id)], limit=1)
        student_register = student_link.student_id
        episode = student_link.episode_id
        if episode.state == 'done':
            stdnt_link = self.env['mk.link'].search([('student_id', '=', student_register.id),
                                                       ('state', '=', 'accept'),
                                                       ('study_class_id.is_default', '=', True)], limit=1)
            if stdnt_link:
                student_link = stdnt_link
        preparation = student_link.preparation_id

        from_aya = self.env['mk.surah.verses'].search([('surah_id', '=', int(from_surah_id)),
                                                          ('original_surah_order', '=', int(from_aya_id))], limit=1)

        to_aya = self.env['mk.surah.verses'].search([('surah_id', '=', int(to_surah_id)),
                                                        ('original_surah_order', '=', int(to_aya_id))], limit=1)

        vals = {'preparation_id':      preparation.id,
                'type_follow':         type_follow,
                'student_id':          student_link.id,
                'student_register_id': student_link.student_id.id,
                'mosque_id':           student_link.mosq_id.id,
                'episode':             student_link.episode_id.id,
                'center_department_id':student_link.mosq_id.center_department_id.id,
                'approache_id':        student_link.approache.id,
                'study_year_id':       student_link.academic_id.id,
                'study_class_id':      student_link.study_class_id.id,
                'actual_date':         actual_date,
                'from_surah':          int(from_surah_id),
                'from_aya':            from_aya.id,
                'to_surah':            int(to_surah_id),
                'to_aya':              to_aya.id,
                'is_from_mobile':      True,
                'total_mstk_qty':      int(data['total_mstk_qty']),
                'total_mstk_read':     int(data['total_mstk_read']),
                'state':               'done'}

        line_id = self.env['mk.listen.line'].sudo().create(vals)

        if line_id:
            listen_lines.update({'line_id': line_id.id })
            existing_presence = self.env['mk.student.prepare.presence'].sudo().search([('preparation_id', '=', preparation.id),
                                                                                        ('presence_date', '=', actual_date)], limit=1)
            if existing_presence:
                existing_presence.write({'status': 'present'})
            else:
                self.env['mk.student.prepare.presence'].create({'preparation_id':      preparation.id,
                                                                'presence_date':       actual_date,
                                                                'status':              'present',
                                                                'link_id':             student_link.id,
                                                                'episode_id':          student_link.episode_id.id,
                                                                'mosque_id':           student_link.mosq_id.id,
                                                                'center_department_id':       student_link.mosq_id.center_department_id.id,
                                                                'student_register_id': student_link.student_id.id,
                                                                'study_year_id':       student_link.academic_id.id,
                                                                'study_class_id':      student_link.study_class_id.id,
                                                                'is_from_mobile':      True})

            new_start_point = self.check_line_state(line_id)
            if new_start_point:
                listen_lines.update({'new_start_point': new_start_point})
        return str(listen_lines)
    #endregion

    #region portal
    @api.model
    def student_plan_lines(self, link_id):
        plan = self.env['mk.student.prepare'].search([('link_id', '=', int(link_id))], limit=1)
        if not plan:
            return []

        plan_id = plan.id

        listen_plan_lines = self.env['mk.listen.line'].search([('preparation_id', '=', plan_id),
                                                               ('type_follow', '=', 'listen')])
        min_rev_plan_lines = self.env['mk.listen.line'].search([('preparation_id', '=', plan_id),
                                                                ('type_follow', '=', 'review_small')])
        max_rev_plan_lines = self.env['mk.listen.line'].search([('preparation_id', '=', plan_id),
                                                                ('type_follow', '=', 'review_big')])
        tlawa_plan_lines = self.env['mk.listen.line'].search([('preparation_id', '=', plan_id),
                                                              ('type_follow', '=', 'tlawa')])
        listen_records = []
        min_rev_records = []
        max_rev_records = []
        tlawa_records = []

        teacher_name = plan.name.name
        episode_name = plan.stage_pre_id.name
        period = plan.stage_pre_id.selected_period
        student_name = plan.link_id.student_id.display_name

        for listen_plan_line in listen_plan_lines:
            listen_records += [
                self.get_student_plan_lines(plan_id, teacher_name, episode_name, student_name, period, 'listen',
                                            listen_plan_line)]

        for min_rev_plan_line in min_rev_plan_lines:
            min_rev_records += [
                self.get_student_plan_lines(plan_id, teacher_name, episode_name, student_name, period, 'review_small',
                                            min_rev_plan_line)]

        for max_rev_plan_line in max_rev_plan_lines:
            max_rev_records += [
                self.get_student_plan_lines(plan_id, teacher_name, episode_name, student_name, period, 'review_big',
                                            max_rev_plan_line)]

        for tlawa_plan_line in tlawa_plan_lines:
            tlawa_records += [
                self.get_student_plan_lines(plan_id, teacher_name, episode_name, student_name, period, 'tlawa',
                                            tlawa_plan_line)]

        return [{'listen': listen_records},
                {'reviewsmall': min_rev_records},
                {'reviewbig': max_rev_records},
                {'tlawa': tlawa_records}]

    @api.model
    def student_attendances(self, link_id):
        plan = self.env['mk.student.prepare'].search([('link_id', '=', link_id)], limit=1)

        if not plan:
            return []

        plan_id = plan.id
        listen_plan_lines = self.env['mk.listen.line'].search([('preparation_id', '=', plan_id),
                                                               ('type_follow', '=', 'listen'),
                                                               ('state', '!=', 'draft')])

        teacher = plan.name
        teacher_id = teacher.id
        teacher_name = teacher.name

        episode = plan.link_id.episode_id
        episode_id = episode.id
        episode_name = episode.name

        period = plan.stage_pre_id.selected_period
        time = episode.test_time

        mosque = episode.mosque_id
        mosque_id = mosque.id
        mosque_name = mosque.name

        student = plan.link_id.student_id
        student_id = student.id
        student_name = student.display_name

        records = []
        record_dates = []
        record_indiscipline_same_date = []

        for listen_plan_line in listen_plan_lines:
            record_same_date = []
            if listen_plan_line.state != 'done':
                continue
            record_same_date = list(record for record in records if
                                    listen_plan_line.actual_date in record_dates and record['status'] == 'done')

            if record_same_date:
                continue
            else:
                records += [{'id': listen_plan_line.id,
                             'date': listen_plan_line.actual_date,
                             'status': 'done',
                             'period': period,
                             'att_time': time,

                             'student_id': student_id,
                             'student_name': student_name,

                             'episode_id': episode_id,
                             'episode_name': episode_name,

                             'mosque_id': mosque_id,
                             'mosque_name': mosque_name,

                             'teacher_id': teacher_id,
                             'teacher_name': teacher_name}]

            if listen_plan_line.actual_date not in record_dates:
                record_dates.append(listen_plan_line.actual_date)

            mistake_lines = listen_plan_line.mistake_line_ids
            if mistake_lines:
                for indiscipline in mistake_lines[0].indiscipline_ids:
                    type_indiscipline = indiscipline.type_indiscipline
                    if type_indiscipline not in ['absent', 'absent_excuse', 'excuse']:
                        continue

                    record_indiscipline_same_date = list(record for record in records if
                                                         indiscipline.date_indiscipline in record_dates and record[
                                                             'status'] == 'done')

                    if record_indiscipline_same_date:
                        continue

                    else:
                        records += [{'id': listen_plan_line.id,
                                     'date': indiscipline.date_indiscipline,
                                     'status': indiscipline.type_indiscipline,
                                     'period': period,
                                     'att_time': time,

                                     'student_id': student_id,
                                     'student_name': student_name,

                                     'episode_id': episode_id,
                                     'episode_name': episode_name,

                                     'mosque_id': mosque_id,
                                     'mosque_name': mosque_name,

                                     'teacher_id': teacher_id,
                                     'teacher_name': teacher_name}]

                record_indiscipline_same_date = []

        return sorted(records, key=lambda d: d['date'])

    @api.model
    def set_not_read(self, plan_id, type_plan_line):
        plan_line = self.env['mk.listen.line'].search([('id', '=', plan_id),
                                                       ('type_follow', '=', type_plan_line),
                                                       ('state', '!=', 'done')], limit=1, order="order")
        self.add_indiscipline(plan_line, 'not_read')
        return True

    @api.model
    def add_indiscipline(self, plan_line, type_indiscipline):
        eval_plan_line = self.env['mk.details.mistake'].search([('mistake_id', '=', plan_line.id),
                                                                ('total_mistake_id', '=', False)], limit=1)
        if eval_plan_line:
            eval_id = eval_plan_line.id

            indisciplines = False
            if type_indiscipline in ['absent', 'absent_excuse']:
                indisciplines = self.env['mk.student.plan.line.indiscipline'].search([('eval_id', '=', eval_id),
                                                                                      ('date_indiscipline', '=',
                                                                                       fields.Date.today())])

            else:
                indisciplines = self.env['mk.student.plan.line.indiscipline'].search([('eval_id', '=', eval_id),
                                                                                      ('date_indiscipline', '=',
                                                                                       fields.Date.today()),
                                                                                      ('type_indiscipline', 'in',
                                                                                       ['absent', 'absent_excuse',
                                                                                        type_indiscipline])])

            if indisciplines:
                indisciplines.unlink()

        else:
            eval_id = self.env['mk.details.mistake'].create({'mistake_id': plan_line.id}).id

        self.env['mk.student.plan.line.indiscipline'].create({'eval_id': eval_id,
                                                              'type_indiscipline': type_indiscipline})

    @api.model
    def add_total_mistake(self, plan_line_id, vals):
        vals_detail = {}

        if 'total_mstk_qty' in vals:
            nbr_mstk_qty = vals.get('total_mstk_qty')
            vals_detail = {'nbr_mstk_qty': nbr_mstk_qty}

        if 'total_mstk_qlty' in vals:
            number_mistake = vals.get('total_mstk_qlty')
            vals_detail.update({'number_mistake': number_mistake})

        if 'total_mstk_read' in vals:
            nbr_mstk_read = vals.get('total_mstk_read')
            vals_detail.update({'nbr_mstk_read': nbr_mstk_read})

        plan_line = self.env['mk.listen.line'].search([('id', '=', plan_line_id)], limit=1)

        approach_id = plan_line.preparation_id.link_id.approache

        line_type_follow = plan_line.type_follow

        if line_type_follow == 'review_small':
            deduct_qty_memorize = approach_id.deduct_qty_small_review
            deduct_memorize = approach_id.deduct_memor_sml_review
            deduct_tajweed = approach_id.deduct_tjwd_sml_review

        elif line_type_follow == 'review_big':
            deduct_qty_memorize = approach_id.deduct_qty_big_review
            deduct_memorize = approach_id.deduct_memor_big_review
            deduct_tajweed = approach_id.deduct_tjwd_big_review

        elif line_type_follow == 'tlawa':
            deduct_qty_memorize = approach_id.deduct_qty_reading
            deduct_memorize = approach_id.deduct_memor_reading
            deduct_tajweed = approach_id.deduct_tjwd_reading

        elif line_type_follow == 'listen':
            deduct_qty_memorize = approach_id.deduct_qty_memorize
            deduct_memorize = approach_id.deduct_memor_memorize
            deduct_tajweed = approach_id.deduct_tjwd_memorize
        deduct_delay = approach_id.late_deduct
        deduct_absence = approach_id.no_excused_absence_deduct

        eval_plan_line = self.env['mk.details.mistake'].search([('mistake_id', '=', plan_line_id),
                                                                ('total_mistake_id', '=', False)], limit=1)
        if not eval_plan_line:
            eval_plan_line = self.env['mk.details.mistake'].create({'mistake_id': plan_line_id,
                                                                           'deduct_qty_memorize': deduct_qty_memorize,
                                                                           'deduct_memorize': deduct_memorize,
                                                                           'deduct_tajweed': deduct_tajweed,
                                                                           'deduct_delay': deduct_delay,
                                                                           'deduct_absence': deduct_absence})

        eval_plan_line.write(vals_detail)

        return eval_plan_line.id

    @api.model
    def add_mistake(self, plan_line_id, aya_id, vals):
        vals_detail = {}
        if 'nbr_mstk_qty' in vals:
            nbr_mstk_qty = vals.get('nbr_mstk_qty')
            vals_detail = {'nbr_mstk_qty': nbr_mstk_qty}

        if 'nbr_mstk_qlty' in vals:
            nbr_mstk_qlty = vals.get('nbr_mstk_qlty')
            vals_detail.update({'number_mistake': nbr_mstk_qlty})

        if 'nbr_mstk_read' in vals:
            nbr_mstk_read = vals.get('nbr_mstk_read')
            vals_detail.update({'nbr_mstk_read': nbr_mstk_read})

        eval_plan_line = self.env['mk.details.mistake'].search([('mistake_id', '=', plan_line_id),
                                                                ('total_mistake_id', '=', False)], limit=1)
        if not eval_plan_line:
            eval_plan_line = self.env['mk.details.mistake'].create({'mistake_id': plan_line_id})

        mistake_detail = self.env['mk.details.mistake'].search([('mistake_id', '=', plan_line_id),
                                                                ('aya_id', '=', aya_id)], limit=1)

        aya = self.env['mk.surah.verses'].search([('id', '=', aya_id)], limit=1)

        if not mistake_detail:
            mistake_detail = self.env['mk.details.mistake'].create({'mistake_id': plan_line_id,
                                                                    'total_mistake_id': eval_plan_line.id,
                                                                    'aya_id': aya_id,
                                                                    'surah_id': aya.surah_id.id})

        if not mistake_detail.aya_id:
            vals_detail.update({'aya_id': aya_id,
                                'surah_id': aya.surah_id.id})

        mistake_detail.write(vals_detail)

        return mistake_detail.id

    @api.model
    def get_verses_plan_line(self, plan_line_id):
        try:
            plan_line_id = int(plan_line_id)
        except:
            pass

        dict_lst = []
        order_pages = []
        plan_line = self.env['mk.listen.line'].search([('id', '=', plan_line_id)], limit=1)

        if plan_line:
            aya_from = plan_line.from_aya.original_accumalative_order
            to_aya = plan_line.to_aya.original_accumalative_order

            dict_lst.append({'from_page': plan_line.from_aya.page_no,
                             'to_page': plan_line.to_aya.page_no})

            if aya_from > to_aya:
                surah_prev_id = False
                aya_id = aya_from

                while True:
                    aya_data = self.env['mk.surah.verses'].search([('original_accumalative_order', '=', aya_id)],
                                                                  limit=1)

                    surah = aya_data.surah_id
                    surah_id = surah.id
                    if surah_prev_id and (surah_prev_id != surah_id):
                        if aya_data:
                            surah_order = aya_data.surah_id.order - 2
                        else:
                            surah_order = 113

                        aya_data = self.env['mk.surah.verses'].search([('original_surah_order', '=', 1),
                                                                       ('surah_id.order', '=', surah_order)], limit=1)

                        surah = aya_data.surah_id
                        surah_id = surah.id
                        aya_id = aya_data.id

                    page_no = aya_data.page_no
                    if page_no not in order_pages:
                        order_pages += [page_no]

                    dict_lst.append({'page_num': aya_data.page_no,

                                     'surah': surah.name,
                                     'surah_id': surah_id,

                                     'aya': aya_data.verse,
                                     'aya_id': aya_data.id,
                                     'aya_order_surah': aya_data.original_surah_order,
                                     'aya_num': aya_data.original_accumalative_order, })

                    if aya_id == to_aya:
                        dict_lst.append({'order_pages': order_pages})
                        return dict_lst

                    aya_id += 1
                    surah_prev_id = surah_id

            for aya_id in list(range(aya_from, to_aya + 1)):
                aya_data = self.env['mk.surah.verses'].search([('original_accumalative_order', '=', aya_id)], limit=1)

                if not aya_data:
                    continue

                page_no = aya_data.page_no
                if page_no not in order_pages:
                    order_pages += [page_no]

                dict_lst.append({'page_num': aya_data.page_no,

                                 'surah': aya_data.surah_id.name,
                                 'surah_id': aya_data.surah_id.id,

                                 'aya': aya_data.verse,
                                 'aya_id': aya_data.id,
                                 'aya_order_surah': aya_data.original_surah_order,
                                 'aya_num': aya_data.original_accumalative_order, })

        dict_lst.append({'order_pages': order_pages})
        return dict_lst

    @api.model
    def add_listen_line(self, order, date_listen, program_type, subject_line_from, subject_line_to, type_follow,link_id, preparation_id, is_test):
        vals = {'order': order,
                'date': date_listen,
                'from_surah': subject_line_from.from_surah.id,
                'from_aya': subject_line_from.from_verse.id if program_type == 'open' else subject_line_from.from_aya.id,
                # using self.program_type in api.model
                'to_surah': subject_line_to.to_surah.id,
                'to_aya': subject_line_to.to_verse.id if program_type == 'open' else subject_line_to.to_aya.id,
                # using self.program_type in api.model
                'type_follow': type_follow,
                'student_id': link_id,
                'preparation_id': preparation_id,
                'is_test': is_test}
        res = self.create(vals)
        return res

    @api.model
    def done_plan_line(self, plan_line_id, date_done):

        plan_line = self.search([('id', '=', int(plan_line_id)),
                                 ('state', '!=', 'done')], limit=1)

        if not date_done:
            actual_date = datetime.strptime(fields.Date.today(), '%Y-%m-%d')
        else:
            actual_date = datetime.strptime(date_done, '%Y-%m-%d')

        if plan_line:
            exist_draft_line_before = self.search([('preparation_id', '=', plan_line.preparation_id.id),
                                                   ('type_follow', '=', plan_line.type_follow),
                                                   ('order', '<', plan_line.order),
                                                   ('state', '!=', 'done')])

            if exist_draft_line_before:
                raise osv.except_osv(_('Error'), _('Check your previous preprations.'))

            exist_draft_line_after = self.search([('preparation_id', '=', plan_line.preparation_id.id),
                                                  ('type_follow', '=', plan_line.type_follow),
                                                  ('order', '>', plan_line.order),
                                                  ('state', '!=', 'done')])
            if not exist_draft_line_after:
                type_follow = plan_line.type_follow
                line_link = plan_line.student_id
                link_id = line_link.id
                preparation_id = plan_line.preparation_id.id

                program_type = plan_line.student_id.program_type
                approach = line_link.approache

                order = plan_line and plan_line.order + 1

                start_memor = ((program_type == 'open') and line_link.save_start_point) or False
                subject_memor_id = start_memor and start_memor.subject_page_id.id or False

                start_date = line_link.registeration_date
                start_date = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=1)

                end_date = line_link.episode_id and line_link.episode_id.end_date or line_link.study_class_id.end_date
                end_date = datetime.strptime(end_date, "%Y-%m-%d")

                student_days = []
                for student_day in line_link.student_days:
                    order_day = student_day.order
                    if order_day == 0:
                        student_days += [6]
                    else:
                        student_days += [order_day - 1]

                nbr_days = 8  # (end_date - start_date).days + 1
                for d in range(nbr_days):
                    date_listen = start_date + timedelta(d)

                    if date_listen > end_date:
                        date_listen = end_date

                    if date_listen.weekday() not in student_days:
                        continue

                    if type_follow == 'review_small':
                        last_s_review = (subject_memor_id and self.env['mk.subject.page'].search(
                            [('subject_page_id', '=', subject_memor_id)], order="order desc", limit=1)) or False
                        last_s_review_order = last_s_review and last_s_review.order or False
                        memorize_line = self.search([('student_id', '=', plan_line.student_id.id),
                                                     ('type_follow', '=', 'listen'),
                                                     ('order', '=', order)], limit=1)

                        next_date = line_link.get_next_date(student_days, start_date, d, nbr_days)

                        s_rev_close_sbjs = ((program_type == 'close') and approach.small_reviews_ids) or []
                        nbr_s_rev_close = len(s_rev_close_sbjs)

                        if start_memor and next_date and order <= last_s_review_order:
                            nbr_s_review = ((program_type == 'open') and approach.lessons_minimum_audit) or False

                            listen_line_to_surah = memorize_line.to_surah
                            listen_line_to_aya = memorize_line.to_aya
                            end_memor = self.env['mk.subject.page'].search([('subject_page_id', '=', subject_memor_id),
                                                                            ('to_surah', '=', listen_line_to_surah.id),
                                                                            ('to_verse', '=', listen_line_to_aya.id)],
                                                                           limit=1)
                            start_s_review_order = end_memor.order - nbr_s_review + 1
                            start_first_s_review = start_memor
                            start_first_s_review_order = start_first_s_review and start_first_s_review.order or 0
                            start_s_review = start_first_s_review
                            if start_s_review_order > start_first_s_review_order:
                                start_s_review = self.env['mk.subject.page'].search(
                                    [('subject_page_id', '=', subject_memor_id),
                                     ('order', '=', start_s_review_order)],
                                    limit=1)

                            line = self.sudo().add_listen_line(order, next_date, program_type, start_s_review,
                                                               end_memor, 'review_small', link_id, preparation_id,
                                                               (start_s_review.is_test or end_memor.is_test))
                            break
                        elif nbr_s_rev_close:
                            index = order - 1
                            if index < nbr_s_rev_close:
                                s_rev_close = s_rev_close_sbjs[index]
                                self.sudo().add_listen_line(order, next_date, program_type, s_rev_close, s_rev_close,
                                                            'review_small', link_id, preparation_id, False)
                                break

                    if type_follow == 'listen':
                        last_memor = (subject_memor_id and self.env['mk.subject.page'].search(
                            [('subject_page_id', '=', subject_memor_id)], order="order desc", limit=1)) or False
                        last_memor_order = last_memor and last_memor.order or False
                        nbr_memor = approach.lessons_memorize

                        memor_close_sbjs = ((program_type == 'close') and approach.listen_ids) or []
                        nbr_memor_close = len(memor_close_sbjs)

                        if start_memor and order <= last_memor_order:
                            start_order = line_link.save_start_point.order + plan_line.order * nbr_memor
                            start_memor = self.env['mk.subject.page'].search(
                                [('subject_page_id', '=', subject_memor_id),
                                 ('order', '=', start_order)], limit=1)

                            end_order = min((start_order + nbr_memor - 1), last_memor_order)
                            end_memor = self.env['mk.subject.page'].search([('subject_page_id', '=', subject_memor_id),
                                                                            ('order', '=', end_order)], limit=1)

                            self.sudo().add_listen_line(order, date_listen, program_type, start_memor, end_memor,
                                                        'listen', link_id, preparation_id,
                                                        (start_memor.is_test or end_memor.is_test))
                            break
                        elif nbr_memor_close:
                            index = order - 1
                            if index < nbr_memor_close:
                                memor_close = memor_close_sbjs[index]
                                self.sudo().add_listen_line(order, date_listen, program_type, memor_close, memor_close,
                                                            'listen', link_id, preparation_id, False)
                                break

                    if type_follow == 'review_big':
                        start_review = ((program_type == 'open') and line_link.start_point) or False
                        subject_review_id = start_review and start_review.subject_page_id.id or False
                        last_review = (subject_review_id and self.env['mk.subject.page'].search(
                            [('subject_page_id', '=', subject_review_id)], order="order desc", limit=1)) or False
                        last_review_order = last_review and last_review.order or False
                        nbr_review = ((program_type == 'open') and approach.lessons_maximum_audit) or False

                        b_rev_close_sbjs = ((program_type == 'close') and approach.big_review_ids) or []
                        nbr_b_rev_close = len(b_rev_close_sbjs)
                        start_order = line_link.start_point.order + plan_line.order * nbr_review

                        if start_review and start_order <= last_review_order:
                            end_order = start_order + nbr_review - 1
                            start_review = self.env['mk.subject.page'].search(
                                [('subject_page_id', '=', subject_review_id),
                                 ('order', '=', start_order)], limit=1)

                            end_review = self.env['mk.subject.page'].search(
                                [('subject_page_id', '=', subject_review_id),
                                 ('order', '=', end_order)], limit=1)

                            self.sudo().add_listen_line(order, date_listen, program_type, start_review, end_review,
                                                        'review_big', link_id, preparation_id,
                                                        (start_review.is_test or end_review.is_test))
                            break
                        elif nbr_b_rev_close:
                            index = order - 1
                            if index < nbr_b_rev_close:
                                b_rev_close = b_rev_close_sbjs[index]
                                self.sudo().add_listen_line(order, date_listen, program_type, b_rev_close, b_rev_close,
                                                            'review_big', link_id, preparation_id, False)
                                break

                    if type_follow == 'tlawa':
                        start_read = ((program_type == 'open') and line_link.read_start_point) or False

                        subject_read_id = start_read and start_read.subject_page_id.id or False
                        last_read = (subject_read_id and self.env['mk.subject.page'].search(
                            [('subject_page_id', '=', subject_read_id)], order="order desc", limit=1)) or False
                        last_read_order = last_read and last_read.order or False
                        nbr_read = ((program_type == 'open') and approach.lessons_reading) or False

                        tlawa_close_sbjs = ((program_type == 'close') and approach.tlawa_ids) or []
                        nbr_tlawa_close = len(tlawa_close_sbjs)
                        start_order = line_link.read_start_point.order + plan_line.order * nbr_read

                        if start_read and start_order <= last_read_order:
                            end_order = start_order + nbr_read - 1

                            start_read = self.env['mk.subject.page'].search([('subject_page_id', '=', subject_read_id),
                                                                             ('order', '=', start_order)], limit=1)

                            end_read = self.env['mk.subject.page'].search([('subject_page_id', '=', subject_read_id),
                                                                           ('order', '=', end_order)], limit=1)

                            self.sudo().add_listen_line(order, date_listen, program_type, start_read, end_read, 'tlawa',
                                                        link_id, preparation_id,
                                                        (start_read.is_test or end_read.is_test))
                            break
                        elif nbr_tlawa_close:
                            index = order - 1
                            if index < nbr_tlawa_close:
                                tlawa_close = tlawa_close_sbjs[index]
                                self.sudo().add_listen_line(order, date_listen, program_type, tlawa_close, tlawa_close,
                                                            'tlawa', link_id, preparation_id, False)
                                break

            vals = {'state': 'done',
                    'actual_date': actual_date}

            if plan_line.state == 'absent':
                vals.update({'check': False})

            plan_line.sudo().write(vals)
            if plan_line.mistake_line_ids:
                indiscipline_ids = plan_line.mistake_line_ids[0].indiscipline_ids

                if indiscipline_ids:
                    for indiscipline in indiscipline_ids:
                        if indiscipline.type_indiscipline != 'delay':
                            indiscipline.unlink()

            return plan_line_id

        return 0

    @api.model
    def get_student_plan_lines(self, plan_id, teacher_name, episode_name, student_name, period, type_follow, plan_line):

        mistake_lines = []

        for mistake_line in plan_line.mistake_line_ids:
            aya = mistake_line.aya_id
            if not aya:
                continue

            mistake_lines += [{'nbr_mstk_qty': mistake_line.nbr_mstk_qty,
                               'number_mistake': mistake_line.number_mistake,
                               'nbr_mstk_qlty': mistake_line.number_mistake,
                               'nbr_mstk_read': mistake_line.nbr_mstk_read,
                               'nbr_abscent': mistake_line.nbr_abscent,

                               'surah_id': mistake_line.surah_id.id,
                               'surah_id_name': mistake_line.surah_id.name,

                               'aya_id': aya.id,
                               'aya_name': aya.original_surah_order}]

        return {'mistakes': mistake_lines,
                'mistake_dict': mistake_lines,

                'actual_day': '',
                'plan_line': plan_line.id,
                'actual_date': plan_line.actual_date,

                'is_test': plan_line.is_test,
                'date': plan_line.date,

                'prep_id': plan_id,
                'episode_name': episode_name,
                'teacher_name': teacher_name,
                'student_name': student_name,
                'type_follow': type_follow,

                'from_sura_name': plan_line.from_surah.name,
                'from_aya': plan_line.from_aya.original_surah_order,

                'to_sura_name': plan_line.to_surah.name,
                'to_aya': plan_line.to_aya.original_surah_order,

                'check': plan_line.check,
                'delay': plan_line.delay,
                'permission_id': plan_line.permission_id.id,
                'state': plan_line.state,

                'mistake': plan_line.mistake,
                # 'mistake':        len(mistake_lines),
                'period': period}

    @api.model
    def update_listen_line_mistakes_page(self, name_mistake_id, number_mistake, line_id, aya_id):
        try:
            name_mistake_id = int(name_mistake_id)
            number_mistake = int(number_mistake)
            line_id = int(line_id)
            aya_id = int(aya_id)
        except:
            pass

        query_string = ''' 
                        UPDATE mk_details_mistake md
        		        SET name_mistake_id={}, number_mistake={}
        		        from  mk_listen_line list
        		        where 
          		        md.mistake_id = list.id and list.id = {} and aya_id ={}
        		        RETURNING name_mistake_id,number_mistake; '''.format(name_mistake_id, number_mistake, line_id,
                                                                             aya_id)
        self.env.cr.execute(query_string)
        item_list = self.env.cr.dictfetchall()
        return item_list

    @api.model
    def update_subjects_lines(self, line_id):
        try:
            line_id = int(line_id)
        except:
            pass

        line = self.browse(line_id)
        updated = line.write({'state': 'done'})

        if updated:
            return 0
        else:
            return 1

    @api.model
    def qualty_rate(self, emp_id, ep_id, follow):
        try:
            emp_id = int(emp_id)
            ep_id = int(ep_id)
            follow = str(follow)
        except:
            pass

        if emp_id > 0 and int(ep_id) > 0:
            query_string = ''' 
                       select sum(l.total*a.listen_total) as total_degree,sum((l.total*a.listen_total) - m.total_mistak) as degree
                       FROM v_total_student_lines l
                         inner join  
                         v_total_student_aproaches a 
                         on l.student_id = a.student_id 
                         left outer join 
                         v_total_student_mistaks m 
                         on l.student_id = m.student_id 
                       and l.type_follow = m.type_follow
                       WHERE 
                         l.type_follow='{}' AND l.teacher_id='{}' and l.episode_id ='{}';
                       '''.format(follow, emp_id, ep_id)
        else:
            query_string = ''' 
                       SELECT 
                       sum(l.total*a.listen_total) as total_degree,sum((l.total*a.listen_total) - m.total_mistak) as degree
                       FROM v_total_student_lines l
                         inner join  
                         v_total_student_aproaches a 
                         on l.student_id = a.student_id 
                         left outer join 
                         v_total_student_mistaks m 
                         on l.student_id = m.student_id 
                       and l.type_follow = m.type_follow
                       WHERE 
                          l.type_follow='{}' AND l.teacher_id='{}';
                       '''.format(follow, emp_id)
        if query_string:
            self.env.cr.execute(query_string)
            item_list = self.env.cr.dictfetchall()
        return item_list

    @api.model
    def qualty_done(self, emp_id, ep_id, follow):
        try:
            emp_id = int(emp_id)
            ep_id = int(ep_id)
            follow = str(follow)
        except:
            pass

        if emp_id > 0 and int(ep_id) > 0:
            query_string = ''' 
                           select sum(l.total*a.listen_total) as total_degree,sum((l.total*a.listen_total) - m.total_mistak) as degree
                           FROM v_total_student_lines l
                             inner join  
                             v_total_student_aproaches a 
                             on l.student_id = a.student_id 
                             left outer join 
                             v_total_student_mistaks m 
                             on l.student_id = m.student_id 
                           and l.type_follow = m.type_follow
                           WHERE 
                             l.type_follow='{}' AND l.teacher_id='{}' and l.episode_id ='{}';
                           '''.format(follow, emp_id, ep_id)
        else:
            query_string = ''' 
                           SELECT 
                           sum(l.total*a.listen_total) as total_degree,sum((l.total*a.listen_total) - m.total_mistak) as degree
                           FROM v_total_student_lines l
                             inner join  
                             v_total_student_aproaches a 
                             on l.student_id = a.student_id 
                             left outer join 
                             v_total_student_mistaks m 
                             on l.student_id = m.student_id 
                           and l.type_follow = m.type_follow
                           WHERE 
                              l.type_follow='{}' AND l.teacher_id='{}';
                           '''.format(follow, emp_id)
        if query_string:
            self.env.cr.execute(query_string)
            item_list = self.env.cr.dictfetchall()
        return item_list

    @api.model
    def get_mistake_aya_page(self, line_id, aya_id):
        try:
            line_id = int(line_id)
            aya_id = int(aya_id)
        except:
            pass

        result = []
        mistake_details = self.env['mk.details.mistake'].search([('mistake_id', '=', line_id),
                                                                 ('aya_id', '=', aya_id)])
        if mistake_details:
            for md in mistake_details:
                result.append({'name_mistake_id': md.name_mistake_id,
                               'number_mistake': md.number_mistake,
                               'aya_id': md.aya_id})
        return result

    @api.model
    def injazz_rate(self, employee_id, episode_id, student_id):
        try:
            employee_id = int(employee_id)
            episode_id = int(episode_id)
            student_id = int(student_id)
        except:
            pass

        query0 = '''SELECT count(*) nbr_lines
                          FROM mk_listen_line 
                          LEFT JOIN mk_student_prepare ON mk_listen_line.preparation_id = mk_student_prepare.id
                          LEFT JOIN mk_episode ON mk_student_prepare.stage_pre_id=mk_episode.id
                          LEFT JOIN hr_employee ON mk_episode.teacher_id=hr_employee.id
                          LEFT JOIN mk_link ON mk_student_prepare.link_id=mk_link.id '''

        if episode_id > 0 and employee_id > 0 and student_id > 0:
            sub_query2 = " AND hr_employee.id={} AND mk_link.student_id={} ".format(employee_id, student_id)

        elif episode_id > 0 and employee_id > 0:
            sub_query2 = " AND hr_employee.id={} AND mk_episode.id={} ".format(employee_id, episode_id)

        elif student_id > 0 and employee_id > 0:
            sub_query2 = " AND hr_employee.id={} AND mk_link.student_id={} ".format(employee_id, student_id)

        elif employee_id > 0:
            sub_query2 = " AND hr_employee.id={}".format(employee_id)
            sub_query2 += " AND mk_episode.state = 'accept' "

        elif student_id > 0 and episode_id > 0:
            sub_query2 = " AND mk_link.student_id={} AND mk_episode.id={} ".format(student_id, episode_id)

        elif student_id > 0:
            sub_query2 = " AND mk_link.student_id={}".format(student_id)

        else:
            sub_query2 = " "

        query_listen = query0 + "WHERE mk_listen_line.type_follow = 'listen' AND mk_student_prepare.check_memory = true "
        query_listen_done = query_listen + " AND mk_listen_line.state = 'done' "
        query_absent = query0 + ''' LEFT JOIN mk_details_mistake ON mk_details_mistake.mistake_id=mk_listen_line.id
                                              LEFT JOIN mk_student_plan_line_indiscipline ON mk_student_plan_line_indiscipline.eval_id=mk_details_mistake.id
                                              WHERE type_indiscipline in ('absent','absent_excuse') AND   
                                                    mk_listen_line.type_follow = 'listen' AND
                                                    mk_student_prepare.check_memory = true AND 
                                                    mk_listen_line.state = 'done' '''

        query_listen += sub_query2
        query_listen_done += sub_query2
        query_absent += sub_query2

        query_review_small = query0 + "WHERE mk_listen_line.type_follow = 'review_small' AND mk_student_prepare.check_minimum = true"
        query_review_small_done = query_review_small + " AND mk_listen_line.state = 'done' "

        query_review_small += sub_query2
        query_review_small_done += sub_query2

        query_review_big = query0 + "WHERE mk_listen_line.type_follow = 'review_big' AND mk_student_prepare.check_max = true"
        query_review_big_done = query_review_big + " AND mk_listen_line.state = 'done' "

        query_review_big += sub_query2
        query_review_big_done += sub_query2

        query = '''SELECT query_listen.nbr_lines nbr_lines_listen, 
                                  query_listen_done.nbr_lines nbr_lines_listen_done, 
                                  query_absent.nbr_lines nbr_lines_absent,
                                  query_review_small.nbr_lines nbr_lines_review_small, 
                                  query_review_small_done.nbr_lines nbr_lines_review_small_done,
                                  query_review_big.nbr_lines nbr_lines_review_big, 
                                  query_review_big_done.nbr_lines nbr_lines_review_big_done

                          FROM (''' + query_listen + ''') query_listen, (''' + \
                query_listen_done + ''') query_listen_done, (''' + \
                query_absent + ''') query_absent, (''' + \
                query_review_small + ''') query_review_small, (''' + \
                query_review_small_done + ''') query_review_small_done, (''' + \
                query_review_big + ''') query_review_big, (''' + \
                query_review_big_done + ''') query_review_big_done '''

        self.env.cr.execute(query)
        res_query = self.env.cr.dictfetchall()

        nbr_lines_listen = res_query[0].get('nbr_lines_listen') or 0
        nbr_lines_listen_done = res_query[0].get('nbr_lines_listen_done') or 0

        nbr_lines_absent = res_query[0].get('nbr_lines_absent') or 0
        nbr_present_require = nbr_lines_absent + nbr_lines_listen_done

        nbr_lines_review_small = res_query[0].get('nbr_lines_review_small') or 0
        nbr_lines_review_small_done = res_query[0].get('nbr_lines_review_small_done') or 0

        nbr_lines_review_big = res_query[0].get('nbr_lines_review_big') or 0
        nbr_lines_review_big_done = res_query[0].get('nbr_lines_review_big_done') or 0

        injazz_listen = 0
        if nbr_lines_listen:
            injazz_listen = round(float(nbr_lines_listen_done) / float(nbr_lines_listen), 2)

        presence = 0
        if nbr_present_require:
            presence = round(float(nbr_lines_listen_done) / float(nbr_present_require), 2)

        injazz_review_small = 0
        if nbr_lines_review_small:
            injazz_review_small = round(float(nbr_lines_review_small_done) / float(nbr_lines_review_small), 2)

        injazz_review_big = 0
        if nbr_lines_review_big:
            injazz_review_big = round(float(nbr_lines_review_big_done) / float(nbr_lines_review_big), 2)

        injaaz_rate = {'injazz_listen': int(injazz_listen * 100),
                       'injazz_review_small': int(injazz_review_small * 100),
                       'injazz_review_big': int(injazz_review_big * 100),
                       'injazz_presence': int(presence * 100),

                       'nbr_lines_listen': nbr_lines_listen,
                       'nbr_lines_listen_done': nbr_lines_listen_done,

                       'nbr_lines_absent': nbr_lines_absent,
                       'nbr_present_require': nbr_present_require,

                       'nbr_lines_review_small': nbr_lines_review_small,
                       'nbr_lines_review_small_done': nbr_lines_review_small_done,

                       'nbr_lines_review_big': nbr_lines_review_big,
                       'nbr_lines_review_big_done': nbr_lines_review_big_done}

        return injaaz_rate

    @api.model
    def count_ep_students(self, episode_id, teacher_id):
        try:
            episode_id = int(episode_id)
            teacher_id = int(teacher_id)
        except:
            pass

        query_string = ''' 
                       SELECT count(mk_link.student_id)
                       FROM 
                       public.mk_episode, 
                       public.mk_link,
                       public.mk_student_register,
                       mk_listen_line
                       WHERE 
                       mk_link.episode_id = mk_episode.id and 
                       mk_episode.id ={} and 
                       mk_episode.teacher_id ={} and 
                       mk_student_register.id = mk_link.student_id and 
                       mk_student_register.id=mk_listen_line.id;

                   '''.format(episode_id, teacher_id)
        self.env.cr.execute(query_string)
        item_list = self.env.cr.dictfetchall()
        return item_list

    @api.model
    def ep_students(self, episode_id, teacher_id):
        try:
            episode_id = int(episode_id)
            teacher_id = int(teacher_id)
        except:
            pass

        query_string = ''' 
                       SELECT mk_link.student_id As id,
                       public.mk_student_register.display_name As name,
                       0 as age,
                       0 as rate,
                       mk_listen_line.state,
                       (SELECT CASE WHEN mk_listen_line.delay = TRUE THEN 1 ELSE 0 END ) AS is_dely,
                       (SELECT CASE WHEN mk_listen_line.state = 'absent' THEN 1 ELSE 0 END ) AS is_absent 
                       FROM 
                       public.mk_episode, 
                       public.mk_link,
                       public.mk_student_register,
                       mk_listen_line
                       WHERE 
                       mk_link.episode_id = mk_episode.id and 
                       mk_episode.id ={} and 
                       mk_episode.teacher_id ={}
                       and mk_student_register.id = mk_link.student_id and 
                       mk_student_register.id=mk_listen_line.id
                       ORDER BY mk_student_register.display_name;
                   '''.format(episode_id, teacher_id)
        self.env.cr.execute(query_string)
        item_list = self.env.cr.dictfetchall()
        return item_list
    #endregion

    #region backend
    # @api.multi
    def get_action_mistake_view_form(self):
        total_mistake = self.env['mk.details.mistake'].search([('mistake_id', '=', self.id),
                                                               ('total_mistake_id', '=', False)], limit=1)
        total_mistake_id = total_mistake and total_mistake.id or False
        view_id = self.env.ref('mk_student_managment.mk_mistake_form').id
        return {'type': 'ir.actions.act_window',
                'name': 'عرض إجمالي للأخطاء',
                'res_model': 'mk.details.mistake',
                'target': 'new',

                'view_type': 'form',
                'view_mode': 'form',

                'res_id': total_mistake_id,
                'view_id': view_id, }

    @api.depends('total_mstk_qty', 'total_mstk_read', 'approache_id',
                 'approache_id.deduct_qty_memorize', 'approache_id.deduct_tjwd_memorize',
                 'approache_id.deduct_qty_small_review', 'approache_id.deduct_tjwd_sml_review',
                 'approache_id.deduct_qty_big_review', 'approache_id.deduct_tjwd_big_review',
                 'approache_id.deduct_qty_reading', 'approache_id.deduct_tjwd_reading')
    def amount_mistake(self):
        for rec in self:
            total = 0
            dgree = 0
            total_mstk_qty = rec.total_mstk_qty
            total_mstk_read = rec.total_mstk_read
            approach = rec.approache_id
            type_follow = rec.type_follow
            if type_follow == 'listen':
                if total_mstk_qty:
                    dgree += total_mstk_qty * approach.deduct_qty_memorize
                if total_mstk_read:
                    dgree += total_mstk_read * approach.deduct_tjwd_memorize
            elif type_follow == 'review_small':
                if total_mstk_qty:
                    dgree += total_mstk_qty * approach.deduct_qty_small_review
                if total_mstk_read:
                    dgree += total_mstk_read * approach.deduct_tjwd_sml_review
            elif type_follow == 'review_big':
                if total_mstk_qty:
                    dgree += total_mstk_qty * approach.deduct_qty_big_review
                if total_mstk_read:
                    dgree += total_mstk_read * approach.deduct_tjwd_big_review
            elif type_follow == 'tlawa':
                if total_mstk_qty:
                    dgree += total_mstk_qty * approach.deduct_qty_reading
                if total_mstk_read:
                    dgree += total_mstk_read * approach.deduct_tjwd_reading

            rec.mistake = total
            rec.degree = 100 - dgree

    # @api.multi
    @api.depends('to_surah', 'from_surah', 'to_aya', 'from_aya')
    def get_nbr_lines(self):
        for rec in self:
            from_surah = rec.from_surah
            from_surah_order = from_surah.order

            to_surah = rec.to_surah
            to_surah_order = to_surah.order

            start_line_from_aya = rec.from_aya.line_start
            end_line_to_aya = rec.to_aya.line_end

            nb_lines = 0
            if from_surah_order <= to_surah_order :
                nb_lines = end_line_to_aya - start_line_from_aya + 1
            else:
                order_to = max(to_surah_order, from_surah_order)
                order_from = min(to_surah_order, from_surah_order)

                surahs = self.env['mk.surah'].search([('order', '<=', order_to),
                                                      ('order', '>=', order_from)], order="order")

                from_surah_id = rec.from_surah.id
                to_surah_id = rec.to_surah.id
                for surah in surahs:
                    surah_id = surah.id
                    if surah_id == from_surah_id:
                        aya_end_first_surah = self.env['mk.surah.verses'].search([('surah_id', '=', surah_id)],order="original_surah_order desc",limit=1)
                        nb_lines += aya_end_first_surah.line_end - start_line_from_aya + 1
                    elif surah_id == to_surah_id:
                        aya_start_last_surah = self.env['mk.surah.verses'].search([('surah_id', '=', surah_id)],order="original_surah_order asc",limit=1)
                        nb_lines += end_line_to_aya - aya_start_last_surah.line_start + 1
                    else:
                        nb_lines += surah.nbr_lines

            rec.nbr_lines = nb_lines
            rec.nbr_pages = nb_lines / 15
    #endregion


class StudentPresence(models.Model):
    _name = 'mk.student.prepare.presence'
    _order = 'presence_date desc ,id desc'

    preparation_id = fields.Many2one('mk.student.prepare', ondelete='cascade')
    presence_date  = fields.Date('التاريخ ', required=True, default=fields.Date.today())
    status         = fields.Selection([('present', 'حاضر'),
                                       ('absent', 'غائب'),
                                       ('absent_excuse', 'غائب بعذر'),
                                       ('delay', 'متأخر'),
                                       ('not_read', 'لم يسمع'),
                                       ('excuse', 'استأذن'), ], string='الحالة', track_visibility='onchange')
    link_id             = fields.Many2one('mk.link', ondelete='cascade')
    student_register_id = fields.Many2one("mk.student.register", string='الطالب')
    episode_id          = fields.Many2one("mk.episode",     string='الحلقة', index=True)
    mosque_id           = fields.Many2one("mk.mosque",      string='المسجد')
    center_department_id= fields.Many2one('hr.department',  string='المركز')
    study_year_id       = fields.Many2one("mk.study.year",  string='العام الدراسي')
    study_class_id      = fields.Many2one("mk.study.class", string='الفصل الدراسي')
    is_from_mobile       = fields.Boolean()

    def name_get(self):
        result = []
        for record in self:
            status = dict(record._fields['status'].selection).get(record.status)
            student = record.student_register_id.name or ''
            episode = record.episode_id.name or ''
            name = str(student) + " / " + str(episode) + "(" + status + ")"
            result.append((record.id, name))
        return result

    @api.constrains('presence_date')
    def check_presence_date(self):
        for record in self:
            if record.presence_date and record.presence_date > fields.Date.today():
                raise ValidationError(_('الرجاء التحقق من التاريخ المحدد! لا يمكن أن يكون أكبر من تاريخ اليوم'))


    @api.onchange('student_register_id')
    def onchange_student(self):
        student_register_id = self.student_register_id
        link_ids = student_register_id.link_ids.filtered(lambda l: l.state == 'accept')
        episodes = [link.episode_id.id for link in link_ids]
        return {'domain': {'episode_id': [('id', 'in', episodes)]}}

    @api.onchange('episode_id')
    def onchange_episode(self):
        if not self.env.context.get('default_student_register_id'):
            episode = self.episode_id
            link_ids = episode.link_ids.filtered(lambda l: l.state == 'accept')
            students = [link.student_id.id for link in link_ids]
            return {'domain': {'student_register_id': [('id', 'in', students)]},
                    'value':   { 'student_register_id': False}}

    @api.model
    def create(self, vals):
        if not vals.get('link_id'):
            if self.env.context.get('default_student_register_id'):

                student_link = self.env['mk.link'].search([('episode_id', '=', vals.get('episode_id')),
                                                       ('student_id', '=', self.env.context.get('active_id'))], limit=1)
            if self.env.context.get('default_episode_id'):

                student_link = self.env['mk.link'].search([('episode_id', '=', self.env.context.get('active_id')),
                                                                   ('student_id', '=', vals.get('student_register_id'))], limit=1)

            vals['preparation_id']          = student_link.preparation_id.id
            vals['link_id']                 = student_link.id
            vals['mosque_id']               = student_link.mosq_id.id
            vals['center_department_id']    = student_link.mosq_id.center_department_id.id
            vals['study_year_id']           =  student_link.academic_id.id
            vals['study_class_id']          = student_link.study_class_id.id
        return super(StudentPresence, self).create(vals)



#region class student behavior
class Behavior(models.Model):
    _name = 'mk.student.behaviors'
    _inherit = ['mail.thread']
    _description = 'Maknoon student Behavior'

    name = fields.Char('Behavior name', required=True, track_visibility='onchange', size=30)
    Dedect_grade = fields.Integer('Deduction grade', required=True, track_visibility='onchange')
    Warning_type = fields.Selection([('oral_warning', 'oral warning'),
                                     ('first_warning', 'first warning'),
                                     ('second_warning', 'second warning'),
                                     ('commitment_warning', 'commitment warning')], string='Warning type',required=True, track_visibility='onchange')

    _sql_constraints = [('name_uniq', 'UNIQUE (name)', 'عذرا اسم السلوك يجب ألا يتكرر')]

    @api.model
    def mk_student_behaviors(self):

        query_string = ''' 
              SELECT id, name
              FROM mk_student_behaviors;
              '''
        self.env.cr.execute(query_string)
        mk_student_behaviors = self.env.cr.dictfetchall()
        return mk_student_behaviors

class StudentBahavior(models.Model):
    _name = 'mk.student.prepare.behavior'

    preparation_id = fields.Many2one('mk.student.prepare', index=True)
    date_behavior  = fields.Date('التاريخ', required=True)
    behavior_id    = fields.Many2one('mk.student.behaviors', string='السلوك', required=True)

    send_to_parent  = fields.Boolean('Send to parent')
    send_to_teacher = fields.Boolean('Send to teacher')

    active = fields.Boolean('Active', related='preparation_id.active', default=True, store=True)
#endregion


#region class Program preparation
class UpdatePreparation(models.TransientModel):
    _name = 'mk.student.prepare.update'

    preparation_id  = fields.Many2one('mk.student.prepare')
    program_type    = fields.Selection([('open', 'مفتوح'),
                                        ('close', 'محدد')], string="program type")
    program_id      = fields.Many2one('mk.programs', 'Program name', domain="[('program_type', '=',program_type)]")
    approache_id    = fields.Many2one('mk.approaches', 'Approach', domain="[('program_id', '=',program_id)]")
    date_start      = fields.Date('التاريخ', default=fields.Date.today())
    is_update_memorize   = fields.Boolean("تعديل مقرر الحفظ")
    is_update_big_review = fields.Boolean("تعديل مقرر المراجعة الكبرى")
    is_update_tlawa      = fields.Boolean('تعديل مقرر التلاوة')
    # Memorize
    is_memorize = fields.Boolean("الحفظ")
    page_id = fields.Many2one('mk.memorize.method', string='Page', ondelete="restrict")
    surah_from_mem_id = fields.Many2one("mk.surah", string="من السورة")
    aya_from_mem_id = fields.Many2one("mk.surah.verses", string="من الآية")
    memory_direction = fields.Selection([('up', 'من الفاتحة للناس'),
                                         ('down', 'من الناس للفاتحة')], string='مسار الحفظ')
    save_start_point = fields.Many2one("mk.subject.page", string="save start point")
    # Max Review
    is_big_review = fields.Boolean("المراجعة الكبرى")
    qty_review_id = fields.Many2one('mk.memorize.method', string='مقدار المراجعة')
    surah_from_rev_id = fields.Many2one("mk.surah", string="من السورة")
    aya_from_rev_id = fields.Many2one("mk.surah.verses", string="من الآية")
    review_direction = fields.Selection([('up', 'من الفاتحة للناس'),
                                         ('down', 'من الناس للفاتحة')], string='Big review direction')
    start_point = fields.Many2one("mk.subject.page", string="from subject")
    # Min review
    is_min_review = fields.Boolean("المراجعة الصغرى")
    # # Reading
    is_tlawa = fields.Boolean('التلاوة')
    qty_read_id = fields.Many2one('mk.memorize.method', string='مقدار التلاوة')
    surah_from_read_id = fields.Many2one("mk.surah", string="من السورة")
    aya_from_read_id = fields.Many2one("mk.surah.verses", string="من الآية")
    read_direction = fields.Selection([('up', 'من الفاتحة للناس'),
                                       ('down', 'من الناس للفاتحة')], string='نقطة بداية التلاوة')
    read_start_point = fields.Many2one("mk.subject.page", string="مسار التلاوة")

    # @api.onchange('program_id')
    # def onchange_program_id(self):
    #     program_id = self.program_id
    #     if program_id:
    #         # self.approache_id = False
    #         self.is_min_review = program_id.minimum_audit
    #         self.is_big_review = program_id.maximum_audit
    #         self.is_tlawa = program_id.reading
    #         self.is_memorize = program_id.memorize

    @api.model
    def default_get(self, default_fields):
        res = super(UpdatePreparation, self).default_get(default_fields)

        preparation_id = res.get('preparation_id')
        preparation = self.env['mk.student.prepare'].browse(preparation_id)
        link = preparation.link_id
        is_meqraa_student = link.student_id.is_student_meqraa
        is_tlawa = link.is_tlawa
        is_big_review = link.is_big_review
        is_min_review = link.is_min_review
        is_memorize = link.is_memorize

        res['is_tlawa'] = is_tlawa
        res['is_big_review'] = is_big_review
        res['is_min_review'] = is_min_review
        res['is_memorize'] = is_memorize
        res['program_id'] = link.program_id.id
        res['approache_id'] = link.approache.id
        if is_meqraa_student:
            memory_direction = link.memory_direction
            page_id = link.page_id.id
            res['memory_direction'] = memory_direction
            res['page_id'] = page_id
            last_plan_line = self.env['mk.listen.line'].search([('preparation_id', '=', preparation_id),
                                                                ('type_follow', '=', 'listen'),
                                                                ('state', '=', 'draft')], limit=1, order="order asc")
            if last_plan_line:
                res['surah_from_mem_id'] = last_plan_line.from_surah.id
                res['aya_from_mem_id'] = last_plan_line.from_aya.id

            else:
                res['surah_from_mem_id'] = link.surah_from_mem_id.id
                res['aya_from_mem_id'] = link.aya_from_mem_id.id

        return res

    @api.onchange('memory_direction')
    def onchange_memory_direction(self):
        if self.is_update_memorize:
            self.page_id = False
            self.surah_from_mem_id = False

    @api.onchange('review_direction')
    def onchange_review_direction(self):
        if self.is_update_big_review:
            self.qty_review_id = False
            self.surah_from_rev_id = False

    @api.onchange('read_direction')
    def onchange_read_direction(self):
        if self.is_min_review:
            self.qty_read_id = False
            self.surah_from_read_id = False

    @api.onchange('surah_from_mem_id', 'page_id')
    def onchange_surah_qty_memorize(self):
        surah_from_mem_id = self.surah_from_mem_id.id
        qty_mem_id = self.page_id.id
        preparation_id = self.preparation_id

        aya_ids = []
        start_pt_ids = []
        if surah_from_mem_id and qty_mem_id:
            is_meqraa_student = preparation_id.link_id.student_id.is_student_meqraa
            if is_meqraa_student:
                plan_lines = self.env['mk.listen.line'].search([('preparation_id', '=', preparation_id.id),
                                                                ('type_follow', '=', 'listen'),
                                                                ('state', '=', 'draft'),
                                                                ('from_surah', '=', surah_from_mem_id)])
                for start_pt in plan_lines:
                    aya_ids += [start_pt.from_aya.id]
            else:
                start_pts = self.env['mk.subject.page'].search([('subject_page_id', '=', qty_mem_id),
                                                                ('from_surah', '=', surah_from_mem_id)])
                for start_pt in start_pts:
                    start_pt_ids += [start_pt.id]
                    aya_ids += [start_pt.from_verse.id]

        if self.is_update_memorize:
            self.aya_from_mem_id = False
            self.save_start_point = False

        return {'domain': {'aya_from_mem_id': [('id', 'in', aya_ids)],
                           'save_start_point': [('id', 'in', start_pt_ids)]}}

    @api.onchange('aya_from_mem_id')
    def onchange_aya_from_memory(self):
        aya_from = self.aya_from_mem_id.id
        qty_id = self.page_id.id
        start_pt = False

        if aya_from and qty_id:
            start_pt = self.env['mk.subject.page'].search([('subject_page_id', '=', qty_id),
                                                           ('from_verse', '=', aya_from)], limit=1)

        if self.is_update_memorize:
            self.save_start_point = start_pt and start_pt.id or False

    @api.onchange('surah_from_rev_id', 'qty_review_id')
    def onchange_surah_qty_review(self):
        surah_from_rev_id = self.surah_from_rev_id.id
        qty_review_id = self.qty_review_id.id

        aya_ids = []
        start_pt_ids = []
        if surah_from_rev_id and qty_review_id:
            start_pts = self.env['mk.subject.page'].search([('subject_page_id', '=', qty_review_id),
                                                            ('from_surah', '=', surah_from_rev_id)])

            for start_pt in start_pts:
                start_pt_ids += [start_pt.id]
                aya_ids += [start_pt.from_verse.id]

        if self.is_update_big_review:
            self.aya_from_rev_id = False
            self.start_point = False

        return {'domain': {'aya_from_rev_id': [('id', 'in', aya_ids)],
                           'start_point': [('id', 'in', start_pt_ids)]}}

    @api.onchange('aya_from_rev_id')
    def onchange_aya_from_review(self):
        aya_from = self.aya_from_rev_id.id
        qty_id = self.qty_review_id.id
        start_pt = False

        if aya_from and qty_id:
            start_pt = self.env['mk.subject.page'].search([('subject_page_id', '=', qty_id),
                                                           ('from_verse', '=', aya_from)], limit=1)

        if self.is_update_big_review:
            self.start_point = start_pt and start_pt.id or False

    @api.onchange('surah_from_read_id', 'qty_read_id')
    def onchange_surah_qty_read(self):
        surah_from_read = self.surah_from_read_id
        qty_read = self.qty_read_id

        aya_ids = []
        start_pt_ids = []
        if surah_from_read and qty_read:
            start_pts = self.env['mk.subject.page'].search([('subject_page_id', '=', qty_read.id),
                                                            ('from_surah', '=', surah_from_read.id)])

            for start_pt in start_pts:
                start_pt_ids += [start_pt.id]
                aya_ids += [start_pt.from_verse.id]

        if self.is_update_tlawa:
            self.aya_from_read_id = False
            self.read_start_point = False

        return {'domain': {'aya_from_read_id': [('id', 'in', aya_ids)],
                           'read_start_point': [('id', 'in', start_pt_ids)]}}

    @api.onchange('aya_from_read_id')
    def onchange_aya_from_read(self):
        aya_from = self.aya_from_read_id.id
        qty_id = self.qty_read_id.id
        start_pt = False

        if aya_from and qty_id:
            start_pt = self.env['mk.subject.page'].search([('subject_page_id', '=', qty_id),
                                                           ('from_verse', '=', aya_from)], limit=1)

        if self.is_update_tlawa:
            self.read_start_point = start_pt and start_pt.id or False

    @api.model
    def get_next_date(self, student_days, start_date, start, nbr_days):

        for d in range(start, nbr_days):
            next_date = start_date + timedelta(d)

            if next_date.weekday() not in student_days:
                continue

            return next_date

        return False

    @api.model
    def get_listen_line(self, order, date_listen, subject_line_from, subject_line_to, type_follow, link_id, is_test,
                        preparation_id):
        l = self.env['mk.listen.line'].create({'order': order,
                                               'preparation_id': preparation_id,
                                               'date': date_listen,
                                               'from_surah': subject_line_from.from_surah.id,
                                               'from_aya': subject_line_from.from_verse.id,
                                               'to_surah': subject_line_to.to_surah.id,
                                               'to_aya': subject_line_to.to_verse.id,
                                               'type_follow': type_follow,
                                               'student_id': link_id,
                                               'is_test': is_test})

    @api.model
    def get_history_line(self, start_date, type_subject, subject_line, direction, preparation_id):
        self.env['mk.student.prepare.history'].create({'date_start': start_date,
                                                       'preparation_id': preparation_id,
                                                       'type_subject': type_subject,
                                                       'qty_id': subject_line and subject_line.subject_page_id.id or False,
                                                       'surah_from_id': subject_line and subject_line.from_surah.id or False,
                                                       'aya_from_id': subject_line and subject_line.from_verse.id or False,
                                                       'direction': direction,
                                                       'start_point_id': subject_line and subject_line.id or False, })

    # @api.multi
    def action_update_preparation(self):
        preparation_id = self.preparation_id

        link_id = preparation_id.link_id

        episode = link_id.episode_id

        start_date = self.date_start
        start_date = datetime.strptime(start_date, "%Y-%m-%d")

        end_date = episode and episode.end_date or link_id.study_class_id.end_date
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        if end_date.date() < datetime.now().date():
            raise ValidationError(_('لا يمكنك تعديل منهج الطالب بعد نهاية الحلقة'))
        elif link_id and link_id.action_done and link_id.action_done != False:
            raise ValidationError(_('لا يمكنك تعديل منهج الطالب لحلقة منتهية'))

        elif not self.is_tlawa and not self.is_memorize and not self.is_big_review and not self.is_min_review:
            raise ValidationError(_('لا يمكنك تعديل منهج الطالب دون تحديد نوع المتابعة'))
        elif link_id and link_id.program_type and link_id.program_type == 'close':
            raise ValidationError(_('منهج الطالب محدد لا يمكنك تعديله'))
        else:
            program_id = self.program_id.id
            approache_id = self.approache_id.id
            is_memorize = self.is_memorize
            is_min_review = self.is_min_review
            is_big_review = self.is_big_review
            is_tlawa = self.is_tlawa
            old_values = {'program_id': link_id.program_id.id,
                          'program_type': self.program_type,
                          'approache_id': link_id.approache.id,
                          'is_memorize': link_id.is_memorize,
                          'is_min_review': link_id.is_min_review,
                          'is_big_review': link_id.is_big_review,
                          'is_tlawa': link_id.is_tlawa}

            update_vals = {'program_type': self.program_type,
                           'program_id': program_id,
                           'approache_id': approache_id,
                           'is_memorize': is_memorize,
                           'is_min_review': is_min_review,
                           'is_big_review': is_big_review,
                           'is_tlawa': is_tlawa}
            if old_values != update_vals:
                update_vals['date_start'] = start_date
                preparation_id.history_ids.create(update_vals)
                del update_vals['date_start']

                preparation_id.write(update_vals)
                update_vals['approache'] = update_vals['approache_id']
                link_id.write(update_vals)
        return {'type': 'ir.actions.act_window_close'}

    # @api.multi
    def action_update_meqraa_preparation(self):
        preparation = self.preparation_id
        preparation_id = preparation.id
        surah_from_mem_id = self.surah_from_mem_id
        aya_from_mem_id = self.aya_from_mem_id
        current_order = 0
        current_plan_line = self.env['mk.listen.line'].search([('preparation_id', '=', preparation_id),
                                                               ('type_follow', '=', 'listen'),
                                                               ('from_surah', '=', surah_from_mem_id.id),
                                                               ('from_aya', '=', aya_from_mem_id.id)], limit=1)

        if current_plan_line:
            current_order = current_plan_line.order
        last_plan_lines = self.env['mk.listen.line'].search([('preparation_id', '=', preparation_id),
                                                             ('type_follow', '=', 'listen'),
                                                             ('order', '<', current_order)])
        if last_plan_lines:
            last_plan_lines.write({'state': 'done',
                                   'actual_date': datetime.strptime(fields.Date.today(), '%Y-%m-%d').date()})
        old_values = {'surah_from_id': preparation.history_ids[-1].surah_from_id.id,
                      'aya_from_id': preparation.history_ids[-1].aya_from_id.id, }
        update_vals = {'surah_from_id': surah_from_mem_id.id,
                       'aya_from_id': aya_from_mem_id.id, }
        if old_values != update_vals:
            preparation.history_ids.create({'date_start': datetime.strptime(fields.Date.today(), '%Y-%m-%d'),
                                            'is_memorize': True,
                                            'qty_id': preparation.history_ids[-1].qty_id.id,
                                            'surah_from_id': surah_from_mem_id.id,
                                            'aya_from_id': aya_from_mem_id.id,
                                            'direction': self.memory_direction,
                                            'start_point_id': preparation.history_ids[-1].start_point_id.id,
                                            'program_id': preparation.program_id.id,
                                            'approache_id': preparation.link_id.approache.id, })

        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def plan_student_update(self, plan_id, d, type, direction, page, surah, aya):
        user = self.env.ref('mk_student_register.portal_user_id')

        is_memorize = False
        is_min_review = False
        is_big_review = False
        is_tlawa = False
        vals_update = {}

        save_start_point = None
        start_point = None
        read_start_point = None
        preparation_id = int(plan_id)

        page = int(page)
        surah = int(surah)
        aya = int(aya)

        preparation = self.env['mk.student.prepare'].search([('id', '=', preparation_id)], limit=1)

        if preparation and direction and page and surah and aya:

            link = preparation.link_id

            episode = link.episode_id
            link_id = link.id

            program_type = link.program_type
            approach = link.approache

            start_date = d
            start_date = datetime.strptime(start_date, "%Y-%m-%d")

            end_date = episode and episode.end_date or link.study_class_id.end_date
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

            if end_date.date() > datetime.now().date() and not link.student_id.is_student_meqraa and link.program_type != 'close':

                student_days = []
                for student_day in link.student_days:
                    order_day = student_day.order
                    if order_day == 0:
                        student_days += [6]
                    else:
                        student_days += [order_day - 1]

                if type == 'm':
                    is_memorize = True
                    memory_direction = direction

                    page_id = self.env['mk.memorize.method'].search([('id', '=', page)], limit=1)
                    surah_from_mem_id = self.env['mk.surah'].search([('id', '=', surah)], limit=1)
                    aya_from_mem_id = self.env['mk.surah.verses'].search([('id', '=', aya)], limit=1)
                    save_start_point = self.env['mk.subject.page'].search([('subject_page_id', '=', page),
                                                                           ('from_surah', '=', surah),
                                                                           ('from_verse', '=', aya)], limit=1)
                    start_memor = ((program_type == 'open') and save_start_point) or False
                    subject_memor_id = start_memor and start_memor.subject_page_id.id or False
                    last_memor = (subject_memor_id and self.env['mk.subject.page'].search(
                        [('subject_page_id', '=', subject_memor_id)], order="order desc", limit=1)) or False
                    last_memor_order = last_memor and last_memor.order or False
                    nbr_memor = approach.lessons_memorize

                    is_min_review = is_memorize and link.program_id.minimum_audit
                    start_first_s_review = start_memor
                    start_first_s_review_order = start_first_s_review and start_first_s_review.order or False
                    nbr_s_review = ((program_type == 'open') and approach.lessons_minimum_audit) or False

                    memor_close_sbjs = ((program_type == 'close') and approach.listen_ids) or []
                    start_subject_memor = memor_close_sbjs and memor_close_sbjs[0] or start_memor
                    nbr_memor_close = len(memor_close_sbjs)

                    self.sudo().get_history_line(start_date, 'm', start_subject_memor, memory_direction, preparation_id)
                    vals_update = {'memory_direction': memory_direction or False,
                                   'page_id': page_id and page_id.id or False,
                                   'surah_from_mem_id': surah_from_mem_id and surah_from_mem_id.id or False,
                                   'aya_from_mem_id': aya_from_mem_id and aya_from_mem_id.id or False,
                                   'save_start_point': save_start_point and save_start_point.id or False, }

                    memorize_lines = self.env['mk.listen.line'].search([('preparation_id', '=', preparation_id),
                                                                        ('type_follow', '=', 'listen'),
                                                                        ('state', '=', 'draft')])

                    if memorize_lines:
                        memorize_lines.unlink()

                    s_rev_close_sbjs = ((program_type == 'close') and approach.small_reviews_ids) or []
                    nbr_s_rev_close = len(s_rev_close_sbjs)

                    s_review_lines = self.env['mk.listen.line'].search([('preparation_id', '=', preparation_id),
                                                                        ('type_follow', '=', 'review_small'),
                                                                        ('state', '=', 'draft')])

                    if s_review_lines:
                        s_review_lines.unlink()

                elif type == 'r':
                    is_big_review = True
                    review_direction = direction

                    qty_review_id = self.env['mk.memorize.method'].search([('id', '=', page)], limit=1)
                    surah_from_rev_id = self.env['mk.surah'].search([('id', '=', surah)], limit=1)
                    aya_from_rev_id = self.env['mk.surah.verses'].search([('id', '=', aya)], limit=1)
                    start_point = self.env['mk.subject.page'].search([('subject_page_id', '=', page),
                                                                      ('from_surah', '=', surah),
                                                                      ('from_verse', '=', aya)], limit=1)

                    start_review = ((program_type == 'open') and start_point) or False
                    subject_review_id = start_review and start_review.subject_page_id.id or False
                    last_review = (subject_review_id and self.env['mk.subject.page'].search(
                        [('subject_page_id', '=', subject_review_id)], order="order desc", limit=1)) or False
                    last_review_order = last_review and last_review.order or False
                    nbr_review = ((program_type == 'open') and approach.lessons_maximum_audit) or False

                    b_rev_close_sbjs = ((program_type == 'close') and approach.big_review_ids) or []
                    start_subject_b_review = b_rev_close_sbjs and b_rev_close_sbjs[0] or start_review
                    nbr_b_rev_close = len(b_rev_close_sbjs)

                    self.sudo().get_history_line(start_date, 'r', start_subject_b_review, review_direction,
                                                 preparation_id)

                    vals_update.update({'review_direction': review_direction or False,
                                        'qty_review_id': qty_review_id and qty_review_id.id or False,
                                        'surah_from_rev_id': surah_from_rev_id and surah_from_rev_id.id or False,
                                        'aya_from_rev_id': aya_from_rev_id and aya_from_rev_id.id or False,
                                        'start_point': start_point and start_point.id or False, })

                    b_review_lines = self.env['mk.listen.line'].search([('preparation_id', '=', preparation_id),
                                                                        ('type_follow', '=', 'review_big'),
                                                                        ('state', '=', 'draft')])

                    if b_review_lines:
                        b_review_lines.unlink()

                elif type == 't':
                    is_tlawa = True
                    read_direction = direction

                    qty_read_id = self.env['mk.memorize.method'].search([('id', '=', page)], limit=1)
                    surah_from_read_id = self.env['mk.surah'].search([('id', '=', surah)], limit=1)
                    aya_from_read_id = self.env['mk.surah.verses'].search([('id', '=', aya)], limit=1)
                    read_start_point = self.env['mk.subject.page'].search([('subject_page_id', '=', page),
                                                                           ('from_surah', '=', surah),
                                                                           ('from_verse', '=', aya)], limit=1)

                    start_read = ((program_type == 'open') and read_start_point) or False
                    subject_read_id = start_read and start_read.subject_page_id.id or False
                    last_read = (subject_read_id and self.env['mk.subject.page'].search(
                        [('subject_page_id', '=', subject_read_id)], order="order desc", limit=1)) or False
                    last_read_order = last_read and last_read.order or False
                    nbr_read = ((program_type == 'open') and approach.lessons_reading) or False

                    tlawa_close_sbjs = ((program_type == 'close') and approach.tlawa_ids) or []
                    start_subject_tlawa = tlawa_close_sbjs and tlawa_close_sbjs[0] or start_read
                    nbr_tlawa_close = len(tlawa_close_sbjs)

                    self.sudo().get_history_line(start_date, 't', start_subject_tlawa, read_direction, preparation_id)

                    vals_update.update({'read_direction': read_direction or False,
                                        'qty_read_id': qty_read_id and qty_read_id.id or False,
                                        'surah_from_read_id': surah_from_read_id and surah_from_read_id.id or False,
                                        'aya_from_read_id': aya_from_read_id and aya_from_read_id.id or False,
                                        'read_start_point': read_start_point and read_start_point.id or False, })

                    tlawa_lines = self.env['mk.listen.line'].search([('preparation_id', '=', preparation_id),
                                                                     ('type_follow', '=', 'tlawa'),
                                                                     ('state', '=', 'draft')])

                    if tlawa_lines:
                        tlawa_lines.unlink()

                last_plan_line = self.env['mk.listen.line'].search([('preparation_id', '=', preparation_id)], limit=1,
                                                                   order="order desc")

                i = last_plan_line and (last_plan_line.order + 1) or 1
                end = True
                next_date = False
                nbr_days = (end_date - start_date).days + 1

                for d in range(nbr_days):
                    date_listen = start_date + timedelta(d)
                    if date_listen.weekday() not in student_days:
                        continue

                    if is_min_review:
                        next_date = self.get_next_date(student_days, start_date, d + 1, nbr_days)

                    if is_memorize:
                        if start_memor:
                            start_order = start_memor.order
                            end_order = min((start_order + nbr_memor - 1), last_memor_order)
                            end_memor = self.env['mk.subject.page'].search([('subject_page_id', '=', subject_memor_id),
                                                                            ('order', '=', end_order)], limit=1)
                            self.sudo().get_listen_line(i, date_listen, start_memor, end_memor, 'listen', link_id,
                                                        (start_memor.is_test or end_memor.is_test), preparation_id)

                            if next_date:
                                start_s_review_order = end_order - nbr_s_review + 1
                                start_s_review = start_first_s_review
                                if start_s_review_order > start_first_s_review_order:
                                    start_s_review = self.env['mk.subject.page'].search(
                                        [('subject_page_id', '=', subject_memor_id),
                                         ('order', '=', start_s_review_order)], limit=1)
                                self.sudo().get_listen_line(i, next_date, start_s_review, end_memor, 'review_small',
                                                            link_id,
                                                            (start_s_review.is_test or end_memor.is_test),
                                                            preparation_id)

                            start_memor = self.env['mk.subject.page'].search(
                                [('subject_page_id', '=', subject_memor_id),
                                 ('order', '=', (end_order + 1))], limit=1)
                            end = False
                        elif nbr_memor_close:
                            memor_close = memor_close_sbjs[i - 1]
                            self.sudo().get_listen_line(i, date_listen, memor_close, memor_close, 'listen', link_id,
                                                        False,
                                                        preparation_id)
                            end = False
                            if nbr_memor_close == i:
                                nbr_memor_close = 0

                    if next_date and nbr_s_rev_close:
                        s_rev_close = s_rev_close_sbjs[i - 1]
                        self.sudo().get_listen_line(i, next_date, s_rev_close, s_rev_close, 'review_small', link_id,
                                                    False,
                                                    preparation_id)
                        end = False
                        if nbr_s_rev_close == i:
                            nbr_s_rev_close = 0

                    if not is_memorize and is_big_review:
                        if start_review:
                            start_order = start_review.order
                            end_order = min((start_order + nbr_review - 1), last_review_order)
                            end_review = self.env['mk.subject.page'].search(
                                [('subject_page_id', '=', subject_review_id),
                                 ('order', '=', end_order)], limit=1)
                            self.sudo().get_listen_line(i, date_listen, start_review, end_review, 'review_big', link_id,
                                                        (start_review.is_test or end_review.is_test), preparation_id)
                            start_review = self.env['mk.subject.page'].search(
                                [('subject_page_id', '=', subject_review_id),
                                 ('order', '=', end_order + 1)], limit=1)
                            end = False
                        elif nbr_b_rev_close:
                            b_rev_close = b_rev_close_sbjs[i - 1]
                            self.sudo().get_listen_line(i, date_listen, b_rev_close, b_rev_close, 'review_big', link_id,
                                                        False,
                                                        preparation_id)
                            end = False
                            if nbr_b_rev_close == i:
                                nbr_b_rev_close = 0

                    elif is_tlawa:
                        if start_read:
                            start_order = start_read.order
                            end_order = min((start_order + nbr_read - 1), last_read_order)
                            end_read = self.env['mk.subject.page'].search([('subject_page_id', '=', subject_read_id),
                                                                           ('order', '=', end_order)], limit=1)
                            self.sudo().get_listen_line(i, date_listen, start_read, end_read, 'tlawa', link_id,
                                                        (start_read.is_test or end_read.is_test), preparation_id)
                            start_read = self.env['mk.subject.page'].search([('subject_page_id', '=', subject_read_id),
                                                                             ('order', '=', end_order + 1)], limit=1)
                            end = False

                        elif nbr_tlawa_close:
                            tlawa_close = tlawa_close_sbjs[i - 1]
                            self.sudo().get_listen_line(i, date_listen, tlawa_close, tlawa_close, 'tlawa', link_id,
                                                        False,
                                                        preparation_id)
                            end = False
                            if nbr_tlawa_close == i:
                                nbr_tlawa_close = 0

                    i += 1
                    if end:
                        break
                    end = True

                if vals_update:
                    link.sudo().write(vals_update)
        else:
            raise ValidationError(_('الرجاء تحديد كل البيانات'))

        res = vals_update and 1 or 0
        return res


class PreparationHistory(models.Model):
    _name = 'mk.student.prepare.history'

    preparation_id = fields.Many2one('mk.student.prepare')
    date_start = fields.Date('التاريخ')

    is_memorize = fields.Boolean('Memorize')
    is_min_review = fields.Boolean('Min review')
    is_big_review = fields.Boolean('Big review')
    is_tlawa = fields.Boolean('Tlawa')

    qty_id = fields.Many2one('mk.memorize.method', string='المقدار')
    surah_from_id = fields.Many2one("mk.surah", string="من السورة")
    aya_from_id = fields.Many2one("mk.surah.verses", string="من الآية")
    direction = fields.Selection([('up', 'من الفاتحة للناس'),
                                  ('down', 'من الناس للفاتحة')], string="المسار")
    start_point_id = fields.Many2one("mk.subject.page", string='نقطة بداية')

    active = fields.Boolean('Active', related='preparation_id.active', default=True, store=True)

    @api.model
    def cron_delete_student_prepare_history(self):
        cr = self.env.cr
        start_date = fields.Datetime.now()
        query = ('''delete from mk_student_prepare_history where id not in (select id
                                                                            from mk_student_prepare_history 
                                                                            where preparation_id IN (select DISTINCT(preparation_id) from mk_listen_line));''')
        cr.execute(query)
        end_date = fields.Datetime.now()
#endregion


#region class add nbr_lines
class Mosque(models.Model):
    _inherit = "mk.mosque"

    listen_line_ids = fields.One2many('mk.listen.line', 'mosque_id', 'Listen lines list')

    nbr_lines = fields.Integer('عدد الأسطر', compute='get_nbr_lines', store=True)
    nbr_pages = fields.Float('عدد الأوجه الإجمالي',   compute='get_nbr_lines', store=True)

    nbr_listen_pages        = fields.Float(' أوجه التسميع',         compute='get_nbr_lines', store=True)
    nbr_read_pages          = fields.Float(' أوجه التلاوة',          compute='get_nbr_lines', store=True)
    nbr_small_review_pages  = fields.Float(' أوجه المراجعة الصغرى', compute='get_nbr_lines', store=True)
    nbr_big_review_pages    = fields.Float(' أوجه المراجعة الكبرى', compute='get_nbr_lines', store=True)

    @api.model
    def cron_compute_nbr_lines_pages_listen_mosque(self):
        mosques = self.env['mk.mosque'].search([('episode_id', '!=', False),
                                                ('episode_id.link_ids.listen_lines_ids', '!=', False),
                                                '|', ('active', '=', True),
                                                     ('active', '=', False)])
        total = len(mosques)
        i = 0
        for mosque in mosques:
            i += 1

            nbr_lines = sum(episode.nbr_lines for episode in mosque.episode_id.filtered(lambda e: e.study_class_id.is_default == True))

            nbr_listen_lines = sum(episode.nbr_listen_pages for episode in mosque.episode_id.filtered(lambda e: e.study_class_id.is_default == True))
            nbr_read_lines = sum(episode.nbr_read_pages for episode in mosque.episode_id.filtered(lambda e: e.study_class_id.is_default == True))
            nbr_small_review_lines = sum(episode.nbr_small_review_pages for episode in mosque.episode_id.filtered(lambda e: e.study_class_id.is_default == True))
            nbr_big_review_lines = sum(episode.nbr_big_review_pages for episode in mosque.episode_id.filtered(lambda e: e.study_class_id.is_default == True))
            mosque.nbr_lines = nbr_lines
            mosque.nbr_pages = nbr_lines / 15

            mosque.nbr_listen_pages = nbr_listen_lines
            mosque.nbr_read_pages = nbr_read_lines
            mosque.nbr_small_review_pages = nbr_small_review_lines
            mosque.nbr_big_review_pages = nbr_big_review_lines

    @api.depends('listen_line_ids.nbr_lines', 'listen_line_ids.nbr_pages')
    def get_nbr_lines(self):
        for rec in self:
            total_nbr_lines = 0
            nbr_listen_lines = 0
            nbr_read_lines = 0
            nbr_small_review_lines = 0
            nbr_big_review_lines = 0
            lines_ids = rec.listen_line_ids.filtered(lambda l: l.study_class_id.is_default == True)
            for line in lines_ids:
                nbr_lines = line.nbr_lines
                type_follow = line.type_follow
                total_nbr_lines += nbr_lines
                if type_follow == 'tlawa':
                    nbr_read_lines += nbr_lines
                elif type_follow == 'review_small':
                    nbr_small_review_lines += nbr_lines
                elif type_follow == 'review_big':
                    nbr_big_review_lines += nbr_lines
                else:
                    nbr_listen_lines += nbr_lines

            rec.nbr_lines = total_nbr_lines
            rec.nbr_pages = total_nbr_lines / 15

            rec.nbr_listen_pages = nbr_listen_lines / 15
            rec.nbr_read_pages = nbr_read_lines / 15
            rec.nbr_small_review_pages = nbr_small_review_lines / 15
            rec.nbr_big_review_pages = nbr_big_review_lines / 15

    # @api.multi
    def open_view_listen_lines(self):
        tree_view = self.env.ref('mk_student_managment.mk_listen_line_tree_view_mosque')
        search_id = self.env.ref('mk_student_managment.mk_listenline_search_view')
        vals = {'name': "عدد الأوجه",
                'res_model': 'mk.listen.line',
                'res_id': self.id,
                'views': [(tree_view.id, 'tree')],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'context': {'default_mosque_id': self.id},
                'domain': [('mosque_id', '=', self.id),('study_class_id.is_default','=',True)],
                'search_view_id': search_id.id}
        return vals

    # @api.multi
    def open_view_student_presence_lines(self):
        tree_view = self.env.ref('mk_student_managment.inherit_student_prepare_presence_tree_view')
        search_id = self.env.ref('mk_student_managment.student_prepare_presence_search_view')
        return {'name': "حضور الطلاب",
                'res_model': 'mk.student.prepare.presence',
                'res_id': self.id,
                'views': [(tree_view.id, 'tree')],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('mosque_id', '=', self.id)],
                'context': {'search_default_absent_today':1} ,
                'search_view_id': search_id.id}


class Episode(models.Model):
    _inherit = "mk.episode"

    listen_line_ids = fields.One2many('mk.listen.line', 'episode', 'Listen lines list', copy=False)
    nbr_lines = fields.Integer('عدد الأسطر',          compute='get_nbr_lines', store=True, copy=False)
    nbr_pages = fields.Float('عدد الأوجه الإجمالي',   compute='get_nbr_lines', store=True, copy=False)

    nbr_listen_pages        = fields.Float(' أوجه التسميع',         compute='get_nbr_lines', store=True, copy=False)
    nbr_read_pages          = fields.Float(' أوجه التلاوة',          compute='get_nbr_lines', store=True, copy=False)
    nbr_small_review_pages  = fields.Float(' أوجه المراجعة الصغرى', compute='get_nbr_lines', store=True, copy=False)
    nbr_big_review_pages    = fields.Float(' أوجه المراجعة الكبرى', compute='get_nbr_lines', store=True, copy=False)

    @api.depends('listen_line_ids.nbr_lines', 'listen_line_ids.nbr_pages')
    def get_nbr_lines(self):
        for rec in self:
            total_nbr_lines = 0
            nbr_listen_lines = 0
            nbr_read_lines = 0
            nbr_small_review_lines = 0
            nbr_big_review_lines = 0
            lines_ids = rec.listen_line_ids
            for line in lines_ids:
                nbr_lines = line.nbr_lines
                type_follow = line.type_follow
                total_nbr_lines += nbr_lines
                if type_follow == 'tlawa':
                    nbr_read_lines += nbr_lines
                elif type_follow == 'review_small':
                    nbr_small_review_lines += nbr_lines
                elif type_follow == 'review_big':
                    nbr_big_review_lines += nbr_lines
                else:
                    nbr_listen_lines += nbr_lines

            rec.nbr_lines = total_nbr_lines
            rec.nbr_pages = total_nbr_lines / 15

            rec.nbr_listen_pages = nbr_listen_lines / 15
            rec.nbr_read_pages = nbr_read_lines / 15
            rec.nbr_small_review_pages = nbr_small_review_lines / 15
            rec.nbr_big_review_pages = nbr_big_review_lines / 15

    @api.model
    def cron_compute_nbr_lines_pages_listen_line(self):
        listen_lines_ids = self.env['mk.listen.line'].search(['|',('active', '=', True),
                                                                  ('active', '=', False)])
        total = len(listen_lines_ids)
        i = 0
        for rec in listen_lines_ids:
            from_surah = rec.from_surah
            from_surah_order = from_surah.order

            to_surah = rec.to_surah
            to_surah_order = to_surah.order

            start_line_from_aya = rec.from_aya.line_start
            end_line_to_aya = rec.to_aya.line_end

            nb_lines = 0
            if from_surah_order <= to_surah_order:
                nb_lines = end_line_to_aya - start_line_from_aya + 1
            else:
                order_to = max(to_surah_order, from_surah_order)
                order_from = min(to_surah_order, from_surah_order)

                surahs = self.env['mk.surah'].search([('order', '<=', order_to),
                                                      ('order', '>=', order_from)], order="order")

                from_surah_id = rec.from_surah.id
                to_surah_id = rec.to_surah.id
                for surah in surahs:
                    surah_id = surah.id
                    if surah_id == from_surah_id:
                        aya_end_first_surah = self.env['mk.surah.verses'].search([('surah_id', '=', surah_id)],
                                                                                 order="original_surah_order desc",
                                                                                 limit=1)
                        nb_lines += aya_end_first_surah.line_end - start_line_from_aya + 1
                    elif surah_id == to_surah_id:
                        aya_start_last_surah = self.env['mk.surah.verses'].search([('surah_id', '=', surah_id)],
                                                                                  order="original_surah_order asc",
                                                                                  limit=1)
                        nb_lines += end_line_to_aya - aya_start_last_surah.line_start + 1
                    else:
                        nb_lines += surah.nbr_lines

            rec.nbr_lines = nb_lines
            rec.nbr_pages = nb_lines / 15

    @api.model
    def cron_compute_nbr_lines_pages_link(self):
        link_ids = self.env['mk.link'].search([('listen_lines_ids', '!=', False)])
        total = len(link_ids)
        i = 0
        for link in link_ids:
            i += 1
            listen_lines_ids = link.listen_lines_ids
            nbr_lines = sum(line.nbr_lines for line in listen_lines_ids)
            nbr_listen_lines = sum(line.nbr_lines for line in listen_lines_ids.filtered(lambda l: l.type_follow == 'listen'))
            nbr_read_lines = sum(line.nbr_lines for line in listen_lines_ids.filtered(lambda l: l.type_follow == 'tlawa'))
            nbr_small_review_lines = sum(line.nbr_lines for line in listen_lines_ids.filtered(lambda l: l.type_follow == 'review_small'))
            nbr_big_review_lines = sum(line.nbr_lines for line in listen_lines_ids.filtered(lambda l: l.type_follow == 'review_big'))
            link.nbr_lines = nbr_lines
            link.nbr_pages = nbr_lines / 15

            link.nbr_listen_pages =  nbr_listen_lines/ 15
            link.nbr_read_pages = nbr_read_lines / 15
            link.nbr_small_review_pages = nbr_small_review_lines / 15
            link.nbr_big_review_pages = nbr_big_review_lines / 15

    @api.model
    def cron_compute_nbr_lines_pages_listen_episode(self):
        episodes = self.env['mk.episode'].search([('link_ids', '!=', False),
                                                  ('link_ids.listen_lines_ids', '!=', False),
                                                  '|', ('active', '=', True),
                                                       ('active', '=', False)])
        total = len(episodes)
        i = 0
        computed = 0
        for episode in episodes:
            i+= 1
            nbr_lines = sum(link.nbr_lines for link in episode.link_ids)
            episode.nbr_lines = nbr_lines
            episode.nbr_pages = nbr_lines / 15
            lines_ids = self.env['mk.listen.line'].search([('episode', '=', episode.id)])
            if lines_ids:
                nbr_listen_lines = sum(line.nbr_lines for line in lines_ids.filtered(lambda l: l.type_follow == 'listen'))
                nbr_read_lines = sum(line.nbr_lines for line in lines_ids.filtered(lambda l: l.type_follow == 'tlawa'))
                nbr_small_review_lines = sum(line.nbr_lines for line in lines_ids.filtered(lambda l: l.type_follow == 'review_small'))
                nbr_big_review_lines = sum(line.nbr_lines for line in lines_ids.filtered(lambda l: l.type_follow == 'review_big'))

                episode.nbr_listen_pages = nbr_listen_lines / 15
                episode.nbr_read_pages = nbr_read_lines / 15
                episode.nbr_small_review_pages = nbr_small_review_lines / 15
                episode.nbr_big_review_pages = nbr_big_review_lines / 15
                computed += 1

    #region app api
    @api.model
    def teacher_offline_check_episodes(self, data):
        start_time = time.time()
        teacher_id = data['teacher_id']
        app_episode_ids = data['episodes']
        current_episode_ids = self.env['mk.episode'].search([('teacher_id', '=', teacher_id),
                                                             ('study_class_id.is_default', '=', True),
                                                             ('state', '=', 'accept')]).ids
        deleted_episodes = []
        new_episodes = []
        update = False

        set_app_episode_ids = set(app_episode_ids)
        set_current_episode_ids = set(current_episode_ids)

        if set_app_episode_ids != set_current_episode_ids:
            update = True
            items = set_app_episode_ids.intersection(set_current_episode_ids)
            deleted_episodes = list(set_app_episode_ids - items)
            new_episode_ids = list(set_current_episode_ids - items)
            if new_episode_ids:
                new_links = self.env['mk.link'].search([('episode_id', 'in', new_episode_ids),
                                                    ('state', '=', 'accept')])
                for new_episode in new_episode_ids:
                    students = []
                    episode = False
                    links = new_links.filtered(lambda l: l.episode_id.id == new_episode)
                    if not links:
                        continue
                    for link in links:
                        student = link.student_id
                        if not episode:
                            episode = link.episode_id

                        age = 0
                        # dob = link.student_id.birthdate
                        # if dob:
                        #     d1 = datetime.strptime(dob, "%Y-%m-%d").date()
                        #     d2 = date.today()
                        #     age = relativedelta(d2, d1).years

                        # test_session = self.env['student.test.session'].search([('student_id', '=', link_id),
                        #                                                         ('state', '!=', 'cancel')], limit=1)

                        students += [{'id':                    link.id,
                                      'student_id':            student.id,
                                      'plan_id':               link.preparation_id.id,
                                      'general_behavior_type': False,
                                      'name':                  student.display_name,
                                      'rate': 0,
                                      'age': age,
                                      'test_register': False,
                                      'session_id':    False,
                                      'type_exam_id':  False,
                                      'track':         False,
                                      'branch_id':     False,
                                      'period_id':     False,
                                      'state': 'تحضير الطالب'}]

                    new_episodes += [{'id':           new_episode,
                                      'display_name': episode.display_name,
                                      'name':         episode.name,
                                      'epsd_type':    episode.program_id.name,
                                      'epsd_work':    episode.approache_id.name,
                                      'students':     students}]

        result = {'update':           update,
                  'deleted_episodes': deleted_episodes,
                  'new_episodes':     new_episodes}
        return result

    @api.model
    def teacher_episodes(self, teacher_id):
        teacher_id = int(teacher_id)
        query_string = ''' 
           select e.id, e.display_name, e.name, prg.name as epsd_type, app.name as epsd_work
           from mk_episode e left join mk_programs prg on e.program_id=prg.id
                             left join mk_approaches app on e.approache_id=app.id
           where e.teacher_id={} and
           e.state='accept' and
           e.active=True;
           '''.format(teacher_id)

        self.env.cr.execute(query_string)
        teacher_episodes = self.env.cr.dictfetchall()
        return teacher_episodes
    #endregion


class Link(models.Model):
    _inherit = "mk.link"

    listen_lines_ids = fields.One2many("mk.listen.line", "student_id", "Listen lines list", copy=False)
    presence_ids     = fields.One2many('mk.student.prepare.presence', 'link_id', string='حضور الطالب' , copy=False)
    nbr_lines = fields.Integer('عدد الأسطر', compute='get_nbr_lines', store=True, copy=False)
    nbr_pages = fields.Float('عدد الأوجه الإجمالي',   compute='get_nbr_lines', store=True, copy=False)

    nbr_listen_pages        = fields.Float(' أوجه التسميع',         compute='get_nbr_lines', store=True, copy=False)
    nbr_read_pages          = fields.Float(' أوجه التلاوة',          compute='get_nbr_lines', store=True, copy=False)
    nbr_small_review_pages  = fields.Float(' أوجه المراجعة الصغرى', compute='get_nbr_lines', store=True, copy=False)
    nbr_big_review_pages    = fields.Float(' أوجه المراجعة الكبرى', compute='get_nbr_lines', store=True, copy=False)


    @api.depends('listen_lines_ids.nbr_lines', 'listen_lines_ids.nbr_pages')
    def get_nbr_lines(self):
        for rec in self:
            total_nbr_lines = 0
            nbr_listen_lines = 0
            nbr_read_lines = 0
            nbr_small_review_lines = 0
            nbr_big_review_lines = 0
            lines_ids = rec.listen_lines_ids
            for line in lines_ids:
                nbr_lines = line.nbr_lines
                type_follow = line.type_follow
                total_nbr_lines += nbr_lines
                if type_follow == 'tlawa':
                    nbr_read_lines += nbr_lines
                elif type_follow == 'review_small':
                    nbr_small_review_lines += nbr_lines
                elif type_follow == 'review_big':
                    nbr_big_review_lines += nbr_lines
                else:
                    nbr_listen_lines += nbr_lines

            rec.nbr_lines = total_nbr_lines
            rec.nbr_pages = total_nbr_lines / 15
            rec.nbr_listen_pages = nbr_listen_lines / 15
            rec.nbr_read_pages = nbr_read_lines / 15
            rec.nbr_small_review_pages = nbr_small_review_lines / 15
            rec.nbr_big_review_pages = nbr_big_review_lines / 15
#endregion


#region class old
class mk_ditels_mistake_line(models.Model):
    _name = 'mk.details.mistake'
    _description = 'Description'

    @api.one
    @api.depends('mistake_details', 'mistake_details.nbr_mstk_qty', 'nbr_mstk_qty')
    def get_total_mstk_qty(self):
        total_mstk_qty = sum(mstk.nbr_mstk_qty for mstk in self.mistake_details)
        self.total_mstk_qty = total_mstk_qty or self.nbr_mstk_qty

    @api.one
    @api.depends('mistake_details', 'mistake_details.number_mistake', 'number_mistake')
    def get_total_mstk_qlty(self):
        total_mstk_qlty = sum(mstk.number_mistake for mstk in self.mistake_details)
        self.total_mstk_qlty = total_mstk_qlty or self.number_mistake

    @api.one
    @api.depends('mistake_details', 'mistake_details.nbr_mstk_read', 'nbr_mstk_read')
    def get_nbr_mstk_read(self):
        total_mstk_read = sum(mstk.nbr_mstk_read for mstk in self.mistake_details)
        self.total_mstk_read = total_mstk_read or self.nbr_mstk_read

    mistake_id = fields.Many2one('mk.listen.line', string='Mistake Details', ondelete='cascade')
    name_mistake_id = fields.Many2one('mk.test.error', string='Error')

    surah_id = fields.Many2one('mk.surah', string='Surah')
    aya_id = fields.Many2one('mk.surah.verses', string='آخر آية')

    from_surah = fields.Many2one('mk.surah', string='From Sura')
    from_aya = fields.Many2one('mk.surah.verses', string='From Aya')
    to_surah = fields.Many2one('mk.surah', string='To Sura')
    to_aya = fields.Many2one('mk.surah.verses', string='To Aya')

    nbr_abscent = fields.Integer('عدد أيام الغياب')
    nbr_mstk_qty = fields.Integer('عدد أخطاء كمية الحفظ')
    number_mistake = fields.Integer('عدد أخطاء جودة الحفظ')
    nbr_mstk_read = fields.Integer('عدد أخطاء التجويد')

    mistake_details = fields.One2many('mk.details.mistake', 'total_mistake_id')
    total_mistake_id = fields.Many2one('mk.details.mistake')
    total_mstk_qty = fields.Integer('إجمالي أخطاء كمية الحفظ', compute=get_total_mstk_qty, store=True)
    total_mstk_qlty = fields.Integer('إجمالي أخطاء جودة الحفظ', compute=get_total_mstk_qlty, store=True)
    total_mstk_read = fields.Integer('إجمالي أخطاء التجويد', compute=get_nbr_mstk_read, store=True)

    is_late = fields.Boolean('متأخر')
    curriculum_id = fields.Many2one('mk.subject.page', string='المنهج')
    deduct_delay = fields.Float('الخصم على التأخير')
    deduct_absence = fields.Float('الخصم على الغياب')
    deduct_qty_memorize = fields.Float('الخصم على كمية الحفظ')
    deduct_memorize = fields.Float('الخصم على جودة الحفظ')
    deduct_tajweed = fields.Float('الخصم على جودة التجويد')

    indiscipline_ids = fields.One2many('mk.student.plan.line.indiscipline', 'eval_id', string='أيام الغياب')
    active = fields.Boolean('Active', track_visibility='onchange', default=True)

    @api.model
    def detail_mistakes_plan_line(self, plan_line_id):
        try:
            plan_line_id = int(plan_line_id)
        except:
            pass

        query_string = ''' 
            SELECT m.id,
            m.nbr_mstk_qty,
            m.number_mistake nbr_mstk_qlty,
            m.nbr_mstk_read,
            m.surah_id,
            s.name surah_id_name,
            m.aya_id,
            v.original_surah_order aya_name
            FROM mk_details_mistake m left join mk_surah s on m.surah_id=s.id
            left join mk_surah_verses v on m.aya_id=v.id
            WHERE m.total_mistake_id is not null AND mistake_id={};
            '''.format(plan_line_id)

        self.env.cr.execute(query_string)
        detail_mistakes_plan_line = self.env.cr.dictfetchall()
        return detail_mistakes_plan_line

    @api.model
    def mistake_detail(self, plan_line_id, aya_id):
        try:
            plan_line_id = int(plan_line_id)
            aya_id = int(aya_id)
        except:
            pass

        query_string = ''' 
              SELECT COALESCE(nbr_mstk_qty,0) nbr_mstk_qty,
              COALESCE(number_mistake,0) nbr_mstk_qlty,
              COALESCE(nbr_mstk_read,0) nbr_mstk_read
              FROM mk_details_mistake 
              WHERE mistake_id={} AND 
              aya_id={};
              '''.format(plan_line_id, aya_id)

        self.env.cr.execute(query_string)
        mistake_detail = self.env.cr.dictfetchall()
        if len(mistake_detail) < 0:
            return {'nbr_mstk_qty': 0, 'nbr_mstk_qlty': 0, 'nbr_mstk_read': 0}

        return mistake_detail

    @api.model
    def mistakes_plan_line(self, plan_line_id):
        try:
            plan_line_id = int(plan_line_id)
        except:
            pass

        query_string = ''' 
              SELECT m.total_mstk_qty,
              m.total_mstk_qlty,
              m.total_mstk_read

              FROM mk_details_mistake m
              LEFT JOIN mk_listen_line l
              ON l.id=m.mistake_id

              WHERE m.total_mistake_id is null AND
              l.id={};
              '''.format(plan_line_id)

        self.env.cr.execute(query_string)
        mistakes_plan_line = self.env.cr.dictfetchall()
        return mistakes_plan_line

    @api.model
    def get_mistakes_ids(self, line_id, mistake_name_id):
        try:
            line_id = int(line_id)
            mistake_name_id = int(mistake_name_id)
        except:
            pass

        query_string = ''' select id from  mk_details_mistake where mistake_id={} and name_mistake_id={} '''.format(
            line_id, mistake_name_id)

        self.env.cr.execute(query_string)
        item_list = self.env.cr.dictfetchall()
        return item_list

    @api.model
    def mistake_count(self, line_id):
        try:
            line_id = int(line_id)
        except:
            pass

        query_string = ''' 
               SELECT  count(te.code) FILTER (WHERE  
                te.code = 'galy') AS total_galy , count(te.code) FILTER (WHERE 
                te.code = 'khafy') AS total_khafy,count(te.code) FILTER (WHERE  
                te.code = 'lafzy') AS total_lafzy , count(te.code) FILTER (WHERE  
                te.code = 'Tjweed') AS total_Tjweed
               FROM 
                 mk_details_mistake md
                join mk_test_error te on te.id = md.name_mistake_id

                where mistake_id = {}
              '''.format(line_id)

        self.env.cr.execute(query_string)
        item_list = self.env.cr.dictfetchall()
        return item_list

    @api.model
    def cron_delete_mistakes_draft_lines(self):
        cr = self.env.cr
        start_date = fields.Datetime.now()
        query1 = '''select count(md.id) from mk_details_mistake as md 
                          left join mk_listen_line as mlist on md.mistake_id = mlist.id
                          left join mk_student_prepare as mprep on mlist.preparation_id = mprep.id
                          left join mk_episode as mp on mp.id = mprep.stage_pre_id
                          where mp.study_class_id < 102 and mlist.state = 'draft'; '''
        self.env.cr.execute(query1)
        mistakes = self.env.cr.dictfetchall()
        query = ('''delete from mk_details_mistake where id in(select md.id from mk_details_mistake as md  
                                                                          left join mk_listen_line as mlist on md.mistake_id = mlist.id
                                                                          left join mk_student_prepare as mprep on mlist.preparation_id = mprep.id
                                                                          left join mk_episode as mp on mp.id = mprep.stage_pre_id
                                                                          where mp.study_class_id < 102 and mlist.state = 'draft');''')
        cr.execute(query)
        end_date = fields.Datetime.now()

    @api.model
    def cron_delete_mistakes_lines_with_no_episode(self):
        cr = self.env.cr
        start_date = fields.Datetime.now()
        query1 = '''select count(md.id) from mk_details_mistake as md  
                          left join mk_listen_line as mlist on md.mistake_id = mlist.id
                          left join mk_student_prepare as mprep on mlist.preparation_id = mprep.id
                          where mprep.stage_pre_id is null; '''
        self.env.cr.execute(query1)
        mistakes = self.env.cr.dictfetchall()
        query = ('''delete from mk_details_mistake where id in(select md.id from mk_details_mistake as md  
                                                              left join mk_listen_line as mlist on md.mistake_id = mlist.id
                                                              left join mk_student_prepare as mprep on mlist.preparation_id = mprep.id
                                                              where mprep.stage_pre_id is null);''')
        cr.execute(query)
        end_date = fields.Datetime.now()


class StudentPlanLineIndiscipline(models.Model):
    _name = 'mk.student.plan.line.indiscipline'

    eval_id = fields.Many2one('mk.details.mistake')
    date_indiscipline = fields.Date('تاريخ ', required=True, default=fields.Date.today())
    type_indiscipline = fields.Selection([('absent', 'غائب'),
                                          ('absent_excuse', 'غائب بعذر'),
                                          ('delay', 'متأخر'),
                                          ('not_read', 'لم يسمع'),
                                          ('excuse', 'استأذن'), ], string='نوع عدم الإنضباط')
    active = fields.Boolean('Active', track_visibility='onchange', default=True)

    @api.model
    def create(self, vals):
        type_indiscipline = vals.get('type_indiscipline', False)
        date_indiscipline = vals.get('date_indiscipline', False)
        eval_id = vals.get('eval_id', False)
        indicipline_lines = self.env['mk.student.plan.line.indiscipline'].search(
            [('date_indiscipline', '=', date_indiscipline),
             ('eval_id', '=', eval_id),
             ('type_indiscipline', '=', type_indiscipline)])
        indicipline_lines.unlink()

        if type_indiscipline in ['absent', 'absent_excuse']:
            indicipline_lines = self.env['mk.student.plan.line.indiscipline'].search(
                [('date_indiscipline', '=', date_indiscipline),
                 ('eval_id', '=', eval_id)])
            indicipline_lines.unlink()

        if type_indiscipline in ['delay', 'not_read', 'excuse']:
            indicipline_lines = self.env['mk.student.plan.line.indiscipline'].search(
                [('date_indiscipline', '=', date_indiscipline),
                 ('eval_id', '=', eval_id),
                 ('type_indiscipline', 'in', ['absent', 'absent_excuse'])])
            indicipline_lines.unlink()
        return super(StudentPlanLineIndiscipline, self).create(vals)

    # @api.multi
    def write(self, vals):
        if 'type_indiscipline' in vals or 'date_indiscipline' in vals:
            type_indiscipline = vals.get('type_indiscipline', False)
            date_indiscipline = vals.get('date_indiscipline', False)
            eval_id = vals.get('eval_id', False)
            indicipline_lines = self.env['mk.student.plan.line.indiscipline'].search(
                [('date_indiscipline', '=', date_indiscipline),
                 ('eval_id', '=', eval_id),
                 ('type_indiscipline', '=', type_indiscipline)])
            indicipline_lines.unlink()

            if type_indiscipline in ['absent', 'absent_excuse']:
                indicipline_lines = self.env['mk.student.plan.line.indiscipline'].search(
                    [('date_indiscipline', '=', date_indiscipline),
                     ('eval_id', '=', eval_id)])
                indicipline_lines.unlink()

            if type_indiscipline in ['delay', 'not_read', 'excuse']:
                indicipline_lines = self.env['mk.student.plan.line.indiscipline'].search(
                    [('date_indiscipline', '=', date_indiscipline),
                     ('eval_id', '=', eval_id),
                     ('type_indiscipline', 'in', ['absent', 'absent_excuse'])])
                indicipline_lines.unlink()

        return super(StudentPlanLineIndiscipline, self).write(vals)

    @api.model
    def delete_all_plan_line_indiscipline_cron_fct(self):
        start_date = fields.Datetime.now()
        query1 = '''select count(indisc.id) from mk_student_plan_line_indiscipline as indisc
                        left join mk_details_mistake as md on indisc.eval_id=md.id
                        left join mk_listen_line as mlist on md.mistake_id = mlist.id
                        left join mk_student_prepare as mprep on mlist.preparation_id = mprep.id
                        left join mk_episode as mp on mp.id = mprep.stage_pre_id
                        where mp.study_class_id < 102 and mlist.state = 'draft'; '''
        self.env.cr.execute(query1)
        indiscipline = self.env.cr.dictfetchall()
        query = """DELETE FROM mk_student_plan_line_indiscipline
                        where id in (select indisc.id 
                                 from mk_student_plan_line_indiscipline as indisc
                                            left join mk_details_mistake as md on indisc.eval_id=md.id
                                            left join mk_listen_line as mlist on md.mistake_id = mlist.id
                                            left join mk_student_prepare as mprep on mlist.preparation_id = mprep.id
                                            left join mk_episode as mp on mp.id = mprep.stage_pre_id
                                            where mp.study_class_id < 102 and mlist.state = 'draft');"""
        self.env.cr.execute(query)
        end_date = fields.Datetime.now()

    @api.model
    def delete_plan_line_indiscipline_with_no_episode_cron_fct(self):
        start_date = fields.Datetime.now()
        query1 = '''select count(indisc.id) from mk_student_plan_line_indiscipline as indisc
                        left join mk_details_mistake as md on indisc.eval_id=md.id
                        left join mk_listen_line as mlist on md.mistake_id = mlist.id
                        left join mk_student_prepare as mprep on mlist.preparation_id = mprep.id
                        where mprep.stage_pre_id is null; '''
        self.env.cr.execute(query1)
        indiscipline = self.env.cr.dictfetchall()
        query = """DELETE FROM mk_student_plan_line_indiscipline
                        where id in (select indisc.id from mk_student_plan_line_indiscipline as indisc
                                    left join mk_details_mistake as md on indisc.eval_id=md.id
                                    left join mk_listen_line as mlist on md.mistake_id = mlist.id
                                    left join mk_student_prepare as mprep on mlist.preparation_id = mprep.id
                                    where mprep.stage_pre_id is null);"""
        self.env.cr.execute(query)
        end_date = fields.Datetime.now()

class test_line(models.Model):
    _name = 'mk.test.line'
    _description = 'Description'
    _order = 'order asc'

    line_id = fields.Many2one('mk.student.prepare', string='line', ondelete='cascade')
    subject_id = fields.Many2one('mk.subject.configuration', string='Subject', ondelete='restrict')
    order = fields.Integer(related="subject_id.order", string='Order', store=True, )
    date = fields.Date('Date')
    day = fields.Selection([('0', 'Monday'),
                            ('1', 'Tuseday'),
                            ('2', 'Wednsday'),
                            ('3', 'Thursday'),
                            ('4', 'Friday'),
                            ('5', 'Saturday'),
                            ('6', 'Sunday')], 'Day')
    actual_date = fields.Date('Actual Date')
    actual_day = fields.Selection([('0', 'Monday'),
                                   ('1', 'Tuseday'),
                                   ('2', 'Wednsday'),
                                   ('3', 'Thursday'),
                                   ('4', 'Friday'),
                                   ('5', 'Saturday'),
                                   ('6', 'Sunday')], 'Actual Day')
    check = fields.Boolean('Matching', default=True)
    degree = fields.Integer('Degree', compute='total_degree', store=True)
    test_question_ids = fields.One2many('mk.test.question', 'question_id', string='Questions Test')
    state = fields.Selection([('draft', 'Draft'),
                              ('absent', 'Absent'),
                              ('start_test', 'Start Test'),
                              ('done', 'Done')], 'Status', default='draft')

    @api.one
    def wkf_draft(self):
        self.state = 'draft'

    @api.one
    def random_questions(self):
        line_ids = self.search([('line_id', '=', self.line_id.id),
                                ('subject_id.order', '<', self.subject_id.order),
                                ('state', '!=', 'done')])
        if line_ids:
            raise osv.except_osv(_('Error'), _('Check your previous Tests.'))

        for line in self.test_question_ids:
            line.unlink()

        verses_obj = self.env['mk.surah.verses']
        question_obj = self.env['mk.test.question']
        from_aya = self.subject_id.detail_id.from_verse.original_accumalative_order
        to_aya = self.subject_id.detail_id.to_verse.original_accumalative_order
        quest = sorted([randint(from_aya, to_aya) for a in range(0, 10)])

        for i in [1, 3, 5, 7, 9]:
            from_verse = verses_obj.search([('original_accumalative_order', '=', quest[i - 1])])
            to_verse = verses_obj.search([('original_accumalative_order', '=', quest[i])])
            question_obj.create({'from_surah': from_verse[0].surah_id.id,
                                 'from_verse': from_verse[0].id,
                                 'to_surah': to_verse[0].surah_id.id,
                                 'to_verse': to_verse[0].id,
                                 'question_id': self.id})

        self.state = 'start_test'

    @api.one
    def wkf_done(self):
        start_date = datetime.strptime(fields.Date.today(), '%Y-%m-%d')
        self.actual_day = str(start_date.weekday())
        self.actual_date = start_date
        self.state = 'done'

    # @api.multi
    @api.depends('test_question_ids')
    def total_degree(self):
        total = 0
        for rec in self:
            for line in rec.test_question_ids:
                for l in line.quest_mistake_ids:
                    total += (l.number_mistake * l.name_mistake_id.degree_deduct)
            rec.degree = 100 - total

    # @api.multi
    def get_test_record(self, student_id):
        # pre_obj=self.env['mk.student.prepare']
        obj_test = self.env['mk.test.line'].search([('line_id.link_id.student_id', '=', student_id)])

        records = []
        rec_dict = []
        dict_line1 = []
        dict_error = []

        teatcher_id = 0
        teacher_name = ''
        episode_id = 0
        episode_name = ''
        date = ''
        # type_follow = ''

        for rec in obj_test:
            #
            # object_mistakes=self.env['mk.details.mistake']
            episode_id = rec.line_id.stage_pre_id.id
            if rec.line_id.stage_pre_id:
                episode_name = rec.line_id.stage_pre_id.name
            else:
                episode_name = False

            teacher_id = rec.line_id.name.id
            if rec.line_id.name.name:
                teacher_name = rec.line_id.name.name
            else:
                teacher_name = False

            subject_id = rec.subject_id.name
            date = rec.date
            day = rec.day
            actual_day = rec.actual_day
            actual_date = rec.actual_date
            check = rec.check
            degree = rec.degree
            date = rec.line_id.prepare_date
            state = rec.state
            line_id = rec.line_id

            for rec_que in rec.test_question_ids:
                from_verse = rec_que.from_verse.id
                to_verse = rec_que.to_verse.id
                from_surah = rec_que.from_surah.name
                to_surah = rec_que.to_surah.name
                mistake_q = rec_que.mistake

                for rec_error in rec_que.quest_mistake_ids:
                    name_mistake_id = rec_error.name_mistake_id.name
                    number_mistake = rec_error.number_mistake
                    lst1 = []
                    dict_error = ({'name_mistake_id': name_mistake_id,
                                   'number_mistake': number_mistake, })
                    lst1.append(dict_error)

                dict_qute = ({'from_surah': from_surah,
                              'from_verse': from_verse,
                              'to_surah': to_surah,
                              'to_verse': to_verse,
                              'mistake_q': mistake_q,
                              'lst1': lst1})
                records.append(dict_qute)

            rec_dict = ({'line_id': line_id,
                         'episode_name': str(episode_name),
                         'teacher_name': str(teacher_name),
                         'subject_id': subject_id,
                         'actual_day': actual_day,
                         'actual_date': actual_date,
                         'check': check,
                         'date': date,
                         'degree': degree,
                         'state': state})
            records.append(rec_dict)
        return records


class mk_test_question(models.Model):
    _name = 'mk.test.question'
    _description = 'Subjects Pages Configuration'

    question_id = fields.Many2one('mk.test.line', string='Question', ondelete='cascade')
    from_surah = fields.Many2one('mk.surah', string='From: Surah', ondelete='restrict')
    from_verse = fields.Many2one('mk.surah.verses', string='Verse', ondelete='restrict')
    to_surah = fields.Many2one('mk.surah', string='To: Surah', ondelete='restrict')
    to_verse = fields.Many2one('mk.surah.verses', string='Verse', ondelete='restrict')
    mistake = fields.Integer('Mistaks', compute='amount_mistake', store=True)
    quest_mistake_ids = fields.One2many('mk.question.mistake', 'mistake_id', string='Question Mistake')

    # @api.multi
    @api.depends('quest_mistake_ids')
    def amount_mistake(self):
        total = 0
        for rec in self:
            for line in rec.quest_mistake_ids:
                total += (line.number_mistake * line.name_mistake_id.degree_deduct)
            rec.mistake = total


class mk_question_mistake(models.Model):
    _name = 'mk.question.mistake'
    _description = 'Description'

    mistake_id = fields.Many2one('mk.test.question', string='Mistake Details', ondelete='cascade')
    name_mistake_id = fields.Many2one('mk.test.error', string='Error')
    number_mistake = fields.Integer('Number of Error')
#endregion