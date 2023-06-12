# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)


class mk_student_register(models.Model):
    _inherit = 'mk.student.register'
    
    is_student_meqraa   = fields.Boolean(string='Is student Meqraa', default=False)
    number_parts_saved  = fields.Integer(string='The number of parts you save')
    business_career     = fields.Char(string='Your business career')
    riwaya              = fields.Selection([('riwaya1',   u'حفص عن عاصم الكوفي'), 
                                           ('riwaya2', u'قالون عن نافع المدني'),
                                           ('riwaya3', u'ورش عن نافع المدني')], string='Riwaya')
    
    arabic_lang_level   = fields.Selection([('good', 'Good'),
                                           ('medium', 'Medium'),
                                           ('low', 'Low')], string='Arabic language level')
    
    khota_type          = fields.Selection([('khota_one_year', 'Memorizing Quran within one year'),
                                           ('khota_two_year', 'Memorizing Quran within two years'),
                                           ('khota_three_year', 'Memorizing Quran within three years')], string='Khota')
    
    days_recitation     = fields.Selection([('recitation1', 'Saturday/Monday/Wednesday'),
                                            ('recitation2', 'Sunday/Tuesday/Thursday')], string='Days of recitation')
    
    memory_direction    = fields.Selection([('up',   'من الفاتحة للناس'), 
                                           ('down', 'من الناس للفاتحة')],  string='المسار')
    
    @api.multi
    def action_request_meqraa(self):
        view_id = self.env.ref('mk_meqraa.view_mq_student_link_form').id
        program_id = self.env.ref('mk_meqraa.program_meqraa').id 
        student_request = self.env['mk.link'].search([('student_id','=',self.id)], limit=1)
        if self.khota_type=='khota_one_year':
            approache_id = self.env.ref('mk_meqraa.approache_meqraa1').id
            page = self.env['mk.memorize.method'].search([('name', '=', 'مقرر صفحة واحدة'), ('direction', '=', self.memory_direction)]).id
        elif self.khota_type == 'khota_two_year':
            approache_id = self.env.ref('mk_meqraa.approache_meqraa2').id
            page = self.env['mk.memorize.method'].search([('name', '=', 'مقرر نصف صفحة'), ('direction', '=', self.memory_direction)]).id
        elif  self.khota_type == 'khota_three_year':
            approache_id = self.env.ref('mk_meqraa.approache_meqraa3').id
            page = self.env['mk.memorize.method'].search([('name', '=', 'مقرر صغحة وثلاثة ارباع'), ('direction', '=', self.memory_direction)]).id

        if self.memory_direction == 'up':
            surah_id = 229
        if self.memory_direction=='down':         
            surah_id = 342

        vals = {'name':      'تصديق طلب الانضمام',
                'view_type': 'form',
                'view_mode': 'tree',
                'views' :    [(view_id,'form')],
                'res_model': 'mk.link',
                'view_id':   view_id,
                'type':      'ir.actions.act_window',
                'res_id':    student_request.id,
                'target':    'new',}
        if not student_request:
            vals.update({'context': {'default_student_id': self.id, 
                                     'default_program_id': program_id,
                                     'default_approache': approache_id,
                                     'default_memory_direction': self.memory_direction,
                                     'default_page_id': page,
                                     'default_surah_from_mem_id': surah_id,
                                     'default_program_type' : 'open'}})
        return vals

    @api.one
    def write(self, vals):
        if 'active' in vals and self.is_student_meqraa:
            active = vals.get('active')
            if active == False and not self.env.user._is_superuser():
                msg = ' لا يمكنك أرشفة طالب المقرأة' + '!'
                raise ValidationError(msg)
            else:
                return super(mk_student_register, self).write(vals)
        else:
            return super(mk_student_register, self).write(vals)

    @api.model
    def create_meqraa_student(self, data):
        if 'mosque_id' in data:
            mosque_id = data['mosque_id']
            data['is_online_student'] = True
            data['mosq_id'] = int(mosque_id)
            mosque = self.env['mk.mosque'].sudo().search([('id', '=', int(mosque_id))], limit=1)
            data['district_id'] = mosque.district_id.id
        else:
            data['is_student_meqraa'] = True
        nationality = data['nationality']
        data['country_id'] = int(nationality)
        data.pop('nationality')
        meqraa_student = self.env['mk.student.register'].sudo().create(data)
        return meqraa_student.id

    @api.model
    def get_mosq_mobile(self, data):
        phone = False
        if 'mosque_id' in data:
            mosque_id = data['mosque_id']
            mosque = self.env['mk.mosque'].sudo().search([('id', '=', int(mosque_id))], limit=1)
            phone = mosque.phone
        return phone


    @api.multi
    def action_student_request_multi(self):
        student_id = self.env['mk.student.register'].browse(self.env.context.get('active_id'))
        meqraa_assign_episode_form = self.env.ref('mk_meqraa.view_meqraa_student_request_multi_form')
        is_meqraa = student_id.is_student_meqraa
        if is_meqraa:
            return {
                'name': _('تنسيب لحلقة مقرأة'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mk.student.internal_transfer',
                'views': [(meqraa_assign_episode_form.id, 'form')],
                'view_id': meqraa_assign_episode_form.id,
                'target': 'new',
                'context': {'default_student_ids': self.env.context.get('active_ids', []),
                            'default_type_order': 'assign'}
            }
        else:
            return super(mk_student_register, self).action_student_request_multi()

class InternalTransferInherit(models.TransientModel):
    _inherit = 'mk.student.internal_transfer'

    @api.onchange('student_ids', 'episode_id', 'msg_error', 'msg_error2')
    def onchange_episode_meqraa(self):
        episode = self.episode_id
        student_ids = self.student_ids
        episode_riwaya = episode.riwaya
        episode_days_recitation = episode.days_recitation
        msg_error = ''
        if student_ids and student_ids[0].is_student_meqraa:
            assign_msg_error = self.msg_error
            assign_msg_error2 = self.msg_error2

            self.program_type = ''
            self.program_id = False
            self.approach_id = False
            self.memory_direction = ''
            self.page_id = False
            self.surah_from_mem_id = False
            self.aya_from_mem_id = False

            program_id = False
            approach_id = False
            page_id = False
            khota_type = student_ids[0].khota_type
            days_recitation = student_ids[0].days_recitation
            riwaya = student_ids[0].riwaya
            memory_direction = student_ids[0].memory_direction
            for student in student_ids:
                student_khota_type = student.khota_type
                student_riwaya = student.riwaya
                student_days_recitation = student.days_recitation
                student_memory_direction = student.memory_direction
                if student_riwaya != riwaya:
                    msg_error = 'الطلاب المختارون ليس لديهم نفس الرواية' + ' ' + '!'
                    break
                if student_khota_type != khota_type:
                    msg_error = 'الطلاب المختارون ليس لديهم نفس الخطة' + ' ' + '!'
                    break
                if student_days_recitation != days_recitation:
                    msg_error = 'الطلاب المختارون ليس لديهم نفس أيام التسميع' + ' ' + '!'
                    break
                if student_memory_direction != memory_direction:
                    msg_error = 'الطلاب المختارون ليس لديهم نفس المسار' + ' ' + '!'
                    break
                if episode and episode.is_episode_meqraa:
                    if student_riwaya != episode_riwaya:
                        msg_error = ' رواية الطلاب المختارون تختلف عن رواية الحلقة المحددة' + ' ' + '!'
                        break
                    if student_days_recitation != episode_days_recitation:
                        msg_error = ' أيام تسميع الطلاب المختارون تختلف عن أيام تسميع الحلقة المحددة' + ' ' + '!'
                        break
            vals_value = {'episode_id': episode and episode.id or False,
                          'msg_error2': msg_error}
            if episode and not assign_msg_error and not assign_msg_error2 and not msg_error:
                khota_type = student_ids[0].khota_type

                if khota_type == 'khota_one_year':
                    approach_id = self.env.ref('mk_meqraa.approache_meqraa1').id
                    if memory_direction:
                        page = self.env['mk.memorize.method'].search([('name', '=', 'مقرر صفحة واحدة'), ('direction', '=', memory_direction)])
                        page_id = page.id
                elif khota_type == 'khota_two_year':
                    approach_id = self.env.ref('mk_meqraa.approache_meqraa2').id
                    if memory_direction:
                        page = self.env['mk.memorize.method'].search([('name', '=', 'مقرر نصف صفحة'), ('direction', '=', memory_direction)])
                        page_id = page.id
                elif khota_type == 'khota_three_year':
                    approach_id = self.env.ref('mk_meqraa.approache_meqraa3').id
                    if memory_direction:
                        page = self.env['mk.memorize.method'].search([('name', '=', 'مقرر صغحة وثلاثة ارباع'),('direction', '=', memory_direction)])
                        page_id = page.id
                if memory_direction == 'up':
                    surah_id = 229
                if memory_direction == 'down':
                    surah_id = 342
                subject_page = self.env['mk.subject.page'].search([('subject_page_id','=',page_id),
                                                               ('from_surah','=',surah_id)], limit=1)
                vals_value.update({'program_type': 'open',
                                   'program_id': self.env.ref('mk_meqraa.program_meqraa').id,
                                   'approach_id': approach_id,
                                   'page_id': page_id,
                                   'memory_direction': memory_direction,
                                   'surah_from_mem_id': surah_id,
                                   'aya_from_mem_id': subject_page.from_verse.id})
            return {'value': vals_value}

    @api.multi
    def mq_multi_action_accept(self):
        type_order = self.type_order
        episode = self.episode_id
        student_ids = self.student_ids
        episode_id = episode.id
        episode_name = episode.name

        program_type = self.program_type
        program = self.program_id
        program_id = program.id
        approach = self.approach_id
        start_date = self.registeration_date
        memory_direction = self.memory_direction
        surah_from_mem_id = self.surah_from_mem_id
        aya_from_mem_id = self.aya_from_mem_id
        save_start_point = self.save_start_point

        if not episode.teacher_id:
            raise ValidationError(_('عذرا ! لابد من اختيار معلم للحلقة أولا'))
        else:
            vals = {'year': self.year.id,
                    'registeration_date': self.registeration_date,
                    'episode_id': episode_id,
                    'type_order': type_order,
                    'program_type': program_type,
                    'program_id': program_id,
                    'approache':  approach.id,
                    'memory_direction': memory_direction,
                    'surah_from_mem_id': surah_from_mem_id.id,
                    'aya_from_mem_id': aya_from_mem_id.id,
                    'save_start_point': save_start_point.id,
                    'state': 'accept'}
            if not approach:
                msg = 'يجب تحديد المنهج بالنسبة للطلاب' + 'في حلقة' + ' ' + episode_name + '" ' + '!'
                raise ValidationError(msg)

            if not student_ids:
                msg = 'الرجاء تحديد قائمة الطلاب' + ' ' + '!'
                raise ValidationError(msg)
            else:
                for student in student_ids:
                    vals.update({'student_id': student.id})
                    link_id = self.env['mk.link'].sudo().create(vals)

                    is_memorize = self.is_memorize
                    start_memor = ((program_type == 'open') and self.save_start_point) or False
                    if is_memorize and not start_memor and program_type != 'close':
                        msg = 'يجب تحديد نقطة بداية الحفظ بالنسبة للطلاب' + ' ' + 'في حلقة' + ' ' + episode_name + '" ' + '!'
                        raise ValidationError(msg)

                    subject_memor_id = start_memor and start_memor.subject_page_id.id or False
                    last_memor = (subject_memor_id and self.env['mk.subject.page'].search([('subject_page_id', '=', subject_memor_id)], order="order desc", limit=1)) or False
                    last_memor_order = last_memor and last_memor.order or False
                    nbr_memor = approach.lessons_memorize

                    memor_close_sbjs = ((program_type == 'close') and approach.listen_ids) or []
                    start_subject_memor = memor_close_sbjs and memor_close_sbjs[0] or start_memor

                    start_date = datetime.strptime(str(self.registeration_date), "%Y-%m-%d")

                    end_date = start_date + relativedelta(years=20)

                    student_days = []
                    if student.days_recitation == 'recitation1':
                        student_days = [5, 0, 2]
                    if student.days_recitation == 'recitation2':
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
                                  'link_id': link_id.id,
                                  'program_id': program_id,
                                  'stage_pre_id': episode_id}

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
                    session_bbb = session_obj.search([('episode_id', '=', episode_id)], limit=limit_nbr_session)
                    list_session_datetime = {}
                    for session in session_bbb:
                        session_datetime = datetime.strptime(session.start_date, '%Y-%m-%d')
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
                                memor_pages += [link_id.get_listen_line(i, date_listen.date(), start_memor, end_memor, 'listen',link_id.id, (start_memor.is_test or end_memor.is_test))]
                                start_memor = self.env['mk.subject.page'].search([('subject_page_id', '=', subject_memor_id),
                                                                                  ('order', '=', (end_order + 1))], limit=1)
                                end = False

                                # add session_id for preparation if exist or create a new session
                                session = session_obj.search([('episode_id', '=', episode_id),
                                                              ('start_date', '=', date_listen.date())], limit=1)

                                if not session:
                                    session = session_obj.create({'episode_id': episode_id,
                                                                  'teacher_id': episode.teacher_id.id,
                                                                  'start_date': date_listen,
                                                                  'student_ids': [(0, 0, {'session_id': session.id, 'mk_link': link_id.id})]})
                                else:
                                    session.write({'student_ids': [(0, 0, {'session_id': session.id,
                                                                           'mk_link': link_id.id})]})

                        i += 1
                        if end:
                            break
                        end = True

                    history = []
                    if is_memorize:
                        history += [link_id.get_history_line(start_date, 'm', start_subject_memor, self.memory_direction)]
                        vals_prepa.update({'std_save_ids': memor_pages})

                    vals_prepa.update({'history_ids': history})

                    prepa = self.env['mk.student.prepare'].sudo().create(vals_prepa)
                    self.preparation_id = prepa.id

