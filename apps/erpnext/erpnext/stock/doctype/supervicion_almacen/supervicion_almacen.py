# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import frappe
from datetime import datetime

class SupervicionAlmacen(Document):
	pass

@frappe.whitelist()
def get_courts(month=None, year=None, current_date=None):
	items = frappe.db.sql("""
		SELECT
			ct.dia_inicio AS dateInit,
			ct.dia_final AS dateEnd
		FROM
			`tabCortes` ct
		WHERE
			ct.mes = '"""+month+"""' and ct.año = '"""+year+"""'
	""", as_dict=1)

	if len(items) == 0:
		return True

	current_day = datetime.strptime(current_date, "%Y-%m-%d")
	current_date_date = current_day.date()

	if items[0].dateInit <= current_date_date <= items[0].dateEnd:
		return True
	else:
		return False

@frappe.whitelist()
def get_employee(id_employee=None):
	items = frappe.db.sql("""
		SELECT
			emp.nombre_completo AS name_employee,
			emp.designation AS designation,
			emp.branch AS branch,
			emp.passport_number AS passport_number
		FROM
			`tabEmployee` emp
		WHERE
			emp.name = '"""+id_employee+"""'
	""", as_dict=1)

	return items
