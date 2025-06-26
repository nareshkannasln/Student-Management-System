# Copyright (c) 2025, Nareshkanna and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document


class FeePayment(Document):
    def validate(self):
        self.balance_fee = self.total_fee - self.amount
        if self.balance_fee < 0:
            frappe.throw("Paid amount cannot exceed total fee.")