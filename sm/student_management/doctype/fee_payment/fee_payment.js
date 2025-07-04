frappe.ui.form.on('Fee Payment', {
    validate: function(frm) {
        let total_fee = 0;

        // Calculate total from child table
        (frm.doc.fee_structure || []).forEach(row => {
            total_fee += row.total_fee || 0;
        });

        // Set total fee amount
        frm.set_value('amount', total_fee);

        // Optional: if you allow custom payment amount (e.g., partially paid)
        const paid = frm.doc.amount || 0;
        const balance = total_fee - paid;
        frm.set_value('balance_fee', balance);

        // Set payment status
        if (paid >= total_fee) {
            frm.set_value('payment_status', "Full Paid");
        } else if (paid > 0) {
            frm.set_value('payment_status', "Partially Paid");
        } else {
            frm.set_value('payment_status', "Unpaid");
        }
    }
});
