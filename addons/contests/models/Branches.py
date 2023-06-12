#-*- coding:utf-8 -*-


from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class branches(models.Model):
    _name = 'branches'
    
    name        = fields.Char('branche name' , required=True,)
    no          = fields.Integer('branche number' , required=True,)
    B_type      = fields.Selection(string='branche Type', selection=[('Qaran', 'Qaran'),('other', 'other')])
    other_info  = fields.Char('Other info', size=50)
    from_p      = fields.Many2one(string='From part', comodel_name='mk.parts', ondelete='cascade',)
    to_p        = fields.Many2one(string='To part',   comodel_name='mk.parts',ondelete='cascade')
    part_o      = fields.Selection(string='part order',   selection=[('Ascending', 'Ascending'),
                                                                     ('descending', 'descending')])
    age_r       = fields.Selection(string='Age range',    selection=[('specified', 'specified'), 
                                                                     ('not_specified', 'not specified')])
    age_cat     = fields.Many2one(string='Age cat',   comodel_name='mk.age.category', ondelete='cascade')
    age_o       = fields.Selection(string='Age order',   selection=[('ascending', 'ascending'),
                                                                    ('descending', 'descending')])
    performance = fields.Boolean('performance')
    sound_g     = fields.Boolean('sound goodness',) 
    tfseer      = fields.Boolean('tfseer',)       
    tjweed      = fields.Boolean('tjweed',)
   # @api.constrains('to_p')
    #def _check_first_part(self):
       # for r in self:
          #  if 
               # raise models.ValidationError('')

    @api.onchange
    def parts_change(self):
        if self.B_type=='other':
            self.from_p=False
            self.to_p=False
        elif self.B_type=='Qaran':
            self.other_info=False
    #@api.constrains('to_a')
    #def _check_age(self):
        #for r in self:
            #if r.to_p < from_a
            #raise models.ValidationError('Age range must be valid')

