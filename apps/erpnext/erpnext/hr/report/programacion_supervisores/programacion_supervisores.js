// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */
let today = frappe.datetime.get_today();
frappe.query_reports["Programacion Supervisores"] = {

	"filters": [
		{
			"fieldname":"date_init",
			"label": __("From"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(frappe.datetime.get_today()),
			"width": "100px"
		},
		{
			"fieldname":"date_end",
			"label": __("Hasta"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_end(frappe.datetime.get_today()),
			"width": "100px"
		}
	]
};