# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import odoo
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
from odoo.tools.safe_eval import safe_eval, test_python_expr
from odoo.tools import pycompat
from odoo.http import request

from collections import defaultdict
import datetime
import dateutil
import logging
import time

from pytz import timezone

_logger = logging.getLogger(__name__)


class IrActionsServer(models.Model):
    _inherit = 'ir.cron'

    @api.multi
    def method_direct_trigger(self):
        for cron in self:
            self.sudo(user=cron.user_id.id).ir_actions_server_id.run2()
        return True


    @api.model
    def _callback(self, cron_name, server_action_id, job_id):
        """ Run the method associated to a given job. It takes care of logging
        and exception handling. Note that the user running the server action
        is the user calling this method. """
        try:
            if self.pool != self.pool.check_signaling():
                # the registry has changed, reload self in the new registry
                self.env.reset()
                self = self.env()[self._name]

            log_depth = (None if _logger.isEnabledFor(logging.DEBUG) else 1)
            odoo.netsvc.log(_logger, logging.DEBUG, 'cron.object.execute', (self._cr.dbname, self._uid, '*', cron_name, server_action_id), depth=log_depth)
            start_time = False
            if _logger.isEnabledFor(logging.DEBUG):
                start_time = time.time()
            self.env['ir.actions.server'].browse(server_action_id).run2()
            if start_time and _logger.isEnabledFor(logging.DEBUG):
                end_time = time.time()
            self.pool.signal_changes()
        except Exception as e:
            self.pool.reset_changes()
            self._handle_callback_exception(cron_name, server_action_id, job_id, e)