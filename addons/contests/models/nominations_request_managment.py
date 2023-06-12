from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError

class NominationTypes(models.Model):
    _name = 'nomination.request.managment'
    _rec_name='contest'

    nomation_date   = fields.Date(string="Nomation Date",default=fields.Date.today(), required=True)
    nomination_type = fields.Many2one('nomination.types',    string='nomination.type',required=True)
    contest         = fields.Many2one('contest.preparation', string='contest',        required=True)
    notify          = fields.Boolean('Notify')
    candidaties     = fields.Many2many('nomination.process', 'nomination_manag_nomination_process_student_rel', 'nomination_manag_id', 'nomination_process_id', string='candidates',domain=[('nomination_type','=','student')])
    work_plan_ids   = fields.One2many('mk.work_plan','nomination_request',string='nomination request')
    result_ids      = fields.One2many('mk.results','nomination_request',  string='results')
    managers        = fields.Many2many('nomination.process', 'nomination_manag_nomination_process_manag_rel', 'nomination_manag_id', 'nomination_process_id', string='candidates',domain=[('nomination_type','=','manager')])
    man             = fields.Many2many('nomination.process', 'nomination_manag_nomination_process_ref_rel', 'nomination_manag_id', 'nomination_process_id', string='candidates',domain=[('nomination_type','=','ref')])
    
#     @api.onchange('contest')
#     def on_contest(self):        
#         students = self.env['nomination.process'].search([('contest','=',self.contest.id),('nomination_type','=','student')])        
#         list.append(students.ids)
#         self.candidaties = list
#         manager = self.env['nomination.process'].search([('contest','=',self.contest.id),('nomination_type','=','ref')])
#         self.managers = manager.ids
    
    @api.onchange('contest')
    def onchange_contest(self):
        students = self.env['nomination.process'].search([('contest','=',self.contest.id),('nomination_type','=','student')])
        
        self.update({'candidaties':[(4, student_id)for student_id in students.ids]})
        
        manager = self.env['nomination.process'].search([('contest','=',self.contest.id),('nomination_type','=','manager')])
        self.update({'managers':[(4, manager_id)for manager_id in manager.ids]})

        man = self.env['nomination.process'].search([('contest','=',self.contest.id),('nomination_type','=','ref')])
        self.update({'man':[(4, ref_id)for ref_id in man.ids]})

    @api.multi
    def accept_all_student(self):
        for rec in self.candidaties:
            rec.write({'state':'accept'})

    @api.multi
    def accept_all_managers(self):
        for rec in self.managers:
            rec.write({'state':'accept'})

    @api.multi
    def accept_all_refrees(self):
        for rec in self.man:
            rec.write({'state':'accept'})
        #for st in students:
        #    result.append((0, 0, {'make': line.make, 'type': line.type}))
        #self.car_ids = result

    #candidat
    

class work_plan(models.Model):
    _name = 'mk.work_plan'
    _description = u'work plan'
    rec_name='day'

    day                = fields.Selection(string='Day', selection=[('sat', 'saturday'), 
                                                                   ('sun', 'sunday'),
                                                                   ('mon','monday'),
                                                                   ('tues','tuesday'),
                                                                   ('wedn','wednesday'),
                                                                   ('thurs','thursday'),
                                                                   ('friday','friday')])
    program_name       = fields.Char('program name', required=True, index=True, size=50)
    nomination_request = fields.Many2one(string='nomination request', comodel_name='nomination.request.managment', ondelete='cascade')
    date               = fields.Date('Date')
    place              = fields.Char('Place', size=50)
    attachment         = fields.Many2many(string='Attachement',       comodel_name='ir.attachment', ondelete='cascade')
    achived            = fields.Selection(string='Achieved', selection=[('achive', 'achived'),
                                                                        ('not', 'not achived')])
    notice             = fields.Char('Notice')
    
    @api.constrains('date')
    def contest_date(self):
        for rec in self:
            if rec.date and rec.nomination_request.contest.StartD:
                if (rec.date < rec.nomination_request.contest.StartD):
                    raise models.ValidationError('تاريخ بداية الخطة يجب أن يكون داخل الفترة الزمنية المسابقة')
            if rec.date and rec.nomination_request.contest.endD:
                if rec.date> rec.nomination_request.contest.endD:
                    raise models.ValidationError('تاريخ نهاية الخطة يجب أن يكون داخل الفترة الزمنية للمسابقة')


class results(models.Model):
    _name = 'mk.results'
    _description = u'results'
    rec_name='test'

    @api.onchange('result_id.contest','student')
    def onchange_contest(self):
        students=self.env['nomination.process'].sudo().search([('nomination_type','=','student'),
                                                               ('contest','=',self.result_id.contest.id),
                                                               ('state','=','accept')])
       
        return {'domain':{'student':[('id','in', students.ids)]}}

    student            = fields.Many2one(string='Student', comodel_name='nomination.process', ondelete='cascade', domain=onchange_contest, required=True)
    mosque_id          = fields.Many2one(string='Mosque',  comodel_name='mk.mosque',     ondelete='cascade')
    center             = fields.Many2one( string='Center', comodel_name='hr.department', ondelete='cascade')
    student_phone      = fields.Char("student phone", related='student.student_phone',)   
    order              = fields.Integer('Order')
    degree             = fields.Float('Degree', default=0.0,digits=(16, 2))
    nomination_request = fields.Many2one(string='nomination request', comodel_name='nomination.request.managment',                   ondelete='cascade')
    result_id          = fields.Many2one(string='result request',     comodel_name='result.managment',                               ondelete='cascade')
    test_type          = fields.Many2one(string='Test Type',          comodel_name='mk.test.names',domain=[('is_contest','=', True)],ondelete='cascade',)
    test_branches      = fields.Many2one(string='Branches',           comodel_name='mk.branches.master', ondelete='cascade')
  
    @api.onchange('test_branches')
    def get_degree(self):
        degree=self.env['student.test.session'].sudo().search([('state','=','done'),('student_id','=',self.student.candidate_student.id),('branch','=',self.test_branches.id)])
        if degree:
            self.degree=degree.degree
        else:
            self.degree=0.00
    

    # test = fields.Char(
    #     string='Test',
    #     required=False,
    #     readonly=False,
    #     index=False,
    #     default=None,
    #     help=False,
    #     size=50,
    #     translate=False
    # )


    @api.onchange('student')
    def on_student(self):
        #students=self.env['nomination.process'].search([('contest','=',self.contest.id),('nomination_type','=','student')])
        self.mosque_id=self.student.mosque.id
        self.center=self.student.mosque.center_department_id.id
        #manager=self.env['nomination.process'].search([('contest','=',self.contest.id),('nomination_type','=','manager')])
        #self.update({'managers':[(4, id)for id in manager.ids]})

    @api.onchange('test_type')
    def get_branches(self):
        branches_ids=self.env['mk.branches.master'].sudo().search([('test_name','=',self.test_type.id)]).ids
        return {'domain':{'test_branches':[('id', 'in', branches_ids)]}}
    

