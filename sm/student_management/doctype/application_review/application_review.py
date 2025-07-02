import frappe
from frappe.model.document import Document
from frappe.utils import get_url

class ApplicationReview(Document):

    def on_submit(self):
        if self.status == "Approved":  # use your exact workflow state value
            admission = frappe.get_doc("Admission Application", self.admission_id)
            # print("Debug:", doctype_fieldname, "in", doctype)

            # 1. Create Admitted Student
            self.create_admitted_student(admission)

            # 2. Create Student User
            self.create_student_user(admission)

            # 3. Send Welcome Email
            self.send_welcome_email(admission)

    def create_admitted_student(self, admission):
        if not frappe.db.exists("Admitted Student", {"email": admission.email}):
            admitted_student = frappe.get_doc({
                "doctype": "Admitted Student",
                "student_name": admission.name1 ,
                "email": admission.email,
                "student_class": admission.class_applying_for,
                "application_id": admission.name
            })
            admitted_student.insert(ignore_permissions=True)
            frappe.db.commit()

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
            user.add_roles("Student")  # Assign role

    def send_welcome_email(self, admission):
        if self.workflow_state == "Approved":
            subject = "Admission Application Status"
            message = f"""
            <h3>Hello {admission.student_name},</h3>
            <p>Congratulations! Your admission has been <b>{self.workflow_state}</b> for Class <strong>{admission.student_class}</strong>.</p>
            <p>You can now log in using your email: <strong>{admission.email}</strong>.</p>
            <br>
            <p>Regards,<br>Admissions Team</p>
            """
        elif self.workflow_state == "Rejected":
            subject = "Admission Application Status"
            message = f"""
            <h3>Hello {admission.student_name},</h3>
            <p>We regret to inform you that your admission application for Class <strong>{admission.student_class}</strong> has been <b>{self.workflow_state}</b>.</p>
            <p>If you have any questions, please contact our admissions office.</p>
            <br>
            <p>Regards,<br>Admissions Team</p>
            """
        else:
            return  # Do not send email for other states

        frappe.sendmail(
            recipients=admission.email,
            subject=subject,
            message=message
        )
