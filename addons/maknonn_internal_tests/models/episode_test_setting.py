#-*- coding:utf-8 -*-

##############################################################################
#
#    Copyright (C) Appness Co. LTD **hosam@app-ness.com**. All Rights Reserved
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from odoo.tools.translate import _

class EpisodeTestSetting(models.Model):
	_name = 'episode.internal.test'
	name=fields.Char(string="Test Name",required="1")
	test_date=fields.Date(string="Test Date",required="1")
	start_point=fields.Selection([('from_start','From start'),('from_last','From Last')],string="start point",default='from_last')
	state=fields.Selection([('draft','Draft'),('start','Start'),('done','Done')],string="Status")
	maximum_degree=fields.Integer(string="Maximum degree",required="1")
	minumim_degree=fields.Integer(string="Minum degree",required="1")
	#relation with episode
	episode_id=fields.Many2one("mk.episode",string="episode")
	#relation with altaqum
	passing_items=fields.Many2many("mk.passing.items",string="passing items")
	evaluation_items=fields.Many2many("mk.evaluation.items",string="evaluation")

class studentTestSession(models.Model):
	_name = 'episode.student.test.session'
	_rec_name='student_id'

	student_id=fields.Many2one("mk.link",string="student")
	test_id=fields.Many2one("episode.internal.test",string="Test")
	state=fields.Selection([('draft','Draft'),('absent','absent'),('start','start'),('done','Done test')],default="draft",string="status")
	test_question=fields.One2many("test.questions","internal_session_id","session questions",domain=[('follow_type','=','listen')])
	test_question_big=fields.One2many("test.questions","internal_session_id","session questions",domain=[('follow_type','=','big')])
	degree=fields.Integer(string="Deserved degree")
	maximum_degree=fields.Integer(related='test_id.maximum_degree',string="Maximum degree")
	appreciation=fields.Selection([
	    ('excellent','Excellent'),('v_good','Very good'),
	    ('good','Good'),('acceptable','Acceptable'),
	    ('fail','Fail')],string="appreciation")




	def start_exam(self):

			#@## CASE 1
		if self.test_id.start_point=='from_start':
			# go to student preparatin and get done sves lines as quation
			student_prepration=self.env['mk.student.prepare'].search([('link_id','=',self.student_id.id)])
			if student_prepration:
				save_lines=self.env['mk.listen.line'].search([('preparation_id','=',student_prepration[0].id),
															  ('type_follow','=','listen'),
															  ('state','=','done')])
				if save_lines:
					for line in save_lines:
						self.env['test.questions'].create({
							'internal_session_id':self.id,
							'from_surah':line.from_surah.id,
							'from_aya':line.from_aya.id,
							'to_surah':line.to_surah.id,
							'to_aya':line.to_aya.id,
							'follow_type':'listen',
							#'listen_order':line.order
						})
						line.write({'is_test':False})
					save_lines[len(save_lines)-1].write({'is_test':True})
						
				big_lines=self.env['mk.listen.line'].search([('preparation_id','=',student_prepration[0].id),
															 ('type_follow','=','review_big'),
															 ('state','=','done')])
				if big_lines:
					#big_lines[]
					for line in big_lines:
						self.env['test.questions'].create({
							'internal_session_id':self.id,
							'from_surah':line.from_surah.id,
							'from_aya':line.from_aya.id,
							'to_surah':line.to_surah.id,
							'to_aya':line.to_aya.id,
							'follow_type':'big',
							#'big_order':line.order
						})
						line.write({'is_test':False})
					big_lines[len(big_lines)-1].write({'is_test':True})

			self.write({
				'state':'start'
				})
		
		#@## CASE 1
		if self.test_id.start_point=='from_last':
			#print("############################# case 2")
			student_prepration=self.env['mk.student.prepare'].search([('link_id','=',self.student_id.id)])
			if student_prepration:
				start_point=self.env['mk.listen.line'].search([('is_test','=',True),
															('preparation_id','=',student_prepration[0].id),
															('type_follow','=','listen'),
															('state','=','done')])
				if start_point:
					start_point[0].write({'is_test':False})
					save_lines=self.env['mk.listen.line'].search([('id','>',start_point[0].id),
																  ('preparation_id','=',student_prepration[0].id),
																  ('type_follow','=','listen'),
																  ('state','=','done')])
					
				else:
					save_lines=self.env['mk.listen.line'].search([('preparation_id','=',student_prepration[0].id),
																  ('type_follow','=','listen'),
																  ('state','=','done')])
				if save_lines:
					for line in save_lines:
						self.env['test.questions'].create({
							'internal_session_id':self.id,
							'from_surah':line.from_surah.id,
							'from_aya':line.from_aya.id,
							'to_surah':line.to_surah.id,
							'to_aya':line.to_aya.id,
							'follow_type':'listen',
							#'listen_order':line.order
						})
						line.write({'is_test':True})
				big_start_point=self.env['mk.listen.line'].search([('is_test','=',True),
																   ('preparation_id','=',student_prepration[0].id),
																   ('type_follow','=','review_big'),
																   ('state','=','done')])
				if big_start_point:
					big_start_point[0].write({'state','=',True})
					big_start_point=self.env['mk.listen.line'].search([('id','>',big_start_point[0].id),
																	   ('preparation_id','=',student_prepration[0].id),
																	   ('type_follow','=','review_big'),
																	   ('state','=','done')])

				else:
					big_start_point=self.env['mk.listen.line'].search([('preparation_id','=',student_prepration[0].id),
																	   ('type_follow','=','review_big'),
																	   ('state','=','done')])

				if big_lines:
					for line in big_lines:
						self.env['test.questions'].create({
							'internal_session_id':self.id,
							'from_surah':line.from_surah.id,
							'from_aya':line.from_aya.id,
							'to_surah':line.to_surah.id,
							'to_aya':line.to_aya.id,
							'follow_type':'big',
							#'big_order':line.order
						})
						line.write({'is_test':True})
				"""self.write({
				'state':'start'
				})"""

	#def end_exam_session(self,session_id):

	@api.multi
	def end_exam(self):
		degree=0
		for q in self.test_question:
			#print("#####################3",q)
			for error in q.error_details:
				#print("#####################3",error)
				degree=degree+(error.value*error.item.amount)
		for q in self.test_question_big:
			#print("#####################3",q)
			for error in q.error_details:
				#print("#####################3",error)
				degree=degree+(error.value*error.item.amount)


		self.degree=self.test_id.maximum_degree-degree
		self.state='done'

		appreciation_ids=self.env['mk.passing.items'].search(['&','&',('internal_tests','in',self.test_id.id),'|',('from_degree','>',self.test_id.maximum_degree-degree),('from_degree','=',self.test_id.maximum_degree-degree),'|',('to_degree','<',self.test_id.maximum_degree-degree),('to_degree','=',self.test_id.maximum_degree-degree)])
		if appreciation_ids:
			#print("****************",appreciation_ids)
			self.appreciation=appreciation_ids[0].appreciation


class TestRegister(models.Model):    
	_inherit="test.questions"
	internal_session_id=fields.Many2one("episode.student.test.session",string="internal session")
	state=fields.Selection([('draft','draft'),('done','done')],string="state",default="draft")
class episode(models.Model):    
	_inherit="mk.episode"

	episode_tests=fields.One2many("episode.internal.test","episode_id","Inernal test")

class TestPassingItems(models.Model):
    _inherit = 'mk.passing.items'
    internal_tests=fields.Many2many("episode.internal.test",string="Internal tests")


class TestEvaluationItems(models.Model):
    _inherit = 'mk.evaluation.items'

    internal_tests=fields.Many2many("episode.internal.test",string="Internal tests")

class mk_link(models.Model):
    _inherit = 'mk.link'

    internal_tests=fields.One2many("episode.student.test.session","student_id","internal test result")

