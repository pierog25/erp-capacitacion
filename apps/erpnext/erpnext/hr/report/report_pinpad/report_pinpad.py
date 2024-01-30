# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import requests

def execute(filters=None):
	columns, data = [], []
	supervisor = requests.get("https://sysqa.shalomcontrol.com/reports/operatividad_finanzas/"+filters.get("date_init")+"/"+filters.get("date_end"))
	supervisor = supervisor.json()
	return get_columns(), supervisor

def get_columns():
	columns = [
		{
			'label': "CODIGO DE AGENCIA",
			'fieldname': 'ter_id',
			'fieldtype': 'Data',
			'width': 150
		},
		{
			'label': "AGENCIA",
			'fieldname': 'ter_nombre',
			'fieldtype': 'Data',
			'width': 180
		},
		{
			'label': "CODIGO DE COMERCIO",
			'fieldname': 'codigo_comercio',
			'fieldtype': 'Data',
			'width': 180
		},
		{
			'label': "CANTIDAD DE PINPADS",
			'fieldname': 'qty_pinpad',
			'fieldtype': 'Data',
			'width': 180
		},
		{
			'label': "CANTIDAD DE OPERACIONES EXITOSAS",
			'fieldname': 'qty_operaciones',
			'fieldtype': 'Int',
			'width': 170
		},
		{
			'label': "CANTIDAD EN SOLES",
			'fieldname': 'amount_operaciones',
			'fieldtype': 'Float',
			'width': 170
		},
		{
			'label': "CANTIDAD DE OPERACIONES ANULADAS",
			'fieldname': 'qty_anuladas',
			'fieldtype': 'Int',
			'width': 170
		},
		{
			'label': "MONTO DE OPERACIONES ANULADAS",
			'fieldname': 'amount_anuladas',
			'fieldtype': 'Int',
			'width': 170
		}
	]

	return columns