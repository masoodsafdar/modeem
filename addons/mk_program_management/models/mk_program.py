#-*- coding:utf-8 -*-
from odoo import models, fields, api

    
class MkProgram(models.Model):
    _name = 'mk.program'
        
    name 							= fields.Char('Name')
    approach_id 					= fields.Many2one('mk.approach', string='Approach')
    level_id 						= fields.Many2one('mk.level', string='Level')
    
    saving 							= fields.Boolean('Saving')
    minimum_audit 					= fields.Boolean('Minimum Audit')
    maximum_audit 					= fields.Boolean('Maximum Audit')
    reading 						= fields.Boolean('Reading')
    all 							= fields.Boolean('All')
    
    saving_lines_number 			= fields.Integer('Number of Lines')
    saving_full_quantity_mark 		= fields.Float('Full Quantity Mark')
    saving_full_mastery_mark 		= fields.Float('Full Mastery Mark')
    saving_direction 				= fields.Selection([('a','AlBaqarah-AlNass'),('d','AlNass-AlBaqarah')],string='Direction')
    saving_from_surah 				= fields.Many2one('mk.surah', string='From Surah')
    saving_to_surah 				= fields.Many2one('mk.surah', string='To Surah')
    saving_from_verses			 	= fields.Integer('From Verses ')
    saving_to_verses 				= fields.Integer('To Verses ')
    
    
    minimum_audit_lines_number		 = fields.Integer('Number of Lines')
    minimum_audit_full_quantity_mark = fields.Float('Full Quantity Mark')
    minimum_audit_full_mastery_mark	 = fields.Float('Full Mastery Mark')
    minimum_audit_direction 		= fields.Selection([('a','AlBaqarah-AlNass'),('d','AlNass-AlBaqarah')],string='Direction')
    minimum_audit_from_surah 		= fields.Many2one('mk.surah', string='From Surah')
    minimum_audit_to_surah 			= fields.Many2one('mk.surah', string='To Surah')
    minimum_audit_from_verses 		= fields.Integer('From Verses ')
    minimum_audit_to_verses 		= fields.Integer('To Verses ')
    
    maximum_audit_lines_number 		= fields.Integer('Number of Lines')
    maximum_audit_full_quantity_mark = fields.Float('Full Quantity Mark')
    maximum_audit_full_mastery_mark = fields.Float('Full Mastery Mark')
    maximum_audit_direction			= fields.Selection([('a','AlBaqarah-AlNass'),('d','AlNass-AlBaqarah')],string='Direction')
    maximum_audit_from_surah 		= fields.Many2one('mk.surah', string='From Surah')
    maximum_audit_to_surah 			= fields.Many2one('mk.surah', string='To Surah')
    maximum_audit_from_verses 		= fields.Integer('From Verses ')
    maximum_audit_to_verses 		= fields.Integer('To Verses ')
    
    reading_lines_number 			= fields.Integer('Number of Lines')
    reading_full_quantity_mark 		= fields.Float('Full Quantity Mark')
    reading_full_mastery_mark 		= fields.Float('Full Mastery Mark')
    reading_direction 				= fields.Selection([('a','AlBaqarah-AlNass'),('d','AlNass-AlBaqarah')],string='Direction')
    reading_from_surah 				= fields.Many2one('mk.surah', string='From Surah')
    reading_to_surah 				= fields.Many2one('mk.surah', string='To Surah')
    reading_from_verses 			= fields.Integer('From Verses ')
    reading_to_verses 				= fields.Integer('To Verses ')
    
    full_preparation_mark 			= fields.Float('Full Preparation Mark')
    late_deduct 					= fields.Float('Late Deduct')
    excused_absence_deduct 			= fields.Float('Excused Absence Deduct')
    no_excused_absence_deduct 		= fields.Float('No Excused Absence Deduct')
    level_type 						= fields.Selection([('s','Specific'),('o','Open')],string='Level Type')
    test_mark 						= fields.Float('Test Mark')
    reading_mark 					= fields.Float('Reading Mark')
    behavior_mark 					= fields.Float('Behavior Mark')
    registeration_fees 				= fields.Float('Registeration Fees')
    
    excused_absence 				= fields.Boolean('Excused Absence')
    no_excused_absence 				= fields.Boolean('No Excused Absence')
    comments 						= fields.Boolean('Comments')
    not_saving 						= fields.Boolean('Not Saving')
    late 							= fields.Boolean('Late')
    all_message 					= fields.Boolean('All')
