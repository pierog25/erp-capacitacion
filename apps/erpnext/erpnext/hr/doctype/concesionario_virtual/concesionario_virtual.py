# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
import requests

class ConcesionarioVirtual(Document):
	
	def db_insert(self):
		pass

	def load_from_db(self):
		pass

	def db_update(self):
		pass

	def get_count(args):
		data = requests.get("https://qawebservices.shalom.com.pe/empresarial/terminal/concesionarias")
		data = data.json()
		return len(data)

	def get_list(self, args):

		data = requests.get("https://qawebservices.shalom.com.pe/empresarial/terminal/concesionarias")
		data = data.json()
		return data
