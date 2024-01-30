// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['Sales Invoice'] = {
	add_fields: ["customer", "customer_name", "base_grand_total", "outstanding_amount", "due_date", "company",
		"currency", "is_return"],
	get_indicator: function(doc) {
		var status_color = {
			"Draft": "grey",
			"Unpaid": "green",
			"Paid": "green",
			"Return": "gray",
			"Credit Note Issued": "gray",
			"Unpaid and Discounted": "orange",
			"Overdue and Discounted": "red",
			"Overdue": "red",
			"Internal Transfer": "darkgrey"
		};

		var status = "";

		if (doc.status == "Unpaid") {

			status = "Paid";

		} else {

			status = doc.status;

		}

		console.log(status)

		return [__(status), status_color[doc.status], "status,=,"+status];
	},
	right_column: "grand_total"
};
