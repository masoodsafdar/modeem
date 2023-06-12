# -*- coding: utf-8 -*-
from openerp import models,fields,api,_


class MkEpisodeProductivity(models.Model):
    _name ='mk.episode_productivity'
    _description ='Episode productivity'

    @api.one
    @api.depends('episode_ids')
    def get_episode_details(self):
        for episode in self.episode_ids:
            episode_type = episode.episode_type
            self.type_test = episode_type.type_test
            self.min_students_number = episode_type.students_no

    @api.one
    @api.depends('episode_ids')
    def get_productivity(self):
        parts_count = 0
        students_number_count = 0
        student_test_list =[]
        teacher_test_list =[]
        for episode in self.episode_ids :
            episode_type = episode.episode_type
            type_test = episode_type.type_test

            if type_test == 'parts_final':
                domain = [('test_name.type_test', 'in', ['parts', 'final'])]
            else:
                domain = [('test_name.type_test', '=', type_test)]

            tests = self.env['student.test.session'].search([('episode_id', '=', episode.id),
                                                             ('state', '=', 'done')] + domain)
            student_test_list.append(tests)
            students_number_count += len(episode.link_ids)
            for test in tests:
                parts_count += len(test.branch.parts_ids)
            # if episode_type == self.env.ref('mk_productivity.episode_type5'):
            #     employee_tests = self.env['employee.test.session'].search([('episode_id', '=', episode.id),
            #                                                                 ('state', '=', 'done')] + domain)
            #     teacher_test_list.append(employee_tests)
            #     # students_number_count += len(episode.link_ids)
            #     for test in employee_tests:
            #         parts_count += len(test.branch.parts_ids)
        self.productivity = parts_count
        self.student_test_ids = tests
        self.teacher_test_ids = teacher_test_list
        self.students_number = students_number_count

    @api.depends('productivity')
    @api.one
    def get_productiviy_incentive(self):
        if self.min_students_number <= self.students_number:
            productivity_incentive = self.env['mk.productivity_incentive'].search([('type_episode_id', '=', self.type_episode_id.id),
                                                                                   ('min_nbr_part', '<=', self.productivity)], order="max_nbr_part desc", limit=1)
            self.incentive_id = productivity_incentive.id
            self.type_mark = productivity_incentive.type_mark

    productivity_id     = fields.Many2one("mk.productivity")
    episode_ids         = fields.Many2many('mk.episode', string='Episodes')
    type_episode_id     = fields.Many2one("mk.episode_type", string="Episode type")
    productivity        = fields.Integer(string="Productivity",                           compute="get_productivity", store=True)
    student_test_ids    = fields.Many2many("student.test.session", string="Student tests",compute="get_productivity", store=True)
    teacher_test_ids    = fields.Many2many("employee.test.session", string="Teacher tests",compute="get_productivity", store=True)
    type_test           = fields.Selection(string="Test type", selection=[('parts', 'Parts'),
                                                                           ('final', 'Final'),
                                                                           ('parts_final', 'Parts and Final'),
                                                                           ('contest', 'Contest'),
                                                                           ('diploma', 'Diploma')], compute="get_episode_details", store=True)
    min_students_number = fields.Integer(string="Minimum number of students",  compute="get_episode_details", store=True)
    students_number     = fields.Integer(string="Students number",  compute="get_productivity", store=True)
    incentive_id        = fields.Many2one("mk.productivity_incentive", string="Incentive",                compute="get_productiviy_incentive", store=True )
    type_mark           = fields.Selection(string="", selection=[('perfect', 'Perfect'),
                                                                 ('excellent', 'Excellent'),
                                                                 ('very good', 'Very Good'),
                                                                 ('good', 'Good'),
                                                                 ('low', 'Low')], compute="get_productiviy_incentive", store=True )

