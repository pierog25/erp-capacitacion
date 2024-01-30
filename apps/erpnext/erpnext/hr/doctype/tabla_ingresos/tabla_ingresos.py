# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from erpnext.permissions import check_cortes_permissions

class tabla_ingresos(Document):
	def validate(self):
		check_cortes_permissions()
	def before_insert(self):
		check_cortes_permissions()
