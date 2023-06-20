#-*- coding:utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class MkStudyClass(models.Model):
    _name = 'mk.study.class'
    _inherit=['mail.thread','mail.activity.mixin']
    _order = 'order'
    
    # @api.multi
    def unlink(self):
        try:
            super(MkStudyClass, self).unlink()
        except:
            raise ValidationError(_('لا يمكنك حذف هذا السجل لإرتباطه بسجلات أخرى'))

    # @api.multi
    # @api.constrains('is_default')
    # def _check_default_class(self):
    #     for rec in self:
    #         class_ids=self.search([('is_default', '=', True), ('id', '!=', rec.id),])
    #         if class_ids and rec.is_default:
    #             raise ValidationError("عذرا! لا يسمح بتفعيل أكثر من فصل دراسي")

    @api.model
    def create(self,vals):
        is_default = vals.get('is_default', False)
        if is_default:
            ids = self.env['mk.study.class'].search([('is_default', '=', True),
                                                      '|', ('active', '=', False),('active', '=', True)])
            for rec in ids:
                rec.write({'is_default': False, })
        return super(MkStudyClass, self).create(vals)

    # @api.multi
    def write(self,vals):
        user = self.env.user
        if user.id != self.env.ref('base.user_root').id:
            if not user.has_group('mk_master_models.group_study_class_edit'):
                raise ValidationError('عذرا ليس لديك صلاحية التعديل على الفصل الدراسي')
            else:
                is_default = vals.get('is_default', False)
                if is_default:
                    ids = self.env['mk.study.class'].search([('is_default', '=', True),
                                                              '|', ('active', '=', False),('active', '=', True)])
                    for rec in ids:
                        rec.write({'is_default': False, })
        return super(MkStudyClass, self).write(vals)


    # @api.multi
    def get_year_default(self):
        academic_year = self.env['mk.study.year'].search([('is_default', '=', True)], limit=1)
        return academic_year and academic_year.id or False     
    
    name               = fields.Char('Name', tracking=True)
    company_id         = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get('mk.study.class'))
    order              = fields.Integer('Order', tracking=True)
    study_year_id      = fields.Many2one('mk.study.year', 'Study Year', default=get_year_default, tracking=True)
    start_date         = fields.Date('Start Date', tracking=True)
    end_date           = fields.Date('End Date', tracking=True)
    islamic_start_date = fields.Date('Islamic Start Date', tracking=True)
    islamic_end_date   = fields.Date('Islamic End Date', tracking=True)
    active             = fields.Boolean('Active', default=True, tracking=True)
    is_default         = fields.Boolean('Is default', default=True, tracking=True)
    
    @api.constrains('start_date', 'end_date')
    def _check_date(self): 
        if self.study_year_id.start_date and self.study_year_id.end_date:
            if self.start_date < self.study_year_id.start_date :
                raise ValidationError(_('تاريخ البداية اقل من تاريخ بداية السنة الدراسية'))
            if self.end_date > self.study_year_id.end_date:
                raise ValidationError(_('تاريخ النهاية اكبر من تاريخ نهاية السنة الدراسية'))
            if self.start_date > self.end_date:
                raise ValidationError(_('تاريخ البداية اكبر من تاريخ نهاية الفصل الدراسي'))
            if self.islamic_start_date > self.islamic_end_date:
                raise ValidationError(_('تاريخ البداية اكبر من تاريخ نهاية الفصل الدراسي'))
        else:
            raise   ValidationError(_('رجاء أدخل تاريخ بداية و نهاية السنة الدراسية '))
                
                
    """@api.model    
    def fields_view_get(self, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(MkStudyClass, self).fields_view_get(view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='company_id']")
        company_ids = []
        company_recs= self.env['mk.study.year'].search([])
        company_ids = [x.company_id.id for x in company_recs]
        domain = "[('id', 'in', " + str(company_ids) + ")]"
        for node in nodes:
            node.set('domain', domain)
            res['arch'] = etree.tostring(doc)
        return res
    """

    @api.model
    def _notify_for_upcoming_mk_study_class(self):
        tomorrow_date = (date.today() + timedelta(days=1))
        upcoming_study_classes = self.env['mk.study.class'].search([('start_date', '=', tomorrow_date)])

        for rec in upcoming_study_classes:
            class_episodes = self.env['mk.episode'].search([('study_class_id', '=', rec.id)])
            for episode in class_episodes:
                responsible = episode.mosque_id.responsible_id.user_id.partner_id
                if responsible:
                    notif = self.env['mail.message'].create({'message_type': "notification",
                                                            "subtype": self.env.ref("mail.mt_comment").id,
                                                            'body': "نعلمكم ببداية الفصل الدراسي الجديد غدا",
                                                            'subject': "بدء الفصل الدراسي",
                                                            'needaction_partner_ids': [(4, responsible.id)],
                                                            'model': self._name,
                                                            'res_id': rec.id})
