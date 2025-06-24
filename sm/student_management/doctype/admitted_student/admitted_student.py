# Copyright (c) 2025, Nareshkanna and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document

class AdmittedStudent(Document):
	def autoname(self):
		class_name = (self.get("class") or "CLASS").replace(" ", "").upper()
		count = frappe.db.count("Admitted Student", filters={"class": self.get("class")})
		self.name = f"{class_name}-{count + 1:03d}"
