# -*- coding: utf-8 -*-

from odoo import models, fields, api


class account_journal_inherit(models.Model):
    _inherit = 'account.journal'

    receipt_branch_Code = fields.Char('Receipt Branch Code')
    deviceSerialNumber = fields.Char('Device Serial Number')
    receipt_activity_code = fields.Char('Receipt Activity Code')
