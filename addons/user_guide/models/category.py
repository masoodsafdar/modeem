from datetime import date, timedelta,datetime
from dateutil.relativedelta import relativedelta, MO
from odoo import api , fields, models,_
from odoo.exceptions import UserError, ValidationError

class GuideCategory(models.Model):
    _name = "user.guide.category"

    name = fields.Char(string="Category Name", )
    department_id = fields.Many2one('hr.department', string='Department')


