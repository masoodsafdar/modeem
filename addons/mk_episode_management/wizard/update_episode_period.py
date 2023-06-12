from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class PopupUpdate(models.TransientModel):

    _name = 'episode.update.periode.wizard'

    updated_period = fields.Selection([('subh', 'subh'),
                                        ('zuhr', 'zuhr'),
                                        ('aasr','aasr'),
                                        ('magrib','magrib'),
                                        ('esha','esha')], string='فترة', required=True)
    episode_id     = fields.Many2one('mk.episode', string="حلقة")


    def action_update(self):
        episode_id = self.episode_id
        selected_period = episode_id.selected_period
        parent_episode = episode_id.parent_episode
        updated_period = self.updated_period
        period_verif = self.env['mk.episode'].sudo().search([('selected_period', '=', updated_period),
                                                            ('parent_episode', '=', parent_episode.id)])

        if period_verif:
            raise ValidationError(('عذرا ، هذه الفترة موجودة مسبقا لنفس الحلقة'))
        else:
            episode_links = episode_id.link_ids.filtered(lambda l: l.state != 'done')  # state != done
            students = self.env['mk.student.register'].sudo().search([('link_ids', 'in', episode_links.ids)])
            for student in students:
                student_period = student.link_ids.filtered(lambda l: l.state == 'accept' and l.action_done == False and l.selected_period == updated_period
                                                                        and l.study_class_id.is_default == True)
                if student_period:
                    raise ValidationError(('الطالب ' + str(student_period.display_name) + ' مسجل في هذه الحلقة و مسجل في حلقة أخرى في نفس الفترة'))

            period = {'subh': False,      'zuhr': False,     'aasr':False,     'magrib':False,     'esha': False,}
            period_flag = {'subh_flag': False, 'zuhr_flag': False,'aasr_flag':False,'magrib_flag':False,'esha_flag': False}
            period[updated_period]= True
            period_flag[updated_period+'_flag']= True
            parent_episode.write(period)
            parent_episode.write(period_flag)

            period.update({'selected_period': updated_period})
            episode_id.write(period)
            episode_links.write({'selected_period': updated_period})

    @api.model
    def cron_selected_period_link(self):
        self.env.cr.execute(''' UPDATE mk_link link
                                SET selected_period = episode.selected_period
                                FROM mk_episode episode
                                WHERE link.episode_id = episode.id ''')