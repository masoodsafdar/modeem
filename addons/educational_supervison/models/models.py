# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Items(models.Model):
    _name = 'edu.item'

    # master
    item_number = fields.Integer()
    name = fields.Char()
    item_degree = fields.Char()
    need_approve = fields.Boolean()
    approval_type = fields.Binary()
    item_description = fields.Char()
    criterion = fields.Many2many('edu_v2.criterion')
    #all_centers = fields.Boolean()
    #all_supervisors = fields.Boolean()
    #company_required_pointers = fields.Integer()
    
    '''
    @api.constrains('company_required_pointers')
    def _check_required_pointers(self):
        sup_count=number of supervisors fe aljm3ia
        for r in self:
            
            if r.all_centers&&r.all_supervisors&&company_required_pointers< r.sup_count:
                raise models.ValidationError('المؤشر المطلوب من جميع الجمعية يجب ان يساوي او يزيد عن عدد المشرفين التربويين')
    '''

    #item type (visit / date)
class Criteria(models.Model):
    _name = 'edu.criterion'
    # master
    criterion_number = fields.Integer()
    name = fields.Char()
    criterion_weight = fields.Integer()
    items = fields.Many2many('edu_v2.item')

class Names(models.Model):
    _name = 'edu_v2.name'

    # master
    name = fields.Char()
    number = fields.Integer()

class Fields(models.Model):
    _name = 'edu.field'
    # master
    name = fields.Char()
    number = fields.Integer()

class Visits(models.Model):
    _name = 'edu_v2.visit'
    # master
    name = fields.Char()
    number = fields.Integer()
    sudden = fields.Boolean()

class Approvess(models.Model):
    _name = 'edu_v2.approve'
    #master
    name = fields.Char()
    number = fields.Integer()



class ItemsManagement(models.Model):
    #_name = 'edu_v2.pointer'
    _name='center.distribuation'
    # Items Managment (Centers distribuation)
    
    _rec_name = 'date'

    date=fields.Date(string="date")

    lines = fields.One2many('parent.item','pointer_dist')



    """name = fields.Char(compute="get_name")

    @api.one
    def get_name(self):
        self.name = str(self.create_date)

    state = fields.Selection([('draft','draft'),('confirm','confirmed'),('c_distribute','Center Distributed'),('s_distribute','Supervisor Distributed'),('done','منجز')],default="draft")

    field = fields.Many2one('edu_v2.field')
    center = fields.Many2many('hr.department', 'pointer')
    supervisors = fields.One2many('edu_v2.supervisor', 'distribute')
    supervision = fields.Many2one('edu_v2.name')

    lines = fields.One2many('edu_v2.pointer.line','pointer_dist')
    # lines_dist = fields.One2many('edu_v2.pointer.line','pointer_dist')
    pointers = fields.Integer()
    assigned = fields.Integer(compute="get_item_assigned",store=True)
    item_count = fields.Integer(compute="get_item_count")


    @api.depends('lines')
    def get_item_assigned(self):
        count=0
        for item in self.lines:
            if item.state=='assigned':
                count+=1
        self.assigned=count

    @api.one
    def get_item_count(self):
        count = 0
        for line in self.lines:
            count += 1
        self.item_count = count

    @api.one
    def confirm(self):
        self.state = 'confirm'

    @api.one
    def distribute(self):
        self.state = 'c_distribute'

    @api.multi
    def s_distribute(self):
        if self.lines:
            for line in self.lines:
                for supervisor in self.supervisors:
                    line.supervisors = [(4,supervisor.id)]
            self.state = 's_distribute'

    """
class DistributionWizard(models.TransientModel):
    _name = 'edu_v2.distribute.supervisor'

    name = fields.Char()

    # center = fields.Many2one('edu_v2.center',كز")
    # supervisors = fields.One2many('edu_v2.supervisor','distribute',المشرف")
    # supervision = fields.Many2one('edu_v2.name', الإشراف")
    # lines = fields.One2many('edu_v2.distribute.supervisor.line','distribute')

    # item_count = fields.Integer(لي عدد البنود",compute="get_item_count")

    # @api.one
    # def get_item_count(self):
    #     count = 0
    #     for line in self.lines:
    #         count += 1
    #     self.item_count = count

    # @api.one
    # def distribute(self):
    #     if self.lines:
    #         for line in self.lines:
    #             line.state = 'distributed'
        

