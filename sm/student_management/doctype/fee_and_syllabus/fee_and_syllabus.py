import frappe
from frappe.model.document import Document
from frappe.utils import flt

class FeeandSyllabus(Document):
    def autoname(self):
        class_name = getattr(self, "class", None)
        if class_name:
            self.name = class_name
        else:
            frappe.throw("Class is required to name the document.")

    def validate(self):
        self.total = flt(self.tuition_fee) + flt(self.miscellaneous_fee)
