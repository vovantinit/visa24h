openerp.sky_company_currency = function (instance) {
// "use strict";

var _t = instance.web._t,
_lt = instance.web._lt;
var QWeb = instance.web.qweb;

instance.sky_company_currency = instance.sky_company_currency || {};

// instance.web.views.add('sky_pivot', 'instance.web.sky_company_currency.SkyPivot');
setTimeout(function(){
// instance.sky_company_currency.SkyPivot = 
    instance.web_graph.GraphView.include({

        init: function(parent, dataset, view_id, options) {
            this._super.apply(this, arguments);
            this.periods = [];
            this.period_from = null;
            this.period_to = null;
            this._super.apply(this, arguments);
            var self = this;
            if (self.dataset.context.close_so) {
                setTimeout(function(){
                  $('.graph_measure_selection').parent().parent().append('<label class="btn btn-primary btn_sky_close_so" style="margin-left: 7px;">Chốt doanh số</label>');

                  $('.btn_sky_close_so').click(function() {
                    self.do_action({
                        "name": "Tính năng quản lý đơn hàng",
                        "type": "ir.actions.act_window",
                        "res_model": "close.analytic.account",
                        "views": [[false, "form"]],
                        "target": "new",              
                    });
                  });
                  self.search_view.drawer.toggle();
                }, 3000);
            }
          // console.log(self, self.dataset.context);

        },

        start:function(){
            var tmp = this._super.apply(this, arguments);
            var self = this;
            var defs = [];

            if (self.dataset.context.close_so) {
                this.$el.parent().prepend(QWeb.render("SearchWithPeriod", {widget: this}));

                this.$el.parent().find('.oe_account_select_period_from').change(function() {
                    self.period_from = this.value === '' ? null : this.value;
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });

                this.$el.parent().find('.oe_account_select_period_to').change(function() {
                    self.period_to = this.value === '' ? null : this.value;
                    self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });

                var mod = new instance.web.Model("sale.report", self.dataset.context, self.dataset.domain);
                defs.push(mod.call("list_periods", []).then(function(result) {
                    self.periods = result;
                }));
            }

            return $.when(tmp, defs);
        },

        do_search: function(domain, context, group_by) {
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            var o;
            self.$el.parent().find('.oe_account_select_period_from').children().remove().end();
            self.$el.parent().find('.oe_account_select_period_from').append(new Option('', ''));
            for (var i = 0;i < self.periods.length;i++){
                o = new Option(self.periods[i].name, self.periods[i].date_start);
                self.$el.parent().find('.oe_account_select_period_from').append(o);
            }    
            self.$el.parent().find('.oe_account_select_period_from').val(self.period_from).attr('selected',true);

            self.$el.parent().find('.oe_account_select_period_to').children().remove().end();
            self.$el.parent().find('.oe_account_select_period_to').append(new Option('', ''));
            for (var i = 0;i < self.periods.length;i++){
                o = new Option(self.periods[i].name, self.periods[i].date_stop);
                self.$el.parent().find('.oe_account_select_period_to').append(o);
            }    
            self.$el.parent().find('.oe_account_select_period_to').val(self.period_to).attr('selected',true);

            return self.search_by_period();
        },

        search_by_period: function() {
            var self = this;
            var domain = [];

            if (self.period_from !== null) domain.push(["x_ngaytinhdoanhso", ">=", self.period_from]);
            if (self.period_to !== null) domain.push(["x_ngaytinhdoanhso", "<=", self.period_to]);
            

            self.last_context["period_from"] = self.period_from === null ? false : self.period_from;
            self.last_context["period_to"] = self.period_to === null ? false : self.period_to;

            var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();

            // console.log('domain', compound_domain, self.last_context, self.last_group_by);

            return self.old_search(compound_domain, self.last_context, self.last_group_by);
        },


    });

}, 2000);

};
