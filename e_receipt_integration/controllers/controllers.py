# -*- coding: utf-8 -*-
from odoo import http

# class SchneiderApArDebitCredit(http.Controller):
#     @http.route('/schneider_ap_ar_debit_credit/schneider_ap_ar_debit_credit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/schneider_ap_ar_debit_credit/schneider_ap_ar_debit_credit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('schneider_ap_ar_debit_credit.listing', {
#             'root': '/schneider_ap_ar_debit_credit/schneider_ap_ar_debit_credit',
#             'objects': http.request.env['schneider_ap_ar_debit_credit.schneider_ap_ar_debit_credit'].search([]),
#         })

#     @http.route('/schneider_ap_ar_debit_credit/schneider_ap_ar_debit_credit/objects/<model("schneider_ap_ar_debit_credit.schneider_ap_ar_debit_credit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('schneider_ap_ar_debit_credit.object', {
#             'object': obj
#         })