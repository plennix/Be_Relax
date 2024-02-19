odoo.define("hr_attendance_base.kiosk_confirm", function (require) {
  "use strict";

  const KioskConfirm = require("hr_attendance.kiosk_confirm");
  const session = require('web.session');


  const BaseKioskModeConfirm = KioskConfirm.include({
    events: _.extend(
      {
        "click .o_hr_attendance_break_resume_icon": _.debounce(function () {
          var self = this;
          this._rpc({
            model: 'hr.employee',
            method: 'attendance_break_manual',
            args: [[this.employee_id],
              "hr_attendance.hr_attendance_action_kiosk_mode", false, this.$('.o_hr_attendance_PINbox').val(),],
            context: session.user_context,
          })
            .then(function (result) {
              if (result.action) {
                self.pin_is_send = true
                self.do_action(result.action);
              } else if (result.warning) {
                self.displayNotification({ title: result.warning, type: 'danger' });
              }
            });
        }, 200, true),
      },
      KioskConfirm.prototype.events,
    ),

    willStart: function () {
      const superDef = this._super.apply(this, arguments);
      const def = this._rpc({
        model: "hr.employee",
        method: "search_read",
        args: [[["id", "=", this.employee_id]], ["attendance_break_state"]],
      }).then((attendance_break_state) => {
        this.attendance_break_state = attendance_break_state[0] || false;
      });

      return Promise.all([superDef, def]);
    },

    send_data_break: function () {
      this._rpc({
        model: "hr.employee",
        method: "attendance_break_manual",
        args: [
          [this.employee_id],
          "hr_attendance.hr_attendance_kiosk_mode", false, this.$('.o_hr_attendance_PINbox').val(),
        ],
      }).then((result) => {
        if (result.action) {
          self.pin_is_send = true

          this.do_action(result.action);
        } else if (result.warning) {
          this.do_warn(result.warning);
        }
      });
    },
  });
});
