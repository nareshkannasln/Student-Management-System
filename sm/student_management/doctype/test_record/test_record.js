// frappe.ui.form.on('Test Record', {
//     admission_id: function(frm) {
//         const admission_id = frm.doc.admission_id;
//         if (!admission_id) return;

//         frappe.call({
//             method: "frappe.client.get",
//             args: {
//                 doctype: "Admitted Student",
//                 name: admission_id
//             },
//             callback: function(r) {
//                 const student = r.message;
//                 if (!student) return;

//                 const student_class = student.class;

//                 frappe.call({
//                     method: "frappe.client.get_list",
//                     args: {
//                         doctype: "Fee and Syllabus",
//                         filters: { "class": student_class },
//                         fields: ["name"]
//                     },
//                     callback: function(res) {
//                         if (!res.message || res.message.length === 0) return;

//                         const syllabus_name = res.message[0].name;

//                         frappe.call({
//                             method: "frappe.client.get",
//                             args: {
//                                 doctype: "Fee and Syllabus",
//                                 name: syllabus_name
//                             },
//                             callback: function(doc_res) {
//                                 const syllabus_doc = doc_res.message;
//                                 if (!syllabus_doc || !syllabus_doc.subjects) return;

//                                 frm.clear_table('test_marks');
//                                 syllabus_doc.subjects.forEach(subject_row => {
//                                     const row = frm.add_child('test_marks');
//                                     row.subjects = subject_row.subject_name;  // 🔁 Corrected to use `subject_name`
//                                 });
//                                 frm.refresh_field('test_marks');
//                             }
//                         });
//                     }
//                 });
//             }
//         });
//     }
// });
