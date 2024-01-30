from frappe.utils.pdf import get_pdf
import frappe
import pdfkit
import jinja2
import os
from frappe.utils import getdate, nowdate
from frappe.utils import cstr, get_datetime, formatdate
from datetime import datetime
from datetime import date
from itertools import groupby
from operator import itemgetter
import copy
import requests
import numpy as np
import json
from frappe.utils.nestedset import get_root_of
from erpnext.accounts.doctype.pos_profile.pos_profile import get_item_groups
from erpnext.accounts.doctype.pos_invoice.pos_invoice import get_stock_availability
from frappe.model.document import Document

@frappe.whitelist(allow_guest=True)
def insert_marking_employee():

    dataSend = frappe.form_dict.sendData
    values = json.loads(dataSend)

    sql_insert_query = f"""
        INSERT INTO `tabEmployee Checkin` (
        `name`, 
        `employee`, 
        `urlimagen`, 
        `log_type`, 
        `time` ,
        `coordenadas` ,
        `urlimagen2`, 
        `fecha_de_consolidado`, 
        `sucursal`, 
        `employee_name`, 
        `departamento`,
        `creation`,
        `modified`,
        `offline`
        )
        VALUES (
        '{values.get("name")}', 
        '{values.get("employee")}', 
        '{values.get("urlimagen")}',
        '{values.get("log_type")}',
        '{values.get("time")}',
        '{values.get("coordenadas")}',
        '{values.get("urlimagen2")}',
        '{values.get("fecha_de_consolidado")}',
        '{values.get("sucursal")}',
        '{values.get("employee_name")}',
        '{values.get("departamento")}',
        '{values.get("creation")}',
        '{values.get("modified")}',
        '{values.get("offline")}'
        )
    """

    responseData = dict()

    try:

        data = frappe.db.sql(sql_insert_query)
        frappe.db.commit()
        responseData["msn"] = "Exito"
        responseData["status"] = True

    except Exception as e:

        responseData["msn"] = e
        responseData["status"] = False

    frappe.response['response'] =  responseData


@frappe.whitelist(allow_guest=True)
def insert_doctype():
    data = frappe.form_dict.sendData
    doctype = frappe.form_dict.doctype
    dataSend = json.loads(data)

    columns = ", ".join([f"`{key}`" for key in dataSend.keys()])
    placeholders = ", ".join([f"%({key})s" for key in dataSend.keys()])
    sql = f"""INSERT INTO `{doctype}` ({columns}) VALUES ({placeholders})"""

    responseData = dict()

    try:

        data = frappe.db.sql(sql, values=dataSend)
        frappe.db.commit()
        responseData["msn"] = "Exito"
        responseData["status"] = True

    except Exception as e:

        responseData["msn"] = e
        responseData["status"] = False

    frappe.response['response'] =  responseData


@frappe.whitelist(allow_guest=True)
def update_massive_register():

    json_data = frappe.local.form_dict
    registros = frappe.get_all(json_data["doctype"], filters={"branch": json_data["branch"]})
    for registro in registros:
        doc = frappe.get_doc(json_data["doctype"], registro.name)
        doc.categoria_sucursal = json_data["categoria"]
        doc.save()

    return "Se actualizaron los empleados"

@frappe.whitelist()
def get_items_test():
    start = 0
    page_length = 40
    price_list = "Venta estándar"
    item_group = "Todos los grupos de artículos"
    search_term = ""
    pos_profile = "JAUJA"
    packaging = "false"
    warehouse, hide_unavailable_items = frappe.db.get_value(
        'POS Profile', pos_profile, ['warehouse', 'hide_unavailable_items'])

    lft, rgt = frappe.db.get_value('Item Group', item_group, ['lft', 'rgt'])
    condition = get_conditions(search_term)
    condition += get_item_group_condition(pos_profile)
    bin_join_selection, bin_join_condition, packaging_condition = "", "", ""


    items_data = frappe.db.sql("""
		SELECT
			item.name AS item_code,
			item.item_name,
			item.description,
			item.stock_uom,
			item.image AS item_image,
			item.embalaje AS item_embalaje,
			substring(item.item_code,1,6) AS substring_embalaje,
			item.is_stock_item,
			item.posicion
		FROM
			`tabItem` item {bin_join_selection}
		WHERE
			item.disabled = 0
			AND item.has_variants = 0
			AND item.is_sales_item = 1
			AND item.is_fixed_asset = 0
			AND substring(item.item_code,1,6) != 'SEREMB'
			AND item.item_group in (SELECT name FROM `tabItem Group` WHERE lft >= {lft} AND rgt <= {rgt})
			AND {condition}
			{bin_join_condition}
		ORDER BY
			item.name asc
		LIMIT
				{start}, {page_length}"""
        .format(
        start=start,
        page_length=page_length,
        lft=lft,
        rgt=rgt,
        condition=condition,
        bin_join_selection=bin_join_selection,
        bin_join_condition=bin_join_condition
    ), {'warehouse': warehouse}, as_dict=1)

    return items_data


@frappe.whitelist()
def get_report():

    productos = [
        {
            "descripcion":"PRUEBA",
            "importe":15,
            "precioUnitario":15,
            "cantidad":1
        }
    ]

    datos = {
        "tipoComprobante":'boleta',
        "entidadPaga":"75013406",
        "razonSocial": "GIAN PIERO VILLANUEVA GASTELLO",
        "productos":productos,
        "cdn": "ACC-PSINV-2023-00003",
        "userDni":'70503353',
        "medio_pago": 'CONTADO'
    }

    response = requests.post('https://fileserver.shalomcontrol.com/api/registrar-comprobante-erp', data=datos)

    return response


@frappe.whitelist()
def search_for_serial_or_batch_or_barcode_number(search_value):
    # search barcode no
    barcode_data = frappe.db.get_value('Item Barcode', {'barcode': search_value}, ['barcode', 'parent as item_code'], as_dict=True)
    if barcode_data:
        return barcode_data

    # search serial no
    serial_no_data = frappe.db.get_value('Serial No', search_value, ['name as serial_no', 'item_code'], as_dict=True)
    if serial_no_data:
        return serial_no_data

    # search batch no
    batch_no_data = frappe.db.get_value('Batch', search_value, ['name as batch_no', 'item as item_code'], as_dict=True)
    if batch_no_data:
        return batch_no_data

    return {}

@frappe.whitelist()
def search_by_term(search_term, warehouse, price_list):
    result = search_for_serial_or_batch_or_barcode_number(search_term) or {}

    item_code = result.get("item_code") or search_term
    serial_no = result.get("serial_no") or ""
    batch_no = result.get("batch_no") or ""
    barcode = result.get("barcode") or ""

    if result:
        item_info = frappe.db.get_value("Item", item_code,
                                        ["name as item_code", "item_name", "description", "stock_uom", "image as item_image", "is_stock_item"],
                                        as_dict=1)

        item_stock_qty = get_stock_availability(item_code, warehouse)
        price_list_rate, currency = frappe.db.get_value('Item Price', {
            'price_list': price_list,
            'item_code': item_code
        }, ["price_list_rate", "currency"]) or [None, None]

        item_info.update({
            'serial_no': serial_no,
            'batch_no': batch_no,
            'barcode': barcode,
            'price_list_rate': price_list_rate,
            'currency': currency,
            'actual_qty': item_stock_qty
        })

        return {'items': [item_info]}

@frappe.whitelist()
def get_conditions(search_term):
    condition = "("
    condition += """item.name like {search_term}
		or item.item_name like {search_term}""".format(search_term=frappe.db.escape('%' + search_term + '%'))
    condition += add_search_fields_condition(search_term)
    condition += ")"

    return condition

@frappe.whitelist()
def add_search_fields_condition(search_term):
    condition = ''
    search_fields = frappe.get_all('POS Search Fields', fields = ['fieldname'])
    if search_fields:
        for field in search_fields:
            condition += " or item.`{0}` like {1}".format(field['fieldname'], frappe.db.escape('%' + search_term + '%'))
    return condition

