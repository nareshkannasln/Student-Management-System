import frappe

def execute():
    if not frappe.db.table_exists("tabSubjects"):
        print("Subjects Master table does not exist. Skipping patch.")
        return

    subjects = ["Math", "Physics", "Chemistry", "Biology", "English", "Computer Science"]

    for subj in subjects:
        if not frappe.db.exists("Subjects", {"subjects": subj}):
            frappe.db.insert("Subjects Master", {
                "subjects": subj
            })

    print("Subjects Master patched successfully.")
