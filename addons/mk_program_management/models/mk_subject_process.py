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


class MkSubjectProcess(models.Model):
	_name = 'mk.subject.process'

	# @api.one
	def create_subjects(self):
		parts= []
		surah_obj = self.env['mk.surah']
		subject_obj = self.env['mk.subject.configuration']
		verses_obj = self.env['mk.surah.verses']
		if self.program_id.program_purpose == 'memorize_quran':
			parts= self.env['mk.parts'].search([])
		elif self.program_id.program_purpose == 'memorize_part':
			for part in self.approach_id.part_ids:
				parts.append(part)
		parts_ids = [x.id for x in parts]
		verses= verses_obj.search([('part_id','in',parts_ids)],order="original_accumalative_order asc")
		if self.program_id.program_purpose == 'memorize_surah':
			verses= verses_obj.search([('surah_id','in',[x.id for x in self.approach_id.surah_ids])],order="original_accumalative_order asc")
		lines_total= 0
		for v in verses:
			lines_total += (v.line_no or 0)
		line_subject= (self.subject_no > 0) and (lines_total/self.subject_no) or 0
		if (line_subject - int(line_subject)) > 0:
			line_subject = int(line_subject) + 1
		c= 0
		lst=[]
		from_verse= False
		to_verse= False
		from_surah= False
		to_surah= False
		parts= False
		last_verse = False
		last_surah = False
		order = False
		if line_subject > 0:
			while (c < self.subject_no):
				count = 0
				from_verse= False
				to_verse= False
				from_surah= False
				to_surah= False
				parts= False
				for ve in verses:
					if order and (ve.original_accumalative_order < order):
						continue
					if not from_verse:
						from_verse= ve.id
						from_surah= ve.surah_id.id
					count += (ve.line_no or 0)
					if count >= line_subject:
						to_verse= ve.id
						to_surah= ve.surah_id.id
						parts= ve.part_id.id
						order= ve.original_accumalative_order
						break
				c += 1
				lst.append({
					'from_verse':from_verse,
					'to_verse':to_verse or from_verse,
					'from_surah':from_surah,
					'to_surah':to_surah or from_surah,
					'part_id':parts,
					'is_test':self.is_test,
					'order':c,
					'program_id':self.program_id.id,
					'approach_id':self.approach_id.id,
					'mosque_id':self.mosque_id.id,
					'center_department_id':self.center_department_id.id,
					'subject_process_id': self.id,
					'name':str(self.program_id and (self.program_id.name.encode('utf-8','ignore') + '-') or '') + str(self.approach_id and (self.approach_id.name.encode('utf-8','ignore') + '-') or '') + str(c),
					})
			for lin in lst:
				subject_obj.create(lin)




	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mk.subject.process'))  
	center_department_id = fields.Many2one('hr.department', string='Center')
	mosque_id = fields.Many2one('mk.mosque', string='Mosque')
	program_id = fields.Many2one('mk.programs', string='Program') 
	approach_id = fields.Many2one('mk.approaches', string='Approach') 
	subject_no = fields.Integer('Number of Subjects')
	is_test = fields.Boolean('Test After End of Subject')

		#_sql_constraints = [
		#   ('approach_id_uniq', 'unique (approach_id)', "The Approach must be Unique!"),
		#]

	"""@api.model    
		def fields_view_get(self, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
		res = super(MkSubjectProcess, self).fields_view_get(view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		nodes = doc.xpath("//field[@name='company_id']")
		company_ids = []
		company_recs= self.env['mk.study.year'].search([])
        company_ids = [x.company_id.id for x in company_recs]
        domain = "[('id', 'in', " + str(company_ids) + ")]"
	for node in nodes:
		node.set('domain', domain)
        res['arch'] = etree.tostring(doc)
        return res
    """