@frappe.whitelist()
def get_item_group_condition(pos_profile):
    cond = "and 1=1"
    item_groups = get_item_groups(pos_profile)
    if item_groups:
        cond = "and item.item_group in (%s)"%(', '.join(['%s']*len(item_groups)))

    return cond % tuple(item_groups)

@frappe.whitelist()
def filter_service_items(items):
    for item in items:
        if not item['is_stock_item']:
            if not frappe.db.exists('Product Bundle', item['item_code']):
                items.remove(item)

    return items

@frappe.whitelist()
def get_items():

    start = 0
    page_length = 40
    price_list = "Venta estándar"
    item_group = "Todos los grupos de artículos"
    pos_profile = "JAUJA"
    packaging = "true"
    search_term = ""

    warehouse, hide_unavailable_items = frappe.db.get_value(
        'POS Profile', pos_profile, ['warehouse', 'hide_unavailable_items'])

    result = []

    if search_term:
        result = search_by_term(search_term, warehouse, price_list) or []
        if result:
            return result

    if not frappe.db.exists('Item Group', item_group):
        item_group = get_root_of('Item Group')

    condition = get_conditions(search_term)
    condition += get_item_group_condition(pos_profile)

    lft, rgt = frappe.db.get_value('Item Group', item_group, ['lft', 'rgt'])

    bin_join_selection, bin_join_condition, packaging_condition = "", "", ""
    if hide_unavailable_items:
        bin_join_selection = ", `tabBin` bin"
        bin_join_condition = "AND bin.warehouse = %(warehouse)s AND bin.item_code = item.name AND bin.actual_qty > 0 "
    if packaging == "true":
        items_data = frappe.db.sql("""
		SELECT
			item.name AS item_code,
			item.item_name,
			item.description,
			item.stock_uom,
			item.image AS item_image,
			item.embalaje AS item_embalaje,
			substring(item.item_code,1,6) AS substring_embalaje,
			item.is_stock_item
		FROM
			`tabItem` item
		WHERE
			substring(item.item_code,1,6) = 'SEREMB'
		"""
                                   , {'warehouse': warehouse}, as_dict=1)
    else:
        items_data = frappe.db.sql("""
		SELECT
			item.name AS item_code,
			item.item_name,
			item.description,
			item.stock_uom,
			item.image AS item_image,
			item.embalaje AS item_embalaje,
			substring(item.item_code,1,6) AS substring_embalaje,
			item.is_stock_item
		FROM
			`tabItem` item {bin_join_selection}
		WHERE
			item.disabled = 0
			AND item.has_variants = 0
			AND item.is_sales_item = 1
			AND item.is_fixed_asset = 0
			AND substring(item.item_code,1,6) != 'SEREMB'
			AND item.item_group in (SELECT name FROM `tabItem Group` WHERE lft >= {lft} AND rgt <= {rgt})
			AND {condition}
			{bin_join_condition}
		ORDER BY
			item.name asc
		LIMIT
				{start}, {page_length}"""
            .format(
            start=start,
            page_length=page_length,
            lft=lft,
            rgt=rgt,
            condition=condition,
            bin_join_selection=bin_join_selection,
            bin_join_condition=bin_join_condition
        ), {'warehouse': warehouse}, as_dict=1)

    if items_data:
        items_data = filter_service_items(items_data)
        items = [d.item_code for d in items_data]
        item_prices_data = frappe.get_all("Item Price",
                                          fields = ["item_code", "price_list_rate", "currency"],
                                          filters = {'price_list': price_list, 'item_code': ['in', items]})

        item_prices = {}
        for d in item_prices_data:
            item_prices[d.item_code] = d

        for item in items_data:
            item_code = item.item_code
            item_price = item_prices.get(item_code) or {}
            item_stock_qty = get_stock_availability(item_code, warehouse)

            row = {}
            row.update(item)
            row.update({
                'price_list_rate': item_price.get('price_list_rate'),
                'currency': item_price.get('currency'),
                'actual_qty': item_stock_qty,
            })
            result.append(row)

    sorted_data = sorted(result, key=lambda x: x["price_list_rate"])

    return {'items': sorted_data}

@frappe.whitelist()
def download_excel_attendance(head=[], only_data=[], month="", year=""):
    from frappe.utils.xlsxutils import build_xlsx_response

    data_head = [head]
    data_values = only_data
    data = data_head + data_values

    title = "Asistencia "+month+" "+year
    build_xlsx_response(data, title)

