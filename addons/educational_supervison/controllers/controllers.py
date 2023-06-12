# -*- coding: utf-8 -*-
from odoo import http

# class Edu(http.Controller):
#     @http.route('/edu/edu/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/edu/edu/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('edu.listing', {
#             'root': '/edu/edu',
#             'objects': http.request.env['edu.edu'].search([]),
#         })

#     @http.route('/edu/edu/objects/<model("edu.edu"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('edu.object', {
#             'object': obj
#         })