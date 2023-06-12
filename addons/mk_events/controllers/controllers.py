# -*- coding: utf-8 -*-
from odoo import http

# class MkEvents(http.Controller):
#     @http.route('/mk_events/mk_events/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mk_events/mk_events/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mk_events.listing', {
#             'root': '/mk_events/mk_events',
#             'objects': http.request.env['mk_events.mk_events'].search([]),
#         })

#     @http.route('/mk_events/mk_events/objects/<model("mk_events.mk_events"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mk_events.object', {
#             'object': obj
#         })