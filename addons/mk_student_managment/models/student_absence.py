# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.osv import osv
from odoo.exceptions import Warning
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class student_absence(models.Model):    
    _name = 'mk.student_absence'
    _description = u'student_absence'
    
    # @api.multi
    def unlink(self):
        for rec in self:
            # if rec.state == "accept":
            #     raise ValidationError(_('لا يمكنك حذف سجل تم تأكيده'))
            try:
                super(student_absence, rec).unlink()
            except:
                raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))
    
    # @api.multi
    def name_get(self):
        result =[]
        
        for record in self:
            result.append((record.id, "%s, %s ,%s,%s" % (record.student_id.student_id.display_name, record.episode_id.name, record.date_from, record.date_to, )))

        return result

    leave_type  = fields.Many2one('hr.holidays.status', string='Leave type', required=True)
    date_from   = fields.Date('Date from', required=True)
    date_to     = fields.Date('Date to',   required=True)
    student_id  = fields.Many2one('mk.link', string='Student', domain = [('category', '=', False)], required=True)
    state       = fields.Selection([('draft',  'Draft'),
                                    ('accept', 'Accepted'), 
                                    ('refuse', 'Rejected')], string='State', default='draft')
    episode_id  = fields.Many2one('mk.episode', string='Episode')
    mosque_id   = fields.Many2one('mk.mosque',  string='Mosque')
    description = fields.Text('Description')

    
    @api.model
    def create(self, vals):
        user = self.env.ref('mk_student_register.portal_user_id')

        episode_id = vals.get('episode_id', False)
        mosque_id = vals.get('mosque_id', False)
        
        if not episode_id or not mosque_id:
            link_id = vals.get('student_id', False)
            link = self.env['mk.link'].search([('id','=',link_id)], limit=1)
            
            if link:
                episode = link.episode_id
                vals.update({'episode_id': episode.id,
                             'mosque_id':  episode.mosque_id.id})
        st_absence = super(student_absence, self.sudo(user.id)).create(vals)
        #create notification for mosq supervisor
        mosq_supervisor = st_absence.mosque_id.responsible_id.user_id.partner_id
        if mosq_supervisor:
            notif = self.env['mail.message'].sudo(user.id).create({'message_type': "notification",
                                                                   "subtype": self.env.ref("mail.mt_comment").id,
                                                                   'body': "لديكم طلب استأذان جديد",
                                                                   'subject': "طلب استأذان",
                                                                   'needaction_partner_ids': [(4, mosq_supervisor.id)],
                                                                   'model': self._name,
                                                                   'res_id': st_absence.id,
                                                                   })
        return st_absence
    
    @api.constrains('date_to', 'date_from')
    def _check_date(self):
        if (self.date_to < self.date_from):
                raise ValidationError(_('Invalid Date To'))
            
        if (self.date_to < self.episode_id.study_class_id.start_date or self.date_to > self.episode_id.study_class_id.end_date):
                raise ValidationError(_('absence request must be within episode study class period'))
                
    @api.onchange('mosque_id')
    def onchange_mosque(self):
        mosque_id = self.env['mk.mosque'].search([('id', '=', self.mosque_id.id)])
        res = {'domain': {'episode_id':[('id', 'in', mosque_id.episode_id.ids)]}}
        
        return res

    @api.onchange('episode_id')
    def onchange_episode(self):
        students = []
        link_ids = self.env['mk.link'].search([('episode_id', '=', self.episode_id.id),
                                               ('state','=','accept')])
        for link in link_ids:
            students.append(link.student_id.id)
            
        res = {'domain': {'student_id':[('id', 'in', link_ids.ids)]}}
        
        return res  
    
    # @api.multi
    def action_accept(self):
        self.write({'state':'accept'})

    # @api.multi
    def action_draft(self):
        self.write({'state':'draft'})

    # @api.multi
    def action_reject(self):
        self.write({'state':'refuse'})

    @api.model
    def student_permissions(self, link_id):
        query_string = ''' 
              select to_char(p.create_date, 'YYYY-MM-DD') as create_date, 
                     student_id, 
                     to_char(date_from, 'YYYY-MM-DD') as date_from, 
                     to_char(date_to, 'YYYY-MM-DD') as date_to,
                     tp.name as leave_type,
                     state,
                     episode_id, 
                     mosque_id
              from mk_student_absence p left join hr_holidays_status tp on tp.id=p.leave_type
              where student_id={};
              '''.format(link_id)
        self.env.cr.execute(query_string)
        student_permissions = self.env.cr.dictfetchall()
        return student_permissions
