# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from time import strftime
from odoo.addons.resource.models.resource import  to_naive_user_tz, to_naive_utc

import random
import string
from bigbluebutton_api_python import BigBlueButton
import uuid
import logging

from odoo import models, api, fields, _, tools
from odoo.exceptions import UserError, ValidationError
from urllib.error import URLError
_logger = logging.getLogger(__name__)


def get_random_alphanumeric_string(length=8):
    letter_vocab = string.ascii_letters + string.digits
    return ''.join((random.choice(letter_vocab) for i in range(length)))


class Session(models.Model):
    _name = 'mq.session'
    _description = "Session"

    def generate_bbb_room(self):
        # params
        unique_room_id = uuid.uuid4()
        return unique_room_id
       
    @api.multi 
    def get_name(self):
        for session in self:
            session.name = f"{session.episode_id.name or ''} {session.start_date or ''}"
            
    @api.one
    @api.depends('episode_id')
    def get_time_session(self):
        self.time_session_id = self.episode_id.time_id

    @api.depends('episode_id','episode_id.is_online')
    def get_is_online_episode(self):
        for rec in self :
            rec.is_online = rec.episode_id.is_online

    name                    = fields.Char(compute="get_name")
    start_date              = fields.Date('Start date')
    start_datetime          = fields.Datetime('Start Time', compute='_compute_start_end_session_time', store = True)
    end_datetime            = fields.Datetime('End Time',  compute="_compute_start_end_session_time", store = True)
    episode_id              = fields.Many2one('mk.episode', 'Course', required=True, domain ="[('is_episode_meqraa', '=', True)]")
    is_online               = fields.Boolean(string='Online', compute=get_is_online_episode, store=True)
    teacher_id              = fields.Many2one(related= 'episode_id.teacher_id', string='Teacher', store = True)
    color                   = fields.Integer('Color Index')
    active                  = fields.Boolean(default=True)
    duration                = fields.Float('Duration', compute="_compute_start_end_session_time", store = True)
    status                  = fields.Selection([('planned', 'Planned'),
                                                ('active', 'Active'),
                                                ('done', 'Done'),
                                                ('error', 'Error')],default='planned', string='Status', store=True, copy=False)
    # bbb_url_record_id      = fields.Char('BBB Url Record', compute='get_recording')
    time_session_id         = fields.Many2one('mq.time', string='Time Session',compute=get_time_session, store=True)
    bbb_password_moderator  = fields.Char('Session Moderator Password')
    bbb_password_attandee   = fields.Char('Session Attandee Password')
    id_bbb_room             = fields.Char('BBB Room ID')
    id_hook                 = fields.Char(related = 'episode_id.id_hook',string='Hook ID')
    id_internal_meeting     = fields.Char('Internal meeting ID')
    url_internal_meeting     = fields.Char('Internal meeting URL')
    student_ids             = fields.One2many('mq.session.student', 'session_id', string='Student list')

                
    @api.depends('start_date', 'time_session_id', 'time_session_id.time_from', 'time_session_id.time_to')
    def _compute_start_end_session_time(self):
        for session in self:
            date = datetime.strptime(session.start_date,'%Y-%m-%d')
            time_session_id = session.time_session_id
            time_from = (time_session_id.time_from) * 3600
            time_to = (time_session_id.time_to) * 3600
            fromordinal = datetime.fromordinal(date.toordinal())
            combined_date_start = fromordinal +  timedelta(seconds=time_from)
            combined_date_end = fromordinal +  timedelta(seconds=time_to)
            diff_utc = timedelta(hours=3)
            session.start_datetime = combined_date_start - diff_utc
            session.end_datetime = combined_date_end - diff_utc
            diff =  combined_date_end - combined_date_start
            session.duration = diff.total_seconds() / 3600

    def generate_password(self):
        random_pass = get_random_alphanumeric_string(10)
        return random_pass
    
    def get_join_url_moderator(self, partner, password):
        if password:
            bbb_session = self.get_bbb_session()
            params = {"userID": partner.id, }
            bigbluebutton_link = bbb_session.get_join_meeting_url(partner.name, self.id_bbb_room, password=password, params=params)
            return bigbluebutton_link
        return False

    @api.one
    def action_stop_meeting(self):
        try:
            bbb_session = self.get_bbb_session()
            bbb_session.end_meeting(self.id_bbb_room, self.bbb_password_moderator)
            self.status = 'done'
        except Exception as e:
            _logger.error(f"Stop Meeting error: ({e})")
            raise UserError(_('Unable to close the meeting'))
        
    @api.model
    def create(self, vals):
        vals['bbb_password_moderator'] = self.generate_password()
        vals['bbb_password_attandee'] = self.generate_password()
        vals['id_bbb_room'] = self.generate_bbb_room()
        return super(Session, self).create(vals)

    def get_bbb_session(self):
        bigbluebutton_url = self.env['ir.config_parameter'].sudo().get_param('bigbluebutton_url', False)
        bigbluebutton_secret = self.env['ir.config_parameter'].sudo().get_param('bigbluebutton_secret', False)

        if bigbluebutton_url and bigbluebutton_secret:
                bigbluebutton_session = BigBlueButton(bigbluebutton_url, bigbluebutton_secret)
                return bigbluebutton_session
        else:
            raise UserError(_("Could not get session, check bbb url and secret code"))

    def generate_meeting(self):
        # import pdb; pdb.set_trace()
        bbb_session = self.get_bbb_session()

        meeting_pass_moderator = self.bbb_password_moderator
        meeting_pass_attandee = self.bbb_password_attandee
        meeting_id = self.id_bbb_room
        duration = self.duration

        # #TODO timedelta (30min) value should be dynamic and from configuration
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', False)

        params = {
            'moderatorPW': meeting_pass_moderator,
            'attendeePW': meeting_pass_attandee,
            'meetingID': meeting_id,
            'meetingName': self.name,
            'name':self.episode_id.name,
            'logoutURL':base_url + '/mqr/session/logout',
            'duration': duration or 0,
            'logo':base_url + '/logo.png?company=' + str(self.env.user.company_id.id),
            #'record':True,
            # 'autoStartRecording' :True,
            #'allowStartStopRecording' :True,
            'recordID': meeting_id,
        }

        meet = bbb_session.create_meeting(meeting_id, params=params)

        self.id_internal_meeting = meet['xml']['internalMeetingID']
        return meet

    def action_join_session(self):
        student_ids = self.student_ids
        try:
            self.generate_meeting()
            meeting_link = self.get_join_url_moderator(self.teacher_id.resource_id.user_id.partner_id, self.bbb_password_moderator)
            self.url_internal_meeting = meeting_link
            password = self.bbb_password_attandee
            bbb_session = self.get_bbb_session()
            id_bbb_room = self.id_bbb_room

            for rec in student_ids:
                partner = rec.mk_link.student_id
                if password:
                    params = {"userID": partner.id}
                    bigbluebutton_link = bbb_session.get_join_meeting_url(partner.display_name, id_bbb_room, password=password, params=params)
                    # return bigbluebutton_link
                    rec.id_bbb_url_student = bigbluebutton_link    
            self.status = 'active'

            return {
                'type': 'ir.actions.act_url',
                'url': meeting_link,
                'target': 'new',
            }
        except Exception as e:
            _logger.error(f"Join session Meeting error: ({e})")
            raise UserError(_('Please try again in a minute'))

    # This function to get url for record session if exist
    @api.depends('status')
    def get_recording(self):
        for session in self:
            bbb_url_record_id = False
            try :
                bbb_session = self.get_bbb_session()
                meeting_id = self.id_internal_meeting
                record = bbb_session.get_recordings(meeting_id, meeting_id)
                if session.mode == 'done':
                    try :
                        if record['xml']['returncode'] == 'SUCCESS' and record['xml']['recordings']['recording']['playback']['format']['url'] != '':
                            bbb_url_record_id = record['xml']['recordings']['recording']['playback']['format']['url']
                    except Exception as e:
                        _logger.error(f"could not read BBB recording data: ({e})")
            except URLError as e:
                _logger.error(f"Unable to get BBB session recordings: ({e})")
            except Exception as e:
                _logger.error(f"Unable to get BBB session recordings: ({e})")
            session.bbb_url_record_id = bbb_url_record_id

    @api.model
    def bbb_url_teacher_session(self, episode_id):
        try:
            episode_id = int(episode_id)
        except:
            pass
        url = False
        msg = False
        episode = self.env['mk.episode'].search([('id', '=', episode_id)], limit=1)
        if episode.is_episode_meqraa:
            current_datetime = datetime.strptime(strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") + timedelta(hours=3)
            current_date = datetime.now().date()
            session = self.env['mq.session'].search([('episode_id', '=', episode_id),
                                                     ('start_date', '=', current_date)], limit=1)
        else:
            session = self.env['mq.session'].search([('episode_id', '=', episode_id)], limit=1)

        if session:
            session_start_datetime = datetime.strptime(session.start_datetime,"%Y-%m-%d %H:%M:%S") + timedelta(hours=3)
            if session.status == 'active':
                if episode.is_episode_meqraa:
                    url = session.url_internal_meeting
                else:
                    try:
                        session.generate_meeting()
                        meeting_link = session.get_join_url_moderator(session.teacher_id.resource_id.user_id.partner_id, session.bbb_password_moderator)
                        session.url_internal_meeting = meeting_link
                        url = meeting_link
                    except Exception as e:
                        _logger.error(f"Join session Meeting error: ({e})")
                        raise UserError(_('Please try again in a minute'))
                msg = 'الرابط متاح '
            elif session.status == 'planned':
                if  current_datetime < session_start_datetime :
                    msg = 'لم يحن الوقت بعد الحصة تبدأ ' + str(session_start_datetime)
                else:
                    student_ids = session.student_ids
                    try:
                        session.generate_meeting()
                        meeting_link = session.get_join_url_moderator(session.teacher_id.resource_id.user_id.partner_id, session.bbb_password_moderator)
                        session.url_internal_meeting = meeting_link
                        password = session.bbb_password_attandee
                        bbb_session = session.get_bbb_session()
                        id_bbb_room = session.id_bbb_room

                        for rec in student_ids:
                            partner = rec.mk_link.student_id
                            if password:
                                params = {"userID": partner.id}

                                bigbluebutton_link = bbb_session.get_join_meeting_url(partner.name, id_bbb_room,password=password, params=params)

                                # return bigbluebutton_link
                                rec.id_bbb_url_student = bigbluebutton_link
                        session.status = 'active'

                        url = meeting_link

                        msg = 'الرابط متاح '

                    except Exception as e:
                        _logger.error(f"Join session Meeting error: ({e})")
                        msg = 'الرجاء التجربة بعد قليل او في وقت لاحق'

            elif session.status == 'done':
                msg = 'انتهت الحصة اليوم '
        else:
            msg = 'لا توجد حصة مبرمجة لليوم'

        vals = {'url':             url,
                'state':           session and session.status or False,
                'start_datetime':  session and str(datetime.strptime(session.start_datetime,"%Y-%m-%d %H:%M:%S") + timedelta(hours=3)) or False,
                'msg':             msg}
        return str(vals)

    @api.model
    def get_teacher_link_bbb_room(self, episode_id):
        try:
            episode_id = int(episode_id)
        except:
            pass
        episode = self.env['mk.episode'].search([('id', '=', episode_id)], limit=1)
        res = []
        if episode.is_episode_meqraa:
            current_date = datetime.now().date()
            teacher_session = self.env['mq.session'].search([('episode_id', '=', episode_id),
                                                             ('start_date', '=', current_date)], limit=1)
        else:
            teacher_session = self.env['mq.session'].search([('episode_id', '=', episode_id)], limit=1)

        if teacher_session:
            res.append({'id'            : teacher_session.id,
                        'start_session': datetime.strptime(teacher_session.start_datetime, "%Y-%m-%d %H:%M:%S") + timedelta(hours=3) })
        return res

    @api.model
    def add_session_link_online_episode_44_C1_cron(self, id_from):
        online_episodes = self.env['mk.episode'].search([('study_class_id.is_default', '=', True),
                                                         ('is_online', '=', True),
                                                         #('link_ids', '!=', False),
                                                         ('id', '>', id_from)], order="id asc", limit=5000)
        total = len(online_episodes)
        x = 0
        failed = 0
        for episode in online_episodes:
            x += 1
            session_obj = self.env['mq.session']
            session = session_obj.search([('episode_id', '=', episode.id)], limit=1)
            if not session:
                session = session_obj.create({'episode_id': episode.id,
                                              'teacher_id': episode.teacher_id.id,
                                              'start_date': datetime.now(),
                                              'status': 'active'})
                try:
                    session.generate_meeting()
                    meeting_link = session.get_join_url_moderator(session.teacher_id.resource_id.user_id.partner_id,
                                                                  session.bbb_password_moderator)
                    session.url_internal_meeting = meeting_link
                except Exception as e:
                    #_logger.error(f"Join session Meeting error: ({e})")
                    failed += 1
                    pass
                    # raise UserError(_('Please try again in a minute'))
            link_ids = episode.link_ids.filtered(lambda x: x.state == 'accept' and x.action_done == False)
            for link_id in link_ids:
                student_session = self.env['mq.session.student'].search([('mk_link', '=', link_id.id)], limit=1)

                password = session.bbb_password_attandee
                bbb_session = session.get_bbb_session()
                id_bbb_room = session.id_bbb_room
                partner = link_id.student_id
                params = {"userID": partner.id}

                if not student_session:
                    if password:
                        bigbluebutton_link = bbb_session.get_join_meeting_url(partner.name, id_bbb_room, password=password, params=params)
                        # return bigbluebutton_link
                        session.write({'student_ids': [(0, 0, {'session_id': session.id,
                                                               'mk_link': link_id.id,
                                                               'id_bbb_url_student': bigbluebutton_link})]})
                else:
                    if not student_session.id_bbb_url_student:
                        bigbluebutton_link = bbb_session.get_join_meeting_url(partner.name, id_bbb_room, password=password, params=params)
                        student_session.write({'id_bbb_url_student': bigbluebutton_link})

class mk_listen_line(models.Model):
    _inherit = 'mk.listen.line'
        
    session_id  = fields.Many2one('mq.session', 'Session')
    
    
class mk_student_session(models.Model):
    _name = 'mq.session.student'
    
    def _get_default_access_token(self):
        return str(uuid.uuid4())

    session_id  = fields.Many2one('mq.session', 'Session', ondelete='cascade')
    mk_link     = fields.Many2one('mk.link', 'Student', ondelete='cascade')

    id_bbb_url_student           = fields.Char('BBB Url Student')
    bbb_url_student_access_token = fields.Char('BBB Url token', default=lambda self: self._get_default_access_token(), copy=False)

    @api.model
    def bbb_url_student_session(self, link_id):
        try:
            link_id = int(link_id)
        except:
            pass
        url = False
        msg = False
        link = self.env['mk.link'].search([('id', '=', link_id)], limit=1)
        episode_id = link.episode_id
        if episode_id.is_episode_meqraa:
            current_date = datetime.now().date()
            student_session = self.env['mq.session.student'].search([('mk_link', '=', link_id),
                                                                     ('session_id.start_date','=', current_date)], limit=1)
        else:
            student_session = self.env['mq.session.student'].search([('mk_link', '=', link_id)], limit=1)

        if student_session:
            if episode_id.is_episode_meqraa:
                url = student_session.id_bbb_url_student
            else:
                session = student_session.session_id
                password = session.bbb_password_attandee
                bbb_session = session.get_bbb_session()
                id_bbb_room = session.id_bbb_room

                partner = student_session.mk_link.student_id
                if password:
                    params = {"userID": partner.id}
                    bigbluebutton_link = bbb_session.get_join_meeting_url(partner.display_name, id_bbb_room, password=password, params=params)

                student_session.write({'id_bbb_url_student': bigbluebutton_link })
                url = bigbluebutton_link

            start_datetime = datetime.strptime(student_session.session_id.start_datetime, "%Y-%m-%d %H:%M:%S") + timedelta(hours=3)
            session_status = student_session.session_id.status
            if student_session and session_status == 'active':
                msg = 'الرابط متاح '
            elif student_session and session_status == 'planned':
                msg =  'الرابط غير متاح, الحصة تبدأ' + str(start_datetime)
            elif student_session and session_status == 'done':
                msg = "الحصة انتهت"
            elif student_session and session_status == 'error':
                msg = "الرجاء التجربة بعد قليل او في وقت لاحق"
        else:
            msg = "لا توجد حصة مبرمجة لليوم"

        vals = {'start_datetime':  student_session and str(start_datetime) or False,
                'session_status':  student_session and session_status or False,
                'student_link':    url,
                'msg':             msg }
        return str(vals)

    @api.model
    def get_student_link_bbb_room(self, link_id):
        try:
            link_id = int(link_id)
        except:
            pass
        res = []
        link = self.env['mk.link'].search([('id', '=', link_id)], limit=1)
        episode_id = link.episode_id
        if episode_id.is_episode_meqraa:
            current_date = datetime.now().date()
            student_session = self.env['mq.session.student'].search([('mk_link', '=', link_id),
                                                                     ('session_id.start_date','=', current_date)], limit=1)
        else:
            student_session = self.env['mq.session.student'].search([('mk_link', '=', link_id)],limit=1)

        if student_session:
            res.append({'id':             student_session.id,
                        'start_session': datetime.strptime(student_session.session_id.start_datetime, "%Y-%m-%d %H:%M:%S") + timedelta(hours=3) })
        return res


class MkLink(models.Model):
    _inherit = 'mk.link'

    def generate_bbb_room(self):
        # params
        unique_room_id = uuid.uuid4()
        return unique_room_id

    @api.one
    def create_student_preparation(self):
        super(MkLink, self).create_student_preparation()
        episode = self.episode_id
        episode_id = episode.id
        if episode.is_online:
            session_obj = self.env['mq.session']
            session = session_obj.search([('episode_id', '=', episode_id)], limit=1)

            if not session:
                session = session_obj.create({'episode_id': episode_id,
                                                      'teacher_id': episode.teacher_id.id,
                                                      'start_date': datetime.now(),
                                                      'status': 'active'})
            student_session = self.env['mq.session.student'].search([('mk_link', '=', self.id),
                                                                     ('session_id', '=', session.id)], limit=1)
            if not student_session:
                    session.write({'student_ids': [(0, 0, {'session_id': session.id,
                                                           'mk_link': self.id})]})

class InternalTransferInherit(models.TransientModel):
    _inherit = 'mk.student.internal_transfer'

    @api.one
    def action_assign_episode(self):
        super(InternalTransferInherit, self).action_assign_episode()