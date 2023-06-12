# -*- coding: utf-8 -*-
from odoo import models, fields, api ,_
from odoo.exceptions import ValidationError


class CustomPrizeProduct(models.Model):
    _inherit = "product.product"

    code               = fields.Char(string="Code")
    available_quantity = fields.Integer(string="Available Quantity")
    publish_prize      = fields.Boolean(string="Puplished On store", default=False)
    image              = fields.Binary("Medium-sized image", attachment=False,
                          help="Medium-sized image of the product. It is automatically "
                          "resized as a 128x128px image, with aspect ratio preserved, "
                          "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")

    @api.constrains('available_quantity','lst_price')
    def points_quantity_validation(self):
        if self.available_quantity < 0 :
            raise ValidationError(_('Available quantity cannot be less than zero'))

        if self.lst_price <= 0.0 :
            raise ValidationError(_('Prize Points cannot be zero or less '))

    @api.one
    def puplish_prize_store(self):
        if self.publish_prize:
            self.publish_prize = False
            return True
        
        if self.publish_prize == False:
            self.publish_prize = True
            return True
