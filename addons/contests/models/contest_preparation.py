#-*- coding:utf-8 -*-
from odoo import models, fields, api
from odoo import api, SUPERUSER_ID
from datetime import datetime, timedelta, date
import logging
_logger = logging.getLogger(__name__)


class contestPreparation(models.Model):
    _name = 'contest.preparation'

    '''
    @api.multi
    def write(self, vals):
        for rec in self:
            if self.create_uid.id != self.env.user.id:
                raise ValidationError(_('عذرا ! لايمكنك تعديل هذه المسابقة '))

        return super(contestPreparation, self).write(vals)
    '''

    @api.onchange('contest_type.method', 'contest_type')
    def on_contest_type(self):
        if self.contest_type.method=='quran':
            self.is_quran=True
        elif self.contest_type.method=='program':
            self.is_quran=False
            
    @api.depends('place','center_id')
    def get_center_emp(self):
        if self.place:
            emps=self.env['hr.employee'].sudo().search([('department_id','=',self.center_id.id),('category2','in',['admin','supervisor','center_admin'])]).ids
            self.center_emp= emps

    contest_type    = fields.Many2one("contest.type",string="contest type")
    is_quran        = fields.Boolean("is qran")
    name            = fields.Char('contest name', size=50)
    target_grade    = fields.Many2many( string='Target grade categorys', required=True, comodel_name='mk.grade', relation='', column1='',column2='')
    contest_fields  = fields.Many2many( string='contenst fields',        required=True, comodel_name='mk.contenst.fields')
    diff_items      = fields.One2many('contest.diff.items','contest_id',string='contenst differentiation items')
    brochure        = fields.Binary("برشور  المسابقة")
    brochure_active = fields.Boolean('تفعيل البرشور على البورتال')  
    StartD          = fields.Date('Start Date', required=True)
    endD            = fields.Date('End Date',   required=True)
    date_start_reg  = fields.Date('تاريخ بداية التسجيل', default=fields.Date.today())
    date_end_reg    = fields.Date('تاريخ نهاية التسجيل')
    center_emp      = fields.Many2many(string='Center emp', comodel_name='hr.employee', compute=get_center_emp)
    Target_age_cat  = fields.Many2many(string='Target age categorys', required=True, comodel_name='mk.age.category', relation='', column1='', column2='',)
    branches        = fields.Many2many(string='Branches',   comodel_name='mk.branches.master', domain=[('contsets','=',True)],)
    gender_type     = fields.Selection([('male','Male'), 
                                        ('female','Female'),
                                        ('male,female','All')], string="Allowed gender",default="male,female")
    attachment      = fields.Many2many(string='attachment', comodel_name='ir.attachment',)
    gools           = fields.Text('contest gools',required=True)
    conditions      = fields.Text('Conditions',   required=True)
    place           = fields.Selection(string='Place', selection=[('mosque_level', 'mosque_level'), 
                                                         ('center_level', 'center_level'),
                                                         ('organization_level','على مستوى الجمعية  ')]    )
    test_id         = fields.Many2one(string='Contest Namne', comodel_name='mk.test.names', domain=[('is_contest','=', True)])
    center_id       = fields.Many2one(string='Center',        comodel_name='hr.department', ondelete='cascade')
    mosque_id       = fields.Many2one(string='Mosque',        comodel_name='mk.mosque', ondelete='cascade')
    
    @api.model
    def create(self,vals):
        if vals['StartD'] < fields.Date.today():
                raise models.ValidationError('التواريخ المسموح بها ابتداءا من اليوم فمافوق')
        if (vals['endD'] <= fields.Date.today() ):
            raise models.ValidationError('التواريخ المسموح بها ابتداءا من اليوم فمافوق')
        return super(contestPreparation, self).create(vals)

    @api.constrains('endD')
    def _check_end_date(self):
    	for r in self:
            if r.endD< r.StartD:
                raise models.ValidationError('تاريخ نهاية المسابقة يجب أن يكون بعد تاريخ بداية المسابقة')

    @api.onchange('test_id')
    def on_change_test_id(self):
        if self.test_id:
            self.branches=self.test_id.branches.ids
            self.name=self.test_id.name

    def get_regulations(self):
        attachments=self.env['ir.attachment'].search([('res_model','=','regulations')])
        if attachments:
            self.attachment=attachments.ids
    
    @api.model
    def _notify_for_upcoming_contest_preparation(self):
        tomorrow_date = (date.today() + timedelta(days=1))
        upcoming_contest_preparations = self.env['contest.preparation'].search([('StartD', '=', tomorrow_date)])

        for rec in upcoming_contest_preparations:
            responsible = rec.mosque_id.responsible_id.user_id.partner_id
            if responsible:
                notif = self.env['mail.message'].create({'message_type': "notification",
                                                        "subtype": self.env.ref("mail.mt_comment").id,
                                                        'body': "المسابقة ستبدأ غدا",
                                                        'subject': "اشعار ببدء مسابقة",
                                                        'needaction_partner_ids': [(4, responsible.id)],
                                                        'model': self._name,
                                                        'res_id': rec.id,
                                                        })

    @api.model
    def contest_brochure(self):
        contests = self.env['contest.preparation'].search([('brochure_active', '=', True)])
        item_list = []
        if contests:
            for contest in contests:
                item_list.append({'id':   contest.id,
                                  'name': contest.name})
        return item_list

    @api.model
    def get_contests(self, is_quran):
        is_quran = is_quran
        query_string = ''' 
                SELECT id, name 
                FROM contest_preparation
                WHERE date_start_reg <= current_date AND 
                date_end_reg >= current_date AND 
                is_quran={};
                '''.format(is_quran)
        self.env.cr.execute(query_string)
        contests = self.env.cr.dictfetchall()
        return contests


class contestType(models.Model):
    _name="contest.type"

    name   = fields.Char(string="Name",required="1")
    method = fields.Selection([('quran','quran field'),('program','program field')],string="contest field")
