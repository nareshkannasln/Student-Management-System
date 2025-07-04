import frappe

def execute():
    subjects = [
        "Math",
        "Physics",
        "Chemistry",
        "Biology",
        "English",
        "Computer Science"
    ]

    for subject in subjects:
        if not frappe.db.exists("subjects", {"subject_name": subject}):
            frappe.get_doc({
                "doctype": "subjects",  # <-- must be lowercase as per your system
                "subject_name": subject
            }).insert(ignore_permissions=True)
