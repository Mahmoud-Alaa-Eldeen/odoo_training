"""Send passed POS order details to remote soap api"""
import requests
import json
import xmltodict  # @need pip install xmltodict
from xlwt.compat import unicode
from odoo.exceptions import Warning as UserError

import logging

LOGGER = logging.getLogger(__name__)

import multiprocessing

from odoo import api, fields, models, _
from multiprocessing.pool import ThreadPool
import datetime

import time
import threading

from xmlrpc import client as xmlrpc_client
import ssl

import logging

LOGGER = logging.getLogger(__name__)


class SendPosOrder(models.Model):
    """Inherited Product Template Model"""
    _name = 'send.pos.order'


    @api.model
    def cron_oracle_send_pos_order(self, url, username, password, body, orderNumber, customer_name, customer_number,
                                   receipt_Number, amount, receipt_date, taxed, business_unit_id, res):

        # self.set_taxed_value(orderNumber,taxed,res)
        self.handle_soap_in_thread(url, username, password, body, orderNumber, customer_name, customer_number,
                                   receipt_Number, amount, receipt_date, taxed, business_unit_id)


    def handle_soap_in_thread(self, url, username, password, body, orderNumber, customer_name, customer_number,
                              receipt_Number, amount, receipt_date, taxed, business_unit_id):

        #get CustomerSiteUseId
        CustomerSiteUseId=self.get_CustomerSiteUseId(customer_number)
        # get db credentials to save some info after sending order in thread
        server_db = {}
        email_to = ''

        pool = ThreadPool(processes=int(multiprocessing.cpu_count() / 2))
        # remove company name and _ from ordernumber
        orderNumber = orderNumber.replace(orderNumber[:6], '')
        #LOGGER.critical("orderNumber  in sending pos order")
        #LOGGER.critical(orderNumber)
        pool.apply_async(self.send_pos_order_to_soap, (
        url, username, password, body, orderNumber, customer_name, customer_number, receipt_Number, amount,
        receipt_date, taxed, business_unit_id, server_db,email_to,CustomerSiteUseId))




    def send_pos_order_to_soap(self, url, username, password, body, orderNumber, customer_name, customer_number,
                               receipt_Number, amount, receipt_date, taxed, business_unit_id, server_db,email_to,CustomerSiteUseId):
        """#sending passed params to remote soap web service.

                :param: url: (str) the web service URL.
                :param: username: (str) the user to authenticate the request against.
                :param: password: (str) the password used for authentication.
                :param: body: (str) the soap body.

                :return: (status) returns a boolean value TRue i sent succeffuly, false if not"""

        headers = {'Content-type': 'text/xml; charset=utf-8'}  # {'Content-type': 'text/xml'}
        body_bef_encode = body
        body = body.encode('utf-8')
        response = requests.post(url, data=body, headers=headers, auth=(username, password))
        print("body for  sending pos order", body_bef_encode)
        #LOGGER.critical("body for  sending pos order")
        #LOGGER.critical(body_bef_encode)
        print("response content fo sending pos order", response.content)
        #LOGGER.critical("response content fo sending pos order")
        #LOGGER.critical(response.content)

        # check if status returned success,else send again
        json_obj = self.get_json_from_resp(response.content)
        status = json_obj['env:Envelope']['env:Body']['ns0:createOrdersResponse']['ns1:result']['ns0:ReturnStatus']

        if (status != 'SUCCESS'):
            # send email to me and cc as:  oracle developer
            err_msg='order body: '+body_bef_encode+'         response:  '+str(response.content)
            self.send_email_of_pos_order_error(self,err_msg , email_to)


        elif status == 'SUCCESS':

            # save oracle_order_number returned from the response  orderNumber
            oracle_order_number = json_obj['env:Envelope']['env:Body']['ns0:createOrdersResponse']['ns1:result'][
                'ns0:OrderNumber']
            # call_save_oracle_order_number
            self.call_save_oracle_order_number(server_db, orderNumber, oracle_order_number)




        # stop thread for 5 minutes, for some changes to be done in oracle
        #
        # todo test apis and run it
        # time.sleep(350)

