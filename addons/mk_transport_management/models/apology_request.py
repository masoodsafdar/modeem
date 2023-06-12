from odoo import models, fields, api
from odoo.tools.translate import _
from datetime import datetime

class apology_request(models.Model):
    _name = 'apology.request'
    _rec_name = 'student_id'

    student_id=fields.Many2one('mk.link', string='Student')
    date = fields.Date(string='Date', default=fields.datetime.now() ) 
    absent_reason =fields.Char(string='Absent Reason')
    transport_type=fields.Selection([('go&return','ذهاب وعودة'),('go_only','ذهاب فقط'),('return_only','عودة فقط')])
