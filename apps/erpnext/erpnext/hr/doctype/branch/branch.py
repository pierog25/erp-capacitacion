# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.model.document import Document
from frappe.model.db_query import DatabaseQuery
from frappe.utils import flt, cint
from itertools import groupby

class Branch(Document):
	pass

@frappe.whitelist()
def get_available_branches():
	lista_agencias = frappe.db.sql("""
		SELECT
			adm.name AS nameDocument
		FROM
			`tabBranch` adm
		WHERE
			adm.estado_de_sucursal = 1
	""", as_dict=1)

	name_agencias_costo = frappe.db.sql("""
		SELECT
			adm.name AS nameDocument
		FROM
			`tabBranch` adm
		WHERE
			adm.centro_de_costos_por_agencia = 1
	""", as_dict=1)

	if len(name_agencias_costo) >= 0:
		grupos = {}
		for key, group in groupby(name_agencias_costo, key=lambda x: x['nameDocument']):
			grupos[key] = list(group)
		return grupos
		agencias_no_disponibles = frappe.db.sql("""
			SELECT
				adm.agencia AS nameBranch
			FROM
				`tabTabla Costo por Agencia` adm
			WHERE
				adm.parent IN """+name_agencias_costo+"""
		""", as_dict=1)

		return agencias_no_disponibles

	return name_agencias_costo