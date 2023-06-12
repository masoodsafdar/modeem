from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class NominationTypes(models.Model):
    _name = 'result.managment'
    rec_name='name'

    date       = fields.Date("Date", required=True, default=fields.Date.today())
    contest    = fields.Many2one('contest.preparation',    string='contest',required=True)
    result_ids = fields.One2many('mk.results','result_id', string='results')

    @api.onchange('contest')
    def delete_lines(self):
    	if self.contest:
    		result=[]
	    	self.result_ids=result

