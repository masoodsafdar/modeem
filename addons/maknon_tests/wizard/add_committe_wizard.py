# -*- encoding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError


class MigrationWizard(models.TransientModel):
    _name = 'add.comittee.wizard'
    _description = 'Committe Addition Wizard'

    def _get_domain_committee(self):
        sessions = self.env['student.test.session'].search([('id', 'in', self.env.context.get('default_session_ids', []))])
        centers = []
        for session in sessions:
            center_id = session.center_id.id
            if center_id not in centers:
                centers.append(center_id)
        committee_obj = self.env['committee.tests'].search([('commitee_id', 'in', centers)])
        return [('id', 'in', committee_obj.ids)]


    committee_id = fields.Many2one("committee.tests",string="Committee Member",  required=True, domain =_get_domain_committee)
    session_ids  = fields.Many2many('student.test.session', string="Sessions")
    msg_error    = fields.Char('Error Message')

    @api.multi
    def process_add(self, data):
        ids = data.get('default_session_ids', [])
        main_member=self.env['committe.member'].sudo().search([('committe_id','=',self.committee_id.id),('main_member','=',True)])

        if main_member:
            sessions = self.env['student.test.session'].sudo().search([('id', 'in', ids)])

            if not main_member[0].member_id.user_id:
                raise ValidationError(_('عفوا , عضو اللجنة الرئيسي غير مربوط بمستخدم'))

            sessions.sudo(self.env.user.id).write({'committe_id': self.committee_id.id,
                                                   'user_id': main_member[0].member_id.user_id.id})
        else:
            raise ValidationError(_('عفوا , يجب تحديد العضو الرئيسي للجنة اولا من اعدادات المركز'))
