# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe

import requests
from requests.adapters import HTTPAdapter, Retry

def execute(filters=None):
	columns, data = [], []
	session = requests.Session()
	retry = Retry(connect=3, backoff_factor=0.5)
	adapter = HTTPAdapter(max_retries=retry)
	session.mount('http://', adapter)
	session.mount('https://', adapter)
	supervisor = session.post("https://horario-salida-qa-erp.shalom.com.pe/api/supervicion-almacen-reporte", json = filters)
	supervisor = supervisor.json()

	if "data" in supervisor:
		return get_columns() , supervisor.get("data")

def get_columns():
	columns = [
		{
			'label': "ZONA NACIONAL",
			'fieldname': 'zona_nacional',
			'fieldtype': 'Data',
			'width': 300
		},
		{
			'label': "SUPERVISOR",
			'fieldname': 'supervisor',
			'fieldtype': 'Data',
			'width': 300
		},
		{
			'label': "AGENCIA",
			'fieldname': 'branch',
			'fieldtype': 'Data',
			'width': 300 ,
		},
		{
			'label': "TIPO DE AGENCIA",
			'fieldname': 'tipo_agencia',
			'fieldtype': 'Data',
			'width': 300 ,
		},
		{
			'label': "TIPO DE ALMACEN",
			'fieldname': 'tipo_almacen',
			'fieldtype': 'Data',
			'width': 300
		},
		{
			'label': "CATEGORIA",
			'fieldname': 'categoria',
			'fieldtype': 'Data',
			'width': 300
		},
		{
			'label': "CREADO POR",
			'fieldname': 'nombre_completo',
			'fieldtype': 'Data',
			'width': 300
		},
		{
			'label': "ESTADO",
			'fieldname': 'status',
			'fieldtype': 'Data',
			'width': 300
		},
		{
			'label': "CHECK",
			'fieldname': 'check',
			'fieldtype': 'Check',
			'width': 300
		}

	]

	return columns