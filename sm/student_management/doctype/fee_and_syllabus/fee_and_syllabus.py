# Copyright (c) 2025, Nareshkanna and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FeeandSyllabus(Document):
	def validate(self):
		self.total_fee = self.tuition_fee + self.other_fee

	def autoname(self):
		doc_name = self.get("class")
		self.name = doc_name