# Copyright (c) 2025, Nareshkanna and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FeeandSyllabus(Document):
    def validate(self):
        self.calculate_total_fee()

    def calculate_total_fee(self):
        self.total = (self.tution_fee or 0) + (self.miscallneous_fee or 0)


