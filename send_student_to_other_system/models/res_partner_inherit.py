# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta

from xmlrpc import client as xmlrpc_client
import ssl
import requests
import json

import logging

LOGGER = logging.getLogger(__name__)


class res_partner_inherit(models.Model):
    _inherit = 'res.partner'

    def send_student_to_other_system(self, student_data):
        #
        url = 'http://localhost:8014'
        db = 'testing_odoo_receiver'
        username = 'admin'
        password = '1'

        # auth with db
        authenticated = self.auth_with_db(url, username, password, db)
        if authenticated:
            url = url + "/object/res.partner/create_student"

            payload = {
                "params": {
                    "args": [],
                    "kwargs":  student_data

                }

            }
            payload = json.dumps(payload)
            headers = {
                'content-type': "application/json",

            }

            response = requests.request("POST", url, data=payload, headers=headers, cookies=authenticated['cookies'])

            print("result response :> ", response.text)

    def auth_with_db(self, url, username, password, db_name):
        #
        url += "/auth"
        payload = {"params": {"login": username, "password": password,
                              "db": db_name}}

        payload = json.dumps(payload)
        headers = {
            'content-type': "application/json",
            # 'cache-control': "no-cache",
            # 'postman-token': "1c96a08b-f55e-d2b0-b63c-a4eb9b412e74"
        }

        response = requests.request("POST", url, data=payload, headers=headers)
        cookies = response.cookies
        if response.status_code == 200:
            response = json.loads(response.text)
            if "result" in response and response['result']['uid'] > 0:
                return {'cookies': cookies}
            else:
                return False
        else:
            return False

    @api.model
    def create(self, vals):
        record = super(res_partner_inherit, self).create(vals)

        # send student data to other systems
        self.send_student_to_other_system({'name': record.name, 'email': record.email, 'phone': record.phone})

        return record
