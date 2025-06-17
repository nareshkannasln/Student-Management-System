# Copyright (c) 2025, Nareshkanna and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.core.doctype.communication.email import make
from frappe.utils import now

class ApplicationReview(Document):
    def on_submit(self):
        self.validate_application_status()
        self.send_notification_email()

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

        # Email content
        subject = f"Admission Application {self.status} for Class {student_class}"
        if self.status == "Approve":
            message = f"""
            Dear {admission.name1},<br><br>
            Congratulations! Your admission to class <b>{student_class}</b> has been approved.<br><br>
            {fee_syllabus_html}<br><br>
            Regards,<br>
            Admissions Team
            """
        else:
            message = f"""
            Dear {admission.name1},<br><br>
            We regret to inform you that your admission has been rejected.<br><br>
            Regards,<br>
            Admissions Team
            """

        # Send email
        if recipient_email:
            frappe.sendmail(
                recipients=[recipient_email],
                subject=subject,
                message=message
            )
        else:
            frappe.msgprint("Email not sent: No email found in Admission Application.")
