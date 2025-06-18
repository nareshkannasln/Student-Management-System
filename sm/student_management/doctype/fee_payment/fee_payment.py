import frappe
from frappe.model.document import Document

class FeePayment(Document):
    def validate(self):
        self.balance_amount = self.total_fee - self.paid_amount
        self.status = "Paid" if self.balance_amount == 0 else "Partially Paid"

    def on_submit(self):
        self.send_payment_email()
        if self.status == "Paid":
            self.create_student_user()

    def send_payment_email(self):
        student_email = frappe.db.get_value("Admission Application", {"student_name": self.student}, "email")

        message = f"""
        Dear {self.student},<br><br>
        Your payment of ₹{self.paid_amount} has been recorded.<br>
        {"✅ You have paid the full fee. Thank you!" if self.balance_amount == 0 else f"Your remaining balance is ₹{self.balance_amount}."}
        <br><br>
        {"<a href='https://your-site.com/login'>Click here to login</a> using your registered email and password." if self.balance_amount == 0 else ""}
        <br><br>
        Regards,<br>Finance Department
        """

        frappe.sendmail(
            recipients=[student_email],
            subject="Fee Payment Acknowledgement",
            message=message
        )

    def create_student_user(self):
        student_email = frappe.db.get_value("Admission Application", {"student_name": self.student}, "email")
        if not frappe.db.exists("User", student_email):
            user = frappe.get_doc({
                "doctype": "User",
                "email": student_email,
                "first_name": self.student,
                "send_welcome_email": 1
            })
            user.insert(ignore_permissions=True)

        user = frappe.get_doc("User", student_email)
        if "Student" not in user.roles:
            user.add_roles("Student")

        # Give access to Student Present Marks
        if not frappe.db.exists("User Permission", {
            "user": student_email,
            "allow": "Student Present Marks",
            "for_value": self.student
        }):
            frappe.get_doc({
                "doctype": "User Permission",
                "user": student_email,
                "allow": "Student Present Marks",
                "for_value": self.student
            }).insert(ignore_permissions=True)
