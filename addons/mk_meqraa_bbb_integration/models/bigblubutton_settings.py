# -*- coding: utf-8 -*-
from odoo import api, fields, models
import odoo


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bigbluebutton_url    = fields.Char('BigBlueButton Url',    config_parameter='bigbluebutton_url')
    bigbluebutton_secret = fields.Char('BigBlueButton Secret', config_parameter='bigbluebutton_secret')


    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param_obj = self.env['ir.config_parameter'].sudo()

        res.update(
            bigbluebutton_url=param_obj.get_param('bigbluebutton_url'),
            bigbluebutton_secret=param_obj.get_param('bigbluebutton_secret')
        )
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("bigbluebutton_url", self.bigbluebutton_url or ''),
        self.env['ir.config_parameter'].sudo().set_param("bigbluebutton_secret", self.bigbluebutton_secret or '')
        return res
