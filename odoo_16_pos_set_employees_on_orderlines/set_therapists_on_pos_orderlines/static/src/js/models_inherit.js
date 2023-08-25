odoo.define('l10n_co_pos.pos', function (require) {
"use strict";

var { PosGlobalState } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');


const CustomCoPosGlobalState = (PosGlobalState) => class CustomCoPosGlobalState extends PosGlobalState {


       //add  employee model to be load in pos
       async _processData(loadedData) {
            var result = super._processData(loadedData);

            this.env.pos.employees_data = loadedData['hr.employee'];

            return result;
       }


       //override method, add some args and call custom create from ui method like odoo one
       _save_to_server (orders, options) {

        if (!orders || !orders.length) {
            return Promise.resolve([]);
        }
        this.set_synch('connecting', orders.length);
        options = options || {};

        var self = this;
        var timeout = typeof options.timeout === 'number' ? options.timeout : 30000 * orders.length;


        // Keep the order ids that are about to be sent to the
        // backend. In between create_from_ui and the success callback
        // new orders may have been added to it.
        var order_ids_to_sync = _.pluck(orders, 'id');

        // we try to send the order. shadow prevents a spinner if it takes too long. (unless we are sending an invoice,
        // then we want to notify the user that we are waiting on something )
        var args = [_.map(orders, function (order) {
                order.to_invoice = options.to_invoice || false;
                return order;
            })];

        args.push(options.draft || false);

        //omara
        args.push({
        'first_therapist':self.env.pos.first_therapist,
        'second_therapist':self.env.pos.second_therapist,
        'third_therapist':self.env.pos.third_therapist,

        });

       console.log('in community send order to backend',args);
        //omara
        return this.env.services.rpc({
                model: 'pos.order',
                method: 'create_from_ui_custom',//omara
                args: args,
                kwargs: {context: this.env.session.user_context},
            }, {
                timeout: timeout,
                shadow: !options.to_invoice
            })
            .then(function (server_ids) {
                _.each(order_ids_to_sync, function (order_id) {
                    self.db.remove_order(order_id);
                });
                self.failed = false;
                self.set_synch('connected');
                return server_ids;
            }).catch(function (error){
                console.warn('Failed to send orders:', orders);
                if(error.code === 200 ){    // Business Logic Error, not a connection problem
                    // Hide error if already shown before ...
                    if ((!self.failed || options.show_error) && !options.to_invoice) {
                        self.failed = error;
                        self.set_synch('error');
                        throw error;
                    }
                }
                self.set_synch('disconnected');
                throw error;
            });
    }



}


Registries.Model.extend(PosGlobalState, CustomCoPosGlobalState);


});
