from odoo import models, fields, api


class pos_order_inherit(models.Model):

   _inherit = 'pos.order'


   def add_therapists_on_orderlines(self,pos_order,therapists):
      if pos_order and therapists:
         #loop on orderlines, add therapists linked to  product that is in the orderline
         for orderline in pos_order.lines:
            #therapists is a dict like key is product id and value if employee id:
            # {'first_therapist': {'4': '1', '5': '1', '6': '1'}, 'second_therapist': {'4': '', '5': '', '6': ''},
            #  'third_therapist': {'4': '', '5': '1', '6': ''}}
            if orderline.product_id and  str(orderline.product_id.id) in therapists['first_therapist'] and therapists['first_therapist'][str(orderline.product_id.id)]:
               orderline.first_therapist=int(therapists['first_therapist'][str(orderline.product_id.id)])

            if orderline.product_id and  str(orderline.product_id.id) in therapists['second_therapist'] and therapists['second_therapist'][str(orderline.product_id.id)]:
               orderline.second_therapist=int(therapists['second_therapist'][str(orderline.product_id.id)])

            if orderline.product_id and  str(orderline.product_id.id) in therapists['third_therapist'] and therapists['third_therapist'][str(orderline.product_id.id)]:
               orderline.third_therapist=int(therapists['third_therapist'][str(orderline.product_id.id)])



   @api.model
   def create_from_ui_custom(self, orders,draft=False,therapists=None):
      print('orders',orders)
      order = self.env['pos.order'].create_from_ui(orders, draft=False)

      #add therapists on the orderlines of the order
      created_order = self.env['pos.order'].search([('id','=',order[0]['id'])])
      if therapists:
         self.add_therapists_on_orderlines(created_order,therapists)


      return order