@frappe.whitelist(allow_guest=True)
def excel_attendance_cloud(year=None, month=None):
    import calendar
    import datetime
    myobj = {'month': month}
    cortes = requests.post("https://recursoshumanos.shalom.com.pe/api/courts-month", json = myobj)
    cortes = cortes.json()
    cortes = cortes.get("data")
    terminals_empresarial = requests.get("http://moradexx.shalomcontrol.com/query/get_terminals_app_markings")
    terminalJSON = {}
    terminals_empresarial = terminals_empresarial.json()
    for entry in terminals_empresarial:
        terminalJSON[entry['ter_id']] = entry

    branches = frappe.get_all("Branch", fields=['name', 'ideentificador'] , filters=[], as_list=False)
    branchesJSON = {}
    for branch in branches:
        branchesJSON[branch['name']] = str(branch["ideentificador"])
    month_map = get_month_map()
    month_str = str(month_map[month]).zfill(2)
    find_day_now = date.today()

    my_day_now = find_day_now.strftime("%Y-%m-%d")

    # Para fechas de este año
    # today = get_datetime()

    # Para fechas de otros años
    today = datetime.datetime.strptime(year+'-'+month_str+'-'+'01', "%Y-%m-%d")
    nxt_mnth = today.replace(day=28) + datetime.timedelta(days=4)
    res = nxt_mnth - datetime.timedelta(days=nxt_mnth.day)
    last_day = datetime.datetime.strptime(year+'-'+month_str+'-'+str(res.day), "%Y-%m-%d")

    final_range = calendar.monthrange(today.year, month_map[month])[1] + 1
    final_day_month = calendar.monthrange(today.year, month_map[month])[1]
    start_day_month = 1

    dates_of_month = ['{}-{}-{}'.format(today.year, month_str, r) for r in range(1, final_range)]

    array_heads_dates = []
    for day in range(1, final_range):
        daystr = str(day).zfill(2)
        timestamp = datetime.datetime.strptime(year+'-'+month_str+'-'+daystr, "%Y-%m-%d").timestamp()
        date_from_time = datetime.date.fromtimestamp(timestamp)
        d = date_from_time.strftime('%d-%b')
        array_heads_dates.append(d)

    array_head_employee = ["Codigo", "Nombre Completo", "Terminal", "Departamento", "Empresa","Calificación","Tipo Documento","N° Documento","Fecha de Ingreso Real","Fecha de Relevo","Zona","Estado"]

    final_head = array_head_employee + array_heads_dates + ["Id Sucursal"]

    length = len(dates_of_month)
    month_start, month_end = dates_of_month[0], dates_of_month[length-1]

    dates_push = []
    for k in range(start_day_month, final_day_month + 1):
        my_day = str(k).zfill(2)
        dates_push.append(year+'-'+month_str+'-'+my_day)

    holiday_sundays_list = holiday_sundays_dates()
    holiday_this_month = []
    holiday_this_month_holidays = []
    date_start_split = month_start.split('-')
    date_start_validate = date_start_split[0]+"-"+date_start_split[1]+"-0"+date_start_split[2]
    # date_start_time = datetime(int(date_start_split[0]),int(date_start_split[1]),int(date_start_split[2]))
    for this_month_holiday in holiday_sundays_list["domingos"]:
        str_holiday = str(this_month_holiday)
        if check_in_range(str_holiday, month_start, month_end):
            holiday_this_month.append(str_holiday)

    for this_month_holiday_holidays in holiday_sundays_list["feriados"]:
        str_holiday = str(this_month_holiday_holidays)
        if check_in_range(str_holiday, month_start, month_end):
            holiday_this_month_holidays.append(str_holiday)

    # doc_employees = frappe.db.get_list('Employee', fields=["name", "employee_name", "nombre_completo", "company", "branch", "department", "fecha_de_ingreso_real", "fecha_de_relevo", "status","calificacion_trabajador","place_of_issue","passport_number","zona_recursos"], as_list=False)
    doc_employees = frappe.db.sql("""
        SELECT
            emp.name, emp.employee_name, emp.nombre_completo, emp.company,
            emp.branch, emp.department, emp.fecha_de_ingreso_real, emp.fecha_de_relevo,
            emp.status, emp.calificacion_trabajador, emp.place_of_issue, emp.passport_number,
            br.zona_recursos_humanos as zona_recursos
        FROM `tabEmployee` emp 
        LEFT JOIN `tabBranch` br on emp.branch = br.name
        ORDER BY name asc
    """, values={}, as_dict=1)
    json_employee = dict()
    for employee in doc_employees:
        if employee["status"] == "Active" and employee["branch"] != "No especificado":
            json_employee[employee["name"]] = employee
        elif  employee["branch"] != "No especificado" and str(employee["fecha_de_relevo"])>=date_start_validate and str(employee["fecha_de_relevo"])<=month_end :
            json_employee[employee["name"]] = employee
        elif employee["fecha_de_relevo"] is None and (employee["status"] == "Active" or employee["status"]== "No Reportado"):
            json_employee[employee["name"]] = employee
    # values = {'start_date': month_start, 'end_date': month_end}
    # doc_attendances = frappe.db.sql(f"""SELECT employee, employee_name, attendance_date, status, leave_type FROM `tabAttendance` where company='Shalom Empresarial' AND branch!='No especificado' AND docstatus != '2' AND attendance_date >= %(start_date)s AND attendance_date <= %(end_date)s order by attendance_date asc; """, values=values, as_dict=True)
    doc_attendances = frappe.get_all("Attendance", fields=['employee', 'employee_name', 'company', 'attendance_date', 'status','estado_reporte', 'leave_type','docstatus'] , filters=[
        ["attendance_date", ">=", month_start],
        ["attendance_date", "<=", month_end],
        ["branch", "!=", "No especificado"],
        ["docstatus", "!=", 2]
    ], order_by='attendance_date asc', as_list=False)

    groups_attendance_by_employee = dict()
    doc_attendances_copy = []
    new_group = {}

    for val_attendance in doc_attendances:
        key_employee = val_attendance["employee"]
        if key_employee in json_employee:
            doc_attendances_copy.append(val_attendance)

    for key, value in groupby(doc_attendances_copy, key = itemgetter('employee')):
        for k in value:
            new_group[k["employee"]] = [k] if k["employee"] not in new_group.keys() else new_group[k["employee"]] + [k]

    copy_new_group = copy.copy(new_group)
    keys_group_employee_attendance = new_group.keys()
    key_employee = json_employee.keys()

    for key2, val_group in new_group.items():
        for val_employee in key_employee:
            if val_employee != key2:
                if val_employee not in keys_group_employee_attendance:
                    copy_new_group[val_employee] = []

    employe_list_final_group = []
    for hr_emp, val_hr in copy_new_group.items():
        group_final = []
        for r in range(start_day_month, final_day_month + 1):
            result_search = search_for_date(dates_push[r - 1], val_hr)
            count_list_hr = len(val_hr)
            if result_search[1]:
                stat = ""
                dayInit = result_search[0]["status"] if dates_push[r - 1] in cortes and result_search[0]["status"] != "" and result_search[0]["status"] is not None else result_search[0]["status"]
                if result_search[0]["docstatus"] == 1:
                    if dayInit == "On Leave":
                        if result_search[0]["leave_type"] == "VACACIONES":
                            stat = "VAC"
                        if result_search[0]["leave_type"] == "LICENCIA SIN GOCE":
                            stat = "LSG"
                        if result_search[0]["leave_type"] == "COMPENSATORIO":
                            stat = "COM"
                        if result_search[0]["leave_type"] == "LICENCIA CON GOCE":
                            stat = "LCG"
                        if result_search[0]["leave_type"] == "DESCANSO MEDICO":
                            stat = "DME"
                        if result_search[0]["leave_type"] == "PERMISO OCACIONAL":
                            stat = "L-PO"
                        if result_search[0]["leave_type"] == "SUBSIDIO":
                            stat = "LS"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR ENFERMEDAD":
                            stat = "SXE"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR MATERNIDAD":
                            stat = "SXM"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR ACCIDENTE":
                            stat = "SXA"
                        if result_search[0]["leave_type"] == "LICENCIA POR FALLECIMIENTO":
                            stat = "LXF"
                        if result_search[0]["leave_type"] == "LICENCIA POR PATERNIDAD":
                            stat = "LXP"
                    if dayInit == "Present":
                        stat = "P"
                    if dayInit == "Absent":
                        stat = "A"
                    if dayInit == "Half Day":
                        stat = "HD"
                    if dayInit == "Work From Home" or dayInit == "Marcacion Incompleta":
                        stat = "MI"
                    result_search[0]["terminal"] = json_employee[hr_emp]["branch"]
                    result_search[0]["department"] = json_employee[hr_emp]["department"]
                    result_search[0]["company"] = json_employee[hr_emp]["company"]
                    result_search[0]["nombre_completo"] = json_employee[hr_emp]["nombre_completo"]
                    result_search[0]["fecha_de_ingreso_real"] = json_employee[hr_emp]["fecha_de_ingreso_real"]
                    result_search[0]["fecha_de_relevo"] = json_employee[hr_emp]["fecha_de_relevo"]
                    result_search[0]["status"] = stat
                    result_search[0]["status_employee"] = "".join(json_employee[hr_emp]["status"])
                    result_search[0]["calificacion_trabajador"]="".join(json_employee[hr_emp]["calificacion_trabajador"])
                    result_search[0]["place_of_issue"]= json_employee[hr_emp]["place_of_issue"]
                    result_search[0]["passport_number"]="".join(json_employee[hr_emp]["passport_number"])
                    result_search[0]["zona_recursos"]=json_employee[hr_emp]["zona_recursos"]
                    group_final.append(result_search[0])
                elif result_search[0]["docstatus"] == 0:
                    stat = "NV"
                    result_search[0]["terminal"] = json_employee[hr_emp]["branch"]
                    result_search[0]["department"] = json_employee[hr_emp]["department"]
                    result_search[0]["company"] = json_employee[hr_emp]["company"]
                    result_search[0]["nombre_completo"] = json_employee[hr_emp]["nombre_completo"]
                    result_search[0]["fecha_de_ingreso_real"] = json_employee[hr_emp]["fecha_de_ingreso_real"]
                    result_search[0]["fecha_de_relevo"] = json_employee[hr_emp]["fecha_de_relevo"]
                    result_search[0]["status"] = stat
                    result_search[0]["status_employee"] = "".join(json_employee[hr_emp]["status"])
                    result_search[0]["calificacion_trabajador"]="".join(json_employee[hr_emp]["calificacion_trabajador"])
                    result_search[0]["place_of_issue"]= json_employee[hr_emp]["place_of_issue"]
                    result_search[0]["passport_number"]="".join(json_employee[hr_emp]["passport_number"])
                    result_search[0]["zona_recursos"]=json_employee[hr_emp]["zona_recursos"]
                    group_final.append(result_search[0])
            else:
                if str(json_employee[hr_emp]["fecha_de_ingreso_real"]) <= dates_push[r - 1]:
                    if json_employee[hr_emp]["status"] == 'Active':
                        if json_employee[hr_emp]["fecha_de_relevo"] is None:
                            if dates_push[r - 1] in holiday_this_month:
                                status_hr = "WO"
                            elif dates_push[r - 1] in holiday_this_month_holidays:
                                status_hr = "*H*"
                            else:
                                status_hr = "NM"
                        else:
                            if str(json_employee[hr_emp]["fecha_de_relevo"]) < dates_push[r - 1]:
                                status_hr = "C"
                            else:
                                if dates_push[r - 1] in holiday_this_month:
                                    status_hr = "WO"
                                elif dates_push[r - 1] in holiday_this_month_holidays:
                                    status_hr = "*H*"
                                else:
                                    status_hr = "NM"
                    else:
                        if str(json_employee[hr_emp]["fecha_de_relevo"]) < dates_push[r - 1]:
                            status_hr = "C"
                        else:
                            if dates_push[r - 1] in holiday_this_month:
                                status_hr = "WO"
                            elif dates_push[r - 1] in holiday_this_month_holidays:
                                status_hr = "*H*"
                            else:
                                status_hr = "NM"
                else:
                    status_hr = "C"

                not_mark = {
                    "employee": hr_emp,
                    "employee_name": json_employee[hr_emp]["employee_name"],
                    "attendance_date": dates_push[r - 1],
                    "status": status_hr,
                    "leave_type": "",
                    "terminal": json_employee[hr_emp]["branch"],
                    "department": json_employee[hr_emp]["department"],
                    "company": json_employee[hr_emp]["company"],
                    "nombre_completo": json_employee[hr_emp]["nombre_completo"],
                    "fecha_de_ingreso_real": json_employee[hr_emp]["fecha_de_ingreso_real"],
                    "fecha_de_relevo": json_employee[hr_emp]["fecha_de_relevo"],
                    "status_employee": json_employee[hr_emp]["status"],
                    "calificacion_trabajador": str(json_employee[hr_emp]["calificacion_trabajador"]),
                    "place_of_issue": json_employee[hr_emp]["place_of_issue"],
                    "passport_number": json_employee[hr_emp]["passport_number"],
                    "zona_recursos": json_employee[hr_emp]["zona_recursos"],
                }
                group_final.append(not_mark)

        groups_attendance_by_employee[hr_emp] = group_final
    array_data_excel = []
    for key_exc, insert_val_excel in groups_attendance_by_employee.items():
        # if key_exc == "HR-EMP-00753":
        #     return insert_val_excel
        if datetime.datetime.strptime(str(insert_val_excel[0]["fecha_de_ingreso_real"]), "%Y-%m-%d") >= last_day:
            continue
        array_data_dates_excel = []
        data_constant_employee = [key_exc, insert_val_excel[0]["nombre_completo"],
                                  terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])).get("nombre") if terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])) else insert_val_excel[0]["terminal"],
                                  insert_val_excel[0]["department"],
                                  insert_val_excel[0]["company"],
                                  insert_val_excel[0]["calificacion_trabajador"],
                                  insert_val_excel[0]["place_of_issue"],
                                  insert_val_excel[0]["passport_number"],
                                  insert_val_excel[0]["fecha_de_ingreso_real"],
                                  insert_val_excel[0]["fecha_de_relevo"],
                                  insert_val_excel[0]["zona_recursos"],
                                  insert_val_excel[0]["status_employee"]]
        for value_assistance in insert_val_excel:
            if str(value_assistance["attendance_date"]) <= str(my_day_now) or value_assistance["status"] != "":
                array_data_dates_excel.append(value_assistance["status"])
            else:
                array_data_dates_excel.append("")
        data_concat_register = data_constant_employee + array_data_dates_excel
        data_concat_register = data_concat_register + [terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])).get("ter_id") if terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])) else branchesJSON.get(insert_val_excel[0]["terminal"])]
        array_data_excel.append(data_concat_register)

    return array_data_excel, dates_push


