#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date

import logging
_logger = logging.getLogger(__name__)


class Mkepisode(models.Model):
    _name = 'mk.episode'
    _inherit = ['mail.thread']
    rec_name = 'display_name'
    _order = 'create_date desc'
        
    # @api.one
    @api.depends('name','selected_period')
    def _display_name(self):
        name = ''
        selected_period = self.selected_period
        
        if selected_period == 'subh':
            name = 'الصبح'
            
        elif selected_period == 'zuhr':
            name = 'الظهر'
            
        elif selected_period == 'aasr':
            name = 'العصر'
            
        elif selected_period == 'magrib':
            name = 'المغرب'
            
        elif selected_period == 'esha':
            name = 'العشاء'

        self.display_name = str(str(self.name) + " - " + "( "+name+" )")  
            
    @api.model
    def get_year_default(self):
        year = self.env['mk.study.year'].search([('is_default','=',True)], limit=1)
        return year and year.id or False

    @api.model
    def get_study_class(self):
        study_class = self.env['mk.study.class'].search([('study_year_id', '=', self.get_year_default()),
                                                         ('is_default', '=', True)], limit=1)
        return study_class and study_class.id or False
    
    @api.model
    def get_period(self):
        period = self.env['mk.periods'].search([], limit=1)
        return period and period.id or False


    name                = fields.Char('Name', track_visibility='onchange')
    mosque_id           = fields.Many2one('mk.mosque',     string='Masjed',        track_visibility='onchange')
    academic_id         = fields.Many2one('mk.study.year', string='Academic Year', required=True, default=get_year_default, copy=False, track_visibility='onchange')
    error_register      = fields.Selection([('total', 'Overall'), 
                                            ('detailed', 'Detailed')], string='Error register', track_visibility='onchange')
    study_class_id      = fields.Many2one('mk.study.class', string='Study class', default=get_study_class, domain=[('is_default', '=', True)], copy=False, track_visibility='onchange')
    is_study_class_default = fields.Boolean(related='study_class_id.is_default',store=True)
    color               = fields.Integer('Color   Index', default=12)
    teacher_id          = fields.Many2one('hr.employee', string='Teacher',    domain=[('category2','=','teacher')], index=True, track_visibility='onchange')
    teacher_assist_id   = fields.Many2one('hr.employee', string='معلم مساعد', domain=[('category2','=','teacher')], track_visibility='onchange')
    send_time           = fields.Float('Send time', default=0.0, digits=(16, 2))
    episode_season      = fields.Selection([('normal' , 'Normal'),
                                            ('seasonal' , 'Seasonal')], string="Episode Season", default='normal', track_visibility='onchange')
    episode_season_type = fields.Many2one('mk.episode.season',          string="Episode Season types",             track_visibility='onchange')
    state               = fields.Selection([('draft',  'Draft'),
                                            ('accept', 'Accepted'),
                                            ('done',   'مجمدة'), 
                                            ('reject', 'Rejected')], string='الحالة', default='draft',     track_visibility='onchange')
    parent_episode      = fields.Many2one("mk.episode.master",       string="parent episode", copy=False, track_visibility='onchange')
    display_name        = fields.Char(compute="_display_name",       string="Name", store=True)
    selected_period     = fields.Selection([('subh', 'subh'), 
                                            ('zuhr', 'zuhr'),
                                            ('aasr','aasr'),
                                            ('magrib','magrib'),
                                            ('esha','esha')], string='period', track_visibility='onchange')
    start_date          = fields.Date('Start date', copy=False,                track_visibility='onchange')
    active              = fields.Boolean('Active', default=True, copy=False,   track_visibility='onchange')
    women_or_men        = fields.Selection([('men', 'men episode'), 
                                            ('women', 'women episode')], string='women or men', required=True, default='men', track_visibility='onchange')
    end_date            = fields.Date('End date', copy=False, track_visibility='onchange')
    episode_work        = fields.Many2one('mk.epsoide.works',string='episode work',                 track_visibility='onchange')
    episode_type        = fields.Many2one('mk.episode_type', string='Episode Type', required=False, track_visibility='onchange')
    #old version not used
    interval            = fields.Selection([('morning',   'Morning'), 
                                            ('doha',      'Doha'), 
                                            ('afternoon', 'Afternoon'),
                                            ('aasr',      'After Aasr'),
                                            ('maghrib',   'After Maghrib'), 
                                            ('isha',      'After Isha')], string='Interval')
    level_ids           = fields.Many2many('mk.level', 'episode_level_rel', 'episode_id', 'level_id', string='level')
    job_ids             = fields.Many2many('mk.job',   string='Targeted jobs ',)
    grade_ids           = fields.Many2many('mk.grade', string='Grades', domain=[('is_episode','=',True)])
    #program_ids=fields.Many2many(string= 'Programs',comodel_name='mk.programs')    
    company_id          = fields.Many2one('res.company',    string='company', default=lambda self: self.env.user.company_id)
    period_id           = fields.Many2one('mk.periods',     string='Period', required=False, default=get_period, track_visibility='onchange')
    test_time           = fields.Char(compute='_test_time', string='Test Time', store=True)
    subh                = fields.Boolean('Subh',   track_visibility='onchange')
    zuhr                = fields.Boolean('Zuhr',   track_visibility='onchange')
    aasr                = fields.Boolean('Aasr',   track_visibility='onchange')
    magrib              = fields.Boolean('Magrib', track_visibility='onchange')
    esha                = fields.Boolean('Esha',   track_visibility='onchange')
    
    period_subh         = fields.Char('Subh',   track_visibility='onchange')
    period_zuhr         = fields.Char('Zuhr',   track_visibility='onchange')
    period_aasr         = fields.Char('Aasr',   track_visibility='onchange')
    period_magrib       = fields.Char('Magrib', track_visibility='onchange')
    period_esha         = fields.Char('Esha',   track_visibility='onchange')
    
    episode_days        = fields.Many2many('mk.work.days', string='work days', required=True)


    @api.model
    def student_episodes(self, student_id):
        try:
            student_id = int(student_id)
        except:
            pass

        query_string = ''' 
               select e.id, e.display_name, e.name, e.selected_period as period, l.id link_id
               from mk_episode e left join mk_link l on l.episode_id=e.id
               where l.student_id={} and 
               l.state='accept' and
               e.state='accept' and 
               e.active=True;
               '''.format(student_id)
        self.env.cr.execute(query_string)
        student_episodes = self.env.cr.dictfetchall()
        return student_episodes

    @api.model
    def best_episodes(self):
        query_string = ''' 
                 select rate, name display_name
                 from get_top_five_episode
                 order by id desc
                 limit 5;
                 '''
        self.env.cr.execute(query_string)
        best_episodes = self.env.cr.dictfetchall()
        return best_episodes

    @api.model
    def teacher_mobile_episodes(self, teacher_id):
        try:
            teacher_id = int(teacher_id)
        except:
            pass

        query_string = ''' 
               select e.id, e.display_name episode_period, e.name episode, e.state, m.name mosque, c.name city
               from mk_episode e left join mk_mosque m on m.id=e.mosque_id
                                 left join res_country_state c on c.id=m.district_id
               where teacher_id={} and e.state <> 'reject' and 
               e.active=True;
               '''.format(teacher_id)

        self.env.cr.execute(query_string)
        teacher_episodes = self.env.cr.dictfetchall()
        return teacher_episodes

    # @api.multi
    def name_get(self):
        result = []
        
        for rec in self:
            name = ''
            selected_period = rec.selected_period
            
            if selected_period == 'subh':
                name = 'الصبح'
                
            elif selected_period == 'zuhr':
                name = 'الظهر'
                
            elif selected_period == 'aasr':
                name = 'العصر'
                
            elif selected_period == 'magrib':
                name = 'المغرب'
                
            elif selected_period == 'esha':
                name = 'العشاء'
                
            result.append((rec.id, str(str(rec.name) + " - " + "( " + name + " )")))
            
        return result
    
    @api.model
    def create(self, vals):
        study_class_id = vals.get('study_class_id', False)
        parent_episode = vals.get('parent_episode', False)
        is_episode_meqraa = vals.get('is_episode_meqraa', False)
        mosque_id = vals.get('mosque_id', False)
        # if not parent_episode and not is_episode_meqraa:
        #     raise ValidationError('لا يمكنك انشاء فترة دون تحديد الحلقة')
        if not mosque_id and not is_episode_meqraa:
            raise ValidationError('لا يمكنك انشاء فترة دون تحديد المسجد')
        if study_class_id:
            study_class = False
            start_date = vals.get('start_date', False)
            end_date = vals.get('end_date', False)
            
            if not start_date:
                study_class = self.env['mk.study.class'].browse(study_class_id)
                vals.update({'start_date': study_class.start_date})
                
            if not end_date:
                if not study_class:
                    study_class = self.env['mk.study.class'].browse(study_class_id)
                vals.update({'end_date': study_class.end_date})
        
        return super(Mkepisode, self).create(vals)

    # @api.multi
    def unlink(self):
        for rec in self:
