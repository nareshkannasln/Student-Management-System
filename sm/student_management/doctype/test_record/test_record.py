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
          name = self.get("admisson_id")
          self.name = name
    def has_permission(doc, user=None):
        if not user:
            user = frappe.session.user
        # Check if user has 'Student' role
        if "Student" in frappe.get_roles(user):
            # Check if student has paid full fee
            student = frappe.db.get_value("Student", {"user": user}, "name")
            if student:
                fee_status = frappe.db.get_value("Fee", {"student": student}, "status")
                if fee_status == "Paid":
                    # Allow access only to their own test record
                    return doc.admisson_id == student
        return False