frappe.ui.form.on('Student Present Marks', {
    class: function(frm) {
        // Fetch approved students for this class
        if (!frm.doc.class) return;

        // 1. Fetch and set student filter
        frappe.call({
            method: "sm.api.student_filter.get_approved_students",
            args: {
                student_class: frm.doc.class
            },
            callback: function(r) {
                if (r.message) {
                    frm.set_query("name1", () => ({
                        filters: {
                            name: ["in", r.message.map(row => row.value)]
                        }
                    }));
                }
            }
        });

        // 2. Fetch and populate subjects immediately
        frm.clear_table("marks");
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Fee and Syllabus",
                filters: { "class": frm.doc.class },
                fields: ["name"],
                limit_page_length: 1
            },
            callback: function(res) {
                if (res.message.length) {
                    const syllabus_name = res.message[0].name;
                    frappe.call({
                        method: "frappe.client.get",
                        args: {
                            doctype: "Fee and Syllabus",
                            name: syllabus_name
                        },
                        callback: function(r) {
                            if (r.message) {
                                const subjects = r.message.subject || [];
                                subjects.forEach(sub => {
                                    let row = frm.add_child("marks");
                                    row.subject = sub.subject;
                                });
                                frm.refresh_field("marks");
                            }
                        }
                    });
                }
            }
        });
    }
});
