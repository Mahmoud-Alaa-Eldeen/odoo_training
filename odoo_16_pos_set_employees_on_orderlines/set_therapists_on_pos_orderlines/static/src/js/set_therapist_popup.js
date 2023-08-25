odoo.define("sh_pos_keyboard_shortcut.set_therapist_popup", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");

    class set_therapist_popup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
        }

      createObj(obj1, obj2){
            var food = {};
            for (var i in obj1) {
              food[i] = obj1[i];
            }
            for (var j in obj2) {
              food[j] = obj2[j];
            }
            return food;
      };

       getSelectedOption(selection_id) {
        var selectElement = document.querySelector('#'+selection_id);
        return selectElement.value;

    }

        add_therapists(){

           var self = this;

        //omara
        //add therapists to pos env as fields and fill with data
        //note: therapists will be added on orderlines
        var product_id = self.env.pos.get_order().get_selected_orderline().get_product().id;

        //if fields added before merge the dict of data
        var data ={}
        data [product_id]= self.getSelectedOption('first_therapist');
        if (self.env.pos.first_therapist){
            self.env.pos.first_therapist = self.createObj(self.env.pos.first_therapist,data);
        }
        else{
            self.env.pos.first_therapist = data;
        }

        data ={}
        data [product_id]= self.getSelectedOption('second_therapist');
        if (self.env.pos.second_therapist){
            self.env.pos.second_therapist = self.createObj(self.env.pos.second_therapist,data);
        }
        else{
            self.env.pos.second_therapist = data;
        }



        data ={}
        data [product_id]= self.getSelectedOption('third_therapist');
        if (self.env.pos.third_therapist){
            self.env.pos.third_therapist = self.createObj(self.env.pos.third_therapist,data);
        }
        else{
            self.env.pos.third_therapist = data;
        }



        console.log('selfo in save therapists in pos env',self);


        //close popup after add therapists
        this.cancel();

        }

        cancel (){
            super.cancel();
        }
    }

    set_therapist_popup.template = "set_therapist_popup";
    Registries.Component.add(set_therapist_popup);

    return {
        set_therapist_popup,
    };
});
