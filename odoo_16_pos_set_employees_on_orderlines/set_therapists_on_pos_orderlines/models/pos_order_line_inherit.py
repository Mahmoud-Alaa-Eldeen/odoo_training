from odoo import models, fields, api


class pos_order_line_inherit(models.Model):
    _inherit = 'pos.order.line'

    first_therapist = fields.Many2one('hr.employee', string='First Therapist')
    second_therapist = fields.Many2one('hr.employee', string='Second Therapist')
    third_therapist = fields.Many2one('hr.employee', string='Third Therapist')

