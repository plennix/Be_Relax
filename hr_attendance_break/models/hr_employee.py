from odoo import _, api, fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    def parse_param(self, vals, mode="in"):
        if self._context.get("ismobile", None):
            vals.update(
                {"ismobile_check_" + mode: self._context.get("ismobile", None)}
            )
        if self._context.get("geospatial_id", None):
            vals.update(
                {
                    "geospatial_check_"
                    + mode
                    + "_id": self._context.get("geospatial_id", None)
                }
            )
        if self._context.get("ip_id", None):
            vals.update(
                {"ip_check_" + mode + "_id": self._context.get("ip_id", None)}
            )
        if self._context.get("ip", None):
            vals.update({"ip_check_" + mode: self._context.get("ip", None)})
        if self._context.get("geo", None):
            vals.update({"geo_check_" + mode: self._context.get("geo", None)})
        if self._context.get("token", None):
            vals.update(
                {
                    "token_check_"
                    + mode
                    + "_id": self._context.get("token", None)
                }
            )
        if self._context.get("webcam", None):
            vals.update(
                {"webcam_check_" + mode: self._context.get("webcam", None)}
            )
        if self._context.get("user_agent_html", None):
            vals.update(
                {
                    "user_agent_html_check_"
                    + mode: self._context.get("user_agent_html", None)
                }
            )
        if self._context.get("face_recognition_image", None):
            vals.update(
                {
                    "face_recognition_image_check_"
                    + mode: self._context.get("face_recognition_image", None)
                }
            )
        if self._context.get("kiosk_shop_id", None):
            vals.update(
                {
                    "kiosk_shop_id_check_"
                    + mode: self._context.get("kiosk_shop_id", None)
                }
            )

        access_allowed = self._context.get("access_allowed", None)
        access_denied = self._context.get("access_denied", None)
        access_allowed_disable = self._context.get(
            "access_allowed_disable", None
        )
        access_denied_disable = self._context.get("access_denied_disable", None)
        accesses = self._context.get("accesses", None)
        if accesses:
            for key, value in accesses.items():
                if value.get("enable", False):
                    if value.get("access", False):
                        vals.update({key + "_check_" + mode: access_allowed})
                    else:
                        vals.update({key + "_check_" + mode: access_denied})
                else:
                    if value.get("access", False):
                        vals.update(
                            {key + "_check_" + mode: access_allowed_disable}
                        )
                    else:
                        vals.update(
                            {key + "_check_" + mode: access_denied_disable}
                        )

    attendance_break_state = fields.Selection(
        string="Attendance Break Status",
        compute="_compute_attendance_break_state",
        selection=[("break", "Break"), ("resume", "Resume")],
        default="resume",
    )

    @api.depends(
        "last_attendance_id.check_in",
        "last_attendance_id.check_out",
        "last_attendance_id",
    )
    def _compute_attendance_break_state(self):
        for employee in self:
            attendance = employee.last_attendance_id.sudo()
            employee.attendance_break_state = "resume"
            if attendance.break_ids:
                break_obj = self.env["hr.attendance.break"].search(
                    [("attendance_id", "=", attendance.id)],
                    limit=1,
                    order="create_date desc",
                )
                employee.attendance_break_state = (
                    break_obj.attendance_break_state
                    if break_obj.attendance_break_state
                    else "resume"
                )

    @api.model
    def employee_attendance_check(self, barcode):
        employee = self.sudo().search([('barcode', '=', barcode)], limit=1)
        if employee:
            if employee.attendance_state == 'checked_in':
                if employee.attendance_break_state == 'resume':
                    last_break_record = employee.last_attendance_id.break_ids[-1] if employee.last_attendance_id and employee.last_attendance_id.break_ids else False
                    if last_break_record and not last_break_record.resume_time:
                        return {'check_out_break': True, 'employee_id': employee.id, 'want_checkout_break':False}
                    elif not last_break_record:
                        return {'check_out_break': True, 'employee_id': employee.id, 'want_checkout_break': False}
                    else:
                        return {'check_out_break': True, 'employee_id': employee.id, 'want_checkout_break':False}
                if employee.attendance_break_state == 'break':
                    return {'check_out_break': False, 'employee_id': employee.id ,'want_checkout_break':True}
                return {'check_out_break':True,'employee_id':employee.id,'want_checkout_break':False}
            else:
                return {'check_out_break':False,'employee_id':employee.id, 'want_checkout_break':False}
        return {'warning': _("No employee corresponding to Badge ID '%(barcode)s.'") % {'barcode': barcode}}

    def attendance_break_scan(self, next_action, barcode):
        employee = self.sudo().search([('barcode', '=', barcode)], limit=1)
        if employee:
            return self.attendance_break_resume_action(next_action)
        return {'warning': _("No employee corresponding to Badge ID '%(barcode)s.'") % {'barcode': barcode}}

    def attendance_break_manual(self, next_action, snap=None, entered_pin=None):
        self.ensure_one()
        if isinstance(next_action,dict):
            temp_dict = next_action
            next_action = temp_dict.get('next_action', False)
            entered_pin = temp_dict.get('entered_pin', False)
            snap =  temp_dict.get('snap', False)
        can_check_without_pin = not self.env.user.has_group(
            "hr_attendance.group_hr_attendance_use_pin"
        ) or (self.user_id == self.env.user and entered_pin is None)
        if (
            can_check_without_pin
            or entered_pin is not None
            and entered_pin == self.sudo().pin
        ):
            if snap:
                return self.attendance_break_resume_action(next_action, snap)
            else:
                return self.attendance_break_resume_action(next_action)
        return {"warning": _("Wrong PIN")}

    def attendance_break_resume_action(self, next_action, snap=None):
        self.ensure_one()
        self = self.sudo()
        action_date = fields.Datetime.now()
        # TODO: local time
        # local_tz = pytz.timezone(self._context.get('tz') or 'UTC')
        # action_date_utc = action_date.astimezone(pytz.utc)
        # action_date = action_date_utc.astimezone(local_tz)
        for employee in self:
            attendance = employee.last_attendance_id.sudo()
            if employee.attendance_state == "checked_in":
                break_obj = self.env["hr.attendance.break"].search(
                    [
                        ("attendance_id", "=", attendance.id),
                        ("break_time", "!=", False),
                    ],
                    limit=1,
                    order="create_date desc",
                )

                vals = {}
                if (
                    employee.attendance_break_state == "break"
                    and break_obj.break_time != False
                ):
                    break_obj.update(
                        {
                            "resume_time": action_date,
                            "attendance_break_state": "resume",
                            "webcam_check_out": snap,
                        }
                    )
                    self.parse_param(vals, "out")
                    break_obj.write(vals)

                    if attendance.attendance_record_ids:
                        if attendance.attendance_record_ids[0].check_in and attendance.attendance_record_ids[0].break_time and not attendance.attendance_record_ids[
                            0].check_out and not attendance.attendance_record_ids[0].resume_time:
                            attendance.attendance_record_ids[0].write({
                                "resume_time": action_date,
                            })
                else:
                    break_obj.create(
                        {
                            "attendance_id": attendance.id,
                            "pos_attendance_id": employee.last_pos_attendance_record.id if employee.last_pos_attendance_record and attendance == employee.last_pos_attendance_record.attendance_id else False,
                            "employee_id": employee.id,
                            "break_time": action_date,
                            "attendance_break_state": "break",
                            "webcam_check_in": snap,
                        }
                    )

                    if attendance.attendance_record_ids:
                        if attendance.attendance_record_ids[0].check_in and not attendance.attendance_record_ids[0].break_time and not attendance.attendance_record_ids[0].check_out and not attendance.attendance_record_ids[0].resume_time:
                            attendance.attendance_record_ids[0].write({
                                "break_time": action_date,
                            })

                    self.parse_param(vals)
                    break_obj.write(vals)

        action_message = self.env["ir.actions.actions"]._for_xml_id(
            "hr_attendance.hr_attendance_action_greeting_message"
        )
        action_message["previous_attendance_change_date"] = (
            employee.last_attendance_id
            and (
                employee.last_attendance_id.check_out
                or employee.last_attendance_id.check_in
            )
            or False
        )
        action_message["employee_name"] = employee.name
        action_message["barcode"] = employee.barcode
        action_message["next_action"] = next_action
        action_message["hours_today"] = employee.hours_today
        action_message["kiosk_delay"] = (
            employee.company_id.attendance_kiosk_delay * 1000
        )

        action_message["attendance"] = attendance.read()[0]
        # if employee.user_id:
        #     modified_attendance = employee.with_user(employee.user_id).sudo()._attendance_action_change()
        # else:
        #     modified_attendance = employee._attendance_action_change()
        # action_message['attendance'] = modified_attendance.read()[0]
        action_message["total_overtime"] = employee.total_overtime
        # Overtime have an unique constraint on the day, no need for limit=1
        action_message["overtime_today"] = (
            self.env["hr.attendance.overtime"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", employee.id),
                    ("date", "=", fields.Date.context_today(self)),
                    ("adjustment", "=", False),
                ]
            )
            .duration
            or 0
        )

        break_obj = self.env["hr.attendance.break"].search(
            [("attendance_id", "=", attendance.id)],
            limit=1,
            order="create_date desc",
        )
        action_message["attendance_break_state"] = (
            break_obj.attendance_break_state
            if break_obj.attendance_break_state
            else "resume"
        )
        return {"action": action_message}
