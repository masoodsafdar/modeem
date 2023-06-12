#-*- coding:utf-8 -*-
from odoo import models, fields, api

    
class MkBranches(models.Model):
    _name = 'mk.branches'
        
    name		 = fields.Char('Name')
    path		 = fields.Selection([('a','Ascending'),
								 	 ('d','Descending')], string='Path')
    start_date	 = fields.Date('Start Date')
    end_date	 = fields.Date('End Date')
    age_category = fields.Selection([('s','Specific'),
									 ('o','Open')],       string='Age Category')
    from_age	 = fields.Integer('From Age')
    to_age		 = fields.Integer('To Age')
    from_surah	 = fields.Many2one('mk.surah', string='From Surah')
    to_surah	 = fields.Many2one('mk.surah', string='to Surah')
