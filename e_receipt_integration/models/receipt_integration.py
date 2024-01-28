# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests
import json
from datetime import datetime
from odoo.exceptions import ValidationError

import hashlib
import base64
import uuid


class receipt_integration(models.Model):
    _name = 'receipt.integration'

    # steps:
    # first: calling the get token
    # second :prepare receipt data and using token,send it to eta

    # 1- authentication request
    def auth_and_get_token(self):
        param_model = self.env['helper.functions']
        url = param_model.get_api_url('auth_url')
        client_id = param_model.get_api_parameter('client_id')
        client_secret = param_model.get_api_parameter('client_secret')
        posserial = param_model.get_api_parameter('posserial')
        presharedkey = param_model.get_api_parameter('presharedkey')
        pososversion = param_model.get_api_parameter('pososversion')

        payload = 'grant_type=client_credentials&client_id=' + client_id + '&client_secret=' + client_secret
        headers = {
            'posserial': posserial,
            'pososversion': pososversion,
            'presharedkey': presharedkey,
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        token = ''
        if response.status_code == 200:
            token = json.loads(response.text)['access_token']

        return {'token': token}

    # 2- receipt request
    def body_preparation(self, info):
        body = {
            "header": {
                "dateTimeIssued": str(info['receipt_date']) + 'T' + str(datetime.now().strftime("%H:%M:%S")) + 'Z',
                # "dateTimeIssued": str((str(info['receipt_date']) + ' ' + str(datetime.now().strftime("%H:%M:%S"))).strftime(
                #     "%Y-%m-%dT%H:%M:%SZ")),
                "receiptNumber": info['receipt_number'],
                "uuid": "",
                "previousUUID": info['previous_uuid'],
                "referenceOldUUID": info['reference_old_uuid'],
                "currency": info['currency'],
                "exchangeRate": round(info['exchangeRate'], 5),
                "sOrderNameCode": "",
                "orderdeliveryMode": info['orderdeliveryMode'],
                "grossWeight": info['grossWeight'],
                "netWeight": info['netWeight']

            },
            "documentType": {
                "receiptType": info['receiptType'],
                "typeVersion": "1.2"
            },
            "seller": {
                "rin": info['rin'],
                "companyTradeName": info['companyTradeName'],
                "branchCode": info['branchCode'],
                "branchAddress": {
                    "country": info['country'],
                    "governate": info['governate'],
                    "regionCity": info['regionCity'],
                    "street": info['street'],
                    "buildingNumber": info['buildingNumber'],
                    "postalCode": info['postalCode'],
                    "floor": info['floor'],
                    "room": info['room'],
                    "landmark": info['landmark'],
                    "additionalInformation": info['additionalInformation']
                },
                "deviceSerialNumber": info['deviceSerialNumber'],
                "syndicateLicenseNumber": "",
                "activityCode": info['activityCode']
            },
            "buyer": {
                "type": info['buyer_type'],
                "id": info['buyer_id'],
                "name": info['buyer_name'],
                "mobileNumber": "",
                "paymentNumber": ""
            },
            "totalSales": round(info['totalSales'], 5),
            "totalCommercialDiscount": round(info['totalCommercialDiscount'], 5),
            "totalItemsDiscount": round(info['totalItemsDiscount'], 5),
            "extraReceiptDiscountData": [{
                "amount": rece_dis_data['amount'],
                "description": rece_dis_data['description']
            } for rece_dis_data in info['extraReceiptDiscountData']
            ],
            "netAmount": round(info['netAmount'], 5),
            "feesAmount": round(info['feesAmount'], 5),
            "totalAmount": round(info['totalAmount'], 5),
            "taxTotals": [{
                "taxType": tax_total['taxType'],
                "amount": round(tax_total['amount'], 5)
            } for tax_total in info['taxTotals']
            ] if 'taxTotals' in info else [],
            "paymentMethod": info['paymentMethod'],
            "adjustment": round(info['adjustment'], 5),
            "contractor": {
                "name": info['contractor_name'],
                "amount": round(info['contractor_amount'], 5),
                "rate": round(info['contractor_rate'], 5)
            },
            "beneficiary": {
                "amount": round(info['beneficiary_amount'], 5),
                "rate": round(info['beneficiary_rate'], 5)
            }
        }

        # if refund invoice add ref for original invoice
        if info['receiptType'] == 'R':
           body['header']['referenceUUID'] = 'anydata'

        # add receipt lines
        itemData = []
        for line in info['receipt_lines']:
            itemData.append({
                "internalCode": line['internalCode'],
                "description": line['description'],
                "itemType": line['itemType'],
                "itemCode": line['itemCode'],
                "unitType": line['unitType'],
                "quantity": round(line['quantity'], 5),
                "unitPrice": round(line['unitPrice'], 5),
                "netSale": round(line['netSale'], 5),
                "totalSale": round(line['totalSale'], 5),
                "total": round(line['total'], 5),
                "commercialDiscountData": [{
                    "amount": round(comm_dis['amount'], 5),
                    "description": comm_dis['description']
                } for comm_dis in line['commercialDiscountData']
                ],
                "itemDiscountData": [{
                    "amount": round(item_dis['amount'], 5),
                    "description": item_dis['description']
                } for item_dis in line['itemDiscountData']
                ],
                "valueDifference": round(line['valueDifference'], 5),
                "taxableItems": [{
                    "taxType": tax_item['taxType'],
                    "amount": round(tax_item['amount'], 5),
                    "subType": tax_item['subType'],
                    "rate": round(tax_item['rate'], 5)
                } for tax_item in line['taxableItems']

                ]
            })

        body['itemData'] = itemData

        # generate uuid and add in body
        body['header']['uuid'] = self.env['helper.functions'].generate_uuid(body)

        return {"receipts": [body]}

    # send receipt
    def send_receipt(self, receipt_details):
        # 1-call auth to get token
        token = self.auth_and_get_token()['token']

        # prepare send receipt parameters
        body_data = self.body_preparation(receipt_details)
        uuid = body_data['receipts'][0]['header']['uuid']
        payload = json.dumps(body_data, ensure_ascii=False).encode('utf-8')
        url = self.env['api.url'].search([('name', '=', 'submit_receipt')], limit=1).url
        headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',

        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(payload)
        print(response.text)

        submission_resp = json.loads(response.text)
        submission_done = True if (
                    'submissionId' in submission_resp and len(submission_resp['rejectedDocuments']) == 0) else False

        prevent_invalid_receipts = self.env['api.parameter'].search([('name', '=', 'prevent_invalid_receipts'),
                                                                     ('value', '=', 'True')
                                                                     ])
        if not submission_done and prevent_invalid_receipts:
            error_msg = str(
                submission_resp['rejectedDocuments'][0]["error"]) if 'rejectedDocuments' in submission_resp else ''
            raise ValidationError(_(
                "You must solve errors in ETA Response,and validate again, errors are following: " + '\n' + error_msg))

        return {
            'submission_done': True if submission_done else False,
            'uuid': uuid,
            'payload': payload,
            'response': response.text
        }
