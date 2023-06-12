# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


class mak_episode_extend(models.Model):
    _inherit = 'mk.episode'
    
    program_id = fields.Many2one('mk.programs', string='Programs')


class mk_mosque(models.Model):
    _inherit = 'mk.mosque'

    # @api.multi
    def open_episods(self):
        tree_view = self.env.ref('mk_episode_management.mk_episode_tree_view')
        # res_id=self.env['mk.episode'].search([('parent_episode','=',self.id),('selected_period','=','esha')])
        return {'name': "/" + self.name + " / " + "الحلقات" + "/",
                'res_model': 'mk.episode',
                'res_id': 'mk.episode',
                'views': [(tree_view.id, 'tree'), (False, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('mosque_id', '=', self.id),
                           ('state', 'in', ['draft', 'accept'])]}

    # @api.multi
    def write(self, values):
        user = self.env.user
        for rec in self:
            if user.id != self.env.ref('base.user_root').id:
                if rec.is_synchro_edu_admin:
                    if 'categ_id' in values and values.get('categ_id') != rec.categ_id.id:
                        raise ValidationError(
                            'عذرا لا يمكنك تعديل فئة المسجد/لمدرسة بعد الاعتماد و المراجعة من قبل التعليمي')
                    if 'mosq_type' in values and values.get('mosq_type') != rec.mosq_type.id:
                        raise ValidationError('عذرا لا يمكنك تعديل نوع الحلقة بعد الاعتماد و المراجعة من قبل التعليمي')
                    if 'name' in values:
                        raise ValidationError(
                            'عذرا لا يمكنك تعديل إسم المسجد/لمدرسة بعد الاعتماد و المراجعة من قبل التعليمي')
                    if 'complex_name' in values:
                        raise ValidationError('عذرا لا يمكنك تعديل إسم المجمع بعد الاعتماد و المراجعة من قبل التعليمي')
                    if 'district_id' in values and values.get('district_id') != rec.district_id.id:
                        raise ValidationError('عذرا لا يمكنك تعديل حي المسجد بعد الاعتماد و المراجعة من قبل التعليمي')
                    if 'center_department_id' in values and values.get(
                            'center_department_id') != rec.center_department_id.id:
                        raise ValidationError('عذرا لا يمكنك تعديل المركز بعد الاعتماد و المراجعة من قبل التعليمي')

                if not user.has_group('mk_episode_management.group_mosque_name_edit'):
                    if 'name' in values:
                        raise ValidationError('عذرا لا يمكنك تعديل إسم المسجد/لمدرسة ')
                    if 'complex_name' in values:
                        raise ValidationError('عذرا لا يمكنك تعديل إسم المجمع ')
                    if 'categ_id' in values:
                        raise ValidationError('عذرا لا يمكنك تعديل فئة المسجد/لمدرسة')
                if not (self.env.context.get('from_permission')) and (
                        'center_department_id' in values or 'mosq_type' in values or 'district_id' in values):
                    raise ValidationError('عذرا لا يمكنك تعديل بيانات المسجد')
            tools.image_resize_images(values)
            if 'active' in values:
                for rec in self:
                    rec.close_date = fields.Datetime.now()
        return super(mk_mosque, self).write(values)

    @api.depends('supervisors')
    def count_masjed_episodes(self):
        for rec in self:
            rec.superviser_number=len(rec.supervisors)
            
    supervisor_ids    = fields.One2many('supervisor.line', 'order_id', string='supervisor')
    superviser_number = fields.Integer(compute='count_masjed_episodes',string="episode numbers")


class supervisor_line(models.Model):
    _name = 'supervisor.line'
    _description = 'Description'

    @api.onchange('supervisor_id')
    def _onchange_supervisor(self):
        search_supervisor = self.search([])
        for rec in search_supervisor:
            if self.supervisor_id.id== rec.supervisor_id.id:
                raise ValidationError(_('هذا المشرف مشرف على مسجد اخر'))
            
        self.state = self.supervisor_id.state 
        self.registeration_code = self.supervisor_id.registeration_code
   
    order_id           = fields.Many2one('mk.mosque',            string='Order', )
    supervisor_id      = fields.Many2one('mk.supervisor.mosque', string='Supervisor')    
    state              = fields.Selection([('draft', 'Draft'),
                                           ('accept', 'Accepted'), 
                                           ('reject', 'Rejected')], string='State')
    registeration_code = fields.Char('Registeration Code',size=12)
