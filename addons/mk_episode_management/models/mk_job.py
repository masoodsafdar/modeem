# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class hr_job(models.Model):
    _inherit = 'hr.job'

    role_id = fields.Many2one("res.users.role", string="Role")
    is_role = fields.Boolean(strig=" Is Role")

    # @api.one
    def write(self, vals):
        prev_role = self.role_id
        res = super(hr_job, self).write(vals)
        if 'role_id' in vals:
            role_id = vals.get('role_id')
            employees = self.employee_ids
            if employees:
                prev_role_id = prev_role and prev_role.id or False
                employees.update_role(prev_role_id, role_id)
        return res

    @api.model
    def hr_jobs(self):
        jobs = self.env['hr.job'].search([('educational_job', '=', True)])
        item_list = []
        if jobs:
            for job in jobs:
                item_list.append({'name': job.name,
                                  'id':   job.id})
        return item_list


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    is_confirm_info = fields.Boolean('Data request confirmation')
    login_date      = fields.Datetime(string='آخر دخول للنظام', related='user_id.login_date')

    # @api.multi
    def valid_is_confirm_info(self):
        for rec in self:
            if rec.is_confirm_info == False:
                rec.write({'is_confirm_info': True})

    # @api.one
    def update_role(self, prev_role_id, role_id):
        user = self.user_id
        if user:
            user_id = user.id
            if prev_role_id:
                prev_role_line = self.env['res.users.role.line'].sudo().search([('user_id', '=', user_id),
                                                                                ('role_id', '=', prev_role_id)])
                if prev_role_id:
                    prev_role_line.sudo().unlink()

            if role_id:
                self.env['res.users.role.line'].sudo().create({'user_id': user_id,
                                                               'role_id': role_id})

    def accept(self):
        super(hr_employee, self).accept()

        job = self.job_id
        role_id = job and job.role_id.id or False
        self.update_role(role_id, role_id)

    # @api.one
    def write(self, vals):
        job = self.job_id
        res = super(hr_employee, self).write(vals)
        if 'is_confirm_info' in vals:
            if vals['is_confirm_info']:
                home_action = self.env.ref('mk_episode_management.confirmation_request_action')
                self.user_id.action_id = home_action.id
            else:
                self.user_id.action_id = False
        if 'job_id' in vals:
            job_id = vals.get('job_id')
            role_id = False

            if job_id:
                new_job = self.env['hr.job'].sudo().search([('id', '=', job_id)], limit=1)
                role_id = new_job.role_id.id

            prev_role_id = job and job.role_id.id or False

            self.update_role(prev_role_id, role_id)

        if 'country_id' in vals:
            student = self.env['mk.student.register'].sudo().search([('category', '!=', False),
                                                                         '|',('identity_no', '=', self.identification_id),
                                                                             ('passport_no', '=', self.identification_id)])
            if student:
                student.sudo().write({'country_id': vals.get('country_id')})
        return res

    @api.model
    def get_nbr_employee_job(self, department_id, type_mosque, mosque_id, degree_id, code_country, type_contract,type_epiosde_id):
        domain = [('job_id', '!=', False)]

        domain_mosque = []
        domain_episode = []
        mosque_ids = []

        if code_country == 1:
            domain = [('country_id.code', '=', 'SA')]
        elif code_country == 2:
            domain = [('country_id.code', '!=', 'SA')]

        if degree_id:
            domain += [('recruit_ids', 'in', degree_id)]

        if type_contract:
            domain += [('contract_type', '=', type_contract)]

        if mosque_id:
            if not department_id:
                domain += ['|', '&', ('category', 'not in', ['edu_supervisor', 'center_admin']),
                           ('mosqtech_ids', 'in', mosque_id),

                           '&', ('category', '=', 'edu_supervisor'),
                           ('mosque_sup', 'in', mosque_id)]
            else:
                domain += ['|', '&', ('category', 'not in', ['edu_supervisor', 'center_admin']),
                           ('mosqtech_ids', 'in', mosque_id),

                           '|', '&', ('category', '=', 'edu_supervisor'),
                           ('mosque_sup', 'in', mosque_id),

                           '&', ('category', '=', 'center_admin'),
                           ('department_ids', 'in', department_id)]

        else:
            if type_epiosde_id:
                domain_episode = [('episode_type', '=', type_epiosde_id)]

            if type_mosque:
                domain_episode += [('parent_episode.mosque_id.categ_id.mosque_type', '=', type_mosque)]
                domain_mosque += [('categ_id.mosque_type', '=', type_mosque)]

            if department_id:
                domain_episode += [('parent_episode.mosque_id.center_department_id', '=', department_id)]
                domain_mosque += [('center_department_id', '=', department_id)]

            if type_epiosde_id:
                mosque_episode_ids = self.env['mk.episode'].read_group(domain_episode, ['mosque_id'], ['mosque_id'])
                mosque_ids = [mosque_episode.get('mosque_id', (0))[0] for mosque_episode in mosque_episode_ids]

            elif domain_mosque:
                mosques = self.env['mk.mosque'].search(domain_mosque)
                if mosques:
                    mosque_ids = mosques.ids

            if mosque_ids:
                if not department_id:
                    domain += ['|', '&', ('category', 'not in', ['edu_supervisor', 'center_admin']),
                               ('mosqtech_ids', 'in', mosque_ids),

                               '&', ('category', '=', 'edu_supervisor'),
                               ('mosque_sup', 'in', mosque_ids)]
                else:
                    domain += ['|', '&', ('category', 'not in', ['edu_supervisor', 'center_admin']),
                               ('mosqtech_ids', 'in', mosque_ids),

                               '|', '&', ('category', '=', 'edu_supervisor'),
                               ('mosque_sup', 'in', mosque_ids),

                               '&', ('category', '=', 'center_admin'),
                               ('department_ids', 'in', department_id)]

            elif department_id:
                domain += ['|', ('department_id', '=', department_id),
                           '&', ('category', 'not in', ['edu_supervisor', 'center_admin', 'teacher']),
                           ('department_ids', 'in', department_id)]

            elif type_epiosde_id or type_mosque:
                domain += ['|', '&', ('category', 'not in', ['edu_supervisor', 'center_admin']),
                           ('mosqtech_ids', 'in', mosque_ids),

                           '&', ('category', '=', 'edu_supervisor'),
                           ('mosque_sup', 'in', mosque_ids)]

        employees = self.env['hr.employee'].search(domain)
        employee_ids = employees and employees.ids or []

        if len(employee_ids) <= 1:
            employee_ids += [0, 0]

        cr = self.env.cr

        sql_query = ''' SELECT count(emp.job_id) as job,
                                 hr_job.name as name 

                          FROM hr_employee as emp LEFT JOIN hr_job ON emp.job_id=hr_job.id

                          WHERE emp.id in {} 

                          GROUP BY emp.job_id, hr_job.name 

                          Having count(emp.job_id) > 0;'''.format(tuple(employee_ids))

        cr.execute(sql_query)
        res = cr.fetchall()
        return employee_ids

    # @api.multi
    def add_group_read_mosque_supervisor_request_and_permission(self):
        group_id = self.env.ref('mk_episode_management.read_mosque_supervisor_requests_and_permissions')
        users = []
        for rec in self:
            users.append(rec.user_id.id)
        group_id.users = [(4, user) for user in users]

    @api.model
    def add_supervisor_request(self, data):
        identification_id = data['identification_id']
        passport_id = data['passport_id']
        name = data['name'].encode('utf-8')
        mobile_phone = data['mobile_phone']
        work_email = data['work_email']
        country_id = data['country_id']
        job_id = data['job_id']
        gender = data['gender']
        marital = data['marital']
        department_id = data['department_id']
        mosqtech_ids = data['mosqtech_ids']
        active = data['active']
        recruit_ids = data['recruit_ids']
        partner_vals = {'name':name,
                       'company_id':1,
                       'display_name':name,
                       'lang': 'ar_SY',
                       'active':True,
                       'customer':False,
                       'supplier':False,
                       'employee':True,
                       'country_id':country_id,
                       'email':work_email,
                       'mobile':mobile_phone,
                       'is_company':False,
                       'color':0,
                       'no_identity':True,
                       'passport_no':passport_id,
                       'gender':gender,
                       'parent':False,
                       'is_student':False,
                       'invoice_warn':'no-message',
                       'sale_warn':'no-message'}
        partner_id = self.env['res.partner'].sudo().create(partner_vals)
        if partner_id:
            user_vals = {'active': True,
                         'login': passport_id if passport_id != False else identification_id,
                         'company_id': 1,
                         'partner_id': partner_id.id,
                         'notification_type': 'email',
                         'department_id': department_id,
                         'gender': gender}
            user_id = self.env['res.users'].sudo().create(user_vals)
            if user_id:
                resource_vals = {'name': name,
                                 'active': True,
                                 'company_id': 1,
                                 'resource_type': 'user',
                                 'user_id': user_id.id,
                                 'time_efficiency': 1,
                                 'calendar_id': 1}
                resource_id = self.env['resource.resource'].sudo().create(resource_vals)
                if resource_id:
                    employee_vals = {'resource_id': resource_id.id,
                                     'passport_id': passport_id,
                                     'identification_id': identification_id,
                                     'name': name,
                                     'mobile_phone': mobile_phone,
                                     'work_email': work_email,
                                     'country_id': country_id,
                                     'job_id': job_id,
                                     'gender': gender,
                                     'marital': marital,
                                     'department_id': department_id,
                                     'active': active,
                                     'company_id': 1,
                                     'state': 'draft',
                                     'category': 'admin',
                                     'category2': 'admin',
                                     'flag2': False,
                                     'create_date': datetime.now().date(),
                                     'flag': True}
                    employee_id = self.env['hr.employee'].sudo().create(employee_vals)
                    if employee_id and recruit_ids:
                       try:
                           # query1 = ''' INSERT INTO public.mosque_relation(mosq_id, emp_id)
                           # 			            VALUES ({},{});'''.format(mosqtech_ids, employee_id.id)
                           # self.env.cr.execute(query1)
                           # return_row1 = self.env.cr.dictfetchall()

                           query2 = ''' INSERT INTO public.hr_employee_hr_recruitment_degree_rel(hr_employee_id, hr_recruitment_degree_id)
                                                                     VALUES ({},{});'''.format(employee_id.id, recruit_ids)
                           self.env.cr.execute(query2)
                           return_row2 = self.env.cr.dictfetchall()
                       except:
                           pass
        return employee_id.registeration_code if employee_id else False



