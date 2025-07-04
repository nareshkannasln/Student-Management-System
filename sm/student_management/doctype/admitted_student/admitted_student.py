# Copyright (c) 2025, Nareshkanna and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AdmittedStudent(Document):
	def autoname(self):
		name = self.get("admission_id")
		self.name = name
