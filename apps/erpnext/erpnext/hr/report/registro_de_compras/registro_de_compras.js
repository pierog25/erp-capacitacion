// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["REGISTRO DE COMPRAS"] = {
	"filters": [
		{
			"fieldname":"date_init",
			"label": __("From"),
			"fieldtype": "Date",
			"width": "100px"
		},
		{
			"fieldname":"date_end",
			"label": __("Hasta"),
			"fieldtype": "Date",
			"width": "100px"
		},
		{
			"fieldname":"ruc",
			"label": __("Ruc"),
			"fieldtype": "Data",
			"width": "100px"
		},
		{
			"fieldname":"serie",
			"label": __("Serie"),
			"fieldtype": "Data",
			"width": "50px"
		},
		{
			"fieldname":"numero",
			"label": __("Número"),
			"fieldtype": "Data",
			"width": "50px"
		},
		{
			"fieldname":"concepto",
			"label":__("Glosa"),
			"fieldtype":"Select",
			"options":[
				"",
				"Combustible",
				"Seguros Vehiculares",
				"Repuestos y Mant. al crédito",
				"Repuestos y Mant. al contado",
				"Cochera para vehículos",
				"Papeletas vehiculares",
				"Serv. Vigilancia",
				"Serv. Luz / Agua",
				"Serv. Tecnologicos",
				"Serv. Asesorias",
				"Alquiler Transporte de terceros",
				"Sueldos al mes al personal",
				"Beneficios sociales al personal",
				"Seguro para personal",
				"Alquiler Locales",
				"Transacción / Compensaciones",
				"Devolución clientes",
				"Transferencia a las cajas agencias",
				"Compras abastecimiento interno",
				"Compras a Solicitud",
				"Impuestos y tributos",
				"Otros gastos de gestión",
				"Pago a Concesionarios",
				"Prestamos bancarios",
				"Multas / Sunafil",
				"Gasto de Construcción y Mantenimiento de locales",
				"Compra de Vehículos",
				"Compra de Terreno",
				"Préstamo a Accionistas",
				"Gasto De Gerencia",
				"Detracción",
				"Pagos Comercial",
			],
			"width": "100px"
		},
		{
			"fieldname":"moneda",
			"label":__("Moneda"),
			"fieldtype":"Select",
			"options":["","PEN", "USD"],
			"width": "50px"
		}


	]
};
