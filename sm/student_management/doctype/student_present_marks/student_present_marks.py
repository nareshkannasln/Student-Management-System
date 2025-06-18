import frappe
from frappe.model.document import Document

class StudentPresentMarks(Document):
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
