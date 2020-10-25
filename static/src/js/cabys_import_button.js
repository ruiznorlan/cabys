odoo.define('cabys.cabys_import_button', function (require) {
"use strict";
var core = require('web.core');
var ListView = require('web.ListView');

ListView.include({

    render_buttons: function() {
        // GET BUTTON REFERENCE
        this._super.apply(this, arguments);
        if (this.$buttons) {
            var btn = this.$buttons.find('.oe_cabys_import_button');
        }
        // PERFORM THE ACTION
        btn.on('click', this.proxy('cabys_import_button'));
    },

    cabys_import_button: function () {

        console.log('yay importing cabys catalog');
        var self = this;
        // var state = self.model.get(self.handle, {raw: true});
        // var context = state.getContext();
    
        self.do_action({
            type: 'ir.actions.act_window',
            res_model: 'cabys.catalog.import.wizard',
            target: 'new',
            views: [[false, 'form']],
            // context: context,
        });
    
    },


});
    
})