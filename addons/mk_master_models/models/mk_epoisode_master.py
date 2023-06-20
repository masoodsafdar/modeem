#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime
import logging
_logger = logging.getLogger(__name__)


class MkepisodeMaster(models.Model):    
    _name = 'mk.episode.master'
    _inherit=['mail.thread','mail.activity.mixin']

    
    @api.model
    def get_year_default(self):
        year = self.env['mk.study.year'].search([('is_default','=',True)], limit=1)
        return year and year.id or False

    @api.model
    def get_study_class(self):
        study_class = self.env['mk.study.class'].search([('study_year_id', '=', self.get_year_default()),
                                                         ('is_default', '=', True)], limit=1)
        return study_class and study_class.id or False         
        
    name             = fields.Char('Name', tracking=True)
    active           = fields.Boolean("Active", default=True, copy=False, tracking=True)
    mosque_id        = fields.Many2one('mk.mosque',      string='Masjed',        tracking=True)
    company_id       = fields.Many2one('res.company',    string='company',       default=lambda self: self.env.user.company_id, tracking=True)
    academic_id      = fields.Many2one('mk.study.year',  string='Academic Year', default=get_year_default, domain=[('is_default', '=', True)], required=True, copy=False, tracking=True)
    study_class_id   = fields.Many2one('mk.study.class', string='Study class',   default=get_study_class,  domain=[('is_default', '=', True)], copy=False, tracking=True)
    state            = fields.Selection([('active',  'مفعلة'), 
                                         ('done',    'مجمدة')], string='الحالة', default='active', tracking=True)
    episode_category = fields.Selection([('course',  'course'), 
                                         ('episode', 'episode')], string='episode category', tracking=True)
    episode_ids      = fields.One2many("mk.episode", "parent_episode", string="periode list")

    subh             = fields.Boolean('Subh',   tracking=True)
    zuhr             = fields.Boolean('Zuhr',   tracking=True)
    aasr             = fields.Boolean('Aasr',   tracking=True)
    magrib           = fields.Boolean('Magrib', tracking=True)
    esha             = fields.Boolean('Esha',   tracking=True)

    subh_flag        = fields.Boolean('Subh',   tracking=True)
    zuhr_flag        = fields.Boolean('Zuhr',   tracking=True)
    aasr_flag        = fields.Boolean('Aasr',   tracking=True)
    magrib_flag      = fields.Boolean('Magrib', tracking=True)
    esha_flag        = fields.Boolean('Esha',   tracking=True)

    @api.model
    def action_done_episode_bf1444(self):
        master_eps = self.env['mk.episode.master'].search([('study_class_id','<=',108),
                                                           ('state','=','active')])
        
        nbr = len(master_eps)

        i = 0

        for master_ep in master_eps:
            i += 1
            master_ep.action_done()
            _logger.info('\n\n +++++++++++++++ %s / %s * \n', i, nbr)
        _logger.info('\n\n +++++++++++++++ END * \n\n')
    
    @api.model
    def episode144_C3(self, id_from):
        master_eps = self.env['mk.episode.master'].search([('study_class_id','=',110),
                                                           ('id', '>', id_from),
                                                           ('state','=','active')], order="id asc", limit=10)
        errs = []
        nbr = len(master_eps)
        _logger.info('\n\n +++++++++ first START %s %s* \n\n', nbr, datetime.datetime.now())
        
        i = 0
        error = 0
        for master_ep in master_eps:
            i += 1
            try:
                master_ep.copy()
                master_ep.action_done()
            except Exception as e:
                _logger.info('\n\n +++++++++ Exception as e : %s\n\n', e)
                errs += [master_ep.id]
                error += 1
                master_ep.sudo().write({'active': False})
            _logger.info('\n\n +++++++++ first id: %s   %s|%s|%s date: %s\n', master_ep, error , i, nbr, datetime.datetime.now())

        _logger.info('\n\n +++++++++ first masters: %s * \n\n', errs)
        _logger.info('\n\n +++++++++ first last: %s \n **\n', master_ep.id)
        _logger.info('\n\n +++++++++ first END * %s \n\n', datetime.datetime.now())

    @api.model
    def episode144_C31(self, id_from):
        master_eps = self.env['mk.episode.master'].search([('study_class_id', '=', 110),
                                                           ('id', '>', id_from),
                                                           ('state', '=', 'active'),
                                                           '|', ('subh', '=', True),
                                                           '|', ('zuhr', '=', True),
                                                           '|', ('aasr', '=', True),
                                                           '|', ('magrib', '=', True),
                                                           ('esha', '=', True)], order="id asc", limit=10)
        errs = []
        nbr = len(master_eps)
        _logger.info('\n\n +++++++++ second START %s %s* \n\n', nbr, datetime.datetime.now())

        i = 0
        error = 0
        for master_ep in master_eps:
            i += 1
            try:
                master_ep.copy()
                master_ep.action_done()
            except Exception as e:
                _logger.info('\n\n +++++++++ Exception as e : %s\n\n', e)
                errs += [master_ep.id]
                error += 1
                master_ep.sudo().write({'active': False})
            _logger.info('\n\n +++++++++ second id: %s   %s|%s|%s date: %s\n', master_ep, error, i, nbr, datetime.datetime.now())

        _logger.info('\n\n +++++++++ second masters: %s * \n\n', errs)
        _logger.info('\n\n +++++++++ second last: %s \n **\n', master_ep.id)
        _logger.info('\n\n +++++++++ second END * %s \n\n', datetime.datetime.now())

    @api.model
    def episode144_C32(self, id_from):
        master_eps = self.env['mk.episode.master'].search([('study_class_id', '=', 110),
                                                           ('id', '>', id_from),
                                                           ('state', '=', 'active'),
                                                           '|', ('subh', '=', True),
                                                           '|', ('zuhr', '=', True),
                                                           '|', ('aasr', '=', True),
                                                           '|', ('magrib', '=', True),
                                                           ('esha', '=', True)], order="id asc", limit=10)
        errs = []
        nbr = len(master_eps)
        _logger.info('\n\n +++++++++ third START %s %s* \n\n', nbr, datetime.datetime.now())

        i = 0
        error = 0
        for master_ep in master_eps:
            i += 1
            try:
                master_ep.copy()
                master_ep.action_done()
            except Exception as e:
                _logger.info('\n\n +++++++++ Exception as e : %s\n\n', e)
                errs += [master_ep.id]
                error += 1
                master_ep.sudo().write({'active': False})
            _logger.info('\n\n +++++++++ third id: %s   %s|%s|%s date: %s\n', master_ep, error, i, nbr, datetime.datetime.now())

        _logger.info('\n\n +++++++++ third masters: %s * \n\n', errs)
        _logger.info('\n\n +++++++++ third last: %s \n **\n', master_ep.id)
        _logger.info('\n\n +++++++++ third END * %s \n\n', datetime.datetime.now())

    @api.model
    def episode144_C33(self, id_from):
        master_eps = self.env['mk.episode.master'].search([('study_class_id', '=', 110),
                                                           ('id', '>', id_from),
                                                           ('state', '=', 'active'),
                                                           '|', ('subh', '=', True),
                                                           '|', ('zuhr', '=', True),
                                                           '|', ('aasr', '=', True),
                                                           '|', ('magrib', '=', True),
                                                           ('esha', '=', True)], order="id asc", limit=10)
        errs = []
        nbr = len(master_eps)
        _logger.info('\n\n +++++++++ fourth START %s %s* \n\n', nbr, datetime.datetime.now())

        i = 0
        error = 0
        for master_ep in master_eps:
            i += 1
            try:
                master_ep.copy()
                master_ep.action_done()
            except Exception as e:
                _logger.info('\n\n +++++++++ Exception as e : %s\n\n', e)
                errs += [master_ep.id]
                error += 1
                master_ep.sudo().write({'active': False})
            _logger.info('\n\n +++++++++ fourth id: %s   %s|%s|%s date: %s\n', master_ep, error, i, nbr, datetime.datetime.now())

        _logger.info('\n\n +++++++++ fourth masters: %s * \n\n', errs)
        _logger.info('\n\n +++++++++ fourth last: %s \n **\n', master_ep.id)
        _logger.info('\n\n +++++++++ fourth END * %s \n\n', datetime.datetime.now())

    @api.model
    def episode144_C34(self, id_from):
        master_eps = self.env['mk.episode.master'].search([('study_class_id', '=', 110),
                                                           ('id', '>', id_from),
                                                           ('state', '=', 'active'),
                                                           '|', ('subh', '=', True),
                                                           '|', ('zuhr', '=', True),
                                                           '|', ('aasr', '=', True),
                                                           '|', ('magrib', '=', True),
                                                           ('esha', '=', True)], order="id asc", limit=10)
        errs = []
        nbr = len(master_eps)
        _logger.info('\n\n +++++++++ fifth START %s %s* \n\n', nbr, datetime.datetime.now())

        i = 0
        error = 0
        for master_ep in master_eps:
            i += 1
            try:
                master_ep.copy()
                master_ep.action_done()
            except Exception as e:
                _logger.info('\n\n +++++++++ Exception as e : %s\n\n', e)
                errs += [master_ep.id]
                error += 1
                master_ep.sudo().write({'active': False})
            _logger.info('\n\n +++++++++ fifth id: %s   %s|%s|%s date: %s\n', master_ep, error, i, nbr, datetime.datetime.now())

        _logger.info('\n\n +++++++++ fifth masters: %s * \n\n', errs)
        _logger.info('\n\n +++++++++ fifth last: %s \n **\n', master_ep.id)
        _logger.info('\n\n +++++++++ fifth END * %s \n\n', datetime.datetime.now())

    @api.model
    def episode144_C35(self, id_from):
        master_eps = self.env['mk.episode.master'].search([('study_class_id', '=', 110),
                                                           ('id', '>', id_from),
                                                           ('state', '=', 'active'),
                                                           '|', ('subh', '=', True),
                                                           '|', ('zuhr', '=', True),
                                                           '|', ('aasr', '=', True),
                                                           '|', ('magrib', '=', True),
                                                           ('esha', '=', True)], order="id asc", limit=10)
        errs = []
        nbr = len(master_eps)
        _logger.info('\n\n +++++++++ sixth START %s %s* \n\n', nbr, datetime.datetime.now())

        i = 0
        error = 0
        for master_ep in master_eps:
            i += 1
            try:
                master_ep.copy()
                master_ep.action_done()
            except Exception as e:
                _logger.info('\n\n +++++++++ Exception as e : %s\n\n', e)
                errs += [master_ep.id]
                error += 1
                master_ep.sudo().write({'active': False})
            _logger.info('\n\n +++++++++ sixth id: %s   %s|%s|%s date: %s\n', master_ep, error, i, nbr, datetime.datetime.now())

        _logger.info('\n\n +++++++++ sixth masters: %s * \n\n', errs)
        _logger.info('\n\n +++++++++ sixth last: %s \n **\n', master_ep.id)
        _logger.info('\n\n +++++++++ sixth END * %s \n\n', datetime.datetime.now())

    @api.model
    def episode144_C36(self, id_from):
        master_eps = self.env['mk.episode.master'].search([('study_class_id', '=', 110),
                                                           ('id', '>', id_from),
                                                           ('state', '=', 'active'),
                                                           '|', ('subh', '=', True),
                                                           '|', ('zuhr', '=', True),
                                                           '|', ('aasr', '=', True),
                                                           '|', ('magrib', '=', True),
                                                           ('esha', '=', True)], order="id asc", limit=10)
        errs = []
        nbr = len(master_eps)
        _logger.info('\n\n +++++++++ seventh START %s %s* \n\n', nbr, datetime.datetime.now())

        i = 0
        error = 0
        for master_ep in master_eps:
            i += 1
            try:
                master_ep.copy()
                master_ep.action_done()
            except Exception as e:
                _logger.info('\n\n +++++++++ Exception as e : %s\n\n', e)
                errs += [master_ep.id]
                error += 1
                master_ep.sudo().write({'active': False})
            _logger.info('\n\n +++++++++ seventh id: %s   %s|%s|%s date: %s\n', master_ep, error, i, nbr, datetime.datetime.now())

        _logger.info('\n\n +++++++++ seventh masters: %s * \n\n', errs)
        _logger.info('\n\n +++++++++ seventh last: %s \n **\n', master_ep.id)
        _logger.info('\n\n +++++++++ seventh END * %s \n\n', datetime.datetime.now())

    @api.model
    def episode144_C37(self, id_from):
        master_eps = self.env['mk.episode.master'].search([('study_class_id', '=', 110),
                                                           ('id', '>', id_from),
                                                           ('state', '=', 'active'),
                                                           '|', ('subh', '=', True),
                                                           '|', ('zuhr', '=', True),
                                                           '|', ('aasr', '=', True),
                                                           '|', ('magrib', '=', True),
                                                           ('esha', '=', True)], order="id asc", limit=10)
        errs = []
        nbr = len(master_eps)
        _logger.info('\n\n +++++++++ eighth START %s %s* \n\n', nbr, datetime.datetime.now())

        i = 0
        error = 0
        for master_ep in master_eps:
            i += 1
            try:
                master_ep.copy()
                master_ep.action_done()
            except Exception as e:
                _logger.info('\n\n +++++++++ Exception as e : %s\n\n', e)
                errs += [master_ep.id]
                error += 1
                master_ep.sudo().write({'active': False})
            _logger.info('\n\n +++++++++ eighth id: %s   %s|%s|%s date: %s\n', master_ep, error, i, nbr, datetime.datetime.now())

        _logger.info('\n\n +++++++++ eighth masters: %s * \n\n', errs)
        _logger.info('\n\n +++++++++ eighth last: %s \n **\n', master_ep.id)
        _logger.info('\n\n +++++++++ eighth END * %s \n\n', datetime.datetime.now())

    # @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        new_master_episode = super(MkepisodeMaster, self).copy(default)
        _logger.info('\n\n ** new_master_episode **: \n\n %s',new_master_episode)
        new_master_episode_id = new_master_episode.id
        study_class = new_master_episode.study_class_id
        _logger.info('\n\n ** study_class **: \n\n %s',study_class)
        _logger.info('\n\n ** episode_ids **: \n\n %s',self.episode_ids)

        for episode in self.episode_ids:
            _logger.info('\n\n ** episode **: \n\n %s', episode)
            new_episode= episode.copy(default={'parent_episode': new_master_episode_id,
                                              'start_date':     study_class.start_date,
                                              'state':          'accept',
                                              'end_date':       study_class.end_date,})
            _logger.info('\n\n ** new_episode **: \n\n %s', new_episode)

        return new_master_episode

    # shaimaa to solve recursion error
    #
    # @api.multi
    # def go_to_subh_period(self):
    #     tree_view = self.env.ref('mk_episode_management.mk_episode_form_view')
    #     #res_id=self.env['mk.episode'].search([('parent_episode','=',self.id),('selected_period','=','subh')])
    #     query=""" select id from  mk_episode where parent_episode=%d  and selected_period='subh' """ %(self.id)
    #     self.env.cr.execute(query)
    #     res_id=self.env.cr.dictfetchall()
    #     return {#'name': _('Opportunity'),
    #             'res_model': 'mk.episode',
    #             'res_id':    res_id[0]['id'],
    #             'views':     [(tree_view.id, 'form'),],
    #             'type':      'ir.actions.act_window',
    #             'target':    'current',
    #             'domain':    [('parent_episode','=',self.id),('selected_period','=','subh')]}
    #
    # @api.multi
    # def go_to_zuhr_period(self):
    #     tree_view = self.env.ref('mk_episode_management.mk_episode_form_view')
    #     #res_id=self.env['mk.episode'].search([('parent_episode','=',self.id),('selected_period','=','zuhr')])
    #     query=""" select id from  mk_episode where parent_episode=%d  and selected_period='zuhr' """ %(self.id)
    #     self.env.cr.execute(query)
    #     res_id=self.env.cr.dictfetchall()
    #     return {#'name': _('Opportunity'),
    #             'res_model': 'mk.episode',
    #             'res_id':    res_id[0]['id'],
    #             'views':     [(tree_view.id, 'form'),],
    #             'type':      'ir.actions.act_window',
    #             'target':    'current',
    #             'domain':    [('parent_episode','=',self.id),('selected_period','=','zuhr')]}
    #
    # @api.multi
    # def go_to_asaar_period(self):
    #     tree_view = self.env.ref('mk_episode_management.mk_episode_form_view')
    #     #res_id=self.env['mk.episode'].search([('parent_episode','=',self.id),('selected_period','=','aasr')])
    #     query=""" select id from  mk_episode where parent_episode=%d  and selected_period='aasr' """ %(self.id)
    #     self.env.cr.execute(query)
    #     res_id=self.env.cr.dictfetchall()
    #     return {#'name': _('Opportunity'),
    #             'res_model': 'mk.episode',
    #             'res_id':    res_id[0]['id'],
    #             'views':     [(tree_view.id, 'form'),],
    #             'type':      'ir.actions.act_window',
    #             'target':    'current',
    #             'domain':    [('parent_episode','=',self.id),('selected_period','=','aasr')]}
    #
    # @api.multi
    # def go_to_magrib_period(self):
    #     tree_view = self.env.ref('mk_episode_management.mk_episode_form_view')
    #     #res_id=self.env['mk.episode'].search([('parent_episode','=',self.id),('selected_period','=','magrib')])
    #     query=""" select id from  mk_episode where parent_episode=%d  and selected_period='magrib' """  %(self.id)
    #     self.env.cr.execute(query)
    #     res_id=self.env.cr.dictfetchall()
    #     return {#'name': _('Opportunity'),
    #             'res_model': 'mk.episode',
    #             'res_id':    res_id[0]['id'],
    #             'views':     [(tree_view.id, 'form'),],
    #             'type':      'ir.actions.act_window',
    #             'target':    'current',
    #             'domain':    [('parent_episode','=',self.id),('selected_period','=','magrib')]}
    #
    # @api.multi
    # def go_to_esha_period(self):
    #     tree_view = self.env.ref('mk_episode_management.mk_episode_form_view')
    #     #res_id=self.env['mk.episode'].search([('parent_episode','=',self.id),('selected_period','=','esha')])
    #     query=""" select id from  mk_episode where parent_episode=%d  and selected_period='esha' """ %(self.id)
    #     self.env.cr.execute(query)
    #     res_id=self.env.cr.dictfetchall()
    #     return {#'name': _('Opportunity'),
    #             'res_model': 'mk.episode',
    #             'res_id':    res_id[0]['id'],
    #             'views':     [(tree_view.id, 'form'),],
    #             'type':      'ir.actions.act_window',
    #             'target':    'current',
    #             'domain':    [('parent_episode','=',self.id),('selected_period','=','esha')]}

    @api.model
    def data_set_state(self):
        episodes = self.search([('academic_id','!=',19),
                                '|',('active','=',True),
                                    ('active','=',False)])
        nbr_episodes = len(episodes)
        _logger.info('\n\n write nbr_episodes: %s\n\n', nbr_episodes)
        i = 1
        j = 1        
        for episode in episodes:
            episode.action_done()
            
            if j == 20:
                j = 0
                _logger.info('\n\n write episodes: %s / %s\n\n', i, nbr_episodes)
                
            i += 1
            j += 1            

    # @api.one
    def action_done(self):
        self.state = 'done'
        self.active = False
        for episode in self.episode_ids:
            episode.action_done()

    @api.model
    def cron_action_done_episodes(self):
        _logger.info('\n\n +++++++++++++++ START cron_action_done_episodes \n\n')
        # ep_master=self.env['mk.episode.master'].search([('state','=','active'),
        #                                                ('study_class_id.is_default','=',False)])
        episodes = self.env['mk.episode'].search([('state', '!=', 'done'),
                                                   ('study_class_id.is_default', '=', False),
                                                   '|', ('active', '=', True),
                                                        ('active', '=', False)], limit=5000)
        total = len(episodes)
        i = 0
        _logger.info('\n\n +++++++++++++++ total : %s', total)
        for ep in episodes:
            i+=1
            _logger.info('\n\n +++++++++++++++ len links : %s', len(ep.link_ids))
            ep.action_done()
            _logger.info('\n\n +++++++++++++++ %s|%s \n\n', i, total)
        _logger.info('\n\n +++++++++++++++  END  \n\n')


    # @api.one
    def action_reopen(self):
        if self.study_class_id.end_date < fields.Datetime.now():
            msg = 'لا يمكن إعادة تفعيل الحلقة بعد نهاية الفصل' + ' !'
            raise ValidationError(msg)
        episodes = self.env['mk.episode'].sudo().search([('parent_episode','=',self.id),
                                                         ('active','=',False)])
        for episode in episodes:
            episode.action_reopen()
        
        self.state = 'active'
        self.active = True
             
    # @api.one
    def write(self, vals):
        vals_ep_update = {}
        
        if 'name' in vals:
            vals_ep_update.update({'name': vals['name']})        
        
        if 'mosque_id' in vals:
            vals_ep_update.update({'mosque_id': vals['mosque_id']})        
        
        if 'company_id' in vals:
            vals_ep_update.update({'company_id': vals['company_id']})
        
        if 'academic_id' in vals:
            vals_ep_update.update({'academic_id': vals['academic_id']})
            
        if 'study_class_id' in vals:
            vals_ep_update.update({'study_class_id': vals['study_class_id']})
        
        episodes = self.env['mk.episode'].search([('parent_episode','=',self.id),
                                                  '|',('active','=',True),
                                                      ('active','=',False)])
        if episodes:
            episodes.write(vals_ep_update)

        return super(MkepisodeMaster, self).write(vals)
    
    # @api.one
    def unlink(self):
        episodes = self.env['mk.episode'].search([('parent_episode','=',self.id)])
        if episodes:
            episodes.unlink()
                          
        super(MkepisodeMaster, self).unlink()
        