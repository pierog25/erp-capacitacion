from frappe.utils.pdf import get_pdf
import frappe
import pdfkit
import jinja2
import os
from datetime import datetime
from datetime import date

@frappe.whitelist()
def get_cts_masivo(branch=None, department=None, month=None, year=None):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'cts_massive.html')
    route_template = filename
    name_template = route_template.split('/')[-1]
    route_template = route_template.replace(name_template, '')

    filters = {
        'mes': month,
        'año': year
    }
    if department is not None:
        filters["departamento"] = department

    if branch != "TODOS":
        filters["agencia"] = branch

    data_cts = frappe.db.get_list('Compensacion por Tiempo de Servicios', filters=filters, fields=['*'], as_list=False)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(route_template))
    template = env.get_template(name_template)
    my_dict = {'data_cts' : data_cts}
    html = template.render(my_dict)
    frappe.local.response.filename = "cts.pdf"
    frappe.local.response.filecontent = get_pdf(html, {"orientation": "Landscape","page-size":"A4"})
    frappe.local.response.type = "pdf"
    return branch
