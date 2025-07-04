# Copyright (c) 2025, Nareshkanna and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FeeandSyllabus(Document):
	def validate(self):
		for fee in self.fee_structure:
			fee.total_fee = fee.tuition_fee + fee.exam_fee

	def autoname(self):
		doc_name = self.get("class")
		self.name = doc_name