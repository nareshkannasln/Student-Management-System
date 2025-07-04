# Copyright (c) 2025, Nareshkanna and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FeePayment(Document):
	def autoname(self):
		self.name = self.get("admission_id")		
