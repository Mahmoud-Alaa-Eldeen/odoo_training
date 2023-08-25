odoo.define('point_of_sale.ReceiptScreenInherited', function(require) {
"use strict";

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
	const Registries = require('point_of_sale.Registries');
	const InheritedReceiptScreen = ReceiptScreen => class extends ReceiptScreen {

          _show_receipt_template(checkboxElem) {
          self=this;
          if (document.querySelector('#g01-01').checked) {
                    const { name, props } = this.nextScreen;
                    self.env.pos.gift=true;
                    self.showScreen('ReceiptScreen',{gift:true});


          } else {
                   const { name, props } = this.nextScreen;
                   self.env.pos.gift=false;
                   self.showScreen('ReceiptScreen',{gift:false});
        }


         }

}

Registries.Component.extend(ReceiptScreen, InheritedReceiptScreen);

return ReceiptScreen;

});
