# -*- coding: utf-8 -*-
from odoo import models, fields, api ,_
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class CustomSaleOrder(models.Model):
    _inherit = "sale.order"

    state               = fields.Selection([('draft',          'مبدئي'),
                                            ('mosque_approve', 'تصديق المسجد'),
                                            ('deliverd',       'تم التسليم'),
                                            ('refused',        'رفض')],default="draft",string="Order Status")
    partner_id          = fields.Many2one('res.partner',      required=False)
    partner_invoice_id  = fields.Many2one('res.partner',      required=False)
    partner_shipping_id = fields.Many2one('res.partner',      required=False)
    pricelist_id        = fields.Many2one('product.pricelist',required=False)

    student_id          = fields.Many2one('mk.student.register',          string="Student")
    mosque_id           = fields.Many2one(related="student_id.mosq_id",   string="Mosque")
    mosques_ids         = fields.Many2many(related="student_id.mosque_id",string="Mosques")
    refuse_reason       = fields.Text("Refuse Reason")
    has_delivered       = fields.Boolean("Prize Has Delivered")
    total_prize_points  = fields.Float(compute="compute_total_prize_points", string="Total Prize Points",store="True")
    order_date          = fields.Date(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=datetime.now().date())

    @api.one
    @api.depends('order_line.product_id','order_line.product_uom_qty')
    def compute_total_prize_points(self):
        total = 0.0
        for rec in self.order_line:
            total += rec.total_points

        self.total_prize_points = total

    @api.multi
    def draft_action(self):
        self.write({'state': 'draft'})

    @api.multi
    def mosque_approve_action(self):
        '''To Do: take from student points and decrease product quantity'''
        stu_points = self.env['student.points'].search([('name','=', self.student_id.id)])
        if stu_points:
            stu_points.total_points = stu_points.total_points - self.total_prize_points

            if self.order_line:
                for pro in self.order_line:
                    #product = self.env['product.template'].search([('id','=', pro.product_id.id)])
                    pro.product_id.available_quantity -=  pro.product_uom_qty
            else:
                pass

        self.write({'state': 'mosque_approve'})

    @api.multi
    def refuse_action(self):
        if not self.refuse_reason :
            raise UserError(_('Please Specify Refuse reason'))
        
        self.write({'state': 'refused'})

    @api.multi
    def has_deliverd_action(self):
        self.has_delivered = True
        self.write({'state': 'deliverd'})


class CustomSaleOrderLines(models.Model):
    _inherit = "sale.order.line"

    total_points = fields.Float(compute="compute_total_qty_points",string="Total Points",store="True")

    @api.one
    @api.depends('product_uom_qty','product_id.lst_price')
    def compute_total_qty_points(self):
        for rec in self:
            rec.total_points = rec.product_uom_qty * rec.product_id.lst_price
    
