# Copyright (c) 2025, Nareshkanna and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.core.doctype.communication.email import make
from frappe.utils import now


@frappe.whitelist()
def set_status(docname, status):
    if status not in ["Approve", "Reject"]:
        frappe.throw("Invalid status")

    doc = frappe.get_doc("Application Review", docname)
    doc.status = status
    doc.save(ignore_permissions=True)

class ApplicationReview(Document):
    
    def on_submit(self):
        self.validate_application_status()
        self.send_notification_email()
        if self.status == "Approve":
            self.create_student_user()


    def validate_application_status(self):
        if not self.status:
            frappe.throw("Please select a status (Approved or Rejected) before submitting.")

    def send_notification_email(self):
        admission = frappe.get_doc("Admission Application", self.admission_application)
        student_class = admission.class_applying_for
        recipient_email = admission.email

        # --- Fetch Fee and Syllabus ---
        fee_syllabus_html = ""
        fee_syllabus = frappe.get_all("Fee and Syllabus", filters={"class": student_class}, limit=1)
        if fee_syllabus:
            doc = frappe.get_doc("Fee and Syllabus", fee_syllabus[0].name)

            # Syllabus section
            syllabus_html = "<h4>Syllabus</h4><table border='1' cellpadding='5' cellspacing='0'><tr><th>Subject</th></tr>"
            for sub in doc.subject:
                syllabus_html += f"<tr><td>{sub.subject}</td></tr>"
            syllabus_html += "</table>"

            # Fee section
            fee_html = f"""
            <h4>Fee Structure</h4>
            <table border='1' cellpadding='5' cellspacing='0'>
                <tr><td>Tuition Fee</td><td>{doc.tution_fee if hasattr(doc, 'tution_fee') else ''}</td></tr>
                <tr><td>Miscellaneous Fee</td><td>{doc.miscallneous_fee if hasattr(doc, 'miscallneous_fee') else ''}</td></tr>
                <tr><td><strong>Total</strong></td><td><strong>{doc.total if hasattr(doc, 'total') else ''}</strong></td></tr>
            </table>
            """

            fee_syllabus_html = syllabus_html + "<br><br>" + fee_html

        # ---- Generate Fee Payment Web Form URL with pre-filled values ----
        from urllib.parse import urlencode
        base_path = "/student-fee-payment/new"
        params = {
            "student_name": admission.name,
            "student_class": student_class,
            "student_email": recipient_email
        }
        url = frappe.utils.get_url(base_path + "?" + urlencode(params))

        # ---- Compose Email ----
        subject = f"Admission Application {self.status} for Class {student_class}"
        if self.status == "Approve":
            message = f"""
            Dear {admission.name},<br><br>
            Congratulations! Your admission to class <b>{student_class}</b> has been approved.<br><br>
            {fee_syllabus_html}<br><br>
            Please proceed to pay your fees by clicking the button below:<br><br>
            <a href="{url}" style="background-color:#4CAF50;color:white;padding:10px 15px;text-decoration:none;border-radius:5px;">Pay Fee Now</a><br><br>
            Regards,<br>
            Admissions Team
            """
        else:
            message = f"""
            Dear {admission.name},<br><br>
            We regret to inform you that your admission has been rejected.<br><br>
            Regards,<br>
            Admissions Team
            """

        # ---- Send Email ----
        if recipient_email:
            frappe.sendmail(
                recipients=[recipient_email],
                subject=subject,
                message=message
            )
        else:
            frappe.msgprint("Email not sent: No email found in Admission Application.")


    def create_student_user(self):
        admission = frappe.get_doc("Admission Application", self.admission_application)
        email = admission.email
        student_name = admission.student_name or admission.name

        if frappe.db.exists("User", email):
            return  # Skip if already exists

        # Create system user
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": student_name,
            "send_welcome_email": 1,
            "user_type": "System User"
        })
        user.append("roles", {"role": "Student"})
        user.insert(ignore_permissions=True)

        # Set random password
        temp_password = frappe.generate_hash(length=10)
        user.new_password = temp_password
        user.save(ignore_permissions=True)

        # Email login credentials
        login_url = f"{frappe.utils.get_url()}/login"
        message = f"""
        Dear {student_name},<br><br>
        Your student account has been created.<br><br>
        <b>Login URL:</b> <a href="{login_url}">{login_url}</a><br>
        <b>Email:</b> {email}<br>
        <b>Password:</b> {temp_password}<br><br>
        You can now pay your fee and later view your test marks.<br><br>
        Regards,<br>Admissions Team
        """
        frappe.sendmail(recipients=email, subject="Student Login Created", message=message)
