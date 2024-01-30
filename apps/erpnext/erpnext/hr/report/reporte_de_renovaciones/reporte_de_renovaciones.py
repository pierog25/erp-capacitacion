# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_data(filters):

	filters = {}

	renovacion = frappe.db.sql(
			"""
				SELECT
					name, empleado, dni, nombre_completo, departamento, sucursal, data_10, data_12, año, estado_de_documento
				FROM `tabSolicitud de Renovaciones`	
			""", values=filters, as_dict=1
		)

	items = {}

	itemsTabla = {}

	for x in renovacion:
		items[x.name] = x
		itemsTabla[x.name] = []

	keysimplode = ' , '.join(items.keys())

	filters2 = {"keys":items.keys()}

	tables_renovaciones = frappe.db.sql(
		"""
			SELECT
				name, codigo, nombre, puesto,motivo, dni, tiempo_renovacion, tipo_de_contraro, texto_boton, parent, renueva
			FROM `tabTrabajadores pendiete de renovar`
		""", values=filters2, as_dict=1
	)

	employees = []

	employees_json = {}

	employees_json_puesto = {}

	employees_json_arr = {}

	puestos = []

	for x in tables_renovaciones:

		employees.append(x.dni)
		puestos.append(x.puesto)
		employees_json[x.dni] = []
		employees_json_puesto[x.puesto] = []
		employees_json_arr[x.dni] = []
		itemsTabla[x.parent].append(x)


	filters3 = {"documentos":employees}


	quiz_activity = frappe.db.sql(
		"""
			SELECT
				dni, quiz, status, score, activity_date
			FROM `tabQuiz Activity`
			WHERE dni IN %(documentos)s ORDER BY creation desc
		""", values=filters3, as_dict=1
	)

	filters4 = {"puestos": puestos}

	quizis = frappe.db.sql(
		"""
			SELECT
				parent, examen
			FROM `tabExamenes Puesto`
			WHERE parent IN %(puestos)s
		""", values=filters4, as_dict=1
	)

	for x in quiz_activity:
		employees_json[x.dni].append(x)
		employees_json_arr[x.dni].append(x.quiz)

	for x in quizis:
		employees_json_puesto[x.parent].append(x)


	data = []

	for x in itemsTabla:


		for y in itemsTabla[x]:


			data_test = {

				"name": x,
				"encargado": items[x].empleado,
				"dni_encargado": items[x].dni,
				"nombre_completo": items[x].nombre_completo,
				"departamento": items[x].departamento,
				"sucursal": items[x].sucursal,
				"id_sucursal": items[x].data_10,
				"month": items[x].data_12,
				"year": items[x].año,
				"estado_documento": items[x].estado_de_documento,

			}

			examenes = ""
			exam = employees_json_puesto[y.puesto]
			results = employees_json[y.dni]
			exam_result = employees_json_arr[y.dni]

			for z in exam:
				if z.examen in exam_result:
					for m in results:
						if z.examen == m.quiz:
							if m.status == "Pass":
								examenes+= z.examen+" "+" Aprobado \n"
								break
							else:
								examenes+= z.examen+" "+" Desaprobado \n"
								break
					continue
				else:
					examenes+= z.examen+" "+" No rendido \n"
					continue

			data_test["empleado"] = y.codigo
			data_test["nombre"] = y.nombre
			data_test["motivo"] = y.motivo
			data_test["pusto"] = y.puesto
			data_test["tiempo_renovacion"] = y.tiempo_renovacion
			data_test["tipo_de_contraro"] = y.tipo_de_contraro
			data_test["texto_boton"] = y.texto_boton
			data_test["dni"] = y.dni
			data_test["examenes"] = examenes
			data_test["renueva"] = y.renueva

			data.append(data_test)

	return data

def get_columns():
	columns = [
		{
			'label': "Name",
			'fieldname': 'name',
			'fieldtype': 'Link',
			'options':'Solicitud de Renovaciones',
			'width': 200
		},
		{
			'label': "Id Encargado",
			'fieldname': 'encargado',
			'fieldtype': 'Link',
			'options':'Employee',
			'width': 100
		},
		{
			'label': "Documento encargado",
			'fieldname': 'dni_encargado',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "Encargado",
			'fieldname': 'nombre_completo',
			'fieldtype': 'Data',
			'width': 200
		},
		{
			'label': "Departamento",
			'fieldname': 'departamento',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "Sucursal",
			'fieldname': 'sucursal',
			'fieldtype': 'Link',
			'options': 'Branch',
			'width': 100
		},
		{
			'label': "Id de Sucursal",
			'fieldname': 'id_sucursal',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "Estado documento",
			'fieldname': 'estado_documento',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "Mes",
			'fieldname': 'month',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "Año",
			'fieldname': 'year',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "Id Empleado",
			'fieldname': 'empleado',
			'fieldtype': 'Link',
			'options':'Employee',
			'width': 100
		},
		{
			'label': "Empleado Nombre",
			'fieldname': 'nombre',
			'fieldtype': 'Data',
			'width': 200
		},
		{
			'label': "Dni Empleado",
			'fieldname': 'dni',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "Renueva",
			'fieldname': 'renueva',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "Motivo",
			'fieldname': 'motivo',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "Tiempo de Renovacion",
			'fieldname': 'tiempo_renovacion',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "Tipo de Contrato",
			'fieldname': 'tipo_de_contraro',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "Examenes Historial",
			'fieldname': 'examenes',
			'fieldtype': 'Data',
			'width': 400
		}

	]
	return columns