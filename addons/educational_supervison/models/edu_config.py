# -*- coding: utf-8 -*-
from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)


class EduNames(models.Model):
    _name = 'edu.name'
    _rec_name = 'name'

    name   = fields.Char('Name')
    number = fields.Integer('Number')


class Fields(models.Model):
    _name = 'edu.field'
    _rec_name = 'name'

    name = fields.Char('Name')
    number = fields.Integer('Number')
    type_evaluation = fields.Selection([('multiple_choice', 'Multiple Choice'),
                                        ('grade_input', 'Grade Input')], string='Evaluation Type',default='grade_input', required=True)


class Visits(models.Model):
    _name = 'edu.visit'
    _rec_name = 'name'

    name        = fields.Char('Name')
    number      = fields.Integer('Number')
    is_suddenly = fields.Boolean('Is suddenly')


class Approvess(models.Model):
    _name = 'edu.approve'
    _rec_name = 'name'

    name = fields.Char('Name')
    number = fields.Integer('Number')