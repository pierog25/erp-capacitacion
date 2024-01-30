# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

import requests
from requests.adapters import HTTPAdapter, Retry


def execute(filters=None):
	columns, data = [], []
	supervisor = requests.post("https://sysqa.shalomcontrol.com/reports/operatividad_finanzas_el_sebas", json = filters)
	supervisor = supervisor.json()

	if "data" in supervisor:
		return get_columns(), supervisor.get("data")

def get_columns():
	columns = [
		{
			'label': "CODIGO DE AGENCIA",
			'fieldname': 'ter_id',
			'fieldtype': 'Data',
			'width': 300
		},
		{
			'label': "AGENCIA",
			'fieldname': 'ter_nombre',
			'fieldtype': 'Data',
			'width': 300
		},
		{
			'label': "CODIGO DE COMERCIO",
			'fieldname': 'codigo_comercio',
			'fieldtype': 'Data',
			'width': 300 ,
		},
		{
			'label': "CANTIDAD DE PINPADS",
			'fieldname': 'qty_pinpad',
			'fieldtype': 'Data',
			'width': 300 ,
		},
		{
			'label': "CANTIDAD DE OPERACIONES EXITOSAS",
			'fieldname': 'qty_operaciones',
			'fieldtype': 'Data',
			'width': 300
		},
		{
			'label': "CANTIDAD EN SOLES",
			'fieldname': 'amount_operaciones',
			'fieldtype': 'Data',
			'width': 300
		},
		{
			'label': "CANTIDAD DE OPERACIONES ANULADAS",
			'fieldname': 'qty_anuladas',
			'fieldtype': 'Data',
			'width': 300
		},
		{
			'label': "MONTO DE OPERACIONES ANULADAS",
			'fieldname': 'amount_anuladas',
			'fieldtype': 'Data',
			'width': 300
		},
	]

	return columns