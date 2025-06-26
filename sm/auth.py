import frappe

def validate_fee_status(login_manager):
    user = login_manager.user

    # Skip guest
    if user == "Guest":
        return

    # Check if Admitted Student exists
    student = frappe.get_value("Admitted Student", {"user_id": user}, ["name", "total_fee"], as_dict=True)
    
    if not student:
        return  # Let others login (admins, etc.)

    # Calculate paid amount
    paid = frappe.db.sql("""
        SELECT SUM(amount) FROM `tabFee Payment`
        WHERE admission_id = %s
    """, (student.name, ))[0][0] or 0

    if paid < student.total_fee:
        frappe.throw("Access denied. Please complete fee payment to proceed.")
