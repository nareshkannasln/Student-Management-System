frappe.ui.form.on('Fee Payment', {
    validate: function(frm) {
        let total_fee = 0;

        // 1. Calculate total for each row and overall total
        (frm.doc.fee_structure_child || []).forEach(row => {
            row.total_fee = (row.tuition_fee || 0) + (row.exam_fee || 0);  // ✅ Assign the value
            total_fee = row.total_fee;  // ✅ Add to grand total
        });

        // 2. Set total fee and balance
        frm.set_value('total_fee', total_fee);

        const paid = frm.doc.amount || 0;
        const balance = total_fee - paid;
        frm.set_value('balance_fee', balance);

        // 3. Determine payment status
        if (paid >= total_fee) {
            frm.set_value('payment_status', "Fully Paid");
        } else if (paid > 0) {
            frm.set_value('payment_status', "Partially Paid");
        } else {
            frm.set_value('payment_status', "Unpaid");
        }
    }
});
