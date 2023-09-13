odoo.define("greeting_message", function (require) {
  "use strict";

  var GreetingMessage = require("hr_attendance.greeting_message");

  var GreetingMessage = GreetingMessage.include({
    init: function (parent, action) {
      var self = this;
      this._super.apply(this, arguments);
      this.attendance_break_state = action.attendance_break_state;
    },
  });
});
