import json

import requests
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class MkNotification(models.Model):
    _name ='mk.notification'

    name                   = fields.Char("Notification", required=True )
    description            = fields.Text("Description")
    department_id          = fields.Many2one("hr.department", string="Department", required=True)
    category               = fields.Selection(string="Category", selection=[('center_admin',   'مدراء / مساعدي مدراء المركز'),
                                                                            ('supervisor',     'مشرفين وإداريين المسجد / المدرسة'),
                                                                            ('admin',          'المشرف العام للمسجد /المدرسة'),
                                                                            ('edu_supervisor', 'مشرف تربوي'),
                                                                            ('teacher',        'المعلمين'),
                                                                            ('managment',      'إداري\إداريين'),
                                                                            ('others',         'خدمات مساعدة'),
                                                                            ('bus_sup',        'مشرف الباص')], required=True)
    employee_ids           = fields.Many2many("hr.employee", string="Employees")
    type_notification      = fields.Selection(string="Notification type", selection=[('general_notif', 'General notification'),
                                                                                     ('personal_notif', 'Personal notification')],default='general_notif', required=True, )
    notification_lines_ids = fields.One2many("mk.notification.line", inverse_name="notification_id", string="Notifications")
    date_notification      = fields.Date("Date", required=True, default=fields.Date.today())
    state                  = fields.Selection(string="State", selection=[('draft',     'Draft'),
                                                                         ('confirmed', 'Employee list confirmed'),
                                                                         ('sent',      'Sent')], default='draft', required=True )

    @api.onchange('department_id','category','type_notification')
    def employee_ids_onchange(self):
        self.employee_ids = False
        department_id = self.department_id
        category = self.category
        type_notification = self.type_notification
        
        if department_id and category and type_notification == 'general_notif':
            employees = self.env['hr.employee'].search([('department_id','=',department_id.id),
                                                        ('category','=',category)])
            self.employee_ids = employees.ids

    @api.one
    def action_confirm(self):
        self.write({'state': 'confirmed'})

    @api.one
    def action_send(self):
        employee_notifications = []
        notification_id = self.id
        date_notification = self.date_notification
        
        for employee in self.employee_ids:
            vals = {'notification_id':   notification_id,
                    'employee_id':       employee.id,
                    'date_notification': date_notification}
            employee_notifications.append((0, 0, vals))
        
        self.notification_lines_ids = employee_notifications
        self.write({'state': 'sent'})
        url = 'https://fcm.googleapis.com/fcm/send'

        headers = {'Content-type': 'application/json','Authorization': 'key=AAAAiPvPe44:APA91bEh3l70jz0lJfkDpyqrqPIjCtdTKbh5nqQO11x9-kkvKtQEEXKZDtT6LYgSGfgeh5ChFz5HctzHvJ1y0cObpI4E-KOalM1wlnStyTmAgJl10rnOUsMgt6OBLQG8rAbMzkEHxzEn'}
        notification_lines = self.notification_lines_ids.ids
        while len(notification_lines) > 0:
            lines = self.env['mk.notification.line'].search([('id', 'in', notification_lines)], limit=5)
            to = ""
            for line in lines:
                to += "'teacher_%d' in topics ||" % (line.employee_id.id)
                notification_lines.pop(0)

            prms = {
                "condition": to[:-2],
                'data': {
                    'click_action': 'FLUTTER_NOTIFICATION_CLICK',
                    'open_screen': 'notifications'
                },
                'notification': {
                    'title': self.name,
                    'body': self.description,
                    'sound': 'default'
                }
            }
            try:
                response = requests.post(url, data=json.dumps(prms), headers=headers)
            except:
                pass


class MkNotificationLine(models.Model):
    _name ='mk.notification.line'

    @api.one
    @api.depends('notification_id', 'employee_id')
    def compute_name(self):
        self.name = self.notification_id.name + ' ل ' + self.employee_id.name

    name              = fields.Char("Name", compute="compute_name", store=True)
    notification_id   = fields.Many2one("mk.notification", string="Notification", required=True)
    date_notification = fields.Date("Date")
    date_viewed       = fields.Date("Date viewed")
    employee_id       = fields.Many2one("hr.employee",              string="Employee",     required=True)
    state             = fields.Selection(string="State", selection=[('draft',               'Draft'),
                                                                    ('notification_viewed', 'Notification viewed')], default='draft', required=True )
    @api.one
    def action_notification_view(self):
        self.write({'state':       'notification_viewed',
                    'date_viewed': fields.Date.today()})
        
    @api.model
    def consult_notification(self, notification_id):

        notification = self.search([('id','=',notification_id),
                                    ('state','=','draft')], limit=1)
        if notification:
            notification.action_notification_view()
            return 1
        return 0

    @api.model
    def teacher_mobile_noitifications(self, teacher_id):
        try:
            teacher_id = int(teacher_id)
        except:
            pass

        query_string = ''' 
            select l.id, 
                   n.name, 
                   n.description, 
                   l.state, to_char(l.date_notification, 'YYYY-MM-DD') date_notification
            from mk_notification_line l left join mk_notification n on l.notification_id=n.id
            where l.employee_id={};
            '''.format(teacher_id)
        self.env.cr.execute(query_string)
        notifications = self.env.cr.dictfetchall()
        return notifications

