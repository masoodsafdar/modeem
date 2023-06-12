from odoo import models, fields, api
from odoo.tools.translate import _


class mk_certification(models.Model):
    _name = 'mk.certification'

    course_id       = fields.Many2one('mk.course.request',   string='Name')
    type_course     = fields.Selection([('quran_day', 'Quran day'),
                                        ('intensive_course', 'Intensive course'),
                                        ('ramadan_course', 'Ramadan course')], string="Course Type")
    students_no     = fields.Integer('Students Number')
    date            = fields.Date('Date', default = lambda self:fields.Date.today())
    #part_from_id = fields.Many2one('mk.parts', string='Part From',ondelete='restrict')
    certificate_ids = fields.One2many('mk.certification.line', 'line_id', string="Certificate")

    @api.onchange('course_id')
    def on_change_course(self):
        if self.course_id:
            self.type_course = self.course_id.course_request_type
            self.students_no = self.course_id.no_student
            
            lst = []
            for line in self.course_id.student_ids:
                dicts = {'student_id':        line.student_id.id,
                         'mosque_id':         self.course_id.mosque_id.id,
                         'state_certificate': line.attende}
                lst.append(dicts)
            
            self.certificate_ids = lst


class mk_certification_line(models.Model):
    _name = 'mk.certification.line'

    line_id           = fields.Many2one('mk.certification',    string="line certificate")
    student_id        = fields.Many2one('mk.student.register', string="Student", ondelete='cascade')
    mosque_id         = fields.Many2one('mk.mosque',                             ondelete="restrict")
    state_certificate = fields.Boolean('Certificate State')
    pass_test         = fields.Boolean('Pass Test')
