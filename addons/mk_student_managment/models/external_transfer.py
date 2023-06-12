from odoo import models,fields,api, tools,_
from odoo.exceptions import UserError

import pytz
from odoo.tools.translate import _

from time import gmtime, strftime
from lxml import etree

import logging
_logger = logging.getLogger(__name__)

mosque_ids=[]
mosques=[]
student_link=0
std_id=0
student_links=[]

class mk_student_external_transfer(models.Model):
    _name='mk.external_transfer'

    @api.model
    def create(self,vals):
        link_ids = self.env['mk.link'].sudo().search([('state','=','accept'),
                                                      ('student_id', '=',vals['student_id'])])        
        student_periods = [link['selected_period'] for link in link_ids]
        if vals['select_period'] in student_periods:
            vals.update({'same_period':True})
        
        return super(mk_student_external_transfer, self).create(vals)

    @api.onchange('identity_no','no_identity','passport_no')
    def invistigate_identity(self):
        global std_id
        global mosques
        if self.no_identity:
            if self.passport_no:
                if not self.create_date:
                    query = """SELECT id, display_name FROM mk_student_register where passport_no = '%s' ;""" %(str(self.passport_no))
                    self.env.cr.execute(query)
                    student = self.env.cr.dictfetchall()
                    emp = self.env['hr.employee'].sudo().search([('user_id','=',self.env.user.id),
                                                                 ('category','in',['admin','supervisor'])])
                    
                    if student:
                        query_mosque = """select mk_mosque.name as mosque_name ,mk_mosque.id, hr_department.name from mk_mosque , hr_department where hr_department.id=mk_mosque.center_department_id and mk_mosque.id in( SELECT mk_mosque_id FROM mk_mosque_mk_student_register_rel where mk_student_register_id = %d);""" %(student[0]['id'])
                        self.env.cr.execute(query_mosque)
                        results=self.env.cr.dictfetchall()
                        
                        self.flag2 = True
                        mosque_names = ""
                        center_names = ""
 
                        if not results:
                            mosque_names = "لا يوجد حاليا إرتباط بمسجد"
                            center_names = "لا يوجد حاليا إرتباط بمركز"
                            
                        for result in results:
                            mosque_names += result['mosque_name']
                            mosque_names += ","
                            center_names += result['name']
                            center_names += ","
                        #global std_id
                        std_id = student[0]['id']
                        self.student_id = student[0]['id']
                        self.student_name = student[0]['display_name']
                        #self.mosque_id=[(4,emp.mosque_id.id)]
                        self.mosque_name = str(mosque_names)
                        self.center_name = str(center_names)
                        self.name = "_"
                        return {'domain':{'from_mosque':[('id','in',result['id'])]}}

        else:
            if self.identity_no:
                mosques=[]
                
                if not self.create_date:
                    student_id = self.env['mk.student.register'].sudo().search([('identity_no','=',self.identity_no)], limit = 1)
                    
                    emp = self.env['hr.employee'].sudo().search([('user_id','=',self.env.user.id),
                                                                 ('category','in',['admin','supervisor'])])
                    if not student_id:
                        self.create_date=strftime("%Y-%m-%d %H:%M:%S", gmtime())
                        
                    if student_id:    
                        self.flag2 = True
                        mosque_names = ""
                        center_names = ""
 
                        if not student_id.mosque_id:
                            mosque_names = "لا يوجد حاليا إرتباط بمسجد"
                            center_names = "لا يوجد حاليا إرتباط بمركز"
                            
                        else:
                            for mosque in student_id.mosque_id:
                                mosque_names += mosque.name
                                mosque_names += ","
                                center_names += mosque.center_department_id.name
                                center_names += ","
                        
                        std_id = student_id.id
                        self.student_id = student_id.id
                        self.student_name = student_id.display_name
                        #self.mosque_id=[(4,emp.mosque_id.id)]
                        mosque_ids = student_id.sudo().mosque_id.ids
                        #global mosques
                        for mos in student_id.mosque_id:
                            mosques.append((str(mos.id),mos.name))
                        self.mosque_name = str(mosque_names)
                        self.center_name = str(center_names)
                        self.name = "_"

                        self.get_mosques(mosques)
                        a = self.get_mosques_ids()
                        return {'domain': {'from_mosque': [('id','in',mosque_ids)]}}

    @api.onchange('from_mosque')
    def get_from_episode(self):
        msq = self.from_mosque.id
        eps_ids = []
        study_year = self.env['mk.study.year'].sudo().search([('active','=',True),
                                                              ('is_default','=',True)],limit=1)

        link_ids = self.env['mk.link'].sudo().search([('year','=',study_year.id),
                                                      ('id','in',self.student_id.link_ids.ids),
                                                      ('state','=','accept'),
                                                      ('mosq_id','=',self.from_mosque.id)])
        for link in link_ids:
            global student_links
            student_links.append({'student_link': link.id,
                                  'episode':      link.episode_id,
                                  'period':       link.episode_id.selected_period})
            
            eps_ids.append(link.episode_id.id)
            
        return {'domain': {'from_episode':[('id','in',eps_ids)]}}

    @api.onchange('to_mosque')
    def get_to_episode(self):
        episode_ids = self.env['mk.episode'].sudo().search([('mosque_id','=',self.to_mosque.id),
                                                            ('unoccupied_no','>',0),
                                                            ('state','=','accept')])

        return {'domain': {'to_episode':[('id','in',episode_ids.ids)]}}

    @api.onchange('to_episode')
    def get_episode(self):
        self.select_period = self.to_episode.selected_period

    def get_mosques(self, mosques):
        return mosques
    
    def get_mosques_ids(self):        
        return [('a','A')]

    def get_mosque(self):
        resource = self.env['resource.resource'].sudo().search([('user_id','=',self.env.user.id)])

        if resource.ids:
            employee_id = self.env['hr.employee'].sudo().search([('resource_id','in',resource.ids)])
            msjd_id=self.env['mk.mosque'].sudo().search([('responsible_id','in',employee_id.ids)])
                    
        return msjd_id
    
    # @api.multi
    def send_clearnce_request(self):
        clearance_ids = self.env['mk.clearance'].sudo().search([('student','=',self.student_id.id),
                                                                ('mosque_id','=',self.from_mosque.id),
                                                                ('episode_id','=',self.from_episode.id)])
        if clearance_ids:
            self.clearance_id=clearance_ids[0].id
            
        else:
            clearance_id = self.env['mk.clearance'].sudo().create({'student':    self.student_id.id,
                                                                   'mosque_id':  self.from_mosque.id,
                                                                   'episode_id': self.from_episode.id})
            self.clearance_id=clearance_id.id
            
        self.write({'state':'clearnce'})

    @api.depends('student_id','from_mosque','from_episode')
    def calcalute_listen_rate(self):
        lines_object=self.env['mk.listen.line']
        study_year=self.env['mk.study.year'].sudo().search([('active','=',True),
                                                            ('is_default','=',True)],limit=1)
        if study_year:
            student=self.env['mk.link'].sudo().search([('id','in',self.student_id.link_ids.ids),
                                                       ('year','=',study_year.id),
                                                       ('mosq_id','=',self.from_mosque.id),
                                                       ('state','=','accept'),
                                                       ('episode_id','=',self.from_episode.id)])
            if len(student.ids) == 1:
                all_planned_lines=lines_object.sudo().search([('student_id','=',student[0].id),
                                                              ('type_follow','=','listen')],order='order')
                done_lines=lines_object.sudo().search([('student_id','=',student[0].id),
                                                       ('type_follow','=','listen'),
                                                       ('state','=','done')],order='order')
                if all_planned_lines:
                    self.listen_rate = (len(done_lines)/len(all_planned_lines))*100
                    self.preparation_id = all_planned_lines[0].preparation_id.id

    @api.depends('clearance_id','state','same_period','student_id')
    def clearance_visibility(self):
        if not self.clearance_id and self.state =='draft' and self.same_period and self.student_id:
            self.clearance_visible=True
            
        if self.clearance_id:
            self.clearance_visible=False

    @api.depends('state','same_period')
    def accept_visibility(self):
        if self.state =='draft' and not self.same_period and self.student_id:
            self.accept_visible=True

    # @api.multi
    def action_accept_transfer(self):
        clearance = self.clearance_id
        if clearance and clearance.state == 'draft':
                raise UserError(_("عذرا! لم يتم قبول طلب خلو الطرف بعد"))
            
        if self.same_period and not clearance:
            raise UserError(_("عذرا! يجب ارسال طلب خلو الطرف لنقل الطالب بفتره مشابهة"))
        
        study_year = self.env['mk.study.year'].sudo().search([('active','=',True),
                                                              ('is_default','=',True)],limit=1)
        
        student = self.env['mk.link'].sudo().search([('id','in',self.student_id.link_ids.ids),
                                                     ('year','=',study_year[0].id),
                                                     ('mosq_id','=',self.from_mosque.id),
                                                     ('state','=','accept'),
                                                     ('episode_id','=',self.from_episode.id)])
        
        values = {'student_id':         self.student_id.id, 
                  'registeration_code': student.student_id.registeration_code, 
                  'episode_id':         self.to_episode.id,
                  'mosq_id':            self.to_mosque.id,
                  'program_id':         student.program_id.id,
                  'approache':          student.approache.id,
                  'program_type':       student.program_type,
                  'page_id':            student.page_id.id,
                  'selected_period':    self.select_period,
                  'part_id':            [(4,part) for part in student.part_id.ids],
                  'start_point':        student.start_point.id,
                  'review_direction':   student.review_direction,
                  'student_days':       [(4,day) for day in self.student_days.ids]}
        
        new_link_student = self.env['mk.link'].sudo().create(values)

        self.write({'state': 'accept'})
        
        if self.to_mosque.id not in self.student_id.mosque_id.ids:
            self.student_id.sudo().write({'mosque_id': [(4,self.to_mosque.id)]})
        
        if clearance:
            new_link_student.sudo().write({'state': 'accept'})
            self.preparation_id.sudo().write({'stage_pre_id': self.to_episode.id,
                                              'link_id':      new_link_student.id,
                                              'name':         self.to_episode.teacher_id.id})
            
        mail = self.env['mail.message']
        message = "تم تنسيب الطالب  "+ self.student_id.display_name + " لمسجدكم"
        message2 = "تم إخلاء طرف الطالب "+ self.student_id.display_name
        
        vals = {'message_type': 'notification',
                'subject':      'نقل ',
                'body':         message,
                'partner_ids':  [(6, 0, [self.to_mosque.responsible_id.resource_id.user_id.partner_id.id])]}
        
        if clearance:
            vals2={'message_type': 'notification',
                   'subject':      'إخلاء طرف ',
                   'body':         message2,
                   'partner_ids':  [(6, 0, [self.clearance_id.create_uid.id])] }
            mail.sudo().create(vals2)
            
        mail.sudo().create(vals)

    # @api.multi
    def action_reject(self):
        self.write({'state':'reject'})
        mail=self.env['mail.message']
        message="تم رفض طلب إخلاء طرف الطالب  "+ self.Student_id.display_name

        vals={'message_type': 'notification',
              'subject':      'نقل ',
              'body':          message,
              'partner_ids':   [(6, 0, [self.to_mosque.responsible_id.resource_id.user_id.partner_id.id])] }
        
        mail.sudo().create(vals)
        self.write({'same_period':False})
    
    @api.onchange('from_episode')
    def get_period(self):
        for item in student_links:
            if item['episode'].id == self.from_episode.id:
                self.period = item['period']
                global student_link
                student_link = item['student_link']

    clearance_visible = fields.Boolean('Accept clearance', compute=clearance_visibility)
    accept_visible    = fields.Boolean('Accept visible',   compute=accept_visibility,)
    no_identity       = fields.Boolean('No Identity')
    identity_no       = fields.Char('Identity No', size=10)
    passport_no       = fields.Char('Passport No', size=10)
    student_id        = fields.Many2one('mk.student.register', string='Student',             ondelete='cascade')
    preparation_id    = fields.Many2one('mk.student.prepare',  string='Student preparation', ondelete='cascade', compute=calcalute_listen_rate)
    listen_rate       = fields.Integer("saving per%")
    student_name      = fields.Char('Student name', size=50, translate=True)
    mosque_name       = fields.Char('Mosque name',  size=50, translate=True)
    center_name       = fields.Char('Center name',  size=50, translate=True)
    flag2             = fields.Boolean('Flag')
    from_episode      = fields.Many2one('mk.episode', string='from episode', required=True, ondelete='restrict')
    period            = fields.Selection([('subh', 'subh'), 
                                          ('zuhr', 'zuhr'),
                                          ('aasr','aasr'),
                                          ('magrib','magrib'),
                                          ('esha','esha')], string='Period')
    to_episode        = fields.Many2one('mk.episode',       string='To episode', required=True, ondelete='restrict')    
    select_period     = fields.Selection([('subh',   'subh'), 
                                          ('zuhr',   'zuhr'),
                                          ('aasr',   'aasr'),
                                          ('magrib', 'magrib'),
                                          ('esha',   'esha')],       string='Select period')
    new_transfer      = fields.Selection([('new',      'New'), 
                                          ('transfer', 'Transfer')], string='New transfer')
    to_mosque         = fields.Many2one('mk.mosque', string='To mosque',   ondelete='cascade')
    from_mosque       = fields.Many2one('mk.mosque', string='from mosque', ondelete='cascade')
    state             = fields.Selection([('draft',    'Draft'),
                                          ('clearnce', 'clearance request'),
                                          ('accept',   'Accept'), 
                                          ('reject',   'Reject')], string='State', readonly=True, default='draft')
    subh              = fields.Boolean('Subh')
    same_period       = fields.Boolean('same')
    zuhr              = fields.Boolean('Zuhr')
    aasr              = fields.Boolean('Aasr')
    maghrib           = fields.Boolean('Maghrib')
    ishaa             = fields.Boolean('Ishaa')
    clearance_id      = fields.Many2one('mk.clearance',  string='Clearance', ondelete='cascade')
    student_days      = fields.Many2many('mk.work.days', string='work days', ondelete="restrict")


class wizard_message(models.TransientModel):
    _name = 'wizard.message'

    name         = fields.Text('Warning',  readonly=True)
    student_id   = fields.Many2one('mk.student.register', string='Student',      ondelete='cascade')
    to_episode   = fields.Many2one('mk.episode',          string='from episode', ondelete='restrict', required=True, store=True)
    from_episode = fields.Many2one('mk.episode',          string='from episode', ondelete='restrict', required=True, store=True)
    to_mosque    = fields.Many2one('mk.mosque',           string='To mosque',    ondelete='cascade')
    from_mosque  = fields.Many2one('mk.mosque',           string='from mosque',  ondelete='cascade')   
    clearance_id = fields.Many2one('mk.clearance',        string='Clearance',    ondelete='cascade')

    # @api.multi
    def ok(self):
        self.env['mk.external_transfer'].sudo().create({'student_id':   self._context.get('student_id',False),
                                                        'from_mosque':  self._context.get('from_mosque'),
                                                        'from_episode': self._context.get('from_episode'),
                                                        'to_mosque':    self._context.get('to_mosque',False),
                                                        'to_episode':   self._context.get('to_episode',False),
                                                        'clearance_id': self._context.get('clearance_id',False)})
