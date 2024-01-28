# -*- coding: utf-8 -*-

from odoo import models, fields, api

class receipt_uuid(models.Model):
    _name = 'receipt.uuid'

    uuid = fields.Char()
