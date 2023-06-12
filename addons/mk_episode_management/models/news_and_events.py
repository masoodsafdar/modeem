# -*- coding: utf-8 -*-
import re
# from odoo.tools import odoo, image, image_colorize, image_resize_image_big
from odoo.tools import odoo, image
from odoo import tools
from odoo import models,fields,api,_
import logging

_logger = logging.getLogger(__name__)



class mk_news_events(models.Model):
    _name = 'mk.news'

    title    = fields.Char(string='title', required=True)
    category = fields.Selection([('news', 'خبر'), 
                                 ('event', 'حدث'),
                                 ('adver','اعلان'),
                                 ('contest','اعلان مسابقة')], string='category')    
    body      = fields.Html(string='body')
    date      = fields.Date(string="Date")
    image     = fields.Binary(string='إضافة صورة ( 1110 * 240 ) – للأخبار والاحداث',)
    image_two = fields.Binary(string='إضافة صورة ( 299 * 538 ) – للإعلانات',)
    state     = fields.Selection(string='State', selection=[('draft', 'Draft'),('accept', 'منشور'), ('reject', 'غير منشور')], default='draft')
    masjed_id = fields.Many2one("mk.mosque",string="masjed")
    
    # @api.multi
    def act_draft(self):
        self.state = 'draft'

    # @api.multi
    def act_accept(self):
        self.state = 'accept'


    # @api.multi
    def act_reject(self):
        self.state = 'reject'

    @api.model
    def create(self, vals):
        #tools.image_resize_images(vals)
        return super(mk_news_events, self).create(vals)

    # @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(mk_news_events, self).write(vals)

    @api.model
    def get_news(self):
        news = self.env['mk.news'].search([('masjed_id', '=', None),
                                           ('state', '=', 'accept')], limit=5)
        item_list = []
        if news:
            for new in news:
                body = ''
                if new.body:
                    body = re.sub("<.*?>", "", new.body)
                item_list.append({"id": new.id,
                                  "title": new.title,
                                  "category": new.category,
                                  "body": body,
                                  "image": new.image,
                                  "image_two": new.image_two})
        return item_list

    @api.model
    def last_news(self):
        query_string = ''' 
             SELECT date, category, title, body, image
             FROM mk_news
             WHERE category='news' AND
             state='accept'
             ORDER BY date
             limit 5;
             '''
        self.env.cr.execute(query_string)
        last_news = self.env.cr.dictfetchall()
        return last_news

    @api.model
    def get_news_mosque(self,mosque_id):
        try:
            mosque_id = int(mosque_id)
        except:
            pass

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        news = self.env['mk.news'].search([('masjed_id', '=', mosque_id),
                                           ('state', '=', 'accept')], limit=5)

        item_list = []
        if news:
            for new in news:
                body_content = ''
                if new.body:
                    body_content = tools.html_sanitize(new.body)
                    # body_content = re.sub("<.*?>", "", new.body).replace('\xa0', ' ')
                item_list.append({"id": new.id,
                                  "title": new.title,
                                  "category": new.category,
                                  "body": body_content,
                                  "image": '%s/web/binary/image/?model=%s&field=image&id=%s' % (base_url,'mk.news',new.id),
                                  "image_two": '%s/web/binary/image/?model=%s&field=image_two&id=%s' % (base_url,'mk.news',new.id)})
        return item_list