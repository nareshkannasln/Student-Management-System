// frappe.ui.form.on('Fee Payment', {
//     // Triggered when form is saved/validated
//     validate: function(frm) {
//         // Get total_fee from the first row only
//         let total_fee = 0;
//         if (frm.doc.fee_structure && frm.doc.fee_structure.length > 0) {
//             total_fee = frm.doc.fee_structure[0].total_fee || 0;
//         }

//         const paid = frm.doc.amount || 0;
//         const balance = total_fee - paid;

//         // Set balance fee and total_fee in parent doc
//         frm.set_value('total_fee', total_fee);
//         frm.set_value('balance_fee', balance);

//         // Set payment status
//         if (paid == total_fee) {
//             frm.set_value('payment_status', "Fully Paid");
//         } else if (paid > 0 && paid < total_fee) {
//             frm.set_value('payment_status', "Partially Paid");
//         } else {
//             frm.set_value('payment_status', "Unpaid");
//         }
//     },

//     // Triggered when amount field is changed
//     amount: function(frm) {
//         const total_fee = frm.doc.fee_structure[0].total_fee || 0;
//         const paid = frm.doc.amount || 0;
//         const balance = total_fee - paid;

//         frm.set_value('balance_fee', balance);

//         // Optional: update payment status on amount change
//         if (paid == total_fee) {
//             frm.set_value('payment_status', "Fully Paid");
//         } else if (paid < total_fee && paid > 0) {
//             frm.set_value('payment_status', "Partially Paid");
//         } else {
//             frm.set_value('payment_status', "Unpaid");
//         }
//     }
// });
