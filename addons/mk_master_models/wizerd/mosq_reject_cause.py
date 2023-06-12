from odoo import models, fields, api

class MosqueRejectWizard(models.TransientModel):
    _name = 'mosq.reject.wizard'

    reject_reason = fields.Text('Reject Reason', required=True)

    # @api.multi
    def action_ok(self):
        mosque_id = self.env['mk.mosque'].browse(self.env.context['active_id'])
        reject_reason = self.reject_reason
        mosque_id.write({'reject_reason': reject_reason,
                         'state': 'reject'})
        return {'type': 'ir.actions.act_window_close'}