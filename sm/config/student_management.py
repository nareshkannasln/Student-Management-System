from frappe import _

def get_data():
    return [
        {
            "module_name": "Student Management",
            "type": "module",
            "label": _("Student Management"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Subjects Master",
                    "label": _("Subjects Master"),
                }
            ]
        }
    ]
