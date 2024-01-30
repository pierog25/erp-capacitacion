
import requests
import json
import datetime
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


@frappe.whitelist(allow_guest=True)
def searchDoctype(data=None):

    responseData = dict()

    try:
        if data is None or data== "":
            responseData["msn"] = 'Error. ingresar data.'
            responseData["status"] = False
            return responseData

        data_search = frappe.db.sql("select * from `tabDriver` where docstatus!=2",as_dict=True)

        if len(data_search)>0:
            responseData["msn"] = 'Driver.'
            responseData["data"] = data_search
            responseData["status"] = True
        else:
            responseData["msn"] = 'No hay registros.'
            responseData["status"] = False

        return responseData

    except Exception as e:
        responseData["msn"] = e
        responseData["status"] = False
        return responseData