// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */
let today = frappe.datetime.get_today();
frappe.query_reports["Supervicion Almacen"] = {
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
		},
		{
			"fieldname":"branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"width": "100px",
		},
		{
			"fieldname":"zona_nacional",
			"label": __("Zonas Nacional"),
			"fieldtype": "Link",
			"options": "Zonas Nacional",
			"width": "100px",
		},
		{
			"fieldname":"tipo_almacen",
			"label": __("Warehouse Type"),
			"fieldtype": "Link",
			"options": "Warehouse Type",
			"width": "100px",
		},
	]
};

