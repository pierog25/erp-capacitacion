# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
import requests

def execute(filters=None):
	columns, data = [], []
	supervisor = requests.get("https://sysqa.shalomcontrol.com/reports/operatividad_finanzas_comodines/"+filters.get("date_init")+"/"+filters.get("date_end"))
	supervisor = supervisor.json()
	return get_columns(), supervisor

def get_columns():
	columns = [
		{
			'label': "CODIGO DE AGENCIA",
			'fieldname': 'ter_codigo',
			'fieldtype': 'Data',
			'width': 150
		},
		{
			'label': "AGENCIA",
			'fieldname': 'agencia',
			'fieldtype': 'Data',
			'width': 180
		},
		{
			'label': "TOPE DE CAJA",
			'fieldname': 'tope_de_caja',
			'fieldtype': 'Data',
			'width': 180
		},
		{
			'label': "TOPE GASTO DIRECTO",
			'fieldname': 'tope_de_gasto_directo',
			'fieldtype': 'Data',
			'width': 180
		},
		{
			'label': "GASTOS DIRECTOS USADOS",
			'fieldname': 'tope_de_gasto_directo_use',
			'fieldtype': 'Data',
			'width': 170
		},
		{
			'label': "TOPE DE GASTO INDIRECTO",
			'fieldname': 'tope_de_gasto_indirecto',
			'fieldtype': 'Data',
			'width': 170
		},
		{
			'label': "GASTO INDIRECTO USADO",
			'fieldname': 'tope_de_gasto_indirecto_use',
			'fieldtype': 'Data',
			'width': 170
		},
		{
			'label': "COMODINES",
			'fieldname': 'comodines',
			'fieldtype': 'Data',
			'width': 170
		},
		{
			'label': "COMODINES USADOS",
			'fieldname': 'comodines_use',
			'fieldtype': 'Data',
			'width': 170
		}
	]

	return columns