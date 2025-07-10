import frappe

def execute():
    roles = ["Student", "Teacher"]

    for role in roles:
        if not frappe.db.exists("Role", {"role_name": role}):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role
            }).insert()
