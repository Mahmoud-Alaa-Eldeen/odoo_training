# -*- coding: utf-8 -*-

from odoo import models, fields, api


class res_partner_inherit(models.Model):
    _inherit = 'res.partner'


    def create_partner(self, args=[], **kwargs):
        self = self.sudo()

        # parameters validations
        if not kwargs['name'] or not isinstance(kwargs['name'], str):
            return "not supported type for name"
        if not kwargs['email'] or not isinstance(kwargs['email'], str):
            return "not supported type for email"
        if not kwargs['phone'] or not isinstance(kwargs['phone'], str):
            return "not supported type for phone"


        # fill data
        vals = {}
        vals['name'] = kwargs['name']
        vals['email'] = kwargs['email']
        vals['phone'] = kwargs['phone']

        created = self.env['res.partner'].create(vals)
        kwargs['id'] = created.id

        return kwargs

