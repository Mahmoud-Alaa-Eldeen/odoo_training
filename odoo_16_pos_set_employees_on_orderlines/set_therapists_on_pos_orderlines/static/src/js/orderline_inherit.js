odoo.define('set_therapists_on_pos_orderlines.Orderline', function(require) {
    'use strict';

    const Orderline = require('point_of_sale.Orderline');
    const Registries = require('point_of_sale.Registries');

    const PosResOrderline = Orderline =>
        class extends Orderline {
          //add function for open add therapists popup to add them on orderlines

        //omara
        add_therapist() {
        //show add therapist popup
            var self = this;
            this.showPopup('set_therapist_popup', {});
        }
        //omara

        };

    Registries.Component.extend(Orderline, PosResOrderline);

    return Orderline;
});
