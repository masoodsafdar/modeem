# -*- coding: utf-8 -*-

from odoo import models, api, fields, _,tools
from datetime import datetime
import uuid
from werkzeug import urls
from lxml import etree
from hashlib import sha1
import logging
_logger = logging.getLogger(__name__)
import requests
from odoo.exceptions import UserError
from urllib.error import URLError

class MqEpisode(models.Model):
    _inherit = 'mk.episode'


    def get_total_session(self):
        session_obj = self.env['mq.session'].search([('episode_id','=',self.id)])
        self.compute_session = len(session_obj)

    id_bbb_room       = fields.Char('BBB Room ID')
    id_hook           = fields.Char('Hook ID')
    compute_session   = fields.Integer(compute=get_total_session, string='Total Session', store=True)

    def generate_bbb_room(self):
        # params
        unique_room_id = uuid.uuid4()
        return unique_room_id

    # This function is used to activate hook for courses that hasn't yet created a id_hook
    def create_course_hook(self):
        if not self.id_hook:
            if not self.id_bbb_room:
                self.id_bbb_room = self.generate_bbb_room()
            # Create Hook
            self.create_hook(self.id_bbb_room)

    # @api.depends('main_teacher_id')
    # def get_teacher_bbb_url(self):
    #     for course in self:
    #         teacher_url = ''
    #         if course.main_teacher_id and isinstance(course.id, int):
    #             base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #             teacher_url = urls.url_join(base_url, "/join/course/%s/teacher/%s/%s" % (course.id, course.main_teacher_id.id, course.main_teacher_access_token))
    #
    #         course.bbb_url_main_teacher_id = teacher_url

    def create_hook(self, meeting_id):
        " This method create a hook, it will be receive information from your bbb"
        try:
            # Create Hook
            bigbluebutton_url = self.env['ir.config_parameter'].sudo().get_param('bigbluebutton_url', False)
            bigbluebutton_secret = self.env['ir.config_parameter'].sudo().get_param('bigbluebutton_secret', False)
            
            # bigbluebutton_url = tools.config['bigbluebutton_endpoint'] if tools.config['bigbluebutton_endpoint'] else ''
            # bigbluebutton_secret = tools.config['bigbluebutton_secret'] if tools.config['bigbluebutton_secret'] else ''

            
            url_hook = bigbluebutton_url + '/api/hooks/create?'
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', False)
            CallbackURL = base_url + '/webbhook/bbb/events/' + str(meeting_id)
            query = '&callbackURL=' + CallbackURL + '&meetingID=' + meeting_id

            call = 'hooks/create'
            prepared = "%s%s%s" % (call, query, bigbluebutton_secret)
            checksum = sha1(prepared.encode('utf-8')).hexdigest()

            urlf = url_hook + "%s&checksum=%s" % (query, checksum)
            reponse = requests.get(urlf)
            xml_data = etree.fromstring(reponse.content)

            hookID = xml_data.find('hookID').text
            if hookID:
                self.id_hook = str(hookID)

        except Exception as e:
            _logger.error(f"Hook create Meeting error: ({e})")

    @api.model
    def create(self, vals):
        course = super(MqEpisode, self).create(vals)
        if course:
            try:
                course.id_bbb_room = course.generate_bbb_room()
                # Create Hook
                # course.create_hook(course.id_bbb_room)
            except:
                raise UserError(_('Please Check Your BBB configuration'))
        return course

    def action_regenerate_room(self):
        try:
            self.id_bbb_room = self.generate_bbb_room()
        except:
            raise UserError(_('Please Check Your BBB configuration'))

    @api.multi
    def action_view_sessions(self):
        self.ensure_one()
        action = self.env.ref('mk_meqraa_bbb_integration.session_session_act').read()[0]
        action['domain'] = [('episode_id', '=', self.id)]
        action['views'] = [(self.env.ref('mk_meqraa_bbb_integration.session_tree_view').id, 'tree'), (self.env.ref('mk_meqraa_bbb_integration.session_form_view').id, 'form')]
        action['search_view_id'] = self.env.ref('mk_meqraa_bbb_integration.session_search_view').id
        return action

    @api.one
    def write(self, vals):
        if 'is_online' in vals and vals.get('is_online'):
            session_obj = self.env['mq.session']
            session = session_obj.search([('episode_id', '=', self.id)], limit=1)
            if not session:
                session = session_obj.create({'episode_id': self.id,
                                              'teacher_id': self.teacher_id.id,
                                              'start_date': datetime.now(),
                                              'status': 'active'})
            link_ids = self.env['mk.link'].search([('episode_id', '=', self.id),
                                                   ('state', '=', 'accept'),
                                                   ('action_done', '=', False)])
            for link_id in link_ids:
                student_session = self.env['mq.session.student'].search([('mk_link', '=', link_id.id)], limit=1)
                if not student_session:
                    session.write({'student_ids': [(0, 0, {'session_id': session.id,
                                                           'mk_link': link_id.id})]})
        return super(MqEpisode, self).write(vals)
