# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from erpnext.permissions import check_cortes_permissions

class SolicituddeViaticosTemporales(Document):
	def on_cancel(self):
		check_cortes_permissions()
	def on_submit(self):
		check_cortes_permissions()
	def on_update(self):
		check_cortes_permissions()
	pass
