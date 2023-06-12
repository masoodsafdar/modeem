#-*- coding:utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class TestRegister(models.Model):    
	_name="test.questions"
	_rec_name="from_surah"

	@api.multi
	def name_get(self):
		result = []
		for record in self:
			result.append((record.id, "%s/ (%s  -  %s)" % (record.from_surah.name, record.from_aya.original_surah_order, record.to_aya.original_surah_order)))
		return result
	
	@api.depends('from_aya','to_aya')
	def get_text(self):
		#get verses between 
		for rec in self:
			#text="      "+"[["+str(rec.from_aya.original_surah_order)+"]]"+"   "+rec.from_aya.verse
			text=" "
			verses_ids=rec.env['mk.surah.verses'].search([('original_accumalative_order','>',rec.from_aya.original_accumalative_order-1),
				('original_accumalative_order','<',rec.to_aya.original_accumalative_order+1)],order='original_accumalative_order')
			if verses_ids:
				for vers in verses_ids:
					text=text+vers.verse+"  "+"[["+str(vers.original_surah_order)+"]]"+"  "
				#text=text+"  "+"[["+str(rec.to_aya.original_surah_order)+"]]"+"  "+rec.to_aya.verse
				rec.text=text	

	set_fail		= fields.Boolean(string="خصم درجة السؤال")
	session_id		= fields.Many2one("student.test.session",  string="session")
	emp_session_id  = fields.Many2one("employee.test.session", string="Emp session")
	from_surah 		= fields.Many2one('mk.surah',              string='From Sura', ondelete='restrict')# from aya
	from_aya 		= fields.Many2one('mk.surah.verses',       string='From Aya', ondelete='restrict')
	#sura 2
	to_surah 		= fields.Many2one('mk.surah',              string='To Sura',ondelete='restrict')
	#aya2
	to_aya 			= fields.Many2one('mk.surah.verses',       string='To Aya',ondelete='restrict')
	text			= fields.Text(string="question text", compute='get_text')
	error_details	= fields.One2many("question.error", "question_id", "error detials")
	follow_type 	= fields.Selection([('listen', 'Listening'),
								    	('big', 'Big Review')], string='Type of Follow', required=False,)
	state			= fields.Selection([('draft','Draft'),
										('absent','absent'),
										('start','start'),
										('done','Done test')],  string="status", default="draft")

	@api.multi
	def toggle_set_fail(self):
		if self.session_id.state!='done':
			if self.set_fail==True:
				self.write({'set_fail':False})
			else:
				self.write({'set_fail':True})

	@api.model
	def verses_test_questions(self, session_id):
		try:
			session_id = int(session_id)
		except:
			pass

		query_string = ''' 
		        SELECT test_questions.id, 
		        mk_surah_verses.id aya_id,
		        mk_surah_verses.verse

		        FROM test_questions,
		        mk_surah_verses,
		        (SELECT test_questions.id as question_id, 
		        from_aya.original_accumalative_order as from_aya_order_acc, 
		        to_aya.original_accumalative_order as to_aya_order_acc

		        FROM test_questions, 
		        student_test_session, 
		        mk_surah_verses as from_aya, 
		        mk_surah_verses as to_aya

		        WHERE test_questions.session_id = student_test_session.id AND
		        student_test_session.id = {} AND
		        test_questions.from_aya = from_aya.id AND
		        test_questions.to_aya = to_aya.id) questions

		        WHERE test_questions.id=questions.question_id AND
		        mk_surah_verses.original_accumalative_order BETWEEN questions.from_aya_order_acc AND to_aya_order_acc

		        order by test_questions.id, mk_surah_verses.id;

		        '''.format(session_id)

		self.env.cr.execute(query_string)
		verses_test_questions = self.env.cr.dictfetchall()
		return verses_test_questions

	@api.model
	def test_questions_session(self, session_id):
		try:
			session_id = int(session_id)
		except:
			pass

		query_string = ''' 
		SELECT test_questions.id as question_id,
		from_surah.name as from_surah_name,
		from_aya.id as from_aya_id,
		from_aya.page_no page_from_aya,
		to_aya.page_no page_to_aya,
		from_aya.original_surah_order as from_aya_order,
		to_surah.name as to_surah_name,
		to_aya.id as to_aya_id,
		to_aya.original_surah_order as to_aya_order,
		mk_branches_master.name,
		mk_branches_master.trackk

		FROM test_questions,
		student_test_session,
		mk_branches_master,
		mk_surah as from_surah,
		mk_surah_verses as from_aya,
		mk_surah as to_surah,
		mk_surah_verses as to_aya

		WHERE test_questions.session_id = student_test_session.id AND
		student_test_session.branch = mk_branches_master.id AND
		test_questions.from_surah = from_surah.id AND
		test_questions.from_aya = from_aya.id AND
		test_questions.to_surah = to_surah.id AND
		test_questions.to_aya = to_aya.id AND
		student_test_session.id = {} order by test_questions.id;
		'''.format(session_id)
		self.env.cr.execute(query_string)
		test_questions_session = self.env.cr.dictfetchall()
		return test_questions_session