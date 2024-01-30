// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */
const pos_profiles = (frappe)=>{
	let nombre_perfil = ["tienda@shalom.com.pe","48191841@shalomcontrol.com","71073387@shalomcontrol.com"].includes(frappe.user.name) ? "":(frappe.defaults.get_user_permissions()["POS Profile"] != undefined ? frappe.defaults.get_user_permissions()["POS Profile"][0].doc : "")

	return nombre_perfil;
}



frappe.query_reports["POS Register"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"pos_profile",
			"label": __("POS Profile"),
			"fieldtype": "Link",
			"options": "POS Profile",
			"default": pos_profiles(frappe),
			"read_only": pos_profiles(frappe) == "" ? 0 : 1
		},
		{
			"fieldname":"cashier",
			"label": __("Cashier"),
			"fieldtype": "Link",
			"options": "User"
		},
		// {
		// 	"fieldname":"customer",
		// 	"label": __("Customer"),
		// 	"fieldtype": "Link",
		// 	"options": "Customer"
		// },
		// {
		// 	"fieldname":"mode_of_payment",
		// 	"label": __("Payment Method"),
		// 	"fieldtype": "Link",
		// 	"options": "Mode of Payment"
		// },
		{
			"fieldname":"group_by",
			"label": __("Group by"),
			"fieldtype": "Select",
			// "options": ["", "POS Profile", "Cashier", "Payment Method", "Customer"],
			"options": ["","POS Profile", "Cashier"],
			// "default": "POS Profile"
		},
		{
			"fieldname":"status_comprobante",
			"label": __("Tipo de Comprobante"),
			"fieldtype": "Select",
			"options": ["", "Boleta", "Factura"],
		},
		{
			"fieldname":"type_payment",
			"label": __("Modo de Pago"),
			"fieldtype": "Select",
			"options": ["", "Efectivo", "Link", "Pago por PINPAD", "QR","Planilla"],
		},
		// {
		// 	"fieldname":"is_return",
		// 	"label": __("Is Return"),
		// 	"fieldtype": "Check"
		// },
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data && data.bold) {
			value = value.bold();

		}
		return value;
	}
};
