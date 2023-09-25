
from odoo import api, fields, models, _
from odoo.exceptions import Warning as UserError

import datetime

import logging
LOGGER = logging.getLogger(__name__)


class Pos_order_inherited(models.Model):
    _inherit = 'pos.order'







    @api.model
    def send_pos_order(self,order_pos_reference):



        pos_id=self.env['pos.order'].search([('pos_reference','=','Order '+order_pos_reference)])
        #if pos not configured to send pos orders to oracle
        if not pos_id.session_id.config_id.send_customer_to_oracle:
            return
        order_date = datetime.datetime.strptime(pos_id.date_order, '%Y-%m-%d %H:%M:%S')
        order_date = order_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        company_name = self.env.user.company_id.name
        order_info={'taxed':pos_id.taxed,'orderNumber':company_name[0]+company_name[1]+company_name[2]+company_name[3]+company_name[4]+' '+pos_id.pos_reference,'client':int(pos_id.partner_id.id),'orderDate':order_date,
               'SourceTransactionSystem':'OPS',
               'customer_number':int(pos_id.partner_id.id), 'receipt_Number':str(pos_id.id),'amount':pos_id.amount_total
               }


        products = []
        is_return_order=False
        line_number = 1
        for line in pos_id.lines :
            #if price in a line is < 0 then this return order
            if (line.price_subtotal_incl/line.qty)<0:
                is_return_order=True

            products.append({
                'ProductName':line.product_id.name,
                'Quantity':str(line.qty),
                'SequenceNumber':str(line_number),
            'UOM':line.product_id.uom_id.name,
            'discount':str(line.discount),
            'SourceTransactionLineIdentifier':str(line_number),
            'ExtendedAmount':str((line.price_subtotal_incl/line.qty)*(100/114)),

            'UnitSellingPrice':str((line.price_subtotal_incl/line.qty)*(100/114)),
            'price':str(line.product_id.lst_price),
            'taxes': self.get_taxes_as_string(line.tax_ids_after_fiscal_position),
            'product_tmpl_id':line.product_id.product_tmpl_id.id,


            })
            line_number = line_number + 1


        #Cash Customer in cient means not sent customer for pos order
        #notset in customer_number means not sent customer for pos order
        receipt_date=str(datetime.date.today()) #.strftime('YYYY-MM-DD')

        TransactionTypeCode=''
        if order_info['taxed']:
            TransactionTypeCode=self.env['oracle.order.type'].sudo().search([('order_category','=','Order'),('order_taxable','=',True)],limit=1).order_type

        else:
            TransactionTypeCode=self.env['oracle.order.type'].sudo().search([('order_category','=','Order'),('order_taxable','=',False)],limit=1).order_type


        #is_return_order==TRUE then get TransactionTypeCode as a  return order type
        if is_return_order:
            if order_info['taxed']:
                TransactionTypeCode = self.env['oracle.order.type'].sudo().search(
                    [('order_category', '=', 'Return'), ('order_taxable', '=', True)], limit=1).order_type

            else:
                TransactionTypeCode = self.env['oracle.order.type'].sudo().search(
                    [('order_category', '=', 'Return'), ('order_taxable', '=', False)], limit=1).order_type





        #todo 20 nov, get info from customer profile
        #=
        res=None
        ShipToPartyIdentifier = ""
        ShipToPartySiteIdentifier = ""
        BillToCustomerIdentifier = ""
        oracle_account_number = ""
        customer_account_id = ""
        RequestingBusinessUnitIdentifier = ""
        if order_info['customer_number']=='notset':
            # order_info['customer_number']=self.env['res.partner'].search([('default_customer','=',True)],limit=1).id
            order_info['customer_number']=self.env['pos.config'].search([('name','=',order_info['SourceTransactionSystem'])],limit=1).default_customer.id
            res=self.env['res.partner'].search([('id','=',order_info['customer_number'])])
            oracle_account_number=res.AccountNumber
            customer_account_id=res.customerAccountId

        elif order_info['customer_number']:
            res=self.env['res.partner'].search([('id','=',order_info['customer_number'])])
            oracle_account_number = res.AccountNumber
            customer_account_id = res.customerAccountId

        if res:

            ShipToPartyIdentifier=res.partyId
            shipto_billto=self.get_shiptosite_billtositeid(res)
            ShipToPartySiteIdentifier=shipto_billto['shiptosite']
            BillToCustomerIdentifier=shipto_billto['billtosite']
            BillToAccountSiteUseIdentifier=shipto_billto['BillToAccountSiteUseIdentifier']
            RequestingBusinessUnitIdentifier=res.business_unit.org_id

        if not RequestingBusinessUnitIdentifier:
            raise UserError(
                _('Selected Customer hasn not business unit, this shouldn not t be occured'))

        #SHIPMENT CODE WAS STANDARD PRIORITY
        # stataic info
        order_info['SourceTransactionSystem'] = 'OPS'
        body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:typ="http://xmlns.oracle.com/apps/scm/fom/importOrders/orderImportService/types/" xmlns:ord="http://xmlns.oracle.com/apps/scm/fom/importOrders/orderImportService/" xmlns:mod="http://xmlns.oracle.com/apps/scm/doo/processOrder/model/">
                   <soapenv:Header/>
                   <soapenv:Body>
                      <typ:createOrders>
                         <typ:request>
                          
                -<ord:Order>

                
                <ord:SourceTransactionSystem>"""+order_info['SourceTransactionSystem']+"""</ord:SourceTransactionSystem>
                <ord:SourceTransactionNumber>"""+order_info['orderNumber']+"""</ord:SourceTransactionNumber>
                <ord:SourceTransactionIdentifier>"""+order_info['orderNumber']+"""</ord:SourceTransactionIdentifier>
                <ord:BuyingPartyId>"""+ShipToPartyIdentifier+"""</ord:BuyingPartyId>
                
                
                
                
                <ord:ShipToPartyIdentifier>"""+ShipToPartyIdentifier+"""</ord:ShipToPartyIdentifier>
                <ord:ShipToPartySiteIdentifier>"""+ShipToPartySiteIdentifier+"""</ord:ShipToPartySiteIdentifier>
                <ord:BillToCustomerIdentifier>"""+BillToCustomerIdentifier+"""</ord:BillToCustomerIdentifier>
                
                
                
                
                <ord:TransactionalCurrencyCode>EGP</ord:TransactionalCurrencyCode>
                <ord:TransactionOn>"""+order_info['orderDate']+"""</ord:TransactionOn>
                <ord:OrigSystemDocumentReference/>
                <ord:RequestingBusinessUnitIdentifier>"""+RequestingBusinessUnitIdentifier+"""</ord:RequestingBusinessUnitIdentifier>
                
                
                
                
                
                
                
                
                
                
                
                <ord:FreezePriceFlag>false</ord:FreezePriceFlag>
                <ord:FreezeShippingChargeFlag>false</ord:FreezeShippingChargeFlag>
                <ord:FreezeTaxFlag>false</ord:FreezeTaxFlag>
                <ord:TransactionTypeCode>"""+TransactionTypeCode+"""</ord:TransactionTypeCode>
                <ord:ShipmentPriorityCode>HIGH</ord:ShipmentPriorityCode>
                <ord:ShipmentPriority/>
                
                
                
                
                
             """


        if BillToAccountSiteUseIdentifier:

            BillToAccountSiteUseIdentifier=BillToAccountSiteUseIdentifier
        else:
            BillToAccountSiteUseIdentifier=''

        for product in products:
           vals=self.get_prod_values(product['product_tmpl_id'])
           product['SourceTransactionLineIdentifier']=product['SequenceNumber']#vals['SourceTransactionLineIdentifier']
           product['SourceTransactionLineNumber']=product['SequenceNumber']#vals['SourceTransactionLineNumber']
           product['InventoryOrganizationIdentifier']=res.business_unit.org_id_for_items  #vals['orgId']


           if order_info['taxed']:
               product['taxes'] = self.get_taxes_as_string(product['taxes'])


           else:
               product['taxes']=""

           body=body+ """
                -<ord:Line>
                <ord:ManualPriceAdjustment>
                <ord:SourceTransactionSystem>"""+order_info['SourceTransactionSystem']+"""</ord:SourceTransactionSystem>
                <ord:SourceTransactionNumber>"""+order_info['orderNumber']+"""</ord:SourceTransactionNumber>
                <ord:SourceTransactionIdentifier>"""+order_info['orderNumber']+"""</ord:SourceTransactionIdentifier>
              
                




                <ord:SourceTransactionLineIdentifier>"""+product['SourceTransactionLineIdentifier']+"""</ord:SourceTransactionLineIdentifier>
                
                
                
                
                
                
                <ord:SourceTransactionLineNumber>"""+product['SourceTransactionLineNumber']+"""</ord:SourceTransactionLineNumber>
                <ord:SourceTransactionScheduleNumber>"""+product['SourceTransactionLineNumber']+"""</ord:SourceTransactionScheduleNumber>
                <ord:SourceTransactionScheduleIdentifier>"""+product['SourceTransactionLineIdentifier']+"""</ord:SourceTransactionScheduleIdentifier>
                
                
                
                
                
                
                    <ord:AdjustmentAmount>"""+product['ExtendedAmount']+"""</ord:AdjustmentAmount>
                    <ord:AdjustmentType>Price override</ord:AdjustmentType>
                    <ord:ChargeDefinitionCode>QP_SALE_PRICE</ord:ChargeDefinitionCode>
                    <ord:ChargeRollupFlag>false</ord:ChargeRollupFlag>
                                    
                    <ord:SourceManualPriceAdjustmentIdentifier>1</ord:SourceManualPriceAdjustmentIdentifier>
                        <ord:SequenceNumber>"""+product['SequenceNumber']+"""</ord:SequenceNumber>
                        <ord:Reason>Other</ord:Reason>
                        </ord:ManualPriceAdjustment>
                        
                        <ord:TransactionTypeCode>"""+TransactionTypeCode+"""</ord:TransactionTypeCode>
                        
                        <ord:OrigSystemDocumentReference/>





                 <ord:SourceTransactionLineIdentifier>"""+product['SourceTransactionLineIdentifier']+"""</ord:SourceTransactionLineIdentifier>
                
                <ord:SourceTransactionLineNumber>"""+product['SourceTransactionLineNumber']+"""</ord:SourceTransactionLineNumber>
                <ord:SourceTransactionScheduleNumber>"""+product['SourceTransactionLineNumber']+"""</ord:SourceTransactionScheduleNumber>
                <ord:SourceTransactionScheduleIdentifier>"""+product['SourceTransactionLineIdentifier']+"""</ord:SourceTransactionScheduleIdentifier>
                
                
            


                
                <ord:ProductNumber>"""+product['ProductName']+"""</ord:ProductNumber>
                <ord:OrderedQuantity unitCode="PC">"""+product['Quantity']+"""</ord:OrderedQuantity>
                <ord:OrderedUOM>"""+product['UOM']+"""</ord:OrderedUOM>
                
                
                
                <ord:RequestedFulfillmentOrganizationIdentifier>"""+product['InventoryOrganizationIdentifier']+"""</ord:RequestedFulfillmentOrganizationIdentifier>
                <ord:RequestedShipDate>"""+order_info['orderDate']+"""</ord:RequestedShipDate>
                <ord:PaymentTermsCode>5</ord:PaymentTermsCode>
                <ord:TransactionCategoryCode>ORDER</ord:TransactionCategoryCode>
                <ord:InventoryOrganizationIdentifier>"""+product['InventoryOrganizationIdentifier']+"""</ord:InventoryOrganizationIdentifier>
                <ord:UnitListPrice currencyCode="EGP">"""+product['price']+"""</ord:UnitListPrice>
                <ord:UnitSellingPrice currencyCode="EGP">"""+product['UnitSellingPrice']+"""</ord:UnitSellingPrice>
                
                
                
                
                
                <ord:BillToCustomerIdentifier>"""+BillToCustomerIdentifier+"""</ord:BillToCustomerIdentifier>
                
                <ord:BillToAccountSiteUseIdentifier>"""+BillToAccountSiteUseIdentifier+"""</ord:BillToAccountSiteUseIdentifier>
                
                <ord:PartialShipAllowedFlag>True</ord:PartialShipAllowedFlag>
                <ord:OrigSystemDocumentReference>ORIGSYS</ord:OrigSystemDocumentReference>
                <ord:OrigSystemDocumentLineReference>ORIGSYSLINE</ord:OrigSystemDocumentLineReference>
                
                <ord:TaxExempt>S</ord:TaxExempt>
                <ord:TaxClassification>"""+product['taxes']+"""</ord:TaxClassification>
                
                <ord:TransactionLineTypeCode>ORA_BUY</ord:TransactionLineTypeCode>
                
                <ord:ShipmentPriorityCode>HIGH</ord:ShipmentPriorityCode>


                </ord:Line>
                     """



        body=body+"""
                    -<ord:OrderPreferences>
                <ord:CreateCustomerInformationFlag>false</ord:CreateCustomerInformationFlag>
                <!-- If no value is passed in the SubmitFlag then the order is submitted for processing. If you want to create the order in DRAFT mode then pass value as false. -->
                <ord:SubmitFlag>true</ord:SubmitFlag>
                </ord:OrderPreferences>
                </ord:Order>
                
                         </typ:request>
                      </typ:createOrders>
                   </soapenv:Body>
                </soapenv:Envelope>


        """

        #save body of api that will be sent to oracle
        #to check it if order not sent, will run it from postman
        pos_id.write({
            'oracle_payload':body
        })
        orderNumber= order_info['orderNumber']
        customer_name= res.name#order_info['client']
        customer_number= str(customer_account_id)
        receipt_Number= order_info['receipt_Number']
        amount= str(order_info['amount'])
        business_unit_id=RequestingBusinessUnitIdentifier
        taxed= order_info['taxed']
        self.env['send.pos.order'].cron_oracle_send_pos_order("https://oracle_fusion:443/fscmService/OrderImportService?wsdl", "*****", "******",body, orderNumber, customer_name,customer_number, receipt_Number,amount,receipt_date,taxed,business_unit_id,res)

