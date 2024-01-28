# -*- coding: utf-8 -*-

from odoo import models, fields, api


class api_url(models.Model):
    _name = 'api.url'

    name = fields.Char('For')
    url = fields.Char('URl')

