# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from itertools import groupby

import frappe
from frappe.model.db_query import DatabaseQuery
from frappe.utils import flt, cint

class ApartadoDescansoMedico(Document):
	pass



@frappe.whitelist()
def get_data():
	items = frappe.db.sql("""
		SELECT
			adm.name AS nameDocument,
			tc.name AS nameDocumentTable,
			adm.nombre_completo AS fullName,
			adm.cantidad_de_llamadas AS qtyCalls,
			adm.fecha_de_fin_de_dm AS endDate
		FROM
			`tabApartado Descanso Medico` adm
		LEFT JOIN
			`tabtable_control` tc ON adm.name = tc.parent
		WHERE
			adm.seguimiento = 'CON SEGUIMIENTO'
	""", as_dict=1)

	if len(items) == 0:
		return {
			"data":[]
		}

	grupos = {}
	for key, group in groupby(items, key=lambda x: x['nameDocument']):
		grupos[key] = list(group)

	nuevo_objeto = {
		"data":[]
	}

	for key, values in grupos.items():
		contador = 0
		objeto = {
			"nameDocument": key,
			"qtyCallsOpen": contador,
			"fullName": "",
			"endDate": "",
			"qtyCalls": ""
		}
		for value in values:
			if value["nameDocumentTable"] is not None:
				contador += 1
			objeto["fullName"] = value["fullName"]
			objeto["endDate"] = value["endDate"]
			objeto["qtyCalls"] = value["qtyCalls"]
		objeto["qtyCallsOpen"] = contador
		nuevo_objeto["data"].append(objeto)
	return nuevo_objeto

