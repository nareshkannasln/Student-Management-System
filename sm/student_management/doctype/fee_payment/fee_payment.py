import frappe
from frappe.model.document import Document

class FeePayment(Document):
  def autoname(self):
    # Get the latest TNX number used
    last_name = frappe.db.get_value(
        "Fee Payment",
        filters={"name": ["like", "TNX%"]},
        fieldname="name",
        order_by="creation desc"
    )

    if last_name and "TNX" in last_name:
        try:
            last_num = int(last_name.replace("TNX", ""))
        except ValueError:
            last_num = 0
    else:
        last_num = 0

    new_num = last_num + 1
    self.name = f"TNX{new_num:03d}"

 
    def validate(self):
        paid_now = self.amount or 0
        self.total_fee = sum(row.total_fee or 0 for row in self.fee_structure)

        # Get sum of all previous payments made by this roll_no (excluding current doc)
        previous_payments = frappe.db.sql("""
            SELECT SUM(amount) FROM `tabFee Payment`
            WHERE roll_no = %s AND name != %s
        """, (self.roll_no, self.name))[0][0] or 0

        total_paid = previous_payments + paid_now
        self.balance_fee = self.total_fee - total_paid


        if total_paid == self.total_fee:
            self.payment_status = "Fully Paid"            
            print(f"Payment status set to Fully Paid ")
            frappe.msgprint(f"Payment status set to Fully Paid for {self.balance_fee}")
            self.enable_user_and_send_welcome(self.email)
            print(f"User enabled and welcome email sent for {self.email}")
        elif total_paid > 0:
            frappe.msgprint(f"Payment status set to Partially Paid for {self.balance_fee}")
            self.payment_status = "Partially paid"
            print(f"{self.balance_fee}")
        else:
            self.payment_status = "Unpaid"

    def enable_user_and_send_welcome(self, email):
        print("Working")
    # frappe.throw("Enabling user and sending welcome email is not allowed in this context. Please use the appropriate method to handle user creation and email notifications.	")
        frappe.msgprint(f"Processing email: {email}")

        if not frappe.db.exists("User", email):
            user = frappe.get_doc({
                "doctype": "User",
                "email": email,
                "first_name": email.split("@")[0],
                "enabled": 1,
                "user_type": "Website User"
            })
            user.insert(ignore_permissions=True)
            frappe.db.commit()
            self.send_welcome_email(user)
            frappe.msgprint(f"User '{email}' created and welcome email sent.")
        else:
            user = frappe.get_doc("User", email)
            updated = False
            if not user.enabled:
                user.enabled = 1
                updated = True
            if updated:
                user.save(ignore_permissions=True)
                frappe.db.commit()
                self.send_welcome_email(user)
                frappe.msgprint(f"User '{email}' has been enabled and welcome email sent.")

    def send_welcome_email(self, user):
        login_link = f"{frappe.utils.get_url()}/login"
        message = f"""
            <p>Hello <b>{user.first_name}</b>,</p>
            <p>Your student account has been successfully activated.</p>
            <p>
                <a href="{login_link}" style="background-color:#4CAF50;color:white;padding:10px 15px;
                text-decoration:none;border-radius:5px;">
                    Login Now
                </a>
            </p>
            <br><p>Thank you!</p>
        """
        frappe.sendmail(
            recipients=[user.email],
            subject="Welcome to the Student Portal",
            message=message
        )