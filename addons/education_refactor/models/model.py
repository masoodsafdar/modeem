from odoo import api, fields, models


class refactor_courses(models.Model):
    _name = 'refactor.courses'

    surah_order = fields.Integer('Surah order')
    part_order = fields.Integer('Part Order')
    verse_original_order = fields.Integer('Verse Order')
    course_type = fields.Integer('Course Type')
    course_id = fields.Integer('Course Number')
    status = fields.Integer('Status')
    test = fields.Integer('Test')

    to_surah_order = fields.Integer('To Surah order')
    to_part_order = fields.Integer('To Part Order')
    to_verse_original_order = fields.Integer('To Verse Order')
    to_course_type = fields.Integer('To Course Type')
    to_course_id = fields.Integer('To Course Number')
    to_status = fields.Integer('To Status')
    to_test = fields.Integer('To Test')
    