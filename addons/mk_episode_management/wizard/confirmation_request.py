import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PopupCustomer(models.TransientModel):
    _name = 'hr.employee.confirm.info'

    mobile = fields.Char('Mobile', size=9, required=True)
    email = fields.Char('Email', required=True)

    def action_update_info(self):
        if self.email and self.mobile:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
            if match == None:
                raise ValidationError('Not a valid E-mail ID')
            match2 = re.match('^[0-9]\d{8}$', self.mobile)
            if match2 == None:
                raise ValidationError('Invalid mobile phone')
            else:
                employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
                try:
                    employee.write({'work_email': self.email,
                                    'mobile_phone': self.mobile,
                                    'is_confirm_info': False})
                except:
                    employee.sudo().write({'work_email': self.email,
                                            'mobile_phone': self.mobile,
                                            'is_confirm_info': False})


