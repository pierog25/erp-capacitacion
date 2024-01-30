# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from erpnext.controllers.trends	import get_columns,get_data
import requests

def execute(filters=None):
	if not filters:
		filters ={}
		sales_invoice = requests.get("https://recursoshumanos.shalom.com.pe/api/sales-invoice-trends/2022/Perfil de POS")
		sales_invoice = sales_invoice.json()
		return sales_invoice.get("columns"), sales_invoice.get("data")
	else:
		sales_invoice = requests.get("https://recursoshumanos.shalom.com.pe/api/sales-invoice-trends/"+filters.get("year")+"/"+filters.get("basado_end"))
		sales_invoice = sales_invoice.json()
		return sales_invoice.get("columns"), sales_invoice.get("data")
