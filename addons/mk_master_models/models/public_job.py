# -*- coding: utf-8 -*-
from odoo import models,fields,api,_

import logging
_logger = logging.getLogger(__name__)

class public_job(models.Model):
    _name = 'mk.job'
    _inherit = ['mail.thread']

    active         = fields.Boolean(string='Active', default=True, track_visibility='onchange')
    age_categories = fields.Many2many("mk.age.category",string="Age Gategories", track_visibility='onchange')
    name           = fields.Char('Name', track_visibility='onchange')

    @api.model
    def get_jobs(self):
        jobs = self.env['mk.job'].search([('active', '=', True)])
        job_list = []
        if jobs:
            for job in jobs:
                job_list.append({'id': job.id,
                                 'name': job.name})
        return job_list
