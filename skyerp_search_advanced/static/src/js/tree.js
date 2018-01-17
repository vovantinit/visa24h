openerp.skyerp_search_advanced = function (instance) {
// "use strict";

var _t = instance.web._t,
_lt = instance.web._lt;
var QWeb    = instance.web.qweb;

instance.skyerp_search_advanced = instance.skyerp_search_advanced || {};


    instance.web.ListView.include({

        load_list: function(data) {
            var self = this;
            this._super.apply(this, arguments);
    
            var l10n = _t.database.parameters;
            var datepickers_options = {
                pickTime: false,
                startDate: moment({ y: 1900 }),
                endDate: moment().add(200, "y"),
                calendarWeeks: true,
                icons : {
                    time: 'fa fa-clock-o',
                    date: 'fa fa-calendar',
                    up: 'fa fa-chevron-up',
                    down: 'fa fa-chevron-down'
                   },
                dateFormat: 'dd/mm/yy',
            }

            if (self.$buttons) {
                self.$buttons.find('.sky-search').remove();

                // Tim kiem theo khoang thoi gian
                var sky_fields = [];
                this.sky_fields = {};
                _.each(self.columns, function(value, key, list){
                    if (value.store && value.type === "datetime" || value.type === "date") {
                        sky_fields.push([value.name, value.string]);
                        self.sky_fields[ value.name ] = value.type;
                    }
                });
                
                if (sky_fields.length > 0) {
                    self.$search_button = $(QWeb.render('SkyERP.buttons', {'sky_fields': sky_fields}))
                    self.$search_button.find('.sky_start_date').datepicker(datepickers_options);
                    self.$search_button.find('.sky_end_date').datepicker(datepickers_options);
                    self.$search_button.find('.sky_start_date').on('change', function() {
                        self.tgl_search();
                    });
                    self.$search_button.find('.sky_end_date').on('change', function() {
                        self.tgl_search();
                    });
                    self.$search_button.find('.sky_select_field').on('change', function() {
                        self.tgl_search();
                    });
                    self.$search_button.appendTo(self.$buttons);

                    if (self.last_context && self.last_context.tgl_start_date) {
                        self.$search_button.find('.sky_start_date').datepicker("setDate",self.last_context.tgl_start_date);
                    }
                    if (self.last_context && self.last_context.tgl_end_date) {
                        self.$search_button.find('.sky_end_date').datepicker("setDate",self.last_context.tgl_end_date);
                    }
                    if (self.last_context && self.last_context.tgl_field_date) {
                        self.$search_button.find('.sky_select_field').val(self.last_context.tgl_field_date);
                    }
                }        
            }

            // self.$buttons.find('.tgl_quick_search').click(function(){
            //     self.$search_button.appendTo(self.$buttons);
            // });

        },

        do_search: function(domain, context, group_by) {
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            return self.tgl_search();
        },

        tgl_search: function() {
            var self = this;
            var domain = [], value, value_tmp;
            var l10n = _t.database.parameters;

            if (self.$search_button) {
                var start_date  = self.$search_button.find('.sky_start_date').val(),
                    end_date    = self.$search_button.find('.sky_end_date').val(),
                    field       = self.$search_button.find('.sky_select_field').val();
                self.last_context.tgl_field_date = field;

                if (start_date) {
                    self.last_context.tgl_start_date = start_date;
                    // instance.web.date_to_str(start_date)
                    if (this.sky_fields && this.sky_fields[ field ] == 'date'){
                        start_date = moment(start_date, 'DD/MM/YYYY').format('YYYY-MM-DD');
                    } else {
                        start_date = moment(start_date, 'DD/MM/YYYY').add(-7, 'hours').format('YYYY-MM-DD HH:mm:ss');
                    }
                    domain.push([field, '>=', start_date]);
                } else {
                    self.last_context.tgl_start_date = null;
                }
                if (end_date) {
                    self.last_context.tgl_end_date = end_date;
                    if (this.sky_fields && this.sky_fields[ field ] == 'date'){
                        end_date = moment(end_date, 'DD/MM/YYYY').add(24, 'hours').format('YYYY-MM-DD');
                    } else {
                        end_date = moment(end_date, 'DD/MM/YYYY').add(17, 'hours').format('YYYY-MM-DD HH:mm:ss');
                    }
                    domain.push([field, '<', end_date]);
                } else {
                    self.last_context.tgl_end_date = null;

                }
            }
            // console.log(domain);
            var compound_domain = new openerp.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();
            return self.old_search(compound_domain, self.last_context, self.last_group_by);
        },

    });


};