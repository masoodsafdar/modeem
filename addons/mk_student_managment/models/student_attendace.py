from odoo import models, fields, api, tools
import datetime
import logging
_logger = logging.getLogger(__name__)

class student_attendace(models.Model):
	_name='mk.student.attendace'

	student =fields.Many2one("mk.link", string="Student", required=True, ondelete='cascade')
	state = fields.Selection([('absent', 'absent'),
							  ('attended','attended'),
							  ('leave','leave')],"state", default="attended")
	absence_request=fields.Many2one("mk.student_absence","absence request",ondelete='restrict')
	episode_attendace_id=fields.Many2one("mk.episode.attendace",string="episode",ondelete='cascade')

	
	episode=fields.Many2one("mk.episode","episode",)
	subh = fields.Boolean('Subh')
	zuhr = fields.Boolean('Zuhr')
	aasr = fields.Boolean('Aasr')
	magrib = fields.Boolean('Magrib')
	esha = fields.Boolean('Esha')

	@api.onchange('subh')
	def subh_onchange(self):
		if self.subh:
			students=[]
			students_object=self.env['mk.link']
			ids=students_object.search(['&','&',('subh','=',True),('episode_id','=',self.episode.id),('state','=','accept')])
			for rec in ids:
				if rec not in students :
					students.append(rec.id)
			return {'domain':{'student':[('id','in',students)]}}

	@api.onchange('zuhr')
	def zuhr_onchange(self):
		if self.zuhr:
			students=[]
			students_object=self.env['mk.link']
			ids=students_object.search(['&','&',('zuhr','=',True),('episode_id','=',self.episode.id),('state','=','accept')])
			for rec in ids:
				if rec not in students :
					students.append(rec.id)
			return {'domain':{'student':[('id','in',students)]}}

	@api.onchange('aasr')
	def aasr_onchange(self):
		if self.aasr:
			students=[]
			students_object=self.env['mk.link']
			ids=students_object.search(['&','&',('aasr','=',True),('episode_id','=',self.episode.id),('state','=','accept')])
			for rec in ids:
				if rec not in students :
					students.append(rec.id)
			return {'domain':{'student':[('id','in',students)]}}

	@api.onchange('magrib')
	def magrib_onchange(self):
		if self.magrib:
			students=[]
			students_object=self.env['mk.link']
			ids=students_object.search(['&','&',('magrib','=',True),('episode_id','=',self.episode.id),('state','=','accept')])
			for rec in ids:
				if rec not in students :
					students.append(rec.id)
			return {'domain':{'student':[('id','in',students)]}}

	@api.onchange('esha')
	def esha_onchange(self):
		if self.esha:
			students=[]
			students_object=self.env['mk.link']
			ids=students_object.search(['&','&',('esha','=',True),('episode_id','=',self.episode.id),('state','=','accept')])
			for rec in ids:
				if rec not in students :
					students.append(rec.id)
			return {'domain':{'student':[('id','in',students)]}}
	_defaults={
			'episode':lambda self, cr, uid, ctx:ctx.get('episode',False),
			'subh':lambda self, cr, uid, ctx:ctx.get('subh',False),
			'zuhr':lambda self, cr, uid, ctx:ctx.get('zuhr',False),
			'aasr':lambda self, cr, uid, ctx:ctx.get('aasr',False),
			'magrib':lambda self, cr, uid, ctx:ctx.get('magrib',False),
			'esha':lambda self, cr, uid, ctx:ctx.get('esha',False),

	}
	
	def get_student_attendance_record(self,student_id):
		academic_recs = self.env['mk.study.year'].search([('active','=',True),
                                                          ('is_default','=',True)])
		year=0
		if academic_recs:
			year=academic_recs[0].id
		mk_student_object=self.env['mk.link'].search([('student_id','=',int(student_id)),('year','=',year)])
		#if mk_student_object:
		mk_student_id=mk_student_object[0].id
		student_object=self.env['mk.student.attendace']
		student_ids=student_object.search([('student','=',mk_student_id)])
		episode_id=0
		episode_name=''
		teacher_id=0
		teacher_name=''
		date=''
		mosque_id=0
		mosque=''
		student_id=0
		student_name=''
		status=''
		records=[]
		period=''
		if student_ids:
			for rec in student_ids:
				episode_id=rec.episode_attendace_id.episode.id
				if rec.episode_attendace_id.episode.name:
					episode_name= rec.episode_attendace_id.episode.name.encode('utf-8','ignore')
				else:
					episode_name=False
				teacher_id=rec.episode_attendace_id.teacher.id
				if rec.episode_attendace_id.teacher.name:
					teacher_name=rec.episode_attendace_id.teacher.name.encode('utf-8','ignore')
				else:
					teacher_name=False
				date=rec.episode_attendace_id.date
				mosque_id=rec.episode_attendace_id.masjed.id
				if rec.episode_attendace_id.masjed.name:
					mosque=rec.episode_attendace_id.masjed.name.encode('utf-8','ignore')
				else:
					mosque=False
				student_id=rec.student.student_id.id
				if rec.student.student_id.display_name:
					student_name=rec.student.student_id.display_name.encode('utf-8','ignore')
				status=rec.state
				if rec.student.subh==True:
					period="subh"
				if rec.student.aasr==True:
					period="asar"
				if rec.student.zuhr==True:
					period="zuhr"
				if rec.student.esha==True:
					period="esha"
				if rec.student.magrib==True:
					period="magrib"
				rec_dict=({
					'id':rec.id,
					'student_id':student_id,
					'student_name':str(student_name),
					'date':date,
					'episode_id':episode_id,
					'episode_name':str(episode_name),
					'mosque_id':mosque_id,
					'mosque_name':str(mosque),
					'teacher_id':teacher_id,
					'teacher_name':str(teacher_name),
					'status':str(status),
					'period':period,
					'absence_request':rec.id
				})
				records.append(rec_dict)


		return records
	# @api.multi
	def test(self):
		self.get_student_attendance_record(3)
