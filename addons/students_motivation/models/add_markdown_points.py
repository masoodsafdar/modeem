# -*- coding: utf-8 -*-
from odoo import models, fields, api ,_
from datetime import datetime
from odoo.exceptions import ValidationError


class StudentPoints(models.Model):
	_name  = 'student.points'

	name         = fields.Many2one('mk.student.register',         string="Student")
	items_ids    = fields.One2many('student.items','stu_point_id',string="Student Items")
	total_points = fields.Float(compute="compute_total_points",   string="Total Points",store=True)

	@api.one
	@api.depends('items_ids.item_id','items_ids.point')
	def compute_total_points(self):
		total = 0.0
		for rec in self.items_ids:
			total += rec.point
		self.total_points = total


class StudentItem(models.Model):
	_name  = 'student.items'

	stu_point_id = fields.Many2one('student.points',     string="Student")
	student_id   = fields.Many2one(related="stu_point_id.name")
	st_id        = fields.Many2one('mk.student.register',string="Student")
	item_id      = fields.Many2one('standard.items',     string="Standard Item")
	point        = fields.Float("Points")
	total_points = fields.Float("Points")


class Add_MarkdownPoints(models.Model):
	_name  = 'add.markdown.points'

	date       = fields.Date(string="Date",default=datetime.today())
	name       = fields.Char(compute="set_model_name",string="Name")
	state      = fields.Selection([('draft','Draft'),
							       ('confirmed','Confirmed'),
							       ('cancel','Cancel')],default='draft',string="Status")
	points_ids = fields.One2many('points.lines','p_id',                 string="Points Lines")

	@api.one
	@api.depends('date')
	def set_model_name(self):
		self.name = 'Students Points  ||  '+ str(self.date) 

	@api.multi
	def confirm_action(self):
		for stu in self.points_ids:
			student_points = self.env['student.points'].search([('name','=', stu.student_id.id)])
			if student_points:
				student_line = self.env['student.items'].search([
					('student_id','=', stu.student_id.id),
					('item_id','=',stu.standard_item_id.id)])

				if student_line:
					current_p = stu.new_item_points
					student_line.point = current_p 

				else:
					self.env['student.items'].create(
						{'stu_point_id':student_points.id,
						'item_id' : stu.standard_item_id.id,
						'point' : stu.new_item_points,
						})
			else:
				st_points = self.env['student.points'].create({
					'name' : stu.student_id.id})

				self.env['student.items'].create({
					'stu_point_id':st_points.id,
					'item_id' : stu.standard_item_id.id,
					'point' : stu.new_item_points,
					})
		self.write({'state': 'confirmed'})

	@api.multi
	def cancel_action(self):
		self.write({'state': 'cancel'})

	@api.multi
	def draft_action(self):
		self.write({'state': 'draft'})


class PointsLines(models.Model):
	_name  = 'points.lines'

	p_id                    = fields.Many2one('add.markdown.points',         string="Points id")
	episode_id              = fields.Many2one('mk.episode',		             string="Episode", required=True)
	student_id              = fields.Many2one('mk.student.register',         string="Student", required=True)
	stu_total_points        = fields.Float(compute="get_points",             string="Total Points",store=True)
	standard_item_id        = fields.Many2one('standard.items',              string="Standard Item")
	item_points             = fields.Float(related="standard_item_id.points",string="Item Points")
	current_stu_item_points = fields.Float(compute="get_points",store=True,  string="Current Standard Item Points")
	new_item_points         = fields.Float(string="New Item Points")

	@api.onchange('episode_id')
	def get_student(self):
		self.student_id = False
		return {'domain':{'student_id':[('id', 'in', self.episode_id.link_ids.ids)]}}  
	
	@api.one
	@api.depends('student_id','standard_item_id')
	def get_points(self):
		stu_points = 0.0
		item_points = 0.0

		for rec in self:
			point_id  = self.env['student.points'].search([('name','=',rec.student_id.id)])
			stu_points = point_id.total_points
			
			item_id  = self.env['student.items'].search([
				('stu_point_id' ,'=', point_id.id),
				('item_id','=',rec.standard_item_id.id)])
			

			for item in item_id:
				item_points = item.point

			rec.stu_total_points = stu_points
			rec.current_stu_item_points = item_points

	@api.constrains('new_item_points')
	def item_points_validation(self):
		for rec in self:
			if rec.new_item_points > rec.standard_item_id.points:
				raise ValidationError(_('Points cannot be greater than standard item points'))

			if rec.new_item_points < 0.0:
				raise ValidationError(_('Points cannot be less than zero'))
