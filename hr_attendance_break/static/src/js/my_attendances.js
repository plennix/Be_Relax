odoo.define("my_attendances", function (require) {
  "use strict";
  var MyAttendances = require("hr_attendance.my_attendances");

  MyAttendances.include({
    events: _.extend(
      {
        "click .o_hr_attendance_break_resume_icon": "click_break_resume_icon",
      },
      MyAttendances.prototype.events,
    ),

    click_break_resume_icon: function () {
      console.log(this);
      if (this.face_recognition_enable)
        this.update_break_resume_with_recognition();
      else this.update_break_resume();
    },

    willStart: function () {
      var self = this;
      var superDef = this._super.apply(this, arguments);
      var def = this._rpc({
        model: "hr.employee",
        method: "search_read",
        args: [
          [["user_id", "=", this.getSession().uid]],
          ["attendance_break_state"],
        ],
      }).then(function (attendance_break_state) {
        self.attendance_break_state = attendance_break_state[0] || false;
      });
      console.log(this);
      return Promise.all([superDef, def]);
    },

    update_break_resume: function () {
      var self = this;
      var token = window.localStorage.getItem("token");
      self.state_read = $.Deferred();
      self.state_save = $.Deferred();

      if (Object.keys(self.data).includes("geo_enable")) {
        self.parse_data_geo();
        self.geolocation();
      }
      if (Object.keys(self.data).includes("webcam_enable"))
        self.parse_data_webcam();
      if (Object.keys(self.data).includes("ip_enable")) self.parse_data_ip();
      if (Object.keys(self.data).includes("token_enable"))
        self.parse_data_token();
      if (Object.keys(self.data).includes("face_recognition_enable"))
        self.parse_data_face_recognition();

      if (Object.keys(self.data).includes("geospatial_enable"))
        self.parse_data_geospatial();
      else self.geo_coords.resolve();

      self.geo_coords.then((result) => {
        this._rpc({
          route: "/hr_attendance_base",
          params: {
            token: token,
            employee: this.employee,
            employee_from_kiosk: this.kiosk,
            latitude: self.latitude,
            longitude: self.longitude,
          },
        }).then(function (data) {
          self.data = data;
          self.state_read.resolve();
          if (!data.length) {
            self.state_save.resolve();
          }
          self.state_save.then(function (data) {
            if (self.webcam_live) {
              console.log("webcam_live");
              Webcam.snap(function (data_uri) {
                self.webcam_access = true;
                // base64 data
                self.webcam_snapshot = data_uri.split(",")[1];
                if (self.check_access()) self.send_data_break();
              });
            } else {
              if (self.check_access()) self.send_data_break();
            }
          });
        });
      });
    },

    send_data_break: function () {
      var self = this,
        geo_str = null;
      self
        ._rpc({
          model: "hr.employee",
          method: "attendance_break_manual",
          args: [
            [self.employee.id],
            "hr_attendance.hr_attendance_action_my_attendances",
          ],
        })
        .then(function (result) {
          if (self.kiosk)
            result.action.next_action = "hr_attendance_kiosk_mode";
          if (result.action) {
            self.do_action(result.action);
          } else if (result.warning) {
            self.do_warn(result.warning);
          }
        });
    },
  });
});
