# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.osv import osv
from datetime import datetime
from odoo.exceptions import Warning

class episode_programs(models.Model):

    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """

    _name = 'mk.episode.program.archive'

    episode_id=fields.Many2one("mk.episode","Episode",)
    academic_id = fields.Many2one(
        'mk.study.year',
        string='Academic Year',
    )
    study_class_id = fields.Many2one(
        'mk.study.class',
        string='Study class',
        required=True
    )

    program_id=fields.Many2one("mk.programs","program")

    # @api.multi
    def get_history(self,ep_id):
        records=[]
        self_ob=self.env['mk.episode.program.archive']
        ep_ids=self_ob.search([('episode_id','=',ep_id)])
        for rec in ep_ids:
            rec_dict=({
                'academic_year_id':rec.academic_id.id,
                'academic_year_name':str(rec.academic_id.name),
                'study_class_id':rec.study_class_id.id,
                'study_class_name':str(rec.study_class_id.name),
                'program_id':rec.program_id.id,
                'program_name':str(rec.program_id.name)
                })
            records.append(rec_dict)
        return records
