# student_records.py

import frappe
from frappe.model.document import Document

class StudentRecords(Document):
    def validate(self):
        total = sum(row.marks or 0 for row in self.marks)
        self.total = total

    def autoname(self):
        class_code = getattr(self, "class", "GEN")
        roll_no = (self.name1 or "UNKNOWN").replace(" ", "").upper()
        t_name = (self.test_name or "TEST").replace(" ", "").upper()
        self.name = f'SPM-{class_code}-{roll_no}-{t_name}'

# ✅ Outside the class
def has_permission(doc, ptype="read", user=None):
    print(f"[DEBUG] Permission check for {user} on {doc.name}")
    
    if not user or user == "Guest" or user == "Administrator":
        return True

    student_id = frappe.get_value("Admitted Student", {"email": user}, "name")
    if not student_id:
        print("[DEBUG] No Admitted Student found.")
        return False

    fee = frappe.get_value("Fee Payment", {"admission_id": student_id}, ["balance_fee"], as_dict=True)
    if not fee:
        print("[DEBUG] No Fee Payment found.")
        return False

    if float(fee.balance_fee or 0) > 0:
        print(f"[DEBUG] Unpaid fee: {fee.balance_fee}")
        return False

    return doc.admission_id == student_id


def get_permission_query_conditions(user):
    if user in ("Administrator", "Guest"):
        return ""

    student_id = frappe.get_value("Admitted Student", {"email": user}, "name")
    if not student_id:
        return "1=0"

    total_fee = frappe.db.get_value("Admitted Student", student_id, "total_fee")
    paid = frappe.db.sql("""
        SELECT SUM(amount) FROM `tabFee Payment`
        WHERE admission_id = %s
    """, (student_id,))[0][0] or 0

    if float(paid) < float(total_fee or 0):
        return "1=0"

    return f"`tabStudent Records`.roll_no = '{student_id}'"

