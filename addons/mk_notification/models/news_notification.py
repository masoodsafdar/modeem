import re
import xml.etree.ElementTree as etree
from odoo import models, fields, api, tools, _
import logging
_logger = logging.getLogger(__name__)

class News(models.Model):
    _name = 'mk.news.notification'
    _inherit=['mail.thread','mail.activity.mixin']

    name     = fields.Char('الاشعار', required=True)
    category = fields.Selection([('teacher', 'المعلمين'),
                                 ('center_admin', 'مدراء / مساعدي مدراء المركز'),
                                 ('bus_sup', 'مشرف الباص'),
                                 ('supervisor', 'مشرفين وإداريين المسجد / المدرسة'),
                                 ('admin', 'المشرف العام للمسجد /المدرسة'),
                                 ('edu_supervisor', 'مشرف تربوي'),
                                 ('managment', 'إداري\إداريين'),
                                 ('others', 'خدمات مساعدة')], string='التصنيف', default='admin', required=True)
    type_news = fields.Selection([('image', 'صورة'),
                                  ('video', 'فيديو'),
                                  ('image_url', 'صورة مع رابط')], string='نوع الاشعار', default='image', required=True)
    image     = fields.Binary('الصورة')
    url       = fields.Char('الرابط')
    url_video = fields.Char('رابط الفيديو')
    embed_url_video = fields.Char('رابط التضمين' , compute='compute_embed_video')

    user_news_ids =  fields.One2many('mk.user.news', 'new_id')

    @api.onchange('type_news')
    def onchange_type_news(self):
        self.image = False
        self.url = ''
        self.url_video = ''
        self.embed_url_video = ''

    @api.multi
    @api.depends("url_video")
    def compute_embed_video(self):
        for rec in self:
            url_video = rec.url_video
            if url_video:
                arg = re.compile(r'^.*((youtu.be/)|(v/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#\&\?]*).*').match(url_video)
                video_id = arg and arg.group(7) or False
                if video_id:
                    rec.embed_url_video = 'https://youtube.com/embed/{video_id}?rel=0&autoplay=1'.format(video_id=video_id)
                else:
                    rec.embed_url_video = _('Link is not valid')

    @api.model
    def create(self, vals):
        category = vals.get('category')
        res = super(News, self).create(vals)
        if not self._context.get('renotify'):
            users = self.env['hr.employee'].search([('user_id', '!=', False),
                                                    ('category2', '=', category)]).mapped('user_id')
            for user in users:
                self.env['mk.user.news'].create({'new_id': res.id,
                                                 'user_id': user.id})
                home_action = self.env.ref('mk_notification.news_notification_pop_up_action')
                user.write({'action_id': home_action.id})
        return res

    @api.multi
    def action_renotify(self):
        draft_user_news_ids = self.user_news_ids.filtered(lambda n: n.status == 'draft').mapped('user_id')
        users = [user for user in draft_user_news_ids]
        res = self.env['mk.news.notification'].with_context(renotify=True).create({'name': self.name,
                                                                                     'image': self.image,
                                                                                     'category': self.category})
        home_action = self.env.ref('mk_notification.news_notification_pop_up_action')
        for user in users:
            self.env['mk.user.news'].create({'new_id': res.id,
                                             'user_id': user.id})
            user.write({'action_id': home_action.id})


class UserNews(models.Model):
    _name = 'mk.user.news'

    user_id   = fields.Many2one('res.users', string="User")
    new_id    = fields.Many2one('mk.news.notification', string="New")
    status  = fields.Selection([('draft', 'Draft'),
                                  ('checked', 'Checked'),], default='draft', string='Status')


class PopupNewsNotification(models.TransientModel):
    _name = 'news.notification.popup'

    user_new_id = fields.Many2one('mk.user.news', string="New")
    type_news = fields.Selection([('image', 'صورة'),
                                  ('video', 'فيديو'),
                                  ('image_url', 'صورة مع رابط')], string='نوع الاشعار', default='image', required=True)
    image = fields.Binary('الصورة')
    url = fields.Char('الرابط')
    url_video = fields.Char('رابط الفيديو')
    embed_url = fields.Char('رابط التضمين')

    @api.model
    def default_get(self, fields):
        res = super(PopupNewsNotification, self).default_get(fields)
        draft_news = self.env['mk.user.news'].sudo().search([('user_id', '=', self.env.user.id),
                                                             ('status', '=', 'draft')], limit=1)
        res['user_new_id'] = draft_news.id
        res['type_news'] = draft_news.new_id.type_news
        res['image'] = draft_news.new_id.image
        res['url'] = draft_news.new_id.url
        res['url_video'] = draft_news.new_id.url_video
        res['embed_url'] = draft_news.new_id.embed_url_video
        return res

    def action_validate(self,):
        current_user = self.env.user
        self.user_new_id.sudo().write({'status': 'checked'})
        current_user.sudo().write({'action_id': False})

        draft_news = self.env['mk.user.news'].sudo().search([('user_id', '=', self.env.user.id),
                                                             ('status', '=', 'draft')], limit=1)
        while draft_news:
            return {
                'name': _('News Popup'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'news.notification.popup',
                'target': 'new',
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
