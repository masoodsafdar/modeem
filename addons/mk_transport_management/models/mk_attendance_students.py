from odoo import models, fields, api
from datetime import datetime
import calendar    
import dateutil.parser
class AttendanceStudent(models.Model):
    _name = 'mk.attendance.students'
    rec_name = 'vehicle_id'

    date = fields.Date('Date', default=fields.Date.today())
    mosque_id=fields.Many2one('mk.mosque', 'Mosque')
    vehicle_id = fields.Many2one('vehicle.records', string='Vehicle')
    supervisor_id = fields.Many2one('hr.employee','Bus Supervisor', domain="[('category','=','bus_sup')]")
    state = fields.Selection([
    ('draft','Draft'),
    ('confirm','Confirm'),
    ('cancle','Cancle')], 'Status', default='draft')
    stud_attend_ids = fields.One2many('attendance.students.line', 'line_id', 'Attendance Students')
    period = fields.Selection(
        string='Period',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False,
        selection=[('subh', 'subh'),('zuhr', 'zuhr'),('aasr','aasr'),('magrib','magrib'),('esha','esha')]
    )
    go_return = fields.Selection(
        string='Go return',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False,
        selection=[('go', 'go'), ('return', 'return')]
    )
    @api.v8
    @api.onchange('vehicle_id','period','go_return','date')
    def get_students(self):
        request_ids=[]
        students=[]
        new_lines=[]
        day = dateutil.parser.parse(self.date).date()
        #day=d.get_weekday()
        week_day=calendar.day_name[day.weekday()]
        
        if week_day=='Saturday':

            week_day ='السبت'
        elif week_day=='Thursday':
            week_day ='الخميس'
        
        elif week_day=='Sunday':
            week_day ='حد'
        elif week_day=='Monday':
            week_day ='ثنين'
        elif week_day=='Tuesday':
            week_day ='الثلاثاء'
        elif week_day=='Wednesday':
            week_day ='ربع'
        elif week_day=='Friday':
            week_day ='الجمعة'
        week_day_id=self.env['mk.work.days'].sudo().search([('name','like',week_day)])
        domain=[('vehicle_id','=',self.vehicle_id.id),('state','=','confirm'),('trans_period','=',self.period),('days_ids','in',week_day_id.ids)]
        apology_domain=[('date','=',self.date)]
        if self.go_return=='go':
            domain=[('transport_type','in',['go_only','go&return']),('vehicle_id','=',self.vehicle_id.id),('state','=','confirm'),('trans_period','=',self.period),('days_ids','in',week_day_id.ids)]
            apology_domain=[('date','=',self.date),('transport_type','in',['go_only','go&return'])]
        elif self.go_return == 'return':
            domain=[('transport_type','in',['return_only','go&return']),('vehicle_id','=',self.vehicle_id.id),('state','=','confirm'),('trans_period','=',self.period),('days_ids','in',week_day_id.ids)]
            apology_domain=[('date','=',self.date),('transport_type','in',['return_only','go&return'])]
        tansport_management=self.env['mk.transport.management'].sudo().search(domain)

        #for rec in tansport_management:
        #    request_ids.append(rec.request_id.id)

        #requests=self.env['transportation.request'].search([('transportation_days','in',week_day_id.ids),('id','in',request_ids)])
        apologize_requests=self.env['apology.request'].sudo().search(apology_domain)
        for apologize in apologize_requests:
            students.append(apologize.student_id.id)
        for trans_rec in tansport_management:
            if trans_rec.request_id.student_id.id in students:
                new_lines.append({'student_id':trans_rec.request_id.student_id.id,'apologize':True})
            else:
                new_lines.append({'student_id':trans_rec.request_id.student_id.id,'presence':True})
        self.stud_attend_ids=[(0,0,new) for new in new_lines]
        '''
        apologize_requests=self.env['apology.request'].search([('date','=',self.date)])
        for apologize in apologize_requests:
            students.append(apologize.student_id.id)
        students_line=self.env['attendance.students.line'].search([('student_id','in',students),('id','in',self.stud_attend_ids.ids)])
        for line in students_line:
            line.write({'apologize':True})
        '''
    @api.one
    def act_confirm(self):
        self.sudo().get_students()
        self.sudo().state='confirm'
        
    @api.one
    def act_cancle(self):
    	self.state='cancle'

    
   
        
class AttendanceStudentLine(models.Model):
    _name = 'attendance.students.line'
    rec_name = 'vehicle_id'

    line_id = fields.Many2one('mk.attendance.students', 'Line ID')
    student_id = fields.Many2one('mk.link', string='Student')
    presence = fields.Boolean('Presence')
    absent = fields.Boolean('Absent')
    delivered = fields.Boolean('Delivered')
    apologize = fields.Boolean(
        string='Apologize',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )
    note = fields.Text('Note')