@frappe.whitelist(allow_guest=True)
def excel_attendance(year=None, month=None):
    import calendar
    import datetime



    myobj = {'month': month}

    cortes = requests.post("https://recursoshumanos.shalom.com.pe/api/courts-month", json = myobj)
    cortes = cortes.json()
    cortes = cortes.get("data")
    # terminals_empresarial = requests.get("http://shalomcontrol.com/shalomprodapp/query/get_terminals_app_markings")
    terminalJSON = {}
    terminals_empresarial = frappe.get_all("Branch", fields=['name', 'ideentificador'] , filters=[], as_list=False)

    for entry in terminals_empresarial:
        terminalJSON[entry['ideentificador']] = entry

    branches = frappe.get_all("Branch", fields=['name', 'ideentificador'] , filters=[], as_list=False)
    branchesJSON = {}
    for branch in branches:
        branchesJSON[branch['name']] = str(branch["ideentificador"])
    month_map = get_month_map()
    month_str = str(month_map[month]).zfill(2)
    find_day_now = date.today()

    my_day_now = find_day_now.strftime("%Y-%m-%d")

    # Para fechas de este año
    # today = get_datetime()

    # Para fechas de otros años
    today = datetime.datetime.strptime(year+'-'+month_str+'-'+'01', "%Y-%m-%d")
    nxt_mnth = today.replace(day=28) + datetime.timedelta(days=4)
    res = nxt_mnth - datetime.timedelta(days=nxt_mnth.day)
    last_day = datetime.datetime.strptime(year+'-'+month_str+'-'+str(res.day), "%Y-%m-%d")

    final_range = calendar.monthrange(today.year, month_map[month])[1] + 1
    final_day_month = calendar.monthrange(today.year, month_map[month])[1]
    start_day_month = 1

    dates_of_month = ['{}-{}-{}'.format(today.year, month_str, r) for r in range(1, final_range)]

    array_heads_dates = []
    for day in range(1, final_range):
        daystr = str(day).zfill(2)
        timestamp = datetime.datetime.strptime(year+'-'+month_str+'-'+daystr, "%Y-%m-%d").timestamp()
        date_from_time = datetime.date.fromtimestamp(timestamp)
        d = date_from_time.strftime('%d-%b')
        array_heads_dates.append(d)

    array_head_employee = ["Codigo", "Nombre Completo", "Terminal", "Departamento", "Empresa","Calificación","Tipo Documento","N° Documento","Fecha de Ingreso Real","Fecha de Relevo","Zona","Estado"]

    final_head = array_head_employee + array_heads_dates + ["Id Sucursal"]

    length = len(dates_of_month)
    month_start, month_end = dates_of_month[0], dates_of_month[length-1]

    dates_push = []
    for k in range(start_day_month, final_day_month + 1):
        my_day = str(k).zfill(2)
        dates_push.append(year+'-'+month_str+'-'+my_day)

    holiday_sundays_list = holiday_sundays_dates()
    holiday_this_month = []
    holiday_this_month_holidays = []
    date_start_split = month_start.split('-')
    date_start_validate = date_start_split[0]+"-"+date_start_split[1]+"-0"+date_start_split[2]
    # date_start_time = datetime(int(date_start_split[0]),int(date_start_split[1]),int(date_start_split[2]))
    for this_month_holiday in holiday_sundays_list["domingos"]:
        str_holiday = str(this_month_holiday)
        if check_in_range(str_holiday, month_start, month_end):
            holiday_this_month.append(str_holiday)

    for this_month_holiday_holidays in holiday_sundays_list["feriados"]:
        str_holiday = str(this_month_holiday_holidays)
        if check_in_range(str_holiday, month_start, month_end):
            holiday_this_month_holidays.append(str_holiday)

    # doc_employees = frappe.db.get_list('Employee', fields=["name", "employee_name", "nombre_completo", "company", "branch", "department", "fecha_de_ingreso_real", "fecha_de_relevo", "status","calificacion_trabajador","place_of_issue","passport_number","zona_recursos"], as_list=False)
    doc_employees = frappe.db.sql("""
        SELECT
            emp.name, emp.employee_name, emp.nombre_completo, emp.company,
            emp.branch, emp.department, emp.fecha_de_ingreso_real, emp.fecha_de_relevo,
            emp.status, emp.calificacion_trabajador, emp.place_of_issue, emp.passport_number,
            br.zona_recursos_humanos as zona_recursos
        FROM `tabEmployee` emp 
        LEFT JOIN `tabBranch` br on emp.branch = br.name
        ORDER BY name asc
    """, values={}, as_dict=1)
    json_employee = dict()
    for employee in doc_employees:
        if employee["status"] == "Active" and employee["branch"] != "No especificado":
            json_employee[employee["name"]] = employee
        elif  employee["branch"] != "No especificado" and str(employee["fecha_de_relevo"])>=date_start_validate and str(employee["fecha_de_relevo"])<=month_end :
            json_employee[employee["name"]] = employee
        elif employee["fecha_de_relevo"] is None and (employee["status"] == "Active" or employee["status"]== "No Reportado"):
            json_employee[employee["name"]] = employee
    # values = {'start_date': month_start, 'end_date': month_end}
    # doc_attendances = frappe.db.sql(f"""SELECT employee, employee_name, attendance_date, status, leave_type FROM `tabAttendance` where company='Shalom Empresarial' AND branch!='No especificado' AND docstatus != '2' AND attendance_date >= %(start_date)s AND attendance_date <= %(end_date)s order by attendance_date asc; """, values=values, as_dict=True)
    doc_attendances = frappe.get_all("Attendance", fields=['employee', 'employee_name', 'company', 'attendance_date', 'status','estado_reporte', 'leave_type','docstatus'] , filters=[
        ["attendance_date", ">=", month_start],
        ["attendance_date", "<=", month_end],
        ["branch", "!=", "No especificado"],
        ["docstatus", "!=", 2]
    ], order_by='attendance_date asc', as_list=False)

    groups_attendance_by_employee = dict()
    doc_attendances_copy = []
    new_group = {}

    for val_attendance in doc_attendances:
        key_employee = val_attendance["employee"]
        if key_employee in json_employee:
            doc_attendances_copy.append(val_attendance)

    for key, value in groupby(doc_attendances_copy, key = itemgetter('employee')):
        for k in value:
            new_group[k["employee"]] = [k] if k["employee"] not in new_group.keys() else new_group[k["employee"]] + [k]

    copy_new_group = copy.copy(new_group)
    keys_group_employee_attendance = new_group.keys()
    key_employee = json_employee.keys()

    for key2, val_group in new_group.items():
        for val_employee in key_employee:
            if val_employee != key2:
                if val_employee not in keys_group_employee_attendance:
                    copy_new_group[val_employee] = []

    employe_list_final_group = []
    for hr_emp, val_hr in copy_new_group.items():
        group_final = []
        for r in range(start_day_month, final_day_month + 1):
            result_search = search_for_date(dates_push[r - 1], val_hr)
            count_list_hr = len(val_hr)
            if result_search[1]:
                stat = ""
                dayInit = result_search[0]["status"] if dates_push[r - 1] in cortes and result_search[0]["status"] != "" and result_search[0]["status"] is not None else result_search[0]["status"]
                if result_search[0]["docstatus"] == 1:
                    if dayInit == "On Leave":
                        if result_search[0]["leave_type"] == "VACACIONES":
                            stat = "VAC"
                        if result_search[0]["leave_type"] == "LICENCIA SIN GOCE":
                            stat = "LSG"
                        if result_search[0]["leave_type"] == "COMPENSATORIO":
                            stat = "COM"
                        if result_search[0]["leave_type"] == "LICENCIA CON GOCE":
                            stat = "LCG"
                        if result_search[0]["leave_type"] == "DESCANSO MEDICO":
                            stat = "DME"
                        if result_search[0]["leave_type"] == "PERMISO OCACIONAL":
                            stat = "L-PO"
                        if result_search[0]["leave_type"] == "SUBSIDIO":
                            stat = "LS"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR ENFERMEDAD":
                            stat = "SXE"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR MATERNIDAD":
                            stat = "SXM"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR ACCIDENTE":
                            stat = "SXA"
                        if result_search[0]["leave_type"] == "LICENCIA POR FALLECIMIENTO":
                            stat = "LXF"
                        if result_search[0]["leave_type"] == "LICENCIA POR PATERNIDAD":
                            stat = "LXP"
                    if dayInit == "Present":
                        stat = "P"
                    if dayInit == "Absent":
                        stat = "A"
                    if dayInit == "Half Day":
                        stat = "HD"
                    if dayInit == "Work From Home" or dayInit == "Marcacion Incompleta":
                        stat = "MI"
                    result_search[0]["terminal"] = json_employee[hr_emp]["branch"]
                    result_search[0]["department"] = json_employee[hr_emp]["department"]
                    result_search[0]["company"] = json_employee[hr_emp]["company"]
                    result_search[0]["nombre_completo"] = json_employee[hr_emp]["nombre_completo"]
                    result_search[0]["fecha_de_ingreso_real"] = json_employee[hr_emp]["fecha_de_ingreso_real"]
                    result_search[0]["fecha_de_relevo"] = json_employee[hr_emp]["fecha_de_relevo"]
                    result_search[0]["status"] = stat
                    result_search[0]["status_employee"] = "".join(json_employee[hr_emp]["status"])
                    result_search[0]["calificacion_trabajador"]="".join(json_employee[hr_emp]["calificacion_trabajador"])
                    result_search[0]["place_of_issue"]= json_employee[hr_emp]["place_of_issue"]
                    result_search[0]["passport_number"]="".join(json_employee[hr_emp]["passport_number"])
                    result_search[0]["zona_recursos"]=json_employee[hr_emp]["zona_recursos"]
                    group_final.append(result_search[0])
                elif result_search[0]["docstatus"] == 0:
                    stat = "NV"
                    result_search[0]["terminal"] = json_employee[hr_emp]["branch"]
                    result_search[0]["department"] = json_employee[hr_emp]["department"]
                    result_search[0]["company"] = json_employee[hr_emp]["company"]
                    result_search[0]["nombre_completo"] = json_employee[hr_emp]["nombre_completo"]
                    result_search[0]["fecha_de_ingreso_real"] = json_employee[hr_emp]["fecha_de_ingreso_real"]
                    result_search[0]["fecha_de_relevo"] = json_employee[hr_emp]["fecha_de_relevo"]
                    result_search[0]["status"] = stat
                    result_search[0]["status_employee"] = "".join(json_employee[hr_emp]["status"])
                    result_search[0]["calificacion_trabajador"]="".join(json_employee[hr_emp]["calificacion_trabajador"])
                    result_search[0]["place_of_issue"]= json_employee[hr_emp]["place_of_issue"]
                    result_search[0]["passport_number"]="".join(json_employee[hr_emp]["passport_number"])
                    result_search[0]["zona_recursos"]=json_employee[hr_emp]["zona_recursos"]
                    group_final.append(result_search[0])
            else:
                if str(json_employee[hr_emp]["fecha_de_ingreso_real"]) <= dates_push[r - 1]:
                    if json_employee[hr_emp]["status"] == 'Active':
                        if json_employee[hr_emp]["fecha_de_relevo"] is None:
                            if dates_push[r - 1] in holiday_this_month:
                                status_hr = "WO"
                            elif dates_push[r - 1] in holiday_this_month_holidays:
                                status_hr = "*H*"
                            else:
                                status_hr = "NM"
                        else:
                            if str(json_employee[hr_emp]["fecha_de_relevo"]) < dates_push[r - 1]:
                                status_hr = "C"
                            else:
                                if dates_push[r - 1] in holiday_this_month:
                                    status_hr = "WO"
                                elif dates_push[r - 1] in holiday_this_month_holidays:
                                    status_hr = "*H*"
                                else:
                                    status_hr = "NM"
                    else:
                        if str(json_employee[hr_emp]["fecha_de_relevo"]) < dates_push[r - 1]:
                            status_hr = "C"
                        else:
                            if dates_push[r - 1] in holiday_this_month:
                                status_hr = "WO"
                            elif dates_push[r - 1] in holiday_this_month_holidays:
                                status_hr = "*H*"
                            else:
                                status_hr = "NM"
                else:
                    status_hr = "C"

                not_mark = {
                    "employee": hr_emp,
                    "employee_name": json_employee[hr_emp]["employee_name"],
                    "attendance_date": dates_push[r - 1],
                    "status": status_hr,
                    "leave_type": "",
                    "terminal": json_employee[hr_emp]["branch"],
                    "department": json_employee[hr_emp]["department"],
                    "company": json_employee[hr_emp]["company"],
                    "nombre_completo": json_employee[hr_emp]["nombre_completo"],
                    "fecha_de_ingreso_real": json_employee[hr_emp]["fecha_de_ingreso_real"],
                    "fecha_de_relevo": json_employee[hr_emp]["fecha_de_relevo"],
                    "status_employee": json_employee[hr_emp]["status"],
                    "calificacion_trabajador": str(json_employee[hr_emp]["calificacion_trabajador"]),
                    "place_of_issue": json_employee[hr_emp]["place_of_issue"],
                    "passport_number": json_employee[hr_emp]["passport_number"],
                    "zona_recursos": json_employee[hr_emp]["zona_recursos"],
                }
                group_final.append(not_mark)

        groups_attendance_by_employee[hr_emp] = group_final
    array_data_excel = []
    for key_exc, insert_val_excel in groups_attendance_by_employee.items():
        # if key_exc == "HR-EMP-00753":
        #     return insert_val_excel
        if datetime.datetime.strptime(str(insert_val_excel[0]["fecha_de_ingreso_real"]), "%Y-%m-%d") >= last_day:
            continue
        array_data_dates_excel = []
        data_constant_employee = [key_exc, insert_val_excel[0]["nombre_completo"],
                                  terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])).get("nombre") if terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])) else insert_val_excel[0]["terminal"],
                                  insert_val_excel[0]["department"],
                                  insert_val_excel[0]["company"],
                                  insert_val_excel[0]["calificacion_trabajador"],
                                  insert_val_excel[0]["place_of_issue"],
                                  insert_val_excel[0]["passport_number"],
                                  insert_val_excel[0]["fecha_de_ingreso_real"],
                                  insert_val_excel[0]["fecha_de_relevo"],
                                  insert_val_excel[0]["zona_recursos"],
                                  insert_val_excel[0]["status_employee"]]
        for value_assistance in insert_val_excel:
            if str(value_assistance["attendance_date"]) <= str(my_day_now) or value_assistance["status"] != "":
                array_data_dates_excel.append(value_assistance["status"])
            else:
                array_data_dates_excel.append("")
        data_concat_register = data_constant_employee + array_data_dates_excel
        data_concat_register = data_concat_register + [terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])).get("ter_id") if terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])) else branchesJSON.get(insert_val_excel[0]["terminal"])]
        array_data_excel.append(data_concat_register)


    return download_excel_attendance(final_head, array_data_excel, month, year)

