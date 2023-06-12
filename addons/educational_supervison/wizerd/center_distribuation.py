#-*- coding:utf-8 -*-

##############################################################################
#
#    Copyright (C) Appness Co. LTD **hosam@app-ness.com**. All Rights Reserved
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
from datetime import datetime
'''
class multiple_assgin(models.TransientModel):
    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """
    
    _name = 'center.assign'
    
    pointer=fields.Many2one('comapany.pointers')
    distribuation_method=fields.Selection([('all','all centers'),('internal','internal')],default="all")
    departments = fields.Many2many('hr.department')

    lines=fields.Many2many('parent.item',string="items")


    
    @api.multi
    def yes(self):
        center_item_object=self.env['center.item']
        if self.distribuation_method=="all":
            for item in self.lines:

                for department in self.env['hr.department'].search([]):
                    item.write({'centers':[(4, department.id)]})
                    center_item_object.create({
                    'code':item.code,
                    'state':'new',
                    'item_field':item.item_field.id,
                    'item_crateria':item.item_crateria.id,
                    'item':item.item.id,
                    'item_type':item.item_type,
                    'women_men':item.women_men,
                    'need_approve':item.need_approve,
                    'item_description':item.item_description,
                    'item_degree':item.item_degree,
                    'distribuation_method':item.distribuation_method,
                    #'number_of_pointers':
                    'center_id':department.id,
                    'center_required_pointers':center_required_pointers,
                    'parent_item':item.id

                    })
                    item.write({'assigned_item_number':item.assigned_item_number+1})
                item.write({'state':'center'})
        else:
            if self.distribuation_method=="internal":
                for item in self.lines:
                    for department in self.departments:
                        item.write({'centers':[(4, department.id)]})
                        center_item_object.create({
                        'code':item.code,
                        'state':'new',
                        'item_field':item.item_field.id,
                        'item_crateria':item.item_crateria.id,
                        'item':item.item.id,
                        'item_type':item.item_type,
                        'women_men':item.women_men,
                        'need_approve':item.need_approve,
                        'item_description':item.item_description,
                        'item_degree':item.item_degree,
                        'distribuation_method':item.distribuation_method,
                        #'number_of_pointers':
                        'center_id':department.id,
                        'parent_item':item.id
                        })

                        item.write({'assigned_item_number':item.assigned_item_number+1})

                    item.write({'state':'center'})
'''
class one_center_assgin(models.TransientModel):
    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """
    _name = 'one.center.assign'
    
    pointer=fields.Many2one('comapany.pointers')
    distribuation_method=fields.Selection([('all','all centers'),('internal','internal')],default="all")
    departments = fields.Many2many('hr.department')

    lines=fields.Many2one('parent.item',string="items")
    # center_required_pointers = fields.Integer(related='lines.center_required_pointers')
    #center_required_pointers = fields.Integer()

    @api.multi
    def assgin_one(self):
        center_item_object=self.env['center.item']
        for department in self.lines.centers:
            self.lines.write({'centers':[(4, department.id)]})
            center_item_object.create({
                'code':self.lines.code,
                'state':'new',
                'item_field':self.lines.item_field.id,
                'item_crateria':self.lines.item_crateria.id,
                'item':self.lines.item.id,
                'item_type':self.lines.item_type,
                'women_men':self.lines.women_men,
                'need_approve':self.lines.need_approve,
                'item_description':self.lines.item_description,
                'item_degree':self.lines.item_degree,
                'distribuation_method':self.lines.distribuation_method,
                #'number_of_pointers':
                'center_id':department.id,
                'parent_item':self.lines.id,
                #'center_required_pointers':center_required_pointers

            })
            self.lines.write({'assigned_item_number':self.lines.assigned_item_number+1})
        self.lines.write({'state':'center'})