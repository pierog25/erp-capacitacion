# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import requests

def execute(filters=None):
	columns, data = [], []
	supervisor = requests.post("https://horario-salida-qa-erp.shalom.com.pe/api/reporte/reporte_supervisores", json = filters)
	supervisor = supervisor.json()

	if "data" in supervisor:
		return get_columns(), supervisor.get("data")


def get_columns():
	columns = [
		{
			'label': "NOMBRE SUPERVISOR",
			'fieldname': 'nombre_supervisor',
			'fieldtype': 'Data',
			'width': 500
		},
		{
			'label': "TOTAL DE PROGRAMACIONES",
			'fieldname': 'total_programaciones',
			'fieldtype': 'Float',
			'width': 180
		},
		{
			'label': "INFORME ADJUNTO",
			'fieldname': 'informe_adjunto',
			'fieldtype': 'Float',
			'width': 180
		},
		{
			'label': "INFORMES APROBADOS",
			'fieldname': 'aprobados',
			'fieldtype': 'Float',
			'width': 180
		},
		{
			'label': "% DE EFICIENCIA",
			'fieldname': 'eficiencia',
			'fieldtype': 'Data',
			'width': 170
		}
	]

	return columns