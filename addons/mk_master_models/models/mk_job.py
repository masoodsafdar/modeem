# -*- coding: utf-8 -*-
from odoo import models,fields,api,_

import logging
_logger = logging.getLogger(__name__)


class hr_job(models.Model):
    _inherit = 'hr.job'
    active = fields.Boolean('Active', default=True)

    age_categories  = fields.Many2many("mk.age.category", string="Age Gategories")
    educational_job = fields.Boolean("Educational job")


class RecruitmentDegreeInherit(models.Model):
    _inherit = "hr.recruitment.degree"

    @api.model
    def get_recruitment(self):
        recruitments = self.env['hr.recruitment.degree'].search([])
        recruitment_list = []
        if recruitments:
            for recruitment in recruitments:
                recruitment_list.append({'id':   recruitment.id,
                                         'name': recruitment.name})
        return recruitment_list

    @api.model
    def get_degrees_employee(self):
        query_string = ''' 
                select id, name
                from hr_recruitment_degree
                order by id;
                '''
        self.env.cr.execute(query_string)
        degrees_employee = self.env.cr.dictfetchall()
        return degrees_employee

