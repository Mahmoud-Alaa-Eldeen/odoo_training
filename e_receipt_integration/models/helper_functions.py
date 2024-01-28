# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json

import hashlib
import base64
import uuid


class helper_functions(models.Model):
    _name = 'helper.functions'


    def get_api_parameter(self, parameter):
        return self.env['api.parameter'].search([('name', '=', parameter)], limit=1).value

    def get_api_url(self, url_for):
        return self.env['api.url'].search([('name', '=', url_for)], limit=1).url


    def body_Serialize_toget_uuid(self, documentStructure):
        #idea: make the text in one line, with removing spaces and capitalize dictionary keys,not values

        if isinstance(documentStructure, str) or isinstance(documentStructure, float) or isinstance(documentStructure,
                                                                                                    int):
            return '"' + str(documentStructure) + '"'

        serializeString = ""
        for elem, val in documentStructure.items():
            if not isinstance(val, list):
                serializeString += '"' + elem.upper() + '"'
                serializeString += self.body_Serialize_toget_uuid(val)

            if isinstance(val, list):
                serializeString += '"' + elem.upper() + '"'
                for array_elem in val:
                    serializeString += '"' + elem.upper() + '"'
                    serializeString += self.body_Serialize_toget_uuid(array_elem)

        return serializeString


    def generate_uuid(self, data):
        #according to serialization algorithm from eta
        #src: https://sdk.invoicing.eta.gov.eg/receiptissuancefaq/#how-to-generate-receipt-uuid

        res = self.body_Serialize_toget_uuid(data)
        res = res.encode("utf-8")
        sha256_hash = hashlib.sha256()
        sha256_hash.update(res)
        result = sha256_hash.hexdigest()
        return result

