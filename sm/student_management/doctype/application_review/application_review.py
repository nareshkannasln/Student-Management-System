import frappe
from frappe.model.document import Document

class ApplicationReview(Document):
    def on_submit(self):
        frappe.logger().info("✅ on_submit triggered for " + self.name)
        frappe.msgprint("✅ on_submit triggered for " + self.name)

        if self.status == "Approve":
            admission = frappe.get_doc("Admission Application", self.admission_application)
            frappe.logger().info(f"📧 Sending welcome email to {admission.email}")
            send_welcome_email(admission.email, admission.name, admission.class_applied_for)

def send_welcome_email(recipient_email, student_name, student_class):
    if not recipient_email:
        frappe.logger().error("❌ Email not sent: recipient email is missing.")
        return

    subject = f"Welcome to Class {student_class}"
    message = f"""Dear {student_name},<br><br>
    Welcome to <b>Class {student_class}</b>!<br>
    Regards,<br>Admissions Team"""

    try:
        frappe.sendmail(
            recipients=[recipient_email],
            subject=subject,
            message=message
        )
        frappe.logger().info(f"✅ Email sent successfully to {recipient_email}")
    except Exception as e:
        frappe.logger().error(f"❌ Email failed: {e}")
