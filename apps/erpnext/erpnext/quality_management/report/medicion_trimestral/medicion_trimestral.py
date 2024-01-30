# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, _dict
from erpnext import get_company_currency, get_default_company
from erpnext.accounts.report.sales_register.sales_register import get_mode_of_payments
import requests
from collections import defaultdict

def execute(filters=None):
    columns = get_columns()
    data = get_data_supervisores(filters)

    for row in data:
        row['class'] = 'align-center-column-report'

    return columns, data


@frappe.whitelist(allow_guest=True)
def get_data_supervisores(filters):

    data_programacion = frappe.db.sql(
        """
        SELECT
            pro.fecha_programada, pro.supervisor as nombre_supervisor, pro.aprobación_del_informe
        FROM
            `tabProgramacion de Supervisores` pro
        WHERE
            pro.aprobación_del_informe = 'Aprobado' AND pro.fecha_programada >= %(date_init)s AND pro.fecha_programada <= %(date_end)s
        """.format(), filters ,  as_dict=1)

    data_zona = frappe.db.sql(
        """
        SELECT
            zn.supervisor as nombre_supervisor, zn.name , tabsuc.agencias , zn.nombre_supervisor as supervisor
        FROM
            `tabZonas Nacional` zn
            LEFT JOIN `tabTabla de Sucursales` tabsuc ON (zn.name = tabsuc.parent)
            """.format(
            ), as_dict=1)

    zona_nacional = {}
    resultados_zona = {}
    programacion_supervisor = {}
    resultados = {}


    for zona in data_zona:
        supervisor = zona["nombre_supervisor"]
        if supervisor in zona_nacional:
            zona_nacional[supervisor].append(zona)
        else:
            zona_nacional[supervisor] = [zona]

    for supervisor, progras in zona_nacional.items():
        lista_items_zona = zona_nacional.get(supervisor, [])
        nombre = zona_nacional[supervisor][0]["supervisor"]  # Suponiendo que el nombre del supervisor es el mismo para todas las entradas

        cantidad_items_zona = len(lista_items_zona)
        resultados_zona[supervisor] = {"cantidad_zona": cantidad_items_zona, "supervisor": nombre}

    for progra in data_programacion:
        supervisor = progra["nombre_supervisor"]
        if supervisor in programacion_supervisor:
            programacion_supervisor[supervisor].append(progra)
        else:
            programacion_supervisor[supervisor] = [progra]

    for supervisor, progras in programacion_supervisor.items():
        lista_items = programacion_supervisor.get(supervisor, [])
        cantidad_items = len(lista_items)
        resultados[supervisor] = {"cantidad_progra": cantidad_items}

    valores = {}

    for supervisorItem, item in resultados_zona.items():
        supervisor = supervisorItem
        zonas_totales = item["cantidad_zona"]

        # Verificar si el supervisor existe en resultados
        if supervisor in resultados:
            programaciones = resultados[supervisor]["cantidad_progra"]
        else:
            programaciones = 0

        eficiencia = (programaciones * 100) / zonas_totales
        eficiencia = int(eficiencia)
        valores[supervisor] = {"supervisores": item["supervisor"], "cantidad_sucursal": zonas_totales, "trimestre": programaciones , "efectividad" : str(eficiencia) + "%"}

    result = []
    for supervisor, valores in valores.items():
        result.append(valores)

    return result


def get_columns():
    columns = [
        {
            'label': "SUPERVISORES",
            'fieldname': 'supervisores',
            'fieldtype': 'Data',
            'width': 400
        },
        {
            'label': "TRIMESTRE",
            'fieldname': 'trimestre',
            'fieldtype': 'Data',
            'width': 300,
        },
        {
            'label': "CANT. SUCURSAL",
            'fieldname': 'cantidad_sucursal',
            'fieldtype': 'Data',
            'width': 300
        },
        {
            'label': "EFECTIVIDAD",
            'fieldname': 'efectividad',
            'fieldtype': 'Data',
            'width': 200
        },
    ]
    return columns
