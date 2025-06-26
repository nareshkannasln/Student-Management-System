import frappe

def get_context(context):
    user = frappe.session.user
    context.admitted = frappe.get_value("Admitted Student", {"email": user}, ["name", "total_fee"], as_dict=True)

    if not context.admitted:
        context.message = "You are not an admitted student."
        return context

    fee_doc = frappe.get_value("Fee Payment", {"admission_id": context.admitted.name}, ["amount", "total_fee"], as_dict=True)

    if fee_doc and float(fee_doc.amount) >= float(fee_doc.total_fee):
        context.show_test_button = True
    else:
        context.show_test_button = False
        context.message = "Please complete your full fee payment to access Test Records."
    
    return context
