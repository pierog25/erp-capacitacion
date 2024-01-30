# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
import requests

def execute(filters=None):
	columns, data = [], []
	payments = requests.post("https://recursoshumanos.shalom.com.pe/api/get-payment-request-report", json = filters)
	payments = payments.json()
	return get_columns(), payments.get("data")


def get_columns():
	columns = [
		{
			'label': "FECHA",
			'fieldname': 'fecha',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "DOC",
			'fieldname': 'docuno',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "SERIE",
			'fieldname': 'serie',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "NUMERO",
			'fieldname': 'numero',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "DOC",
			'fieldname': 'ructipo',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "NUMERO",
			'fieldname': 'ruc',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "RAZON SOCIAL",
			'fieldname': 'razonsocial',
			'fieldtype': 'Data',
			'width': 200
		},
		{
			'label': "TOTAL",
			'fieldname': 'total',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "MONEDA",
			'fieldname': 'moneda',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "TC",
			'fieldname': 'tipodecambio',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "GLOSA",
			'fieldname': 'concepto',
			'fieldtype': 'Data',
			'width': 200
		},

	]
	return columns