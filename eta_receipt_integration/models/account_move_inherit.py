# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class account_move_inherit(models.Model):
    _inherit = 'account.move'

    payload = fields.Text('Payload', copy=False)
    response = fields.Text('Response', copy=False)
    submission_done = fields.Boolean(copy=False)
    uuid = fields.Text('ETA-UUID')

    @api.onchange('partner_id')
    def _set_eta_type(self):
        for rec in self:
            if rec.partner_id:
                if rec.partner_id.vat:
                    rec.eta_type = 'invoice'
                else:
                    rec.eta_type = 'receipt'

    eta_type = fields.Selection(string="ETA-Type", selection=[('receipt', 'Receipt'), ('invoice', 'Invoice')],
                                )

    def sum_of_taxex(self, tax_ids):
        taxes_amount = 0
        for line in tax_ids:
            taxes_amount += line.amount

        return taxes_amount

    def group_tax_by_type(self, taxTotals):
        result = []
        for key, value in taxTotals.items():
            result.append({
                'taxType': key,
                'amount': value,
            })
        return result

    def get_previous_uuid(self):
        # for first receipt,should be not found pervious uuid,else send last one
        self.env.cr.execute('select "uuid" from "receipt_uuid" order by "id" desc limit 1')
        uuid_returned = self.env.cr.fetchone()
        if uuid_returned:
            return uuid_returned[0]
        else:
            return ''

        #

    def send_invoice_to_eta_receipt(self):
        buyer_type = ''
        if self.partner_id.customer_type == 'Individual':
            buyer_type = 'P'
        elif self.partner_id.customer_type == 'Company':
            buyer_type = 'B'
        elif self.partner_id.customer_type == 'Foreigner':
            buyer_type = 'F'

        receipt_lines = []
        totalSales = 0
        totalCommercialDiscount = 0
        totalItemsDiscount = 0
        netAmount = 0
        totalAmount = 0
        taxTotals = []

        # prepare info of receipt
        for inv_line in self.invoice_line_ids:
            itemType = ''
            if inv_line.product_id.code_type == 'gs1':
                itemType = 'GS1'
            elif inv_line.product_id.code_type == 'egs':
                itemType = 'EGS'

            totalSales += inv_line.quantity * inv_line.price_unit
            totalCommercialDiscount += inv_line.total_disc
            totalItemsDiscount += 0#(inv_line.total_disc / (inv_line.quantity * inv_line.price_unit)) * 100
            netAmount += inv_line.price_subtotal
            total_line_val = inv_line.price_subtotal + (
                    self.sum_of_taxex(inv_line.tax_ids) / 100) * inv_line.price_subtotal - totalItemsDiscount
            totalAmount += total_line_val

            taxable_items = []
            for tax in inv_line.tax_ids:
                tax_type_amount = inv_line.price_subtotal * (tax.amount / 100)
                taxable_items.append({
                    "taxType": tax.tax_type,
                    "amount": tax_type_amount,
                    "subType": tax.sub_type,
                    "rate": tax.amount

                })
                # tax amount totals per tax type
                if taxTotals:
                    if tax.tax_type in taxTotals[0]:  # taxTotals[0] dict contains: tax amount totals per tax type
                        taxTotals[0][tax.tax_type] += tax_type_amount
                    else:
                        taxTotals[0][tax.tax_type] = tax_type_amount
                else:
                    taxTotals.append({
                        tax.tax_type: tax_type_amount
                    })
            itemCode = ''
            if inv_line.product_uom_id.is_carton:
                itemCode = inv_line.product_id.carton_barcode
            elif inv_line.product_uom_id.is_box:
                itemCode = inv_line.product_id.box_barcode
            elif inv_line.product_uom_id.is_piece:
                itemCode = inv_line.product_id.piece_barcode

            receipt_lines.append({
                'internalCode': inv_line.product_id.default_code,
                'description': inv_line.name,
                'itemType': itemType,
                'itemCode': itemCode,  # inv_line.product_id.gs1_code if inv_line.product_id.gs1_code else '',
                'unitType': inv_line.product_uom_id.code,
                'quantity': inv_line.quantity,
                'unitPrice': inv_line.price_unit,
                'netSale': inv_line.price_subtotal,
                'totalSale': inv_line.quantity * inv_line.price_unit,
                'total': total_line_val,
                'commercialDiscountData': [{
                    'amount': inv_line.total_disc,
                    'description': inv_line.product_id.name

                }],
                'itemDiscountData': [{
                    'amount': 0,#(inv_line.total_disc / (inv_line.quantity * inv_line.price_unit)) * 100,
                    'description': inv_line.product_id.name

                }],
                'valueDifference': 0,
                'taxableItems': taxable_items,

            })

        # group taxtotals by tax type
        if taxTotals:
            taxTotals = self.group_tax_by_type(taxTotals[0])
        if not self.invoice_number:
            raise ValidationError(_("You must add invoice number,it's the receipt number on ETA"))
        # call send receipt to eta
        response_data = self.env['receipt.integration'].send_receipt({
            'receipt_lines': receipt_lines,
            'receipt_date': self.invoice_date + timedelta(hours=2),  # as difference on odoo server
            'receipt_number': self.invoice_number,
            'previous_uuid': self.get_previous_uuid(),
            'reference_old_uuid': "",
            'currency': self.currency_id.name,
            'exchangeRate': round((1 / self.currency_id.rate), 5) if (self.currency_id.name != 'EGP') else 0.0,
            'orderdeliveryMode': 'FC',
            'grossWeight': 0,
            'netWeight': 0,
            'receiptType': "S" if self.move_type=='out_invoice' else "R",
            'rin': self.company_id.vat,
            'companyTradeName': self.company_id.name,
            'branchCode': self.journal_id.receipt_branch_Code,
            'country': self.company_id.partner_id.country_id.code,
            'governate': self.company_id.partner_id.state_id.name,
            'regionCity': self.company_id.partner_id.city,
            'street': self.company_id.partner_id.street,
            'buildingNumber': str(self.company_id.partner_id.building_number),
            'postalCode': "",
            'floor': "1",
            'room': "1",
            'landmark': "landmark",
            'additionalInformation': "additionalInformation",
            'deviceSerialNumber': self.journal_id.deviceSerialNumber,
            'activityCode': self.journal_id.receipt_activity_code,
            'buyer_type': buyer_type,
            'buyer_id': self.partner_id.vat if self.partner_id.vat else '',
            'buyer_name': self.partner_id.name,
            'totalSales': totalSales,
            'totalCommercialDiscount': totalCommercialDiscount,
            'totalItemsDiscount': totalItemsDiscount,
            'extraReceiptDiscountData': [  # todo remove it
                {
                    "amount": 0,
                    "description": "ABC"
                }
            ],
            'netAmount': netAmount,
            'feesAmount': 0,
            'totalAmount': totalAmount,
            'taxTotals': taxTotals,
            'paymentMethod': 'C',
            'adjustment': 0,
            'contractor_name': '',
            'contractor_amount': 0,
            'contractor_rate': 0,
            'beneficiary_amount': 0,
            'beneficiary_rate': 0,

        })
        self.payload = response_data['payload']
        self.response = response_data['response']
        self.submission_done = response_data['submission_done']

        # if submission id returned,then save the uuid in previous uuid
        if response_data['submission_done']:
            self.env['receipt.uuid'].create({'uuid': response_data['uuid']})
            self.uuid=response_data['uuid']
        self.env.cr.commit()

    def action_post(self):
        res = super(account_move_inherit, self).action_post()

        # send  invoices with  type  out_invoice or out_refund
        if self.move_type in ('out_invoice', 'out_refund') and not self.partner_id.vat:
            self.send_invoice_to_eta_receipt()

        return res
