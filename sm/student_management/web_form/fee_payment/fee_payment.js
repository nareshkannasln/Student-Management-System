frappe.ready(() => {

    // 1. When roll_no is selected, fetch student and fee data
    frappe.web_form.on('roll_no', (field, value) => {
        if (!value) return;

        frappe.call({
            method: "sm.api.get_fee_data", // Your custom backend method
            args: { roll_no: value },
            callback: function (r) {
                if (!r.message) return;

                // Set student info
                frappe.web_form.set_value('name1', r.message.student_name);
                frappe.web_form.set_value('class', r.message.student_class);
                frappe.web_form.set_value('email', r.message.email);

                // Load child table data (fee_structure)
                const cleaned_rows = r.message.fee_structure || [];
                let fee_field = frappe.web_form.fields_dict['fee_structure'];
                if (fee_field) {
                    fee_field.df.data = cleaned_rows;
                    fee_field.grid.refresh();
                }

                // After setting child table, also update total_fee, balance, status
                update_balance_and_status();
            }
        });
    });

    // 2. When amount is changed, recalculate balance and status
    frappe.web_form.on('amount', function() {
        update_balance_and_status();
    });

    // 3. Function to calculate and update total_fee, balance_fee, payment_status
    function update_balance_and_status() {
        const fee_structure = frappe.web_form.doc.fee_structure || [];

        if (fee_structure.length > 0) {
            total_fee = fee_structure[0].total_fee || 0;
        }

        const paid = frappe.web_form.get_value('amount') || 0;
        const balance = total_fee - paid;

        frappe.web_form.set_value('total_fee', total_fee);
        frappe.web_form.set_value('balance_fee', balance);

        if (paid == total_fee) {
            frappe.web_form.set_value('payment_status', "Fully Paid");
        } else if (paid > 0 && paid < total_fee) {
            frappe.web_form.set_value('payment_status', "Partially Paid");
        } else {
            frappe.web_form.set_value('payment_status', "Unpaid");
        }
    }

    // Optional: run once when form loads to update balance and status (for editing)
    update_balance_and_status();
});
