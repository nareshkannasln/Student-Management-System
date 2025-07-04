import frappe
from frappe.model.document import Document

class ApplicationReview(Document):

    def on_submit(self):
        if self.workflow_state == "Approved":

            admission = frappe.get_doc("Admission Application", self.admission_id)
            self.create_admitted_student(admission)
            self.create_student_user(admission)
            self.send_welcome_email(admission)

    def create_admitted_student(self, admission):
        if not frappe.db.exists("Admitted Student", {"email": admission.email}):
            admitted_student = frappe.get_doc({
                "doctype": "Admitted Student",
                "student_name": admission.name,
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
                "user_type": "Website User",
                "send_welcome_email": 1
            })
            user.insert(ignore_permissions=True)
            frappe.db.commit()
            user.add_roles("Student")

    def send_welcome_email(self, admission):
        fee_syllabus = frappe.get_doc("Fee and Syllabus", admission.class_applying_for)
  
        if self.workflow_state == "Approved":
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

            # Email Content
            message = f"""
                <p>Hello <b>{admission.name1}</b> of <strong>{admission.name}</strong>,</p>
                <p>Your admission has been {self.workflow_state}for Class <strong>{admission.class_applying_for}</strong>.</p>

                <h4>Fee Structure</h4>
                {fee_table}

                <h4>Syllabus</h4>
                {syllabus_table}

                <p>Please proceed with the fee payment at your earliest convenience.</p>
                <br>
                <p>Regards,<br>Admissions Office</p>
            """

            subject = "Admission Approved - Fee & Syllabus Details"

        elif self.workflow_state == "Rejected":
            subject = "Admission Application Status"
            message = f"""
                <p>Hello {admission.name},</p>
                <p>We regret to inform you that your admission application for Class <strong>{admission.class_applying_for}</strong> has been <b>{self.workflow_state}</b>.</p>
                <p>If you have any questions, please contact our admissions office.</p>
                <br>
                <p>Regards,<br>Admissions Team</p>
            """

        # Send the email
        frappe.sendmail(
            recipients=admission.email,
            subject=subject,
            message=message
        )
        frappe.msgprint(f"Email sent to {admission.email} regarding application status.")