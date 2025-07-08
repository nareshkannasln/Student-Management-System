import frappe
from frappe.model.document import Document

class TestRecord(Document):
    def validate(self):
        self.calculate_total_marks()

    def calculate_total_marks(self):
        total = 0
        for row in self.test_marks:
            total += row.marks or 0
        self.total = total

    def autoname(self):
        self.name = self.roll_no  # Fixed typo from 'admisson_id'

    def has_permission(self, user=None):
        if not user:
            user = frappe.session.user

        # Only restrict for Student role
        if "Student" in frappe.get_roles(user):
            student = frappe.db.get_value("Student", {"user": user}, "name")
            if student:
                fee_status = frappe.db.get_value("Fee", {"student": student}, "status")
                if fee_status == "Paid":
                    return self.roll_no == student  # Ensure 'admission_id' matches field name

        # For other roles like System Manager, allow
        return True
