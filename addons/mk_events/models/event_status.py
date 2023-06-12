# -*- coding: utf-8 -*-

from odoo import models, fields, api

class mk_events_status(models.Model):
    _name = 'event.status'

    name = fields.Char(string="Name")
    no = fields.Integer(string="event number")