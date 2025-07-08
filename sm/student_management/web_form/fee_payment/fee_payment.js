frappe.ready(() => {
    frappe.web_form.on('roll_no', (field, value) => {
        if (!value) return;

        frappe.call({
            method: "sm.api.get_fee_data", // update to your path
            args: { roll_no: value },
            callback: function (r) {
                if (!r.message) return;

                frappe.web_form.set_value('name1', r.message.student_name);
                frappe.web_form.set_value('class', r.message.student_class);
                frappe.web_form.set_value('email', r.message.email);

                const cleaned_rows = r.message.fee_structure || [];

                let fee_field = frappe.web_form.fields_dict['fee_structure'];
                if (fee_field) {
                    fee_field.df.data = cleaned_rows;
                    fee_field.grid.refresh();
                }
            }
        });
    });
});
