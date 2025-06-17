import frappe
from frappe.model.document import Document

class AdmissionApplication(Document):
    def validate(self):
        total = 0
        for row in self.previous_standard_marks:
            total += row.marks or 0  # Safely add marks (avoid None)

        self.total = total  # Update the total field
