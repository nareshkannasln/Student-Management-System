import frappe

@frappe.whitelist()
def get_approved_students(student_class):
    data = frappe.db.sql("""
        SELECT aa.name, aa.name1
        FROM `tabApplication Review` ar
        JOIN `tabAdmission Application` aa ON ar.admission_application = aa.name
        WHERE ar.status = 'Approve'
        AND aa.class_applying_for = %s
    """, (student_class,), as_dict=True)

    # Return with label-value format for link field
    return [{"value": row.name, "description": f"{row.name} - {row.name1}"} for row in data]
