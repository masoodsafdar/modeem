odoo.define("web_disable_export_delete_button", function(require) {
        console.log("Helloooo!");

"use strict";
    var maknoun_dataexport = require('web.DataExport');
    var core = require('web.core');
    var data = require('web.data');
    var Dialog = require('web.Dialog');

    var QWeb = core.qweb;
    var _t = core._t;

    var session = require("web.session");

    maknoun_dataexport.include({

    	/**
         * Render the sidebar (the 'action' menu in the control panel, right of the
         * main buttons)
         *
         * @param {jQuery Node} $node
         */

            show_exports_list: function() {
                var has_export_group = false;
                        session.user_has_group('web_disable_export_delete_button.group_delete_export_button').then(function(has_group) {
                        console.log(has_group)
                            if(has_group) {
                                has_export_group = true;
                                console.log(has_export_group)
                            } else {
                                has_export_group = false;
                                console.log(has_export_group)

                            }
                        });
                        if (session.is_superuser) {
                                has_export_group = true;
                            }
                if (this.$('.o_exported_lists_select').is(':hidden')) {
                    this.$('.o_exported_lists').show();
                    return $.when();
                }

                var self = this;
                return this._rpc({
                    model: 'ir.exports',
                    method: 'search_read',
                    fields: ['name'],
                    domain: [['resource', '=', this.record.model]]
                }).then(function (export_list) {
                    if (!export_list.length) {
                        return;
                    }
                    self.$('.o_exported_lists').append(QWeb.render('Export.SavedList', {'existing_exports': export_list}));
                    self.$('.o_exported_lists_select').on('change', function() {
                        self.$fields_list.empty();
                        var export_id = self.$('.o_exported_lists_select option:selected').val();
                        if(export_id) {
                            self._rpc({
                                    route: '/web/export/namelist',
                                    params: {
                                        model: self.record.model,
                                        export_id: parseInt(export_id, 10),
                                    },
                                })
                                .then(do_load_export_field);
                        }
                    });
                    self.$('.o_delete_exported_list').click(function() {
                    console.log("ooooleh!");

                        if (has_export_group) {
                           console.log(has_export_group)

                            var select_exp = self.$('.o_exported_lists_select option:selected');
                            var options = {
                                confirm_callback: function () {
                                    if (select_exp.val()) {
                                        self.exports.unlink([parseInt(select_exp.val(), 10)]);
                                        select_exp.remove();
                                        self.$fields_list.empty();
                                        if (self.$('.o_exported_lists_select option').length <= 1) {
                                            self.$('.o_exported_lists').hide();
                                        }
                                    }
                                }
                            };

                            Dialog.confirm(this, _t("Do you really want to delete this export template?"), options);

                        }
                        if(has_export_group === false){
                            Dialog.confirm(this, _t("You do not have permission to delete the data export list"), options);
                        }
                    });
               });

                function do_load_export_field(field_list) {
                    _.each(field_list, function (field) {
                        self.$fields_list.append(new Option(field.label, field.name));
                    });
                }
            },

    });

});
