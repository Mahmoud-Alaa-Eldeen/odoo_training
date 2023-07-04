# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta

from xmlrpc import client as xmlrpc_client
import ssl
import requests
import json

import logging
LOGGER = logging.getLogger(__name__)

class product_template_inherit(models.Model):
    _inherit = 'product.template'



    def send_product_updates_to_store_db(self, store_db, data):
        #
        url = store_db.server_url
        db = store_db.db_name
        username =  store_db.db_user
        password =  store_db.db_password
        print("url :> ",url)
        print("password :> ",password)
        # auth with db
        authenticated = self.auth_with_db(url, username, password, db)
        if authenticated:
            #
            url = url+"/object/res.partner/create_partner"

            payload = {
                "params": {
                    "args": [],
                    "kwargs": {"data": data}

                }

            }
            payload = json.dumps(payload)
            headers = {
                'content-type': "application/json",


            }

            response = requests.request("POST", url, data=payload, headers=headers,cookies=authenticated['cookies'])

            print("result response :> ",response.text)


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
                return {'cookies' :cookies}
            else:
                return False
        else:
            return False
