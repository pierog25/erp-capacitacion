# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import requests

def execute(filters=None):
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
            'width': 100
        },
        {
            'label': "INFORME ADJUNTO",
            'fieldname': 'informe_adjunto',
            'fieldtype': 'Float',
            'width': 100
        },
        {
            'label': "% DE EFICIENCIA",
            'fieldname': 'eficiencia',
            'fieldtype': 'Data',
            'width': 100
        }

    ]
    programacion_supervisores = requests.get("https://horario-salida-qa-erp.shalom.com.pe/api/reporte/reporte_supervisores")
    programacion_supervisores = programacion_supervisores.json()

    return columns, programacion_supervisores



# payments = requests.post("https://recursoshumanos.shalom.com.pe/api/get-payment-request-report", json = filters)
# payments = payments.json()
# return get_columns(), payments.get("data")


def get_columns():
    columns = [
        {
            'label': "NOMBRE SUPERVISOR",
            'fieldname': 'nombre_supervisor',
            'fieldtype': 'Data',
            'width': 100
        },
        {
            'label': "TOTAL DE PROGRAMACIONES",
            'fieldname': 'total_programaciones',
            'fieldtype': 'Data',
            'width': 100
        },
        {
            'label': "INFORME ADJUNTO",
            'fieldname': 'informe_adjunto',
            'fieldtype': 'Data',
            'width': 100
        },
        {
            'label': "% DE EFICIENCIA",
            'fieldname': 'eficiencia',
            'fieldtype': 'Data',
            'width': 100
        }

    ]
    return columns