@frappe.whitelist()
def excel_attendance_qa(year=None, month=None):
    import calendar
    import datetime



    myobj = {'month': month}

    cortes = requests.post("https://recursoshumanos.shalom.com.pe/api/courts-month", json = myobj)
    cortes = cortes.json()
    cortes = cortes.get("data")
    terminals_empresarial = requests.get("http://shalomcontrol.com/shalomprodapp/query/get_terminals_app_markings")
    terminalJSON = {}
    terminals_empresarial = terminals_empresarial.json()
    for entry in terminals_empresarial:
        terminalJSON[entry['ter_id']] = entry

    branches = frappe.get_all("Branch", fields=['name', 'ideentificador'] , filters=[], as_list=False)
    branchesJSON = {}
    for branch in branches:
        branchesJSON[branch['name']] = str(branch["ideentificador"])
    month_map = get_month_map()
    month_str = str(month_map[month]).zfill(2)
    find_day_now = date.today()

    my_day_now = find_day_now.strftime("%Y-%m-%d")

    # Para fechas de este año
    # today = get_datetime()

    # Para fechas de otros años
    today = datetime.datetime.strptime(year+'-'+month_str+'-'+'01', "%Y-%m-%d")
    nxt_mnth = today.replace(day=28) + datetime.timedelta(days=4)
    res = nxt_mnth - datetime.timedelta(days=nxt_mnth.day)
    last_day = datetime.datetime.strptime(year+'-'+month_str+'-'+str(res.day), "%Y-%m-%d")

    final_range = calendar.monthrange(today.year, month_map[month])[1] + 1
    final_day_month = calendar.monthrange(today.year, month_map[month])[1]
    start_day_month = 1

    dates_of_month = ['{}-{}-{}'.format(today.year, month_str, r) for r in range(1, final_range)]

    array_heads_dates = []
    for day in range(1, final_range):
        daystr = str(day).zfill(2)
        timestamp = datetime.datetime.strptime(year+'-'+month_str+'-'+daystr, "%Y-%m-%d").timestamp()
        date_from_time = datetime.date.fromtimestamp(timestamp)
        d = date_from_time.strftime('%d-%b')
        array_heads_dates.append(d)

    array_head_employee = ["Codigo", "Nombre Completo", "Terminal", "Departamento", "Empresa","Calificación","Tipo Documento","N° Documento","Fecha de Ingreso Real","Fecha de Relevo","Zona","Estado"]

    final_head = array_head_employee + array_heads_dates + ["Id Sucursal"]

    length = len(dates_of_month)
    month_start, month_end = dates_of_month[0], dates_of_month[length-1]

    dates_push = []
    for k in range(start_day_month, final_day_month + 1):
        my_day = str(k).zfill(2)
        dates_push.append(year+'-'+month_str+'-'+my_day)

    holiday_sundays_list = holiday_sundays_dates()
    holiday_this_month = []
    holiday_this_month_holidays = []
    date_start_split = month_start.split('-')
    date_start_validate = date_start_split[0]+"-"+date_start_split[1]+"-0"+date_start_split[2]
    # date_start_time = datetime(int(date_start_split[0]),int(date_start_split[1]),int(date_start_split[2]))
    for this_month_holiday in holiday_sundays_list["domingos"]:
        str_holiday = str(this_month_holiday)
        if check_in_range(str_holiday, month_start, month_end):
            holiday_this_month.append(str_holiday)

    for this_month_holiday_holidays in holiday_sundays_list["feriados"]:
        str_holiday = str(this_month_holiday_holidays)
        if check_in_range(str_holiday, month_start, month_end):
            holiday_this_month_holidays.append(str_holiday)

    # doc_employees = frappe.db.get_list('Employee', fields=["name", "employee_name", "nombre_completo", "company", "branch", "department", "fecha_de_ingreso_real", "fecha_de_relevo", "status","calificacion_trabajador","place_of_issue","passport_number","zona_recursos"], as_list=False)
    doc_employees = frappe.db.sql("""
        SELECT
            emp.name, emp.employee_name, emp.nombre_completo, emp.company,
            emp.branch, emp.department, emp.fecha_de_ingreso_real, emp.fecha_de_relevo,
            emp.status, emp.calificacion_trabajador, emp.place_of_issue, emp.passport_number,
            br.zona_recursos_humanos as zona_recursos
        FROM `tabEmployee` emp 
        LEFT JOIN `tabBranch` br on emp.branch = br.name
        ORDER BY name asc
    """, values={}, as_dict=1)
    json_employee = dict()
    for employee in doc_employees:
        if employee["status"] == "Active" and employee["branch"] != "No especificado":
            json_employee[employee["name"]] = employee
        elif  employee["branch"] != "No especificado" and str(employee["fecha_de_relevo"])>=date_start_validate and str(employee["fecha_de_relevo"])<=month_end :
            json_employee[employee["name"]] = employee
        elif employee["fecha_de_relevo"] is None and (employee["status"] == "Active" or employee["status"]== "No Reportado"):
            json_employee[employee["name"]] = employee
    # values = {'start_date': month_start, 'end_date': month_end}
    # doc_attendances = frappe.db.sql(f"""SELECT employee, employee_name, attendance_date, status, leave_type FROM `tabAttendance` where company='Shalom Empresarial' AND branch!='No especificado' AND docstatus != '2' AND attendance_date >= %(start_date)s AND attendance_date <= %(end_date)s order by attendance_date asc; """, values=values, as_dict=True)
    doc_attendances = frappe.get_all("Attendance", fields=['employee', 'employee_name', 'company', 'attendance_date', 'status','estado_reporte', 'leave_type','docstatus'] , filters=[
        ["attendance_date", ">=", month_start],
        ["attendance_date", "<=", month_end],
        ["branch", "!=", "No especificado"],
        ["docstatus", "!=", 2]
    ], order_by='attendance_date asc', as_list=False)

    groups_attendance_by_employee = dict()
    doc_attendances_copy = []
    new_group = {}

    for val_attendance in doc_attendances:
        key_employee = val_attendance["employee"]
        if key_employee in json_employee:
            doc_attendances_copy.append(val_attendance)

    for key, value in groupby(doc_attendances_copy, key = itemgetter('employee')):
        for k in value:
            new_group[k["employee"]] = [k] if k["employee"] not in new_group.keys() else new_group[k["employee"]] + [k]

    copy_new_group = copy.copy(new_group)
    keys_group_employee_attendance = new_group.keys()
    key_employee = json_employee.keys()

    for key2, val_group in new_group.items():
        for val_employee in key_employee:
            if val_employee != key2:
                if val_employee not in keys_group_employee_attendance:
                    copy_new_group[val_employee] = []

    employe_list_final_group = []
    for hr_emp, val_hr in copy_new_group.items():
        group_final = []
        for r in range(start_day_month, final_day_month + 1):
            result_search = search_for_date(dates_push[r - 1], val_hr)
            count_list_hr = len(val_hr)
            if result_search[1]:
                stat = ""
                dayInit = result_search[0]["status"] if dates_push[r - 1] in cortes and result_search[0]["status"] != "" and result_search[0]["status"] is not None else result_search[0]["status"]
                if result_search[0]["docstatus"] == 1:
                    if dayInit == "On Leave":
                        if result_search[0]["leave_type"] == "VACACIONES":
                            stat = "VAC"
                        if result_search[0]["leave_type"] == "LICENCIA SIN GOCE":
                            stat = "LSG"
                        if result_search[0]["leave_type"] == "COMPENSATORIO":
                            stat = "COM"
                        if result_search[0]["leave_type"] == "LICENCIA CON GOCE":
                            stat = "LCG"
                        if result_search[0]["leave_type"] == "DESCANSO MEDICO":
                            stat = "DME"
                        if result_search[0]["leave_type"] == "PERMISO OCACIONAL":
                            stat = "L-PO"
                        if result_search[0]["leave_type"] == "SUBSIDIO":
                            stat = "LS"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR ENFERMEDAD":
                            stat = "SXE"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR MATERNIDAD":
                            stat = "SXM"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR ACCIDENTE":
                            stat = "SXA"
                        if result_search[0]["leave_type"] == "LICENCIA POR FALLECIMIENTO":
                            stat = "LXF"
                        if result_search[0]["leave_type"] == "LICENCIA POR PATERNIDAD":
                            stat = "LXP"
                    if dayInit == "Present":
                        stat = "P"
                    if dayInit == "Absent":
                        stat = "A"
                    if dayInit == "Half Day":
                        stat = "HD"
                    if dayInit == "Work From Home" or dayInit == "Marcacion Incompleta":
                        stat = "MI"
                    result_search[0]["terminal"] = json_employee[hr_emp]["branch"]
                    result_search[0]["department"] = json_employee[hr_emp]["department"]
                    result_search[0]["company"] = json_employee[hr_emp]["company"]
                    result_search[0]["nombre_completo"] = json_employee[hr_emp]["nombre_completo"]
                    result_search[0]["fecha_de_ingreso_real"] = json_employee[hr_emp]["fecha_de_ingreso_real"]
                    result_search[0]["fecha_de_relevo"] = json_employee[hr_emp]["fecha_de_relevo"]
                    result_search[0]["status"] = ("P" if stat == "WFH" else stat) if dates_push[r - 1] in cortes else stat
                    result_search[0]["status_employee"] = "".join(json_employee[hr_emp]["status"])
                    result_search[0]["calificacion_trabajador"]="".join(json_employee[hr_emp]["calificacion_trabajador"])
                    result_search[0]["place_of_issue"]= json_employee[hr_emp]["place_of_issue"]
                    result_search[0]["passport_number"]="".join(json_employee[hr_emp]["passport_number"])
                    result_search[0]["zona_recursos"]=json_employee[hr_emp]["zona_recursos"]
                    group_final.append(result_search[0])
                elif result_search[0]["docstatus"] == 0:
                    stat = "NV"
                    result_search[0]["terminal"] = json_employee[hr_emp]["branch"]
                    result_search[0]["department"] = json_employee[hr_emp]["department"]
                    result_search[0]["company"] = json_employee[hr_emp]["company"]
                    result_search[0]["nombre_completo"] = json_employee[hr_emp]["nombre_completo"]
                    result_search[0]["fecha_de_ingreso_real"] = json_employee[hr_emp]["fecha_de_ingreso_real"]
                    result_search[0]["fecha_de_relevo"] = json_employee[hr_emp]["fecha_de_relevo"]
                    result_search[0]["status"] = stat
                    result_search[0]["status_employee"] = "".join(json_employee[hr_emp]["status"])
                    result_search[0]["calificacion_trabajador"]="".join(json_employee[hr_emp]["calificacion_trabajador"])
                    result_search[0]["place_of_issue"]= json_employee[hr_emp]["place_of_issue"]
                    result_search[0]["passport_number"]="".join(json_employee[hr_emp]["passport_number"])
                    result_search[0]["zona_recursos"]=json_employee[hr_emp]["zona_recursos"]
                    group_final.append(result_search[0])
            else:
                if str(json_employee[hr_emp]["fecha_de_ingreso_real"]) <= dates_push[r - 1]:
                    if json_employee[hr_emp]["status"] == 'Active':
                        if json_employee[hr_emp]["fecha_de_relevo"] is None:
                            if dates_push[r - 1] in holiday_this_month:
                                status_hr = "WO"
                            elif dates_push[r - 1] in holiday_this_month_holidays:
                                status_hr = "*H*"
                            else:
                                status_hr = "NM"
                        else:
                            if str(json_employee[hr_emp]["fecha_de_relevo"]) < dates_push[r - 1]:
                                status_hr = "C"
                            else:
                                if dates_push[r - 1] in holiday_this_month:
                                    status_hr = "WO"
                                elif dates_push[r - 1] in holiday_this_month_holidays:
                                    status_hr = "*H*"
                                else:
                                    status_hr = "NM"
                    else:
                        if str(json_employee[hr_emp]["fecha_de_relevo"]) < dates_push[r - 1]:
                            status_hr = "C"
                        else:
                            if dates_push[r - 1] in holiday_this_month:
                                status_hr = "WO"
                            elif dates_push[r - 1] in holiday_this_month_holidays:
                                status_hr = "*H*"
                            else:
                                status_hr = "NM"
                else:
                    status_hr = "C"

                not_mark = {
                    "employee": hr_emp,
                    "employee_name": json_employee[hr_emp]["employee_name"],
                    "attendance_date": dates_push[r - 1],
                    "status": status_hr,
                    "leave_type": "",
                    "terminal": json_employee[hr_emp]["branch"],
                    "department": json_employee[hr_emp]["department"],
                    "company": json_employee[hr_emp]["company"],
                    "nombre_completo": json_employee[hr_emp]["nombre_completo"],
                    "fecha_de_ingreso_real": json_employee[hr_emp]["fecha_de_ingreso_real"],
                    "fecha_de_relevo": json_employee[hr_emp]["fecha_de_relevo"],
                    "status_employee": json_employee[hr_emp]["status"],
                    "calificacion_trabajador": str(json_employee[hr_emp]["calificacion_trabajador"]),
                    "place_of_issue": json_employee[hr_emp]["place_of_issue"],
                    "passport_number": json_employee[hr_emp]["passport_number"],
                    "zona_recursos": json_employee[hr_emp]["zona_recursos"],
                }
                group_final.append(not_mark)

        groups_attendance_by_employee[hr_emp] = group_final
    array_data_excel = []
    for key_exc, insert_val_excel in groups_attendance_by_employee.items():
        # if key_exc == "HR-EMP-00753":
        #     return insert_val_excel
        if datetime.datetime.strptime(str(insert_val_excel[0]["fecha_de_ingreso_real"]), "%Y-%m-%d") >= last_day:
            continue
        array_data_dates_excel = []
        data_constant_employee = [key_exc, insert_val_excel[0]["nombre_completo"],
                                  terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])).get("nombre") if terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])) else insert_val_excel[0]["terminal"],
                                  insert_val_excel[0]["department"],
                                  insert_val_excel[0]["company"],
                                  insert_val_excel[0]["calificacion_trabajador"],
                                  insert_val_excel[0]["place_of_issue"],
                                  insert_val_excel[0]["passport_number"],
                                  insert_val_excel[0]["fecha_de_ingreso_real"],
                                  insert_val_excel[0]["fecha_de_relevo"],
                                  insert_val_excel[0]["zona_recursos"],
                                  insert_val_excel[0]["status_employee"]]
        for value_assistance in insert_val_excel:
            if str(value_assistance["attendance_date"]) <= str(my_day_now) or value_assistance["status"] != "":
                array_data_dates_excel.append(value_assistance["status"])
            else:
                array_data_dates_excel.append("")
        data_concat_register = data_constant_employee + array_data_dates_excel
        data_concat_register = data_concat_register + [terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])).get("ter_id") if terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])) else branchesJSON.get(insert_val_excel[0]["terminal"])]
        array_data_excel.append(data_concat_register)
    return download_excel_attendance(final_head, array_data_excel, month, year)