# class PointerDistributionSupervisorLine(models.Model):
#     _name = 'edu_v2.distribute.supervisor.line'

#     name = fields.Char()
#     distribute = fields.Many2one('edu_v2.distribute.supervisor')
#     field = fields.Many2one('edu_v2.field',ال")
#     criterion = fields.Many2one('edu_v2.criterion',يار")
#     item = fields.Many2one('edu_v2.item',د")
#     item_degree = fields.Char( البند")
#     pointers = fields.Integer(شر المطلوب")
#     state = fields.Selection([('draft','draft'),('distributed','distributed')])

#     @api.onchange('item')
#     def item_change(self):
#         self.item_degree = self.item.item_degree

# class SupervisorAssessment(models.Model):
#     _name = 'edu_v2.supervisor.assessment'

#     center = fields.Many2one('edu_v2.center')
#     supervision = fields.Many2one('edu_v2.name')

#     lines = fields.One2many('edu_v2.supervisor.assessment.line','assessment')

#     item_count = fields.Integer(compute="get_item_count")

#     @api.one
#     def get_item_count(self):
#         count = 0
#         for line in self.lines:
#             count += 1
#         self.item_count = count

# class SupervisorAssessmentLine(models.Model):
#     _name = 'edu_v2.supervisor.assessment.line'

#     assessment = fields.Many2one('edu_v2.supervisor.assessment')

#     supervisor = fields.Many2one('edu_v2.supervisor')
#     field = fields.Many2one('edu_v2.field')
#     criterion = fields.Many2one('edu_v2.criterion')
#     item = fields.Many2one('edu_v2.item')
#     item_degree = fields.Char()
#     pointers = fields.Integer()
#     done = fields.Integer()
#     notes = fields.Char()

#     @api.onchange('item')
#     def item_change(self):
#         self.item_degree = self.item.item_degree

class SupervisorItemManagement(models.Model):
    _name = 'edu_v2.supervisor.item.management'

    supervisor = fields.Many2one('edu_v2.supervisor')

    items = fields.Many2many('edu_v2.pointer.line')
    visits = fields.One2many('edu_v2.supervisor.item.management.visit','manage')


    @api.multi
    def get_items(self):
        for sup in self.env['edu_v2.pointer.line'].search([('supervisors','in',self.supervisor.id)]):
            self.items = [(4,sup.id)]

    @api.multi
    def confirm(self):
        if self.visits:
            for visit in self.visits:
                if not visit.visit_type.sudden:
                    self.env['edu_v2.visit.assessment'].create({
                        'date': visit.date,
                        'item': visit.item.id,
                        'supervisor' : self.supervisor.id,
                    })

# class SupervisorItemManagementItem(models.Model):
#     _name = 'edu_v2.supervisor.item.management.item'

#     manage = fields.Many2one('edu_v2.supervisor.item.management')

#     item = fields.Many2one('edu_v2.item')
#     item_description = fields.Char()
#     pointer = fields.Many2one('edu_v2.pointer')
#     attachment = fields.Binary()
#     approval_type = fields.Char()
#     date = fields.Date()
#     done = fields.Char()
#     notes = fields.Char()

class SupervisorItemManagementVisit(models.Model):
    _name = 'edu_v2.supervisor.item.management.visit'

    manage = fields.Many2one('edu_v2.supervisor.item.management')

    visit_type = fields.Many2one('edu_v2.visit')
    location = fields.Text()
    date = fields.Date()
    item = fields.Many2one('edu_v2.item')
    attachment = fields.Binary()
    approval_type = fields.Char()
    done = fields.Binary()
    notes = fields.Char()

class VisitAssessment(models.Model):
    _name = 'edu_v2.visit.assessment'

    date = fields.Date()
    item = fields.Many2one('edu_v2.item')
    supervisor = fields.Many2one('hr.employee')
    visited = fields.Boolean()
    notes = fields.Char()
    state = fields.Selection([('draft','Draft'),('done','Done')],default="draft")

    @api.one
    def confirm(self):
        self.state = 'done'
        