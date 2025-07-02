import frappe

def execute():
    if not frappe.db.table_exists("tabSubjects Master"):
        print("Subjects Master table does not exist. Skipping patch.")
        return

    subject_name = ["Math", "Physics", "Chemistry", "Biology", "English", "Computer Science"]

    for subj in subject_name:
        if not frappe.db.exists("Subjects Master", {"subject_name": subj}):
            frappe.db.insert("Subjects Master", {
                "subject_name": subj
            })

    print("Subjects Master patched successfully.")
