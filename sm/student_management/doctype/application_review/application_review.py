import frappe
from frappe.model.document import Document

class ApplicationReview(Document):

    def on_submit(self):
        if self.workflow_state == "Approved":
            try:
                admission = frappe.get_doc("Admission Application", self.admission_id)    
                # admit_student = frappe.get_doc("Admitted Student", {"roll_no": self.name})  #
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"Error fetching Admission Application for ID: {self.admission_id}")
                frappe.throw("Unable to fetch Admission Application. Please check the logs.")

            try:
                self.create_admitted_student(admission)
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"Error creating Admitted Student for ID: {self.admission_id}")
                frappe.throw("Failed to create Admitted Student. Please check the logs.")

            try:
                self.create_student_user(admission)
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"Error creating User for Admission ID: {self.admission_id}")
                frappe.throw("Failed to create Student User. Please check the logs.")

            try:
                self.send_acknowledgement_email(admission)
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"Error sending acknowledgement email for Admission ID: {self.admission_id}")
                frappe.msgprint("Admission approved, but email could not be sent. Check error logs.")


    def create_admitted_student(self, admission):
        if not frappe.db.exists("Admitted Student", {"email": admission.email}):
            admitted_student = frappe.get_doc({
                "doctype": "Admitted Student",
                "student_name": admission.name1,
                "email": admission.email,
                "student_class": admission.class_applying_for,
                "admission_id": admission.name
            })
            admitted_student.insert(ignore_permissions=True)
            frappe.db.commit()
            frappe.msgprint(f"Admitted Student created for {admission.name} in class {admission.class_applying_for}.")

    def create_student_user(self, admission):
        if not frappe.db.exists("User", admission.email):
            user = frappe.get_doc({
                "doctype": "User",
                "email": admission.email,
                "first_name": admission.name1,
                "enabled": 0,  # Enable only after full fee payment
                "user_type": "Website User",
                "send_welcome_email": 0  # Send manually later after full payment
            })
            user.insert(ignore_permissions=True)
            frappe.db.commit()
            # Roles are added via patch, no need to add_roles()

    def send_acknowledgement_email(self, admission):
        fee_syllabus = frappe.get_doc("Fee and Syllabus", admission.class_applying_for)

        # Fee Table
        fee_rows = ""
        for idx, row in enumerate(fee_syllabus.fee_structure, start=1):
            fee_rows += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{row.tuition_fee}</td>
                    <td>{row.exam_fee}</td>
                    <td>{row.total_fee}</td>
                </tr>
            """

        fee_table = f"""
            <table border="1" cellpadding="5" cellspacing="0">
                <tr>
                    <th>No.</th>
                    <th>Tuition Fee</th>
                    <th>Exam Fee</th>
                    <th>Total Fee</th>
                </tr>
                {fee_rows}
            </table>
        """

        # Syllabus Table
        syllabus_rows = "".join(
            f"<tr><td>{subject.subject_name}</td></tr>" for subject in fee_syllabus.subjects
        )
        syllabus_table = f"""
            <table border="1" cellpadding="5" cellspacing="0">
                <tr><th>Subject</th></tr>
                {syllabus_rows}
            </table>
        """

        # ✅ Get roll_no from Admitted Student
        admitted_student = frappe.get_doc("Admitted Student", {"admission_id": admission.name})
        roll_no = admitted_student.name

        # ✅ Final Payment Link
        base_url = frappe.utils.get_url()
        payment_link = f"{base_url}/fee-payment?roll_no={roll_no}"

        # Email Body
        message = f"""
            <p>Hello <b>{admission.name1}</b> of <strong>{admission.name}</strong>,</p>
            <p>Your admission has been <b>{self.workflow_state}</b> for Class <strong>{admission.class_applying_for}</strong>.</p>

            <h4>Fee Structure</h4>
            {fee_table}

            <h4>Syllabus</h4>
            {syllabus_table}

            <p>Please proceed with the fee payment at your earliest convenience.</p>
            <p>
                <a href="{payment_link}" style="background-color:#4CAF50;color:white;padding:10px 15px;text-decoration:none;border-radius:5px;">
                    Pay Fee Now
                </a>
            </p>

            <br>
            <p>Regards,<br>Admissions Office</p>
        """

        # Send email
        frappe.sendmail(
            recipients=admission.email,
            subject="Admission Approved - Fee & Syllabus Details",
            message=message
        )
        frappe.msgprint(f"Acknowledgement email sent to {admission.email}")

