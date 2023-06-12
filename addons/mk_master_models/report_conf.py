from odoo import models, fields, api
from datetime import datetime
from odoo.tools.translate import _


class ReportConfig(models.Model):
    _name = 'mk.report.config'

    company_id = fields.Many2one('res.company', string='Company',
    default=lambda self: self.env.user.company_id.id)

    print_with_header = fields.Boolean(
        string='Print With Header',
    )
    print_with_footer = fields.Boolean(
        string='Print With Footer',
    )
