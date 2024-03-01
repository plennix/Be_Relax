odoo.define('hr_attendance_break.kiosk_mode', function (require) {
"use strict";

    const KioskMode = require("hr_attendance.kiosk_mode");
    var core = require('web.core');
    var Session = require('web.session');

    KioskMode.include({
        start: function () {
             var self = this
             return $.when(this._super()).then(function(){
                $(self.$el).on("click",".o_hr_attendance_sign_in_out_icon", self.attendance_sign_in_out_icon.bind(self));
                $(self.$el).on("click",".o_hr_attendance_break_resume_icon", self.attendance_break_resume_icon.bind(self));
             });
        },
         attendance_break_resume_icon: function(){
            var self = this
            $('#checkOutPopup').modal('hide');
            var barcode = $('#checkOutPopup').data('barcode')
            var employee = $('#checkOutPopup').data('employee')
            this._rpc({
                model: 'hr.employee',
                method: 'attendance_break_scan',
                args: [[employee],
                  "hr_attendance.hr_attendance_action_kiosk_mode",barcode],
                context: self.session.user_context,
              })
                .then(function (result) {
                  if (result.action) {
                    self.do_action(result.action);
                  } else if (result.warning) {
                    self.displayNotification({ title: result.warning, type: 'danger' });
                  }
                });
        },
        attendance_sign_in_out_icon: function(){

            var self = this
            var barcode = $('#checkOutPopup').data('barcode')
            $('#checkOutPopup').modal('hide');
            var self = this;
             self._rpc({
                    model: 'hr.employee',
                    method: 'attendance_scan',
                    args: [barcode, ],
                })
                .then(function (result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.displayNotification({ title: result.warning, type: 'danger' });
                        core.bus.on('barcode_scanned', self, self._onBarcodeScanned);
                    }
                }, function () {
                    core.bus.on('barcode_scanned', self, self._onBarcodeScanned);
                });

        },
        _onBarcodeScanned: function(barcode) {
            var self = this;
            core.bus.off('barcode_scanned', this, this._onBarcodeScanned);
            this._rpc({
                    model: 'hr.employee',
                    method: 'employee_attendance_check',
                    args: [barcode, ],
                }).then(function(result){
                    if(result.check_out_break){
                         $('#checkOutPopup').data('barcode',barcode)
                         $('#checkOutPopup').data('employee',result.employee_id)
                        $('#checkOutPopup').modal('show')
                        $("#checkOutPopup").on('hidden.bs.modal', function () {
                            core.bus.on('barcode_scanned', self, self._onBarcodeScanned);
                        });
                    }
                    else if(result.want_checkout_break){
                         self._rpc({
                                model: 'hr.employee',
                                method: 'attendance_break_scan',
                                args: [[result.employee_id],
                                  "hr_attendance.hr_attendance_action_kiosk_mode",barcode],
                                context: self.session.user_context,
                              })
                                .then(function (result) {
                                  if (result.action) {
                                    self.do_action(result.action);
                                  } else if (result.warning) {
                                    self.displayNotification({ title: result.warning, type: 'danger' });
                                  }
                                });
                    }
                    else{
                        self._rpc({
                                model: 'hr.employee',
                                method: 'attendance_scan',
                                args: [barcode, ],
                            })
                            .then(function (result) {
                                if (result.action) {
                                    self.do_action(result.action);
                                } else if (result.warning) {
                                    self.displayNotification({ title: result.warning, type: 'danger' });
                                    core.bus.on('barcode_scanned', self, self._onBarcodeScanned);
                                }
                            }, function () {
                                core.bus.on('barcode_scanned', self, self._onBarcodeScanned);
                            });

                    }
                });
        },

    })

});