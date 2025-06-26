import frappe
from frappe.model.document import Document

class StudentRecords(Document):
    def validate(self):
        total = 0
        for row in self.marks:
            total += row.marks or 0  # Safely add marks (avoid None)
        self.total = total

    def autoname(self):
        class_code = getattr(self, "class", "GEN") 
        roll_no = (self.name1 or "UNKNOWN").replace(" ", "").upper()
        t_name = (self.test_name or "TEST").replace(" ", "").upper()
        self.name = f'SPM-{class_code}-{roll_no}-{t_name}'
    def has_permission(doc, ptype="read", user=None):
        if not user or user == "Guest":
            return False

        student_id = frappe.get_value("Admitted Student", {"email": user}, "name")

        if not student_id:
            return False

        # Check if student paid full fee
        fee = frappe.get_value("Fee Payment", {"admission_id": student_id}, ["amount", "total_fee"], as_dict=True)
        
        if not fee or float(fee.amount or 0) < float(fee.total_fee or 0):
            return False

        # Allow if Test Record belongs to this student
        return doc.admission_id == student_id
