# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from erpnext.permissions import check_cortes_permissions

class BonoNacional(Document):
	def validate(self):
		check_cortes_permissions()
	def on_trash(self):
		check_cortes_permissions()
	def on_cancel(self):
		check_cortes_permissions()
	def before_submit(self):
		check_cortes_permissions()
	def before_update(self):
		check_cortes_permissions()
	def before_insert(self):
		check_cortes_permissions()