#             prepare_ids = self.env['mk.student.prepare'].search([('stage_pre_id','=',rec.id),
#                                                                  '|', ('active', '=', True),
#                                                                       ('active', '=', False)])
#             if prepare_ids:
#                 prepare_ids.unlink()

            links = self.env['mk.link'].search([('episode_id','=',rec.id)])

            if links:
                links.unlink()                  
            sessions = self.env['mq.session'].search([('episode_id', '=', rec.id)])

            if sessions:
                sessions.unlink()

            selected_period = rec.selected_period
            
            if rec.parent_episode:     
                if selected_period == 'subh':
                    rec.parent_episode.subh = False
                          
                elif selected_period == 'zuhr':
                    rec.parent_episode.zuhr = False
                      
                elif selected_period == 'aasr':
                    rec.parent_episode.aasr = False
                    
                elif selected_period == 'magrib':
                    rec.parent_episode.magrib = False
                    
                elif selected_period == 'esha':
                    rec.parent_episode.esha = False
        res = super(Mkepisode, self).unlink()
        return res

    @api.depends('period_id','subh','zuhr','aasr','magrib','esha')
    def _test_time(self):
        for rec in self:
            time = None
            period = rec.period_id
            if period:
                if rec.subh:
                    time = 'from ' +  str(period.subh_period_from) +' ' +'to ' + str(period.subh_period_to)

                elif rec.zuhr:
                    time = 'from ' +  str(period.zuhr_period_from) +' ' +'to ' + str(period.zuhr_period_to)

                elif rec.aasr:
                    time = 'from ' +  str(period.aasr_period_from) +' ' +'to ' + str(period.aasr_period_to)

                elif rec.magrib:
                    time = 'from ' +  str(period.magrib_period_from) +' ' +'to ' + str(period.magrib_period_to)

                elif rec.esha:
                    time = 'from ' +  str(period.esha_period_from) +' ' +'to ' + str(period.esha_period_to)

                rec.test_time = time

    @api.onchange('mosque_id')
    def onchange_mosque(self):
        teacher_ids = []
        if self.mosque_id:
            teacher_ids = (self.env['hr.employee'].search([('mosque_id','=',self.mosque_id.id)])).ids
            
        return {'domain': {'teacher_id': [('id','in',teacher_ids)]}}

    @api.onchange('academic_id')
    def onchange_academic_year(self):
        study_class_ids = []
        for rec in self.academic_id.class_ids:
            study_class_ids.append(rec.id)
            
        return {'domain': {'study_class_id': [('id','in',study_class_ids)]}} 
        
    # @api.one
    @api.constrains('teacher_id','teacher_assist_id','study_class_id','selected_period')
    def teacher_constrain(self):#TO DO check Dates
        domain = [('id','!=',self.id),
                  ('selected_period','=',self.selected_period),
                  ('study_class_id','=',self.study_class_id.id),]
        teacher_id = self.teacher_id.id
        if teacher_id and not self.is_online:
            domain1 = ['|',('teacher_id','=',teacher_id),
                           ('teacher_assist_id','=',teacher_id)]

            episode = self.env['mk.episode'].search(domain+domain1, limit=1)

            if episode and not self.is_episode_meqraa :
                msg = 'المعلم يدرس في نفس الفترة في حلقة' + ' "' + episode.name + '" ' + 'في مسجد' + ' "' + episode.mosque_id.name + '" ' + ' !'
                raise ValidationError(msg)

        teacher_assist_id = self.teacher_assist_id.id
        if teacher_assist_id and not self.is_online:
            domain2 = ['|',('teacher_id','=',teacher_assist_id),
                           ('teacher_assist_id','=',teacher_assist_id)]

            episode = self.env['mk.episode'].search(domain+domain2, limit=1)

            if episode and not self.is_episode_meqraa:
                msg = 'المعلم المساعد يدرس في نفس الفترة في حلقة' + ' "' + episode.name + '" ' + 'في مسجد' + ' "' + episode.mosque_id.name + '" ' + ' !'
                raise ValidationError(msg)
        
    # @api.one
    @api.constrains('episode_days')
    def _check_days(self):
        if len(self.episode_days) == 0:
            raise ValidationError(_('عذرا ! أدخل أيام الحلقة'))


    @api.model
    def episode_with_no_students_1444_c1(self):
        master_eps = self.env['mk.episode.master'].search([('study_class_id', '=', 109),
                                                           ('state', '=', 'active')])
        total = len(master_eps)
        i = 0
        for master_ep in master_eps:
            i+= 1
            episodes = master_ep.episode_ids
            nbr_episodes = len(episodes.ids)
            if nbr_episodes == 0:
                master_ep.action_done()
                master_ep.unlink()
            if nbr_episodes == 1:
                episode_0 = master_ep.episode_ids[0]
                episode_links = episode_0.link_ids
                if len(episode_links.ids) == 0:
                    master_ep.action_done()
                    master_ep.unlink()

            else:
                for episod in episodes:
                    if len(episod.link_ids.ids) == 0:
                        episod.action_done()
                        episod.unlink()

    @api.model
    def episode_with_no_parent(self):
        episodes = self.env['mk.episode'].search([('parent_episode', '=', False),
                                                  ('is_episode_meqraa', '=', False)], order="id asc")
        nbr_eps = len(episodes)
        nbr_unl = 0
        i = 0
        for episod in episodes:
            i += 1
            if len(episod.link_ids.ids) == 0:
                episod.unlink()
                nbr_unl+=1

            else:
                links = []
                for link in episod.link_ids:
                    links.append(link.id)

                student_test_session = self.env['student.test.session'].search([('student_id', 'in', links),
                                                                                 ('state', '!=', 'cancel')], limit=1)
                if student_test_session:
                    continue

                episod.unlink()
                nbr_unl += 1

    # @api.one
    @api.constrains('study_class_id','start_date','end_date')
    def check_dates(self):
        study_class = self.study_class_id
        start_study_class = study_class.start_date
        start_date = self.start_date
        if not self.is_episode_meqraa:
            if start_date and start_study_class and start_date < start_study_class:
                msg = 'عذرا، تاريخ بداية الحلقة يجب أن يكون بعد تاريخ بداية الفصل الدراسي' + ' ! '
                raise ValidationError(msg)

            end_study_class = study_class.end_date
            end_date = self.end_date
            if end_date and end_study_class and end_date > end_study_class:
                msg = 'عذرا، تاريخ نهاية الحلقة يجب أن يكون قبل تاريخ نهاية الفصل الدراسي' + ' ! '
                raise ValidationError(msg)

            if start_date and end_date and start_date > end_date:
                msg = 'عذرا، تاريخ بداية الحلقة يجب أن يكون قبل تاريخ نهايتها' + ' ! '
                raise ValidationError(msg)
    
    @api.onchange('period_id')
    def period_onchange(self):
        if self.period_id.subh_period:
            self.period_subh = 's'
            
        if self.period_id.zuhr_period:
            self.period_zuhr = 'z'
            
        if self.period_id.aasr_period:
            self.period_aasr = 'a'
             
        if self.period_id.magrib_period:
            self.period_magrib = 'm'
            
        if self.period_id.esha_period:
            self.period_esha = 'e'
        
    # @api.one
    def action_done(self):
        self.state = 'done'
        self.active = False
        parent_episode = self.parent_episode
        selected_period = self.selected_period
        if parent_episode:
            if selected_period == 'subh':
                parent_episode.subh_flag = False
                parent_episode.subh = False
            elif selected_period == 'zuhr':
                parent_episode.zuhr_flag = False
                parent_episode.zuhr = False
            elif selected_period == 'aasr':
                parent_episode.aasr_flag = False
                parent_episode.aasr = False
            elif selected_period == 'magrib':
                parent_episode.magrib_flag = False
                parent_episode.magrib = False
            elif selected_period == 'esha':
                parent_episode.esha_flag = False
                parent_episode.esha = False

    # @api.one
    def action_reopen(self):
        if self.study_class_id.end_date < fields.Datetime.now() and not self.is_episode_meqraa:
            msg = 'لا يمكن إعادة تفعيل الحلقة بعد نهاية الفصل' + ' !'
            raise ValidationError(msg)
        selected_period = self.selected_period
        parent_episode = self.parent_episode
        exist_episode =  self.env['mk.episode'].search([('parent_episode', '=', parent_episode.id),
                                                        ('selected_period', '=', self.selected_period),
                                                        ('id', '!=', self.id)], limit=1)
        if exist_episode and not self.is_episode_meqraa:
            msg = 'عذرا لا يمكنك اعادة تفعيل الفترة, توجد حلقة أخرى بنفس الفترة' + ' !'
            raise ValidationError(msg)
        else:
            self.state = 'accept'
            self.active = True
            if selected_period == 'subh':
                parent_episode.subh_flag = True
                parent_episode.subh = True
            elif selected_period == 'zuhr':
                parent_episode.zuhr_flag = True
                parent_episode.zuhr = True
            elif selected_period == 'aasr':
                parent_episode.aasr_flag = True
                parent_episode.aasr = True
            elif selected_period == 'magrib':
                parent_episode.magrib_flag = True
                parent_episode.magrib = True
            elif selected_period == 'esha':
                parent_episode.esha_flag = True
                parent_episode.esha = True

    @api.model
    def _notify_for_upcoming_episode(self):
        tomorrow_date = (date.today() + timedelta(days=1))
        upcoming_episodes = self.env['mk.episode'].search([('start_date', '=', tomorrow_date),
                                                           ('state', 'not in', ['done', 'reject'])])
        for rec in upcoming_episodes:
            responsible = rec.mosque_id.responsible_id.user_id.partner_id
            teacher = rec.teacher_id.user_id.partner_id
            if responsible:
                notif = self.env['mail.message'].create({'message_type': "notification",
                                                         "subtype": self.env.ref("mail.mt_comment").id,
                                                         'body': "نعلمكم أن الحلقة ستبدأ غدا",
                                                         'subject': "بدء حلقة",
                                                         'needaction_partner_ids': [(4, responsible.id)],
                                                         'model': self._name,
                                                         'res_id': rec.id})
            if teacher:
                notif = self.env['mail.message'].create({'message_type': "notification",
                                                        "subtype": self.env.ref("mail.mt_comment").id,
                                                        'body': "نعلمكم أن الحلقة ستبدأ غدا",
                                                        'subject': "بدء حلقة",
                                                        'needaction_partner_ids': [(4, teacher.id)],
                                                        'model': self._name,
                                                        'res_id': rec.id})

    @api.model
    def get_episode_count(self):
        count = 0
        number_accepted_episodes = self.env['mk.episode'].search([('state', '=', 'accept'),
                                                                  '|', ('active', '=', True),
                                                                       ('active', '=', False)])
        if number_accepted_episodes:
            count = len(number_accepted_episodes)
        return count

    @api.model
    def get_episodes_teacher(self, teacher_id):
        try:
            teacher_id = int(teacher_id)
        except:
            pass

        episodes = self.env['mk.episode'].search([('teacher_id', '=', teacher_id),
                                                  ('state', '=', 'accept'),
                                                  '|', ('active', '=', True),
                                                       ('active', '=', False)])
        item_list = []
        if episodes:
            for episode in episodes:
                item_list.append({'id': episode.id,
                                  'name': episode.name})
        return item_list


class mk_season_type(models.Model):
    _name = 'mk.episode.season'
    _inherit = ['mail.thread']
    _rec_name = 'name'

    active = fields.Boolean(default=True, track_visibility='onchange')
    name   = fields.Char("Name",          track_visibility='onchange')
