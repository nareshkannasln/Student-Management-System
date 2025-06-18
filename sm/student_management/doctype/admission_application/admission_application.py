import frappe
from frappe.model.document import Document

class AdmissionApplication(Document):
    def validate(self):
        total = 0
        for row in self.previous_standard_marks:
            total += row.marks or 0  # Safely add marks (avoid None)

        self.total = total  # Update the total field
    
    def autoname(self):
        class_code = (self.class_applying_for or "GEN").replace(" ", "").upper()
        applicant_name = (self.name1 or "UNKNOWN").replace(" ", "").upper()
        year = frappe.utils.now_datetime().strftime("%Y")  # Optional: use year for uniqueness
        self.name = f'APP-{class_code}-{applicant_name}-{year}'

