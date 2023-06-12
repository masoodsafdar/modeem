# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class mk_mosque(models.Model):
    _inherit = 'mk.mosque'

    @api.depends('supervisors','supervisors.category')
    def get_supervisors(self):
        for rec in self:
            rec.supervisors_no = len(rec.supervisors)

    # @api.one
    @api.depends('permission_ids')
    def get_nbr_permission(self):
        self.nbr_permission = len(self.sudo().permission_ids)

    # @api.one
    @api.depends('permission_requests_ids')
    def get_nbr_permission_requests(self):
        nbr_supervisor_permission_requests = 0
        nbr_admin_permission_requests = 0
        permission_requests_ids = self.sudo().permission_requests_ids
        for request in permission_requests_ids:
            if request.type_request == 'supervisor_request':
                nbr_supervisor_permission_requests += 1
            elif request.type_request == 'admin_request':
                nbr_admin_permission_requests += 1
        self.nbr_supervisor_permission_requests = nbr_supervisor_permission_requests
        self.nbr_admin_permission_requests = nbr_admin_permission_requests

    # @api.multi
    @api.depends('register_code', 'center_department_id', 'district_id')
    def get_permission_code(self):
        for rec in self:
            rec.permission_code = "-".join([ str(rec.center_department_id.code) ,str(rec.district_id.code) , str(rec.register_code)])


    permission_code                    = fields.Char('رقم التصريح',        track_visibility='onchange',compute=get_permission_code, store=True,)
    supervisors_no                     = fields.Integer('supervisors no for mosque', default=0, compute='get_supervisors', track_visibility='onchange')
    active                             = fields.Boolean('Active',                    default=True,                         track_visibility='onchange')
    test_schedule_ids                  = fields.One2many('mk.schedule.test', 'mosque_id', string='Schedule test')
    permission_ids                     = fields.One2many('mosque.permision', 'masjed_id', string='التصاريح')
    nbr_permission                     = fields.Integer('التصاريح', compute='get_nbr_permission', track_visibility='onchange', store=True)
    permission_requests_ids            = fields.One2many('mosque.supervisor.request', 'mosque_id', string='التكاليف')
    nbr_supervisor_permission_requests = fields.Integer('طلبات تكاليف مشرفي المساجد',         compute='get_nbr_permission_requests', track_visibility='onchange')
    nbr_admin_permission_requests      = fields.Integer('طلبات تكاليف مديري المساجد/المدارس', compute='get_nbr_permission_requests', track_visibility='onchange')
    mosque_admin_id                    = fields.Many2one('hr.employee', 'Mosque admin', track_visibility='onchange')

    @api.model
    def get_filtered_mosques(self, district_id,episode_type):
        try:
            district_id = int(district_id)
            episode_type = int(episode_type)
        except:
            pass

        male = []
        female = []
        mosque_ids = self.env['mk.mosque'].search([('district_id', '=', district_id)])
        for mosq in mosque_ids:
            mosque_type = mosq.categ_id.mosque_type
            episode_id = self.env['mk.episode'].search([('mosque_id', '=', mosq.id),
                                                         ('episode_type', '=', episode_type),
                                                         ('state', 'in', ['draft', 'accept'])], limit=1)
            if episode_id:
                if mosque_type == 'male':
                    male.append({'mosque_id': mosq.id,
                                 'mosque_name' : mosq.name,
                                 'lat' : mosq.latitude,
                                 'long' : mosq.longitude,
                                 'shift' : mosq.episode_value})
                if mosque_type == 'female':
                    female.append({'mosque_id': mosq.id,
                                 'mosque_name' : mosq.name,
                                 'lat' : mosq.latitude,
                                 'long' : mosq.longitude,
                                 'shift' : mosq.episode_value})
        vals = {'male': male,
                'female': female}
        return str(vals)

    @api.model
    def delete_archived_mosque(self):
        mosques = self.env['mk.mosque'].search([('active', '=', False)])
        total = len(mosques)
        mosq_with_no_test = []
        mosq_with_test = []
        i = 1
        for mq in mosques:
            i += 1
            verif_mosque_session = self.env['student.test.session'].search([('mosque_id', '=', mq.id),
                                                                            ('state', 'not in', ['cancel', 'draft'])], limit=1)
            if verif_mosque_session:
                mosq_with_test.append(mq.id)
                continue
            mosq_with_no_test.append(mq.id)
        mosq_count = 0
        deleted = 0
        for mosq in mosq_with_no_test:
            mosq_count += 1
            mosque_id = self.env['mk.mosque'].search([('id', '=', mosq),
                                                      ('active', '=', False)])

            mosque_permision = self.env['mosque.permision'].search([('masjed_id', '=', mosq)])
            mosque_permision.unlink()


            mosque_supervisor_request = self.env['mosque.supervisor.request'].search([('mosque_id', '=', mosq),
                                                                                      '|', ('active', '=', True),
                                                                                           ('active', '=', False)])
            mosque_supervisor_request.unlink()

            course_request = self.env['mk.course.request'].search([('mosque_id', '=', mosq),
                                                                  '|', ('active', '=', True),
                                                                       ('active', '=', False)])
            course_request.sudo().unlink()

            events = self.env['event.event'].search([ ('mosque_id', '=', mosq),
                                                        '|',('active', '=', True),
                                                            ('active', '=', False)])
            for event in events:
                event.sudo().write({'mosque_id': False})

            links = self.env['mk.link'].search(['|', ('mosq_id','=',mosq),
                                                     ('mosque_id','=',mosq)])
            links.unlink()
            students = self.env['mk.student.register'].search(['&','|',('active', '=', True),
                                                                       ('active', '=', False),
                                                                   '|',('mosq_id', '=', mosq),
                                                                       ('mosque_new', '=', mosq),
                                                                       ('mosque_id', '=', mosq)])
            for student in students:
                student.sudo().write({'mosq_id': False,
                                      'mosque_new': False,
                                      'mosque_id': False})

            self.env.cr.execute('select count(*) from mk_student_register where mosque_id = {}; '''.format(mosq))

            self.env.cr.execute('update mk_student_register set mosque_id= null  where mosque_id = {}; '''.format(mosq))

            mk_mosque_mk_student_register_rel = self.env.cr.execute('''select count(*) from mk_mosque_mk_student_register_rel WHERE mk_mosque_id = {}; '''.format(mosq))

            self.env.cr.execute('delete from mk_mosque_mk_student_register_rel WHERE mk_mosque_id = {}; '''.format(mosq))

            episodes = self.env['mk.episode'].search([('mosque_id', '=', mosq),
                                                  '|',('active', '=', True),
                                                      ('active', '=', False)])
            for episode in episodes:
                sessions = self.env['mq.session'].search([('episode_id', '=', episode.id),
                                                          '|', ('active', '=', True),
                                                               ('active', '=', False)])
                for session in sessions:
                    session.unlink()
                episode.unlink()

            episodes_master = self.env['mk.episode.master'].search([('mosque_id', '=', mosq),
                                                             '|', ('active', '=', True),
                                                                  ('active', '=', False)])
            for master in episodes_master:
                master.unlink()

            employees = self.env['hr.employee'].search([('mosque_id', '=', mosq),
                                                     '|', ('active', '=', True),
                                                          ('active', '=', False)])

            for emp in employees:
               emp.write({'mosque_id': False})

            mosque_relation = self.env.cr.execute('''select count(*) from mosque_relation WHERE mosq_id = {}; '''.format(mosq))

            self.env.cr.execute('''delete from mosque_relation WHERE mosq_id = {}; '''.format(mosq))

            hr_employee_mk_mosque_rel = self.env.cr.execute('''select count(*) from hr_employee_mk_mosque_rel WHERE mk_mosque_id = {}; '''.format(mosq))

            self.env.cr.execute('''delete from hr_employee_mk_mosque_rel WHERE mk_mosque_id = {}; '''.format(mosq))

            try:
                mosque_id.unlink()
                deleted += 1
            except Exception as e:
                continue


    @api.model
    def check_mosque_center(self):
        mosques = self.env['mk.mosque'].search([('is_synchro_edu_admin', '=', True),
                                                ('permission_ids', '!=', False)])
        total = len(mosques)
        i = 0
        not_perm_count = 0
        multi_perm_count = 0
        verified_count = 0
        to_verify_count = 0
        multi_perm = []
        to_verify = []
        verified = []
        for mosque in mosques:
            i+=1
            permission = mosque.permission_ids.filtered(lambda p: p.is_valid == True)
            if not permission:
                not_perm_count += 1
                continue
            if len(permission) > 1 and id != 2199 :
                permission_id = permission.ids[0]
                center_id = self.env['mosque.permision'].browse(permission_id).center_id.id
                if  mosque.center_department_id.id != center_id:
                    to_verify.append(mosque.id)
                    to_verify_count += 1
            else:
                verified.append(mosque.id)
                verified_count += 1