def search_for_date(date="", array=[]):
    for search_date in array:
        if str(search_date["attendance_date"]) == date:
            return [search_date, True]
    return [[], False]


def get_month_map():
    return frappe._dict({
        "Enero": 1,
        "Febrero": 2,
        "Marzo": 3,
        "Abril": 4,
        "Mayo": 5,
        "Junio": 6,
        "Julio": 7,
        "Agosto": 8,
        "Setiembre": 9,
        "Octubre": 10,
        "Noviembre": 11,
        "Diciembre": 12
    })


@frappe.whitelist()
def holiday_sundays_dates():
    doc = frappe.db.sql(f"""SELECT * FROM `tabHoliday` order by holiday_date asc; """, as_dict=True)
    array_holiday = []
    array_sundays = []
    for holiday in doc:
        if holiday["description"] != 'Sunday':
            array_holiday.append(holiday["holiday_date"])
        else:
            array_sundays.append(holiday["holiday_date"])
    return frappe._dict({
        "feriados": array_holiday,
        "domingos": array_sundays
    })


def check_in_range(date_check="", date_start="", date_end=""):
    my_date = date_check.split('-')
    my_date_start = date_start.split('-')
    my_date_end = date_end.split('-')
    date_now = datetime(int(my_date[0]), int(my_date[1]), int(my_date[2]))
    date_start = datetime(int(my_date_start[0]), int(my_date_start[1]), int(my_date_start[2]))
    date_end = datetime(int(my_date_end[0]), int(my_date_end[1]), int(my_date_end[2]))
    result = False
    if date_start <= date_now <= date_end:
        result = True
    return result

