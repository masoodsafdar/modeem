#-*- coding:utf-8 -*-
from odoo import models, fields, api


class add_employee(models.TransientModel):
    _name = 'add.mosque'
    
    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """

    employee_id   = fields.Many2one("hr.employee",string="employee")
    department_id = fields.Many2one("hr.department","department name")
    is_dept       = fields.Boolean(string="is_dept",default=True)
    mosque_id     = fields.Many2many("mk.mosque",string="chose mosques / mosque")

    @api.onchange('department_id')
    def onchange_department_id(self):
        employee_id = self.employee_id
        category = employee_id.category
        if self.department_id:
            if category != 'edu_supervisor':
                domain = [('id', '!=', employee_id.mosqtech_ids.ids)]
            else:
                domain = [('id', '!=', employee_id.mosque_sup.ids)]
            ids = (self.env['mk.mosque'].search(domain+[('center_department_id','=',self.department_id.id)])).ids
            return {'domain': {'mosque_id': [('id','in',ids)]}}
        
        else:
            self.is_dept = False
            
    # @api.multi
    def yes(self):
        if self.employee_id.category != 'edu_supervisor':
            self.employee_id.write({'mosqtech_ids':  [(4, id)for id in self.mosque_id.ids],
                                    'department_id': self.department_id.id})
        else:
            self.employee_id.write({'mosque_sup':    [(4, id)for id in self.mosque_id.ids],
                                    'department_id': self.department_id.id})
