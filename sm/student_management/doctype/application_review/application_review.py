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
        total_fee = frappe.get_value("Fee and Syllabus", {"class": admission.class_applying_for}, "total")

        if frappe.db.exists("Admitted Student", {"admission_id": admission.name}):
            frappe.msgprint("Student already exists in Admitted Student.")
            return

        user_email = admission.email
        if not frappe.db.exists("User", user_email):
            user = frappe.new_doc("User")
            user.email = user_email
            user.first_name = admission.name
            user.send_welcome_email = 1
            user.role_profile_name = ""
            user.append("roles", {"role": "Student User"})
            user.insert(ignore_permissions=True)

        admitted_doc = frappe.new_doc("Admitted Student")
        admitted_doc.student_name = admission.name
        admitted_doc.email = user_email
        admitted_doc.student_class = admission.class_applying_for
        admitted_doc.admission_id = admission.name
        admitted_doc.total_fee = total_fee or 0
        admitted_doc.status = "Admitted"
        admitted_doc.user_id = user_email
        admitted_doc.insert(ignore_permissions=True)

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

        frappe.msgprint(f"Admitted Student and Website User created for {admission.name}")

    def send_welcome_email(self, admission):
        recipient_email = admission.email
        student_name = admission.name
        student_class = admission.class_applying_for

        # Get the name of the Fee and Syllabus document
        fee_name = frappe.get_value("Fee and Syllabus", {"class": student_class}, "name")
        if not fee_name:
            frappe.throw(f"No 'Fee and Syllabus' document found for Class: {student_class}")

        # Now safely get the full document
        print(f"Fee and Syllabus Document Name: {fee_name}")
        fee_doc = frappe.get_doc("Fee and Syllabus", fee_name)

        total_fee = fee_doc.total
        subjects = [row.subject for row in fee_doc.syllabus]
        subject_html = "<ul>" + "".join([f"<li>{sub}</li>" for sub in subjects]) + "</ul>" if subjects else "N/A"

        base_url = get_url()
        pay_url = f"{base_url}/fee-payment"

        subject = f"Admission Approved - Class {student_class}"
        message = f"""
        <p>Dear {student_name},</p>

        <p>Your application for admission to Class {student_class} has been approved.</p>

        <p>Please find the syllabus and fee structure below. Proceed to pay your fee using the link provided.</p>

        <h4>Syllabus</h4>
        {subject_html}

        <h4>Fee Structure</h4>
        <table border='1' cellpadding='5'>
            <tr><th>Fee Type</th><th>Amount (₹)</th></tr>
            <tr><td>Tuition Fee</td><td>{fee_doc.tuition_fee}</td></tr>
            <tr><td>Miscellaneous Fee</td><td>{fee_doc.miscellaneous_fee}</td></tr>
            <tr><td><strong>Total</strong></td><td><strong>{total_fee}</strong></td></tr>
        </table>

        <br>
        <a href="{pay_url}" style="
            background-color:#007bff;
            color:white;
            padding:10px 20px;
            text-decoration:none;
            border-radius:5px;
            display:inline-block;">
            Proceed to Fee Payment
        </a>

        <p>If you have any questions, please contact the admissions office.</p>

        <p>Regards,<br>
        Admissions Team</p>
        """

        frappe.sendmail(
            recipients=[recipient_email],
            subject=subject,
            message=message
        )

        frappe.msgprint("Admission approval email sent.")



    def send_rejection_email(self, admission):
        recipient_email = admission.email
        student_name = admission.name
        student_class = admission.class_applying_for

        subject = f"Application Status - Class {student_class}"
        message = f"""
        <p>Dear {student_name},</p>

        <p>Thank you for applying to Class {student_class}.</p>

        <p>We regret to inform you that your application was not approved.</p>

        <p>We appreciate your interest and wish you success in the future.</p>

        <p>Sincerely,<br>
        Admissions Committee</p>
        """

        frappe.sendmail(
            recipients=[recipient_email],
            subject=subject,
            message=message
        )

        frappe.msgprint("Rejection email sent.")
