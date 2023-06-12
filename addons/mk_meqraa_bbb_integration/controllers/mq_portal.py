# -*- coding: utf-8 -*-
from ast import literal_eval
from datetime import datetime, timedelta
import logging

import pytz
import json
from odoo import http, _
from odoo.http import request, Response
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

logger = logging.getLogger(__name__)

time_format = "%H:%M"


class MaqraaBBBPortal(http.Controller):


    @http.route(['/mqr/session/logout'], type='http', auth="public")
    def join_session_logoutURL(self):

        return http.request.render('mk_meqraa_bbb_integration.session_logoutpage', {})
