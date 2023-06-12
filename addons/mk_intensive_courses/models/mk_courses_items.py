from odoo import models, fields


class mk_courses_items(models.Model):
    _name = 'mk.courses.items'

    name             = fields.Char('Name course')
    type_course      = fields.Selection([('sum','Summer'),
                                         ('in','Intensive')])
    description      = fields.Text()
    type_courses_ids = fields.Many2one('mk.types.courses', string="courses types")
