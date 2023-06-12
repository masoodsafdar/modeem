from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

class UpdateDegree(models.TransientModel):
    _name = 'update.degree'
    _description = 'Update degree'

    force_degree  = fields.Float(string="Force degree")

    @api.one
    def update_degree(self,data):
        student_session_id = data.get('active_ids', [])
        force_degree = self.force_degree
        if force_degree > 0:
            student_test_session = self.env['student.test.session'].search([('id', '=', student_session_id)])
            student_test_session.write({'force_degree': force_degree})
        else :
            raise ValidationError(_('الدرجة المعدلة يجب أن تكون أكبر من 0 !'))