@frappe.whitelist()
def courses_by_designation():

    user_email = frappe.db.get_value("User",{
        "name": frappe.session.user,
    },"email")
    designation = frappe.db.get_value("Employee",{
        "user_id": user_email,
        "status": "Active"
    },"designation")
    if designation is None or designation == '':
        designation = "ENCARGADO DE AGENCIA"
    courses = frappe.db.get_all("Course",
                                filters=[], as_list=False)
    courses_program = {}
    for course in courses:
        programs = frappe.db.get_all("Program",
                                    filters=[["Program Course","course","=",course.name]], as_list=False)
        if len(programs) > 0:
            courses_program[course.name] = programs[0].name
    # return courses_program
    courses_data =  [frappe.get_doc("Course", course.name) for course in courses]
    # return courses_data[0]
    courses_end = []
    for course_item in courses_data:
        if course_item.name in courses_program:
            course_end = {
                "name": course_item.name,
                "owner": course_item.owner,
                "creation": course_item.creation,
                "modified": course_item.modified,
                "modified_by": course_item.modified_by,
                "idx": course_item.idx,
                "docstatus": course_item.docstatus,
                "course_name": course_item.course_name,
                "department": course_item.department,
                "hero_image": course_item.hero_image,
                "doctype": course_item.doctype,
                "topics": course_item.topics,
                "designation": course_item.designation,
                "assessment_criteria": course_item.assessment_criteria,
                "program": courses_program[course_item.name],
            }
            courses_end.append(course_end)
    return courses_end

