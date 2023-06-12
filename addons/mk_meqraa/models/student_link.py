# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import Warning, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.addons.queue_job.job import job
import logging
_logger = logging.getLogger(__name__)


class link_student(models.Model):
    _inherit = 'mk.link'
    
    riwaya             = fields.Selection(related='student_id.riwaya', string="Riwaya")
    khota_type         = fields.Selection(related='student_id.khota_type', string='Khota')
    is_episode_meqraa  = fields.Boolean(compute='get_is_episode_meqraa', store=True)

    @api.depends('episode_id')
    def get_is_episode_meqraa(self):
        for rec in self:
            rec.is_episode_meqraa = rec.episode_id.is_episode_meqraa

    @api.onchange('surah_from_mem_id','page_id')
    def onchange_surah_qty_memorize(self):
        context = self.env.context
        if 'default_program_id' not in context:
            surah_from_mem_id = self.surah_from_mem_id.id
            qty_mem_id = self.page_id.id
            aya_ids = []
            start_pt_ids = []
            if surah_from_mem_id and qty_mem_id:
                start_pts = self.env['mk.subject.page'].search([('subject_page_id','=',qty_mem_id),
                                                                ('from_surah','=',surah_from_mem_id)])
                            
                for start_pt in start_pts:
                    start_pt_ids += [start_pt.id]
                    aya_ids += [start_pt.from_verse.id]
            
            self.aya_from_mem_id = False
            self.save_start_point = False
            
            return {'domain':{'aya_from_mem_id': [('id', 'in', aya_ids)],
                              'save_start_point': [('id', 'in', start_pt_ids)]}}
                

    @api.onchange('program_type')
    def onchange_program_type(self):
        context = self.env.context
        if 'default_program_id' not in context:
            self.program_id = False
            self.approache = False 
    
    @api.onchange('program_id')
    def onchange_pgm(self):
        context = self.env.context
        if 'default_approache' not in context:

            self.page_id = False   
            self.surah_from_mem_id = False
            self.memory_direction = False
            
            self.qty_review_id = False
            self.surah_from_rev_id = False
            self.review_direction = False
            
            self.qty_read_id = False
            self.surah_from_read_id = False
            self.read_direction = False
     
    @api.onchange('memory_direction')
    def onchange_memory_direction(self):
        context = self.env.context
        if 'default_surah_from_mem_id' not in context:
            self.page_id = False   
            self.surah_from_mem_id = False
        else:
            # if self.memory_direction and self.khota_type == 'khota_one_year':
            #     page = self.env['mk.memorize.method'].search([('name', '=', 'مقرر صفحة واحدة'), ('direction', '=', self.memory_direction)])
            #     self.page_id = page.id
            # if self.memory_direction and self.khota_type == 'khota_two_year':
            #     page = self.env['mk.memorize.method'].search([('name', '=','مقرر نصف صفحة'), ('direction', '=', self.memory_direction)])
            #     self.page_id = page.id
            # if self.memory_direction and self.khota_type == 'khota_three_year':
            #     page = self.env['mk.memorize.method'].search([('name', '=','مقرر صغحة وثلاثة ارباع'), ('direction', '=', self.memory_direction)])
            #     self.page_id = page.id
            if self.surah_from_mem_id and self.page_id:
                start_pts = self.env['mk.subject.page'].search([('subject_page_id','=',self.page_id.id), ('from_surah','=',self.surah_from_mem_id.id)], limit=1)
                self.aya_from_mem_id = start_pts.from_verse.id
    
    @api.one
    def mq_action_accept(self):
        episode = self.episode_id
        if episode.teacher_id:
            self.create_mq_student_preparation()
            # self.with_delay(eta=60*2).create_mq_student_preparation()
            self.write({'state': 'accept'})
            has_link = self.env[('mk.link')].search([('id', '!=', self.id), ('student_id', '=', self.student_id.id)], limit=1)
            if not has_link:
                self.student_id.send_passwd()
            return True

        else:
            raise Warning(_('عذرا ! لابد من اختيار معلم للحلقة أولا'))

    def create_mq_student_preparation(self):
        episode = self.episode_id
        episode_id = episode.id
        episode_name = episode.name

        student = self.student_id
        student_name = student.display_name

        link_id = self.id

        program_type = self.program_type
        program = self.program_id
        program_id = program.id
        approach = self.approache

        if not approach:
            msg = 'يجب تحديد المنهج بالنسبة للطالب' + ' "' + student_name + '" ' + ' ' + 'في حلقة' + ' ' + episode_name + '" ' + '!'
            raise ValidationError(msg)

        is_memorize = self.is_memorize
        start_memor = ((program_type == 'open') and self.save_start_point) or False
        if is_memorize and not start_memor and program_type != 'close':
            msg = 'يجب تحديد نقطة بداية الحفظ بالنسبة للطالب' + ' "' + student_name + '" ' + ' ' + 'في حلقة' + ' ' + episode_name + '" ' + '!'
            raise ValidationError(msg)

        subject_memor_id = start_memor and start_memor.subject_page_id.id or False
        last_memor = (subject_memor_id and self.env['mk.subject.page'].search([('subject_page_id', '=', subject_memor_id)], order="order desc", limit=1)) or False
        last_memor_order = last_memor and last_memor.order or False
        nbr_memor = approach.lessons_memorize

        is_big_review = self.is_big_review
        start_review = ((program_type == 'open') and self.start_point) or False
        if is_big_review and not start_review and program_type != 'close':
            msg = 'يجب تحديد نقطة بداية المراجعة الكبرى بالنسبة للطالب' + ' "' + student_name + '" ' + ' ' + 'في حلقة' + ' ' + episode_name + '" ' + '!'
            raise ValidationError(msg)

        if is_big_review and not start_review and program_type != 'close':
            msg = 'يجب تحديد نقطة بداية التلاوة بالنسبة للطالب' + ' "' + student_name + '" ' + ' ' + 'في حلقة' + ' ' + episode_name + '" ' + '!'
            raise ValidationError(msg)

        memor_close_sbjs = ((program_type == 'close') and approach.listen_ids) or []
        start_subject_memor = memor_close_sbjs and memor_close_sbjs[0] or start_memor

        start_date = self.registeration_date
        start_date = datetime.strptime(start_date, "%Y-%m-%d")

        end_date = start_date + relativedelta(years=20)

        student_days = []
        if self.student_id.days_recitation == 'recitation1':
            student_days = [5, 0, 2]
        if self.student_id.days_recitation == 'recitation2':
            student_days = [6, 1, 3]

        list_days_vacation = []
        vacations = self.env['mq.annual.vacation'].search([])
        for vac in vacations:
            date_from_vacation = vac.date_from
            date_from_vacation = datetime.strptime(date_from_vacation, "%Y-%m-%d")

            date_end_vacation = vac.date_to
            date_end_vacation = datetime.strptime(date_end_vacation, "%Y-%m-%d")
            while date_from_vacation <= date_end_vacation:
                if date_from_vacation not in list_days_vacation:
                    list_days_vacation.append(date_from_vacation)
                date_from_vacation = date_from_vacation + relativedelta(days=1)

        vals_prepa = {'name': episode.teacher_id.id,
                      'prepare_date': start_date,
                      'link_id':      link_id,
                      'program_id':   program_id,
                      'stage_pre_id': episode_id,
                      'is_meqraa_student': True,
                      }

        memor_pages = []
        # list of all exist session
        khota_type = student.khota_type
        if khota_type == "khota_one_year":
            limit_nbr_session = 370
        elif khota_type == "khota_two_year":
            limit_nbr_session = 740
        else:
            limit_nbr_session = 1110
        session_obj = self.env['mq.session']
        session_bbb = session_obj.search([('episode_id','=',episode_id)], limit=limit_nbr_session)
        list_session_datetime = {}
        for session in session_bbb:
            session_datetime = datetime.strptime(session.start_date,'%Y-%m-%d')
            session_datetime = session_datetime.date()
            list_session_datetime.update({session_datetime: session.id})

        i = 1
        end = True
        nbr_days = (end_date - start_date).days + 1
        for d in range(nbr_days):
            date_listen = start_date + timedelta(d)
            if date_listen.weekday() not in student_days or date_listen in list_days_vacation:
                continue

            if is_memorize:
                if start_memor:
                    start_order = start_memor.order
                    end_order = min((start_order + nbr_memor - 1), last_memor_order)
                    end_memor = self.env['mk.subject.page'].search([('subject_page_id', '=', subject_memor_id), ('order', '=', end_order)], limit=1)
                    memor_pages += [self.get_listen_line(i, date_listen.date(), start_memor, end_memor, 'listen', link_id,(start_memor.is_test or end_memor.is_test))]
                    memor_pages.write({'is_meqraa_student': True})
                    start_memor = self.env['mk.subject.page'].search([('subject_page_id', '=', subject_memor_id),
                                                                      ('order', '=', (end_order + 1))], limit=1)
                    end = False

                    # add session_id for preparation if exist or create a new session
                    session = session_obj.search([('episode_id', '=', episode_id),
                                                  ('start_date', '=', date_listen.date())], limit=1)
                    if not session:
                        session = session_bbb.create({'episode_id': episode_id,
                                                      'teacher_id': episode.teacher_id.id,
                                                      'start_date': date_listen})

                    session.write({'student_ids': [(0, 0, {'session_id': session.id,
                                                           'mk_link': link_id})]})

            i += 1
            if end:
                break
            end = True

        history = []
        if is_memorize:
            is_min_review = False
            is_big_review = False
            is_tlawa = False
            history = [self.get_history_line(start_date, is_memorize, is_min_review, is_big_review, is_tlawa,
                                             start_subject_memor, self.memory_direction, program_id, approach.id)]
            vals_prepa.update({'std_save_ids': memor_pages})

        vals_prepa.update({'history_ids': history})

        prepa = self.env['mk.student.prepare'].sudo().create(vals_prepa)
        self.preparation_id = prepa.id

    @api.model
    def update_page_id_student_meqraa_link_cron(self):
        meqraa_students = self.env['mk.student.register'].search([('is_student_meqraa', '=', True),])
        total = len(meqraa_students)
        i = 0
        j = 0
        for student in meqraa_students :
            link = self.env['mk.link'].search([('student_id', '=', student.id)], limit=1)

            if link and not link.page_id:
                khota_type = link.student_id.khota_type
                memory_direction = link.memory_direction
                if memory_direction and khota_type == 'khota_one_year':
                    page = self.env['mk.memorize.method'].search([('name', '=', 'مقرر صفحة واحدة'), ('direction', '=', memory_direction)])
                    page_id = page.id
                if memory_direction and khota_type == 'khota_two_year':
                    page = self.env['mk.memorize.method'].search([('name', '=','مقرر نصف صفحة'), ('direction', '=', memory_direction)])
                    page_id = page.id
                if memory_direction and khota_type == 'khota_three_year':
                    page = self.env['mk.memorize.method'].search([('name', '=','مقرر صغحة وثلاثة ارباع'), ('direction', '=', memory_direction)])
                    page_id = page.id
                link.sudo().write({'page_id': page_id})

                j+= 1
            i += 1