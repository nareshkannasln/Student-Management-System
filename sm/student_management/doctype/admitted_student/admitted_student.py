# Copyright (c) 2025, Nareshkanna and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AdmittedStudent(Document):
	def autoname(self):
		# Generate an auto-increment number based on existing records
		last_student = frappe.db.get_value(
			"Admitted Student",
			{"student_class": self.get("student_class"), "name1": self.get("name1")},
			"MAX(name)",
		)
		if last_student:
			try:
				last_number = int(last_student.split("-")[-1])
			except Exception:
				last_number = 0
		else:
			last_number = 0
		next_number = last_number + 1
		name = f"{self.get('student_class')}-{self.get('name1')}-{next_number:03d}"
		self.name = name                                  