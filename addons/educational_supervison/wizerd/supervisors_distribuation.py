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
from odoo.exceptions import UserError
from odoo import models, fields, api,_
from datetime import datetime
class multiple_assgin(models.TransientModel):
    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """
    _name = 'sup.assign'
    
    item=fields.Many2one('center.item',string="item")

    supervisors = fields.Many2many('supervisor.pointer',string="supervisors")
    required_of_pointers=fields.Integer(string="required pointers number")
    distribuation_method=fields.Selection([('all','all centers'),('internal','internal')],default="all")

    @api.onchange('item')
    def item_change(self):
        if self.item.women_men=='women':
            return {'domain':{'supervisors':[('gender','=','female'),('category','=','edu_supervisor'),('department_id','=',self.item.center_id.id)]}}
        else:
            if self.item.women_men=='men':
                return {'domain':{'supervisors':[('gender','=','male'),('category','=','edu_supervisor'),('department_id','=',self.item.center_id.id)]}}
            else:
                return {'domain':{'supervisors':[('category','=','edu_supervisor'),('department_id','=',self.item.center_id.id)]}}

    @api.multi
    def yes(self):

        sup_item_object=self.env['supervisor.item']
        if self.distribuation_method=='internal':

            for supervisor in self.supervisors:
                sup_item_object.create({
                        'code':self.item.code,
                        'state':'new',
                        'item_field':self.item.item_field.id,
                        'required_of_pointers':self.required_of_pointers,
                        'item_crateria':self.item.item_crateria.id,
                        'item':self.item.item.id,
                        'need_approve':self.item.need_approve,
                        'item_type':self.item.item_type,
                        'women_men':self.item.women_men,
                        'item_description':self.item.item_description,
                        'item_degree':self.item.item_degree,
                        'distribuation_method':self.item.distribuation_method,
                        #'number_of_pointers':
                        'supervisor':supervisor.id,
                        'center_parent':self.item.id
                        })
                self.item.write({'assigned_item_number':self.item.assigned_item_number+1})            
            self.item.write({'state':'distribuated','required_of_pointers':self.required_of_pointers})
            #self.item.parent_item.write({'state':'distribuated'})
        else:
            if self.distribuation_method=='all':
                if self.item.women_men=='women':
                    domain=[('gender','=','female'),('category','=','edu_supervisor'),('department_id','=',self.item.center_id.id)]
                else:
                    if self.item.women_men=='men':
                        domain=[('gender','=','male'),('category','=','edu_supervisor'),('department_id','=',self.item.center_id.id)]
                    else:
                        domain=[('category','=','edu_supervisor'),('department_id','=',self.item.center_id.id)]

                for supervisor in self.env['hr.employee'].search(domain):
                    sup_item_object.create({
                    'code':self.item.code,                        
                    'state':'new',
                    'required_of_pointers':self.required_of_pointers,                    
                    'item_field':self.item.item_field.id,
                    'item_crateria':self.item.item_crateria.id,
                    'item':self.item.item.id,
                    'item_type':self.item.item_type,
                    'women_men':self.item.women_men,                    
                    'need_approve':self.item.need_approve,
                    'item_description':self.item.item_description,
                    'item_degree':self.item.item_degree,
                    'distribuation_method':self.item.distribuation_method,
                    #'number_of_pointers':
                    'supervisor':supervisor.id,
                    'center_parent':self.item.id
                    })
                    self.item.write({'assigned_item_number':self.item.assigned_item_number+1})
                self.item.write({'state':'distribuated','required_of_pointers':self.required_of_pointers})
                #self.item.parent_item.write({'state':'distribuated'}) 

class one_assgin(models.TransientModel):
    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """
    _name = 'one.sup.assign'
    
    item=fields.Many2one('center.item',string="item")

    supervisors = fields.Many2many('hr.employee',string="supervisors",domain=[('category','=','edu_supervisor')])
    required_of_pointers=fields.Integer(string="required pointers number")
    distribuation_method=fields.Selection([('all','all centers'),('internal','internal')],default="all")



    @api.multi
    def assign_one(self):

        sup_item_object=self.env['supervisor.item']
        if self.distribuation_method=='internal':
            for supervisor in self.supervisors:
                sup_item_object.create({
                        'state':'new',
                        'item_field':self.item.item_field.id,
                        'item_crateria':self.item.item_crateria.id,
                        'item':self.item.item.id,
                        'item_type':self.item.item.item_type,
                        'women_men':self.item.item.women_men,                        
                        'need_approve':self.item.need_approve,
                        'item_description':self.item.item_description,
                        'item_degree':self.item.item_degree,
                        'distribuation_method':self.item.distribuation_method,
                        #'number_of_pointers':
                        'supervisor':supervisor.id,
                        'center_parent':self.item.id
                        })
            
            self.item.write({'state':'distribuated','required_of_pointers':self.required_of_pointers})
            self.item.parent_item.write({'state':'distribuated'})
        else:
            if self.distribuation_method=='all':
                for supervisor in self.env['hr.employee'].search([('category','=','edu_supervisor'),('state','=','accept'),('department_id','=',center_parent.center_id)]):
                    sup_item_object.create({
                    'state':'new',
                    'item_field':self.item.item_field.id,
                    'item_crateria':self.item.item_crateria.id,
                    'item_type':self.item.item.item_type,
                    'women_men':self.item.item.women_men,                    
                    'item':self.item.item.id,
                    'need_approve':self.item.need_approve,
                    'item_description':self.item.item_description,
                    'item_degree':self.item.item_degree,
                    'distribuation_method':self.item.distribuation_method,
                    #'number_of_pointers':
                    'supervisor':supervisor.id,
                    'center_parent':self.item.id
                })

                self.item.write({'state':'distribuated','required_of_pointers':self.required_of_pointers})
                self.item.parent_item.write({'state':'distribuated'})     