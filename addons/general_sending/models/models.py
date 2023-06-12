# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from odoo.tools.translate import _
from langdetect import detect

import logging
_logger = logging.getLogger(__name__)


# class my_SmsClient(models.Model):
# 	_inherit = 'smsclient'

# 	def validate_message(self, text):
# 		language = detect(text)
# 		extension=153
# 		validity=False

# 		if language == "en":
# 			extension= 153
# 			if len(text) <= 160:
# 				no_of_messages=1

# 		elif language=="ar":
# 			extension = 67
# 			if len(text) <= 70:
# 				no_of_messages = 1

# 		text_lst=[text[i:i+extension] for i in range(0, len(text),extension)]
# 		no_of_messages=len(text_lst)
# 		if no_of_messages <= 10:
# 			validity=True

# 		else:
# 			raise exceptions.except_orm(_('Error'), _('Message is too long'))

# 		return validity
