// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Reporte de Renovaciones"] = {
	"filters": [
		{
			"fieldname":"branch",
			"label": __("Sucursal"),
			"fieldtype": "Link",
			"options":'Branch'
		},
		{
			"fieldname":"month",
			"label": __("Mes"),
			"fieldtype": "Select",
			"options":[ "Enero"
						"Febrero"
						"Marzo"
						"Abril"
						"Mayo"
						"Junio"
						"Julio"
						"Agosto"
						"Septiembre"
						"Octubre"
						"Noviembre"
						"Diciembre"
			]
		},
		{
			"fieldname":"year",
			"label": __("Año"),
			"fieldtype": "Select",
			"options":[ "2022"
				"2023"
				"2024"
			]
		}
	]
};
