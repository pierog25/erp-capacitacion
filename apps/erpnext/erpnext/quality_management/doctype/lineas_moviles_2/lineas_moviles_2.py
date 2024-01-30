# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Lineasmoviles2(Document):
	pass

@frappe.whitelist()
def lineas_moviles_query(user):
	if user:
		if user == "41918452@shalomcontrol.com":
			return ""
		else:
			search_designer = frappe.db.get_list('Employee',
				 filters={
					 'user_id': user
				 },
				 fields=['department', 'name','branch'],
				 as_list=True
			 )

			if search_designer:
				response_branch = search_designer[0][2]
				return "(`tabLineas moviles 2`.ubicacion = '{ubicacion}')".format(ubicacion=response_branch)
			else:
				return "(`tabLineas moviles 2`.ubicacion = '{ubicacion}')".format(ubicacion="PRUEBA")

	else:
		return ""

@frappe.whitelist()
def lineas_moviles_query_per_departmen(user):
	if user:
		search_designer = frappe.db.get_list('Employee',
			 filters={
				 'user_id': user
			 },
			 fields=['department', 'name','branch'],
			 as_list=True
		 )

		if search_designer:
			response_department = search_designer[0][0]
			response_branch = search_designer[0][2]
			if response_department == "SSOMA - SE":
				return ""
			else:
				return "(`tabLineas moviles 2`.ubicacion = '{ubicacion}')".format(ubicacion=response_branch)
		else:
			return "(`tabLineas moviles 2`.ubicacion = '{ubicacion}')".format(ubicacion="PRUEBA")
	else:
		return ""