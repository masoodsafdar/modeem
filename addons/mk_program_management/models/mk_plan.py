#-*- coding:utf-8 -*-
from odoo import models, fields, api


class MkPlanDetails(models.Model):
    _name = 'mk.plan.details'
    
    course_id 	= fields.Many2one('mk.plan.course', string="Course")
    plan 		= fields.Selection([('s',   'Saving'),
									('mia', 'Minimum Audit'),
									('maa', 'Maximum Audit'),
									('r',   'Reading')], string="Plan")
    from_surah 	= fields.Many2one('mk.surah', string='From Surah')
    to_surah 	= fields.Many2one('mk.surah', string='To Surah')
    from_verses = fields.Integer('From Verses ')
    to_verses 	= fields.Integer('To Verses ')
    
    
class MkPlanCourse(models.Model):
    _name = 'mk.plan.course'
    
    name 		= fields.Char('Name')
    detail_ids 	= fields.One2many('mk.plan.details', 'course_id', string="Details")
    plan_id 	= fields.Many2one('mk.plan',                      string='Plan')
    

class MkPlan(models.Model):
    _name = 'mk.plan'
        
    name 			= fields.Char('Name')
    program_id 		= fields.Many2one('mk.program',  string='Program')
    approach_id 	= fields.Many2one('mk.approach', string='Approach')
    level_id 		= fields.Many2one('mk.level',    string='Level')        
    saving 			= fields.Boolean('Saving')
    minimum_audit 	= fields.Boolean('Minimum Audit')
    maximum_audit 	= fields.Boolean('Maximum Audit')
    reading 		= fields.Boolean('Reading')
    all 			= fields.Boolean('All')
    plan_course_ids = fields.One2many('mk.plan.course', 'plan_id', string="Courses")

