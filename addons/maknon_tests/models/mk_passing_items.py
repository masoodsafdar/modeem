from odoo import models, fields, api

    
class TestPassingItems(models.Model):
    _name = 'mk.passing.items'
    _inherit=['mail.thread','mail.activity.mixin']
    _rec_name = 'display_name'

    @api.multi
    def get_display_name(self):
        for record in self:
            name = " "
            appreciation = record.appreciation
            if appreciation == 'excellent':
                name = "ممتاز"
            elif appreciation == 'v_good':
                name = "جيد جدا"
            elif appreciation == 'good':
                name = "جيد"
            elif appreciation == 'acceptable':
               name = "مقبول"
            elif appreciation == 'fail':
               name = "راسب"

            name = name + " [" + str(record.from_degree) + " - " + str(record.to_degree) + " ]"
            record.display_name = name


    display_name       = fields.Char(compute="get_display_name", string="Name", store=True)
    #Relations Fields
    active   = fields.Boolean(string="active",default=True,groups="maknon_tests.group_passing_items_archives", tracking=True)
    branches = fields.Many2many("mk.branches.master",string="Branches")
    #Primary Fields
    from_degree  = fields.Integer(string="From Degree", required="1", tracking=True)
    to_degree    = fields.Integer(string="to Degree",   required="1", tracking=True)
    appreciation = fields.Selection([('excellent',  'Excellent'),
                                     ('v_good',     'Very good'),
                                     ('good',       'Good'),
                                     ('acceptable', 'Acceptable'),
                                     ('fail',       'Fail')], string="appreciation", tracking=True)
    