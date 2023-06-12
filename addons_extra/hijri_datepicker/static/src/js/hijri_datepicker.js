odoo.define('hijri_datepicker', function (require) {
"use strict"

var core = require('web.core');
var datepicker = require('web.datepicker');
var datetimefield = require('web.basic_fields');
var time = require('web.time');
var field_utils = require('web.field_utils');
var session = require('web.session');

var _t = core._t;
var qweb = core.qweb;
var lang = '';
var date_format = '%m/%d/%Y';

    datepicker.DateWidget.include({
        start: function() {
            var def = new $.Deferred();;
            this.$input = this.$('input.oe_datepicker_master');
            this.$input_picker = this.$('input.oe_datepicker_container');
            this.$input_hijri = this.$el.find('input.oe_hijri');
            $(this.$input_hijri).val('');
            this._super();
            this.$input = this.$('input.oe_datepicker_master');
            var self = this;
            function convert_to_hijri(date){
                if (date.length == 0) {
                
                    return false
                }
                var jd = $.calendars.instance('islamic').toJD(parseInt(date[0].year()),parseInt(date[0].month()),parseInt(date[0].day()));
                var date = $.calendars.instance('gregorian').fromJD(jd);
                var date_value = new Date(parseInt(date.year()),parseInt(date.month())-1,parseInt(date.day()));
                self.$el.find('input.oe_simple_date').val(self.formatClient(date_value, self.type_of_date));
                self.change_datetime();
            }

            this._rpc({
                        model: 'res.users',
                        method: 'get_localisation',
                        args: [session.uid],
            }).then(function (res) {
                def.resolve(res);
            });
            def.done(function(val) {
                $(self.$input_hijri).calendarsPicker({
                    
                    calendar: $.calendars.instance('islamic',val.lang),
                    dateFormat: 'M d, yyyy',
                    onSelect: convert_to_hijri,
                });
            });
            
        },
        formatClient: function (value, type) {
            if (type == 'datetime'){
                var date_format = time.strftime_to_moment_format((this.type_of_date === 'datetime'));
            }
            if (type == 'date'){
                var date_format = time.strftime_to_moment_format((this.type_of_date === 'date'));
            }
            return moment(value).format(date_format);
        },
        convert_greg_to_hijri: function(text) {
            if (text) {
                var cal_greg = $.calendars.instance('gregorian');
                var cal_hijri = $.calendars.instance('islamic');
                var text = text._i;
                //alert(text);
                if (text.indexOf('-')!= -1){
                    //alert(text+"####"+"2");
                    var text_split = text.split('-');
                    var year = parseInt(text_split[0]);
                    var month = parseInt(text_split[1]);
                    var day = parseInt(text_split[2]);

                    var jd = cal_greg.toJD(year,month,day);
                    var date = cal_hijri.fromJD(jd);
                    var m = (date.month() >=10 ? date.month():"0"+date.month());
                    var d = (date.day() >=10 ? date.day():"0"+date.day());
                    $(this.$input_hijri).val(cal_hijri.formatDate('M d, yyyy', date));
                }

                if(text.indexOf('/')!= -1){
                    var text_split = text.split('/');
                    var year = parseInt(text_split[2]);
                    var month = parseInt(text_split[0]);
                    var day = parseInt(text_split[1]);

                    var jd = cal_greg.toJD(year,month,day);
                    var date = cal_hijri.fromJD(jd);
                    var m = (date.month() >=10 ? date.month():"0"+date.month());
                    var d = (date.day() >=10 ? date.day():"0"+date.day());
                    $(this.$input_hijri).val(cal_hijri.formatDate('M d, yyyy', date));

                }
                //alert("text1"+text);
                if(text.indexOf(',')!= -1){
                //alert("case1"+text);
                var res = text.split(",");
                var r=res[0].split(" ")
                var c=String(r).split(",");
                var month='';
                if(c.length==2){
                    month =c[1];
                }else
                {
                if(c.length==3){
                      month =c[1]+" "+c[2];
                  }
                 else{
                       month =c[1]+" "+c[2]+" "+c[3]; 
                    }
                    }

                    var year = parseInt(res[1]);
                    //var month =c[1]+" "+c[2];
                    var day = parseInt(c[0]);
                    //alert(day+" "+"day");
                    //alert(year+" "+"year");
                    //alert(month+" "+"month");
                var months = {
                    'كانون الثاني يناير':1,
                    'شباط فبراير':2,
                    'آذار مارس':3,
                    'نيسان أبريل':4,
                    'أيار مايو':5,
                    'حزيران يونيو':6,
                    'تموز يوليو':7,
                    'آب أغسطس':8,
                    'أيلول سبتمبر':9,
                    'تشرين الأول أكتوبر':10,
                    'تشرين الثاني نوفمبر':11,
                    'كانون الأول ديسمبر':12,
                    'يناير':1,
                    'فبراير':2,
                    'مارس':3,
                    'أبريل':4,
                    'مايو':5,
                    'يونيو':6,
                    'يوليو':7,
                    'أغسطس':8,
                    'سبتمبر':9,
                    'أكتوبر':10,
                    'نوفمبر':11,
                    'ديسمبر':12
                    };
                //alert("fff"+" "+months[month]);

                    var jd = cal_greg.toJD(year,parseInt(months[month]),day);
                    var date = cal_hijri.fromJD(jd);
                    var m = (date.month() >=10 ? date.month():"0"+date.month());
                    var d = (date.day() >=10 ? date.day():"0"+date.day());
                    //alert(date,'bb');
                    //alert(cal_hijri.formatDate('M d, yyyy', date));
                    $(this.$input_hijri).val(cal_hijri.formatDate('M d, yyyy', date));

                    }

            }
        },
        set_value_from_ui: function() {
            var value = this.$input.val() || false;
            this.value = this._parseClient(value);
            this.setValue(this.value);
            this.convert_greg_to_hijri(this.value);
        },
        set_readonly: function(readonly) {
            this._super(readonly);
            this.$input_hijri.prop('readonly', this.readonly);
        },
        change_datetime: function(e) {
            this._setValueFromUi();
            this.trigger("datetime_changed");
        },
        changeDatetime: function () {
            if (this.isValid()) {
                var oldValue = this.getValue();
                this.set_value_from_ui();
                var newValue = this.getValue();

                if (!oldValue !== !newValue || oldValue && newValue && !oldValue.isSame(newValue)) {
                    // The condition is strangely written; this is because the
                    // values can be false/undefined
                    this.trigger("datetime_changed");
                }
            }
        },
    });

    datetimefield.FieldDate.include({
        start: function () {
            var self = this;
            this._super();
            if (this.mode === 'readonly') {
                var date_value = $(this.$el).text();
                var hij_date = self.convert_greg_to_hijri(date_value)
                this.$el.append("<div><span class='oe_hijri oe_hi_label'>"+hij_date+"</span></div>");
            }
            //return $.when(def, this._super.apply(this, arguments));
            return true;
        },



        parseArabic: function(str) {
            //alert("str"+str);
            return Number( str.replace(/[٠١٢٣٤٥٦٧٨٩]/g, function(d) {
                return d.charCodeAt(0) - 1632; // Convert Arabic numbers
            }));
        },



        convert_greg_to_hijri: function(text) {
            if (text) {
                var cal_greg = $.calendars.instance('gregorian');
                var cal_hijri = $.calendars.instance('islamic');

                if (text.indexOf('-')!= -1){
                    var text_split = text.split('-');
                    var year = parseInt(text_split[0]);
                    var month = parseInt(text_split[1]);
                    var day = parseInt(text_split[2]);

                    var jd = cal_greg.toJD(year,month,day);
                    var date = cal_hijri.fromJD(jd);
                    var m = (date.month() >=10 ? date.month():"0"+date.month());
                    var d = (date.day() >=10 ? date.day():"0"+date.day());
                    return cal_hijri.formatDate('M d, yyyy', date);
                }
                
                if(text.indexOf('/')!= -1){

                    var text_split = text.split('/');
                    var year = parseInt(text_split[2]);
                    var month = parseInt(text_split[0]);
                    var day = parseInt(text_split[1]);

                    var jd = cal_greg.toJD(year,month,day);
                    var date = cal_hijri.fromJD(jd);
                    var m = (date.month() >=10 ? date.month():"0"+date.month());
                    var d = (date.day() >=10 ? date.day():"0"+date.day());
                    //alert("before_return",date);
                    return cal_hijri.formatDate('M d, yyyy', date);
                }
                //alert("text2"+text);
                if(text.indexOf(',')!= 1){
                    //alert("case2"+text);
                    var res = text.split(",");
                    var r=res[0].split(" ")
                    var s= String(r).replace('،','');
                    var c=s.split(",");
                    var year=0;
                    var month='';
                    var day=0;
                    if(c.length==4){
                        year = this.parseArabic(c[3]);
                        month =c[1]+' '+c[2];
                        day = this.parseArabic(c[0]);
                        if (isNaN(year)){
                            //alert('hhhhh');
                            year = this.parseArabic(c[2]);
                            month =c[1];
                            day = this.parseArabic(c[0]);

                        }
                    }
                    else
                    {
                      if(c.length==3){
                            year = this.parseArabic(c[2]);
                            month =c[1];
                            day = this.parseArabic(c[0]);
                        }else{
                            year = this.parseArabic(c[4]);
                            month =c[1]+' '+c[2]+' '+c[3];
                            day = this.parseArabic(c[0]);

                        }

                        }
                    //alert(day+" "+"day");
                    //alert(year+" "+"year");
                    //alert(month);
                var months = {
                    'كانون الثاني يناير':1,
                    'شباط فبراير':2,
                    'آذار مارس':3,
                    'نيسان أبريل':4,
                    'أيار مايو':5,
                    'حزيران يونيو':6,
                    'تموز يوليو':7,
                    'آب أغسطس':8,
                    'أيلول سبتمبر':9,
                    'تشرين الأول أكتوبر':10,
                    'تشرين الثاني نوفمبر':11,
                    'كانون الأول ديسمبر':12,
                    'يناير':1,
                    'فبراير':2,
                    'مارس':3,
                    'أبريل':4,
                    'مايو':5,
                    'يونيو':6,
                    'يوليو':7,
                    'أغسطس':8,
                    'سبتمبر':9,
                    'أكتوبر':10,
                    'نوفمبر':11,
                    'ديسمبر':12
                    };
                    var jd = cal_greg.toJD(year,parseInt(months[month]),day);
                    var date = cal_hijri.fromJD(jd);
                    var m = (date.month() >=10 ? date.month():"0"+date.month());
                    var d = (date.day() >=10 ? date.day():"0"+date.day());
                    //alert("before_return",date);
                    return cal_hijri.formatDate('M d, yyyy', date);
                }

            }
        },
    });

});
