from odoo import models, fields, api, _, tools
import logging

_logger = logging.getLogger(__name__)


class MailTemplate(models.Model):
    _name = 'mail.template'
    _inherit = ['mail.template', 'mail.thread']

    back             = fields.Binary('Background', tracking=True)
    repport_type     = fields.Selection([('mosuqe_permession', 'Setting rapport mosque repport'),
                                         ('mosuqe_school_permession', 'إعداد تقريرتصريح مدرسة'),
                                         ('mosque_supervisor', 'إعداد تقريرتكليف مشرف مسجد'),
                                         ('school_supervisor', 'إعداد تقريرتكليف مشرف مدرسة'),
                                         ('mosque_directors',  'إعداد تقرير تكليف مديرة مدرسة')], string='Repport type', required=True, tracking=True)
    body_html2       = fields.Html('Body2', tracking=True)
    is_arabic_number = fields.Boolean('Request Arabic Number', tracking=True)
    width            = fields.Char('Width', tracking=True)
    height           = fields.Char('Height', tracking=True)

    _sql_constraints = [
        ('repport_type', 'unique (repport_type)', 'The Repport type must be unique !')
    ]

    # @api.multi
    def open_template(self):
        model_name = self.model_id.name
        if self.env.ref('mk_episode_management.template_repport_permession').id == self.id:
            obj = self.env[model_name].search([('perm_type', '=', 'mosque_perm'), ('is_valid', '=', True)], limit=1)
            res = self.env.ref('mk_episode_management.report_permitions_k').report_action(obj)

        elif self.env.ref('mk_episode_management.template_repport_school_permession').id == self.id:
            obj = self.env[model_name].search([('perm_type', '=', 'school_perm'), ('is_valid', '=', True)], limit=1)
            res = self.env.ref('mk_episode_management.report_permitions_k').report_action(obj)

        elif self.env.ref('mk_episode_management.repport_mosque_supervisors').id == self.id:
            obj = self.env[model_name].search([('type_request', '=', 'supervisor_request'), ('categ_type', '=', 'male'), ('is_valid', '=', True)], limit=1)
            res = self.env.ref('mk_episode_management.responsible_permision_report_id').report_action(obj)

        elif self.env.ref('mk_episode_management.repport_school_supervisors').id == self.id:
            obj = self.env[model_name].search([('type_request', '=', 'supervisor_request'), ('categ_type', '=', 'female'), ('is_valid', '=', True)], limit=1)
            res = self.env.ref('mk_episode_management.responsible_permision_report_id').report_action(obj)

        elif self.env.ref('mk_episode_management.repport_mosque_directors').id == self.id:
            obj = self.env[model_name].search([('type_request', '=', 'admin_request'), ('is_valid', '=', True)], limit=1)
            res = self.env.ref('mk_episode_management.responsible_permision_report_id').report_action(obj)

        # elif model_name == 'student.test.session':
        #     obj = self.env[model_name].search([('state', '=', 'done')], limit=1)
        #     res = self.env.ref('maknon_tests.parts_certificate_report_id').report_action(obj)

        return res


class MasjedPermision(models.Model):
    _inherit = 'mosque.permision'

    background = fields.Binary('Background', compute='_compute_background', tracking=True)
    body       = fields.Html('Body',         compute='compute_body', tracking=True)

    # @api.one
    def _compute_background(self):
        perm_type = self.perm_type
        if perm_type == 'mosque_perm':
            tmpl = self.env['mail.template'].search([('repport_type', '=', 'mosuqe_permession')], limit=1)
        elif perm_type == 'school_perm':
            tmpl = self.env['mail.template'].search([('repport_type', '=', 'mosuqe_school_permession')], limit=1)
        if self.is_valid:
            self.background = tmpl.back

    # @api.one
    def compute_body(self):
        perm_type = self.perm_type
        if perm_type == 'mosque_perm':
            tmpl = self.env['mail.template'].search([('repport_type', '=', 'mosuqe_permession')], limit=1)
        elif perm_type == 'school_perm':
            tmpl = self.env['mail.template'].search([('repport_type', '=', 'mosuqe_school_permession')], limit=1)

        body = '<div><p class="text-center" style="font-size:42px;font-family:Neo Sans Arabic;padding-top:30px"><br/><br/> <br/><br/><br/>لم يتم إعتماد البيانات لإصدار التكليف <br/></p></div>'
        if self.is_valid:
            if tmpl.is_arabic_number:
                body = tmpl.generate_email(self.id, ['body_html2']).get('body_html2')
            else:
                body = tmpl.generate_email(self.id, ['body_html']).get('body_html')
        self.body = body
        
        
class masjed_supervisor_request(models.Model):
    _inherit = 'mosque.supervisor.request'

    background = fields.Binary('Background', compute='_compute_background', tracking=True)
    body       = fields.Html('Body',         compute='compute_body', tracking=True)

    # @api.one
    def _compute_background(self):
        type_request = self.type_request
        categ_type   = self.categ_type
        if type_request == 'supervisor_request' and categ_type == 'male':
            tmpl = self.env['mail.template'].search([('repport_type', '=', 'mosque_supervisor')], limit=1)
        elif type_request == 'supervisor_request' and categ_type == 'female':
            tmpl = self.env['mail.template'].search([('repport_type', '=', 'school_supervisor')], limit=1)
        elif type_request == 'admin_request':
            tmpl = self.env['mail.template'].search([('repport_type', '=', 'mosque_directors')], limit=1)
        if self.is_valid:
            self.background = tmpl.back

    # @api.one
    def compute_body(self):
        type_request = self.type_request
        categ_type = self.categ_type

        if type_request == 'supervisor_request' and categ_type == 'male':
            tmpl = self.env['mail.template'].search([('repport_type', '=', 'mosque_supervisor')], limit=1)
        elif type_request == 'supervisor_request' and categ_type == 'female':
            tmpl = self.env['mail.template'].search([('repport_type', '=', 'school_supervisor')], limit=1)
        elif type_request == 'admin_request':
            tmpl = self.env['mail.template'].search([('repport_type', '=', 'mosque_directors')], limit=1)
        body = '<div><p class="text-center" style="font-size:42px;font-family:Neo Sans Arabic;padding-top:30px"><br/><br/> <br/><br/><br/>لم يتم إعتماد البيانات لإصدار التكليف <br/></p></div>'
        if self.is_valid:
            if tmpl.is_arabic_number:
                body = tmpl.generate_email(self.id, ['body_html2']).get('body_html2')
            else:
                body = tmpl.generate_email(self.id, ['body_html']).get('body_html')
        self.body=body

