frappe.ready(() => {
    frappe.web_form.on('admission_id', (field, value) => {
        if (!value) return;

        // Step 1: Get student
        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Admitted Student",
                name: value
            },
            callback: function(studentRes) {
                const student = studentRes.message;
                if (!student) return;

                frappe.web_form.set_value('name1', student.name1);
                frappe.web_form.set_value('class', student.student_class);

                // Step 2: Get Fee Syllabus for class
                frappe.call({
                    method: "frappe.client.get_list",
                    args: {
                        doctype: "Fee and Syllabus",
                        filters: { "class": student.student_class },
                        fields: ["name"],
                        limit_page_length: 1
                    },
                    callback: function(feeListRes) {
                        if (!feeListRes.message?.length) return;

                        const fee_doc_name = feeListRes.message[0].name;

                        // Step 3: Get full doc
                        frappe.call({
                            method: "frappe.client.get",
                            args: {
                                doctype: "Fee and Syllabus",
                                name: fee_doc_name
                            },
                            callback: function(fullFeeRes) {
                                const fee_doc = fullFeeRes.message;
                                if (!fee_doc || !Array.isArray(fee_doc.fee_structure)) return;

                                // Clean fee data (avoid metadata)
                                const cleaned_rows = fee_doc.fee_structure.map(row => ({
                                    tuition_fee: row.tuition_fee,
                                    exam_fee: row.exam_fee,
                                    total_fee: row.total_fee
                                }));

                                console.log("Fee Structure cleaned:", cleaned_rows);

                                // ✅ Assign data directly into field dict
                                let fee_field = frappe.web_form.fields_dict['fee_structure'];
                                if (fee_field) {
                                    fee_field.df.data = cleaned_rows;
                                    fee_field.grid.refresh();
                                }
                            }
                        });
                    }
                });
            }
        });
    });
});
