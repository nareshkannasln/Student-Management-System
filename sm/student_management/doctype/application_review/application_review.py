import frappe
from frappe.model.document import Document
from frappe.utils import get_url

class ApplicationReview(Document):
    def on_submit(self):
        if not self.admission_id:
            frappe.throw("Admission ID is missing. Please link an Admission Application.")

        admission = frappe.get_doc("Admission Application", self.admission_id)

        if self.status == "Approve":
            self.create_admitted_students(admission)
            self.send_welcome_email(admission)
        elif self.status == "Reject":
            self.send_rejection_email(admission)

    def create_admitted_students(self, admission):
        # 1. Get total fee from Fee and Syllabus
        total_fee = frappe.get_value("Fee and Syllabus", {"class": admission.class_applying_for}, "total")

        # 2. Prevent duplicate
        if frappe.db.exists("Admitted Student", {"admission_id": admission.name}):
            frappe.msgprint("⚠️ Student already exists in Admitted Student.")
            return

        # 3. Create Website User (if not already exists)
        user_email = admission.email
        if not frappe.db.exists("User", user_email):
            user = frappe.new_doc("User")
            user.email = user_email
            user.first_name = admission.name
            user.send_welcome_email = 1
            user.role_profile_name = ""
            user.append("roles", {"role": "Student Portal User"})
            user.insert(ignore_permissions=True)

        # 4. Create Admitted Student and link to User
        admitted_doc = frappe.new_doc("Admitted Student")
        admitted_doc.student_name = admission.name
        admitted_doc.email = user_email
        admitted_doc.student_class = admission.class_applying_for
        admitted_doc.admission_id = admission.name
        admitted_doc.total_fee = total_fee or 0
        admitted_doc.status = "Admitted"
        admitted_doc.user_id = user_email  # Link to User
        admitted_doc.insert(ignore_permissions=True)

        # 5. Create User Permission (limit user to only their Admitted Student record)
        if not frappe.db.exists("User Permission", {
            "user": user_email,
            "allow": "Admitted Student",
            "for_value": admitted_doc.name
        }):
            frappe.get_doc({
                "doctype": "User Permission",
                "user": user_email,
                "allow": "Admitted Student",
                "for_value": admitted_doc.name,
                "apply_to_all_doctypes": 0
            }).insert(ignore_permissions=True)

        # 6. Success message
        frappe.msgprint(f"✅ Admitted Student and Website User created for {admission.name}")


    def send_welcome_email(self, admission):
        recipient_email = admission.email
        student_name = admission.name
        student_class = admission.class_applying_for

        if not recipient_email:
            frappe.msgprint("⛔ Email not sent: recipient email is missing.")
            return

        try:
            # Get Fee and Syllabus details
            fee_doc = frappe.get_doc("Fee and Syllabus", {"class": student_class})
            total_fee = fee_doc.total
            subjects = [row.subject for row in fee_doc.subject]

            # Subject list as HTML
            subject_html = "<ul>" + "".join([f"<li>{sub}</li>" for sub in subjects]) + "</ul>" if subjects else "N/A"

            # ✅ Simplified and secure payment URL using only email
            base_url = get_url()
            pay_url = f"{base_url}/fee-payment"

            # Email Subject
            subject = f"🎉 Admission Approved - Welcome to Class {student_class}"

            # Email Body
            message = f"""
            <p>Dear <strong>{student_name}</strong>,</p>

            <p>🎉 <strong>Congratulations!</strong> Your application for <strong>Class {student_class}</strong> has been 
            <span style="color:green;"><strong>approved</strong></span>.</p>

            <p>We’re thrilled to welcome you! Here's what's next:</p>

            <ul>
                <li>📚 Below is your syllabus and fee structure.</li>
                <li>💳 Please complete your fee payment using the button below.</li>
                <li>📩 You'll soon receive your class schedule and login credentials.</li>
            </ul>

            <h4>📘 Syllabus</h4>
            {subject_html}

            <h4>💰 Fee Structure</h4>
            <table border='1' cellpadding='5'>
                <tr><th>Fee Type</th><th>Amount (₹)</th></tr>
                <tr><td>Tuition Fee</td><td>{fee_doc.tuition_fee}</td></tr>
                <tr><td>Miscellaneous Fee</td><td>{fee_doc.miscellaneous_fee}</td></tr>
                <tr><td><strong>Total</strong></td><td><strong>{total_fee}</strong></td></tr>
            </table>

            <br>
            <a href="{pay_url}" style="
                background-color:#4CAF50;
                color:white;
                padding:10px 20px;
                text-decoration:none;
                border-radius:5px;
                display:inline-block;">
                Pay Fee Now
            </a>

            <p>If you have any questions, feel free to contact our admissions team.</p>

            <p>Warm regards,<br>
            <strong>Admissions Team</strong></p>
            """

            frappe.sendmail(
                recipients=[recipient_email],
                subject=subject,
                message=message
            )
            frappe.msgprint("✅ Admission approval email sent.")
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Combined Welcome Email Error")
            frappe.msgprint(f"❌ Failed to send welcome email: {str(e)}")


    def send_rejection_email(self, admission):
        recipient_email = admission.email
        student_name = admission.name
        student_class = admission.class_applying_for

        if not recipient_email:
            frappe.msgprint("⛔ Email not sent: recipient email is missing.")
            return

        subject = f"Application Status - Class {student_class}"

        message = f"""
        <p>Dear <strong>{student_name}</strong>,</p>

        <p>Thank you for your interest in <strong>Class {student_class}</strong>.</p>

        <p>After review, we regret to inform you that your admission was not approved at this time.</p>
        
        <p>Wishing you the best in your journey.</p>

        <p>Sincerely,<br>
        <strong>Admissions Committee</strong></p>
        """

        try:
            frappe.sendmail(
                recipients=[recipient_email],
                subject=subject,
                message=message
            )
            frappe.msgprint("📭 Rejection email sent.")
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Rejection Email Sending Error")
            frappe.msgprint(f"❌ Failed to send rejection email: {str(e)}")
