odoo.define('web_hijri_date.web_hijri_date', function (require) {

    var core = require('web.core');
    var data = require('web.data');
    var time = require('web.time');
    var field_utils = require('web.field_utils');
    var datepicker = require('web.datepicker');
    var basic_fields = require('web.basic_fields');
    var ListView  = require('web.ListView');
    var search_filters_datetime = core.search_filters_registry.get('datetime')
    var pyeval = require('web.pyeval');
    var Session = require('web.Session');

    var _t = core._t,
        _lt = core._lt;
    var QWeb = core.qweb;
    var l10n = _t.database.parameters;

    datepicker.DateWidget.include({
        events: {
            'dp.change': 'changeDatetime',
            'dp.show': '_onShow',
            'focus .o_hijripicker_input': '_onShowHijri',
            'load .o_hijripicker_input': '_onLoadHijri',
            'change .o_datepicker_input': 'changeDatetime',
            'change .o_hijripicker_input': 'change_hijri_datetime',
        },
        init: function(parent, options) {
            this._super.apply(this, arguments);
            var l10n = _t.database.parameters;
            this.name = parent.name;
            this.options = _.defaults(options || {}, {
                format : time.strftime_to_moment_format((this.type_of_date === 'datetime')? (l10n.date_format + ' ' + l10n.time_format) : l10n.date_format),
                minDate: moment({ y: 1900 }),
                maxDate: moment().add(200, "y"),
                calendarWeeks: true,
                icons: {
                    time: 'fa fa-clock-o',
                    date: 'fa fa-calendar',
                    next: 'fa fa-chevron-right',
                    previous: 'fa fa-chevron-left',
                    up: 'fa fa-chevron-up',
                    down: 'fa fa-chevron-down',
                    close: 'fa fa-times',
                },
                locale : moment.locale(),
                allowInputToggle: true,
                keyBinds: null,
                widgetParent: 'body',
                useCurrent: false,
            });
            
            var self = this;
            this.editable = this.__parentedParent.field_manager && (this.__parentedParent.field_manager.fields_view.arch.attrs.editable == 'top' || this.__parentedParent.field_manager.fields_view.arch.attrs.editable == 'bottom')
            this.format = time.strftime_to_moment_format((this.type_of_date === 'datetime')? (l10n.date_format + ' ' + l10n.time_format) : l10n.date_format);
            this.hijri_options = {
                persianDigit: true,
                inputDelay: 800,
                format : time.strftime_to_moment_format((this.type_of_date === 'datetime')? (l10n.date_format + ' ' + l10n.time_format) : l10n.date_format),
                altFormat : time.strftime_to_moment_format((this.type_of_date === 'datetime')? (l10n.date_format + ' ' + l10n.time_format) : l10n.date_format),
                viewMode: false,
                autoClose: this.type_of_date === 'date',
                observer: true,
                altField: self.$el.find(".o_hijripicker_input"),
                formatter: function (unixDate) {
                    var udate = new Date(this.state.selected.unixDate)
                    var pdate = new persianDate(udate);
                    pdate.formatPersian = true;
                    return pdate.format(this.format);
                },
                onSelect: function (unixDate) {
                    var udate = new Date(this.state.selected.unixDate)
                    var sdate = field_utils.parse[self.type_of_date](udate, null, {timezone: false})
                    var p_date = new persianDate(udate);
                    self.$input.val(sdate.format(this.format))
                    self.set_simple_date(sdate.format(this.format))
                    return this;
                },
                navigator: {
                    enabled: true,
                    text: {
                        btnNextText: "<",
                        btnPrevText: ">"
                    },
                },
                toolbox: {
                    enabled: true,

                    text: {
                        btnToday: "هجري"
                    },
                },
                timePicker: {
                    enabled: self.type_of_date === 'datetime' ? self.type_of_date === 'datetime' : false,
                    showSeconds: true,
//                    showMeridian: true,
                    scrollEnabled: true
                },
                justSelectOnDate: true,
            }
        },
        start: function() {
            this.$input = this.$('input.o_datepicker_input');
            this.$input.focus(function(e) {
                e.stopImmediatePropagation();
            });
            this.$input.datetimepicker(this.options);
            this.picker = this.$input.data('DateTimePicker');
            this.$hijri_input = this.$('input.o_hijripicker_input');
            this.$input.click(this.picker.toggle.bind(this.picker));
            this.$hijri_input.persianDatepicker(this.hijri_options).data('datepicker');
            this._setReadonly(false);
        },
        set_simple_date: function(sdate){
            if(this.isValid()) {
                var value = this._parseClient(sdate)|| false;
                this.set({'value': value});
                this.$input.val((value)? this._formatClient(value) : '');
                this.picker.date(this._formatClient(value));
                this.trigger("datetime_changed");
            }
        },
        change_hijri_datetime: function() {
            var value = this.$hijri_input.val() || false;
            if(!value){
                this.setValue(false);
                this.trigger("datetime_changed");
            }
        },
        set_hijri_date_value: function(value){
            var self = this;
            if(value){
                var formatted_value = value ? this._formatClient(value) : null;
                var formatted_value = new Date(value)
                var p_date = new persianDate(formatted_value);
                if(this.type_of_date == 'date'){
                    $(self.$hijri_input[0]).pDatepicker("selectDate", p_date.valueOf())
                }
                if(this.type_of_date == 'datetime'){
                    $(self.$hijri_input[0]).pDatepicker("selectDateTime", p_date.valueOf())
                }
                p_date.formatPersian = true;
                var formatted_value = p_date.format(self.format);
                self.$hijri_input.val(formatted_value)
            }else{
                self.$hijri_input.val('')
            }
        },
        setValue: function(value) {
            var self= this;
            this.set({'value': value});
            var formatted_value = value ? this._formatClient(value) : null;
            this.$input.val(formatted_value);
            if (this.picker) {
                this.picker.date(value || null);
            }
            if(this.$hijri_input){
                if(value){
                    var date = new Date(value)
                    var p_date = new persianDate(date);
                    p_date.formatPersian = true;
                    formatted_value = p_date.format(self.format);
                    this.$hijri_input.val(formatted_value)
                }else{
                    self.$hijri_input.val('')
                }
            }
        },
        _onShow: function() {
            if(this.$input.val().length !== 0 && this.isValid()) {
                var value = this._parseClient(this.$input.val());
                this.picker.date(value);
                this.$input.select();
            }
        },
        _onShowHijri: function(ev){
            if(this.$input.val().length !== 0 && this.isValid()) {
                var value = this._parseClient(this.$input.val());
                this.set_hijri_date_value(value);
            }
        }
    });

    basic_fields.FieldDateTime.include({
        init: function (field_manager, node) {
            this._super.apply(this, arguments);
            // use the session timezone when formatting dates
            this.formatOptions.timezone = true;
        },
        _render_value: function() {
            this._super();
            var self = this;
            var field_name = self.name;
            var value = self.get('value')
            if (self.get("effective_readonly") && value) {
                var pdate = new persianDate(time.auto_str_to_date(self.get('value')));
                pdate.formatPersian = true;
                var formatted_value = pdate.format(self.format);
                self.$el.append("<div>"+formatted_value+"</div>")
            }
        },
        set_dimensions: function (height, width) {
            this._super(height, width);
            if (!this.get("effective_readonly")) {
                this.datewidget.$hijri_input.css('height', height);
                this.datewidget.$hijri_input.css('width', width);
            }
        }
    });

    search_filters_datetime.include({
        start: function() {
            var ready = this._super();
            this.$el.find(".o_hijri_datepicker_container").hide();
            return ready;
        }
    });

    Session.include({
        load_modules: function() {
            var self = this;
            $.when(this._super.apply(this, arguments)).then(function() {
                var locale = "/web/webclient/locale/en_US";
                var file_list = [ locale ];
                return self.load_js(file_list);
            }).done(function(){
                moment.locale('ar')
            });
        },
    });

});
