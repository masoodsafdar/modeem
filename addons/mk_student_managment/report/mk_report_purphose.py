from odoo import models, fields, api, tools
import datetime
from odoo.exceptions import Warning
from odoo import models, fields, api, tools
import datetime
from odoo.exceptions import Warning
class mk_report_purphose(models.Model):
    _name='mk.report.purphose'
    _rec_name="name"

    name=fields.Char(string="Name")
    active = fields.Boolean(
        string='Active',default=True
    )