@frappe.whitelist()
def report_pos_register():
    terminals_empresarial = requests.get("http://shalomcontrol.com/shalomprodapp/query/get_terminals_app_markings_pos")
    terminalJSON = {}
    terminals_empresarial = terminals_empresarial.json()
    for entry in terminals_empresarial:
        terminalJSON[entry['ter_id']] = entry

    filters = {"from_date":"2023-02-17","to_date":"2023-03-17"}
    conditions = get_conditions(filters)
    order_by = "p.posting_date"
    select_mop_field, from_sales_invoice_payment, group_by_mop_condition = "", "", ""

    data_entries = frappe.db.sql(
        """
        SELECT 
            p.posting_date,p.posting_time, p.name as pos_invoice, p.pos_profile,br.zona_recursos_humanos as region, pro.branch as sucursal, br.ideentificador as idsucursal,
            br.categoria, us.full_name as owner,us.full_name as owner_name,p.status_comprobante as status_comprobante, p.base_grand_total as grand_total, p.base_grand_total as paid_amount,
            p.customer, p.is_return,p.documento, itm.description as item {select_mop_field}
        FROM
            `tabPOS Invoice Item` itm {from_sales_invoice_payment}
        LEFT JOIN `tabPOS Invoice` p on (itm.parent=p.name)
        LEFT JOIN `tabPOS Profile` pro on (p.pos_profile = pro.name)
        LEFT JOIN `tabBranch` br on (pro.branch = br.name)
        LEFT JOIN tabUser us on( us.name = p.owner )
        WHERE
            p.docstatus = 1 and
            {group_by_mop_condition}
            {conditions}
        ORDER BY
            {order_by}
        """.format(
            select_mop_field=select_mop_field,
            from_sales_invoice_payment=from_sales_invoice_payment,
            group_by_mop_condition=group_by_mop_condition,
            conditions=conditions,
            order_by=order_by
        ), filters, as_dict=1)
    data = []
    for entry in data_entries:
        data.append({
            "posting_date": entry.posting_date,
            "posting_time": entry.posting_time,
            "pos_invoice": entry.pos_invoice,
            "pos_profile": entry.pos_profile,
            "region": entry.region,
            "sucursal": entry.sucursal,
            "idsucursal": entry.idsucursal,
            "categoria": entry.categoria,
            "owner": entry.owner,
            "owner_name": entry.owner_name,
            "status_comprobante": "FACTURA" if entry.documento and len(entry.documento) == 11 else "BOLETA",
            "grand_total": entry.grand_total,
            "paid_amount": entry.paid_amount,
            "customer": entry.customer,
            "is_return": entry.is_return,
            "item": entry.item,
            "tipo_local": terminalJSON[str(entry.idsucursal)]["tipo_local"] if str(entry.idsucursal) in terminalJSON.keys() else "",
            "type_payment": entry.status_comprobante if entry.status_comprobante in ["Pago por PINPAD","QR","Planilla"] else "CONTADO",
        })

    return data