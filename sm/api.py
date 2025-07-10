import frappe 
@frappe.whitelist(allow_guest=True)
def get_fee_data(roll_no):
    if not roll_no:
        frappe.throw("Admission ID is required")

    student = frappe.get_doc("Admitted Student", roll_no)

    fee_doc = frappe.get_doc("Fee and Syllabus", {
        "class": student.student_class
    })

    return {
        "student_name": student.name1,
        "student_class": student.student_class,
        "fee_structure": [
            {
                "tuition_fee": row.tuition_fee,
                "exam_fee": row.exam_fee,
                "total_fee": row.total_fee
            }
            for row in fee_doc.fee_structure
        ]
    }
