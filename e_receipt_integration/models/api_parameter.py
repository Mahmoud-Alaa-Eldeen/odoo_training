# -*- coding: utf-8 -*-

from odoo import models, fields, api


class api_parameter(models.Model):
    _name = 'api.parameter'

    name = fields.Char('For')
    value = fields.Char('Value')
