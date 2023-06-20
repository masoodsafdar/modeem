# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import re


class UserGuide(models.Model):
    _name = 'user.guide'
    _description = 'User Guide'
    _inherit=['mail.thread','mail.activity.mixin']

    active = fields.Boolean("Active", default=True, tracking=True)
    name = fields.Char(string="Guide Name", required=True, tracking=True)
    category_id = fields.Many2one('user.guide.category', string='Category', tracking=True)
    description = fields.Text(string='Description', tracking=True)
    video_URL = fields.Char("Video URL", copy=False)
    embed_video = fields.Char(
        string="Embed video",
        compute='_compute_embed_video',
    )
    num_of_attachments = fields.Integer(
        string="Number Of Attachments",
        compute='_compute_num_of_attachments',
        default=0
    )
    guide_type = fields.Selection(
        [('guide', 'Guide'),
         ('document', 'Document'),
         ('announce', 'Announce'),
         ],
        string='Guide Type', required=True)

    order_by = fields.Integer('Order by')

    def _compute_num_of_attachments(self):
        for rec in self:
            attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'user.guide'), ('res_id', 'in', [rec.id])], ['res_id'], ['res_id'])
            rec.num_of_attachments = sum([data['res_id_count'] for data in attachment_data] )

    def button_redirect_to_attachments(self):
        return {
            'name': _('Attachments'),
            'domain': ['&', ('res_model', '=', 'user.guide'), ('res_id', 'in', [self.id] )],
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">

                                        Attach
        documents of your employee.</p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}"% ('user.guide', self.id)}

    @api.multi
    @api.depends("video_URL")
    def _compute_embed_video(self):
        for rec in self:
            if rec.video_URL:
                arg = re.compile(r'^.*((youtu.be/)|(v/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#\&\?]*).*').match(rec.video_URL)
                video_id = arg and arg.group(7) or False
                if video_id:
                    rec.embed_video = 'https://youtube.com/embed/{video_id}?rel=0&autoplay=1'.format(video_id=video_id)
                else:
                    rec.video_URL = _('Link is not valid')

    def button_redirect_to_video(self):
        for rec in self:
            return {
                'url':rec.embed_video,
                'type':'ir.actions.act_url'
            }