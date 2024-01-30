from frappe.utils.pdf import get_pdf
import frappe
import pdfkit
import jinja2
import os
from datetime import datetime
from datetime import date


@frappe.whitelist()
def get_payroll_by_name(id_salary_slip=None):
    values = {'salary': id_salary_slip}
    data_salary_slip = frappe.db.sql(f"""SELECT * FROM `tabSalary Slip` where name=%(salary)s; """, values=values, as_dict=True)
    mi_fisrt_data = data_salary_slip[0]
    data_name = mi_fisrt_data["name"]
    data_detail_salary = frappe.db.get_list('Salary Detail', filters={'parenttype': 'Salary Slip', 'parent': data_name}, fields=['*'], as_list=False)
    deductions = []
    earnings = []
    for detail in data_detail_salary:
        if detail["parentfield"] == "deductions":
            deductions.append(detail)
        else:
            earnings.append(detail)
    mi_fisrt_data["deductions"] = deductions
    mi_fisrt_data["earnings"] = earnings
    return mi_fisrt_data

@frappe.whitelist()
def get_payroll_by_name_massive(data_salary_slip):
    mi_fisrt_data = data_salary_slip
    data_name = mi_fisrt_data["name"]
    data_detail_salary = frappe.db.get_list('Salary Detail', filters={'parenttype': 'Salary Slip', 'parent': data_name}, fields=['*'], as_list=False)
    deductions = []
    earnings = []
    for detail in data_detail_salary:
        if detail["parentfield"] == "deductions":
            deductions.append(detail)
        else:
            earnings.append(detail)
    mi_fisrt_data["deductions"] = deductions
    mi_fisrt_data["earnings"] = earnings
    return mi_fisrt_data

@frappe.whitelist()
def report_salary_slip(id_salary_slip=None):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'salary_slip_pdf.html')

    route_template = filename
    name_template = route_template.split('/')[-1]
    route_template = route_template.replace(name_template, '')

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(route_template))
    template = env.get_template(name_template)
    doc_data = get_payroll_by_name(id_salary_slip)
    info = doc_data

    # Earnings
    info['haber_mensual']  = 0
    info['vacaciones']  = 0
    info['asignacion_familiar']  = 0
    info['horas_25']  = 0
    info['horas_35']  = 0
    info['horas_100']  = 0
    info['horas_nocturnas']  = 0
    info['movilidad']  = 0
    info['condiciones_trabajo']  = 0
    info['otros_ingresos']  = 0
    info['gratificacion']  = 0
    info['bonif_ext']  = 0
    info['viaticos_earn']  = 0
    info['viaticos_ingreso']  = 0
    info['apoyos']  = 0
    info['movilidad_variable']  = 0
    info['descando_medico']  = 0
    info['licencia']  = 0
    info['LICENCIA_GOCE']  = 0
    info['LICENCIA_FALLECIMIENTO']  = 0
    info['LICENCIA_PATERNIDAD']  = 0
    info['COMPENSATORIO']  = 0
    info['SUBSIDIO_ACCIDENTE']  = 0
    info['SUBSIDIO_ENFERMEDAD']  = 0
    info['SUBSIDIO_MATERNIDAD']  = 0
    info['ingreso_viaticos']  = 0
    info['canasta_navidad_in']  = 0


    # Deductions
    info['snp']  = 0
    info['afp_fondo']  = 0
    info['afp_seguro']  = 0
    info['afp_comision']  = 0
    info['faltas_y_permisos']  = 0
    info['ta_categoria']  = 0
    info['viaticos']  = 0
    info['gratificacion_bonificacion']  = 0
    info['seguros_rimac']  = 0
    info['adelantos']  = 0
    info['desc_alimentos']  = 0
    info['epp']  = 0
    info['otros_descuentos']  = 0
    info['apoyos_deductions']  = 0
    info['seguro_salud_erp'] = 0
    info['vida_ley_componente'] = 0
    info['sctr_componente_pension'] = 0
    info['sctr_componente_salud'] = 0

    info['total_aportes_componente'] = 0
    info['total_aportes_componente_dos_digitos'] = 0

    info['canasta_navidad_eg']  = 0

    # Fecha de boleta
    Meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre']
    Mes_boleta = str(info['start_date']).split(sep='-')
    Mes = str(info['start_date']).split(sep='-')[1]
    Anio = str(info['start_date']).split(sep='-')[0]
    numero_mes = int(Mes)
    info['mes_boleta'] = Meses[numero_mes - 1].upper()
    info['ano_boleta'] = Anio.upper()

    # return info['mes_boleta']

    # Fecha de pago final Dia Mes Año
    fecha_pago = str(info['end_date']).split(sep='-')

    dia_pago  = str(info['end_date']).split(sep='-')[2]
    mes_pago  = str(info['end_date']).split(sep='-')[1]
    anio_pago = str(info['end_date']).split(sep='-')[0]

    fecha_pago_final = dia_pago + '-' + mes_pago + '-' + anio_pago

    info['fecha_final_pago'] = fecha_pago_final

    # fecha de ingreso
    fecha_ingreso = str(info['fecha_ingreso']).split(sep='-')

    anio_ingreso = str(info['fecha_ingreso']).split(sep='-')[0]
    mes_ingreso = str(info['fecha_ingreso']).split(sep='-')[1]
    dia_ingreso = str(info['fecha_ingreso']).split(sep='-')[2]

    fecha_ingreso_final = dia_ingreso + '-' + mes_ingreso + '-' + anio_ingreso

    info['fecha_final_ingreso'] = fecha_ingreso_final

    # Fecha de nacimiento
    fecha_nacimiento_nomina = str(info['fecha_nacimiento']).split(sep='-')

    anio_nacimiento = str(info['fecha_nacimiento']).split(sep='-')[0]
    mes_nacimiento = str(info['fecha_nacimiento']).split(sep='-')[1]
    dia_nacimiento = str(info['fecha_nacimiento']).split(sep='-')[2]

    fecha_nacimiento_final = dia_nacimiento + '-' + mes_nacimiento + '-' + anio_nacimiento

    info['fecha_final_nacimiento'] = fecha_nacimiento_final

    # return fecha_ingreso_final
    #data empleado by PIERO
    info['data_employee'] = frappe.db.get_list('Employee', fields=["*"],filters={'name': info['employee']}, as_list=False)[0]
    # info["VACACIONES"].holidays_validation = False
    # info["VACACIONES"].holidays_periodo = ""
    # info["VACACIONES"].holidays_from_date = ""
    # info["VACACIONES"].holidays_to_date = ""
    # info["VACACIONES"] = {
    #     "holidays_validation" : False
    # }
    # return info
    info["vacaciones_uno"] = {
        "holidays_validation" : False,
        "holidays_periodo" : '',
        "holidays_from_date" : '',
        "holidays_to_date" : ''
    }
    info["vacaciones_compradas_dos"] = {
        "holidays_validation" : False,
        "holidays_periodo" : '',
        "holidays_from_date" : '',
        "holidays_to_date" : ''
    }
    holidays = frappe.db.get_list('Leave Allocation', fields=["from_date","to_date","leave_type","periodo"],filters={'employee': info['employee'],'leave_type':['in',["VACACIONES","VACACIONES COMPRADAS"]]}, as_list=False)
    if len(holidays)>0:
        for n in holidays:
            from_date = str(n.from_date).split('-')
            to_date = str(n.to_date).split('-')
            start_date = str(info['start_date']).split('-')
            end_date = str(info['end_date']).split('-')
            from_date = datetime(int(from_date[0]), int(from_date[1]), int(from_date[2]))
            to_date = datetime(int(to_date[0]), int(to_date[1]), int(to_date[2]))
            start_date = datetime(int(start_date[0]), int(start_date[1]), int(start_date[2]))
            end_date = datetime(int(end_date[0]), int(end_date[1]), int(end_date[2]))
            if start_date<=from_date<=end_date or  start_date<=to_date<=end_date :
                if n.leave_type == "VACACIONES":
                    info["vacaciones_uno"] = {
                        "holidays_validation" : True,
                        "holidays_periodo" : "2022-2023" if (n.periodo is None) else n.periodo,
                        "holidays_from_date" : n.from_date.strftime('%d-%m-%Y'),
                        "holidays_to_date" : n.to_date.strftime('%d-%m-%Y')
                    }
                if n.leave_type == "VACACIONES COMPRADAS":
                    info["vacaciones_compradas_dos"] = {
                        "holidays_validation" : True,
                        "holidays_periodo" : "2022-2023" if (n.periodo is None) else n.periodo,
                        "holidays_from_date" : n.from_date.strftime('%d-%m-%Y'),
                        "holidays_to_date" : n.to_date.strftime('%d-%m-%Y')
                    }
    if info['data_employee'].bank_name == None :
        info['data_employee'].bank_name = '-'
    else:
        info['nombre_banco_erp'] = info['data_employee'].bank_name

    # Conviertiendo a entero
    info['total_dias_trabajo'] = int(info['payment_days'])
    info['ausencias'] = int(info['ausencias_reales'])
    info['dias_subsidio'] = int(info['dias_subsidiados'])
    info['dias_no_subsidio'] = int(info['dias_no_subsidiados'])

    # vacaciones + compras de vacaciones

    info['pago_neto'] = '{:.2f}'.format(info['net_pay'])
    neto_entero = int(float(info['pago_neto']))
    info['vacaciones_cantidad'] = int(info['dias_vaciones'])
    info['vacaciones_compradas_cantidad'] = info['vacaciones_compradas']

    info['vacaciones_con_compradas'] = info['vacaciones_cantidad'] + info['vacaciones_compradas_cantidad']

    info['licencia_falle_pate'] = info['licencia_por_fallecimiento'] + info['licencia_paternidad']

    info['sueldo_empleado'] = '{:.2f}'.format(info['sueldo'])
    info['horas_25_cantidad'] = '{:.2f}'.format(info['n_horas_extras_25'])
    info['horas_35_cantidad'] = '{:.2f}'.format(info['n_horas_extras_35'])
    info['horas_100_cantidad'] = '{:.2f}'.format(info['n_horas_extras_100'])
    info['total_ingresos_nomina'] = '{:.2f}'.format(info['gross_pay'])
    info['total_deduciones_nomina'] = '{:.2f}'.format(info['total_deduction'])

    # info['sueldo'] = '{:.2f}'.format(info['haber_mensual'])

    # Dias Subsidiados
    info['sub_maternidad'] = info['subsidio_por_maternidad']
    info['sub_accidente'] = info['subsidio_accidente']
    info['sub_enfermedad'] = int(info['subsidio_enfermedad'])

    info['dias_subsidio_total'] = info['sub_maternidad'] + info['sub_accidente'] + info['sub_enfermedad']
    info['Dias_No_Laborados_ERP'] = int(info['total_working_days'] - info['payment_days'] - info['dias_subsidio_total'])

    # Dias No Subsidiados
    info['desca_medico'] = int(info['descanso_medico'])

    info['es_salud'] = info['essalud'] if info['essalud'] != None else 0.00


    # Datos de la empresa
    info['ruc_compania'] = info['rucc']
    info['nombre_compania'] = info['razonn_social']
    info['telefono_compania'] = info['telefono']
    info['direccion_compania'] = info['direccion']

    # Nombre de compania
    info['compania_logo'] = info['company']

    if info['telefono_compania'] == None :
        info['telefono_compania'] = '-'


    # Conditions Earnings
    for n in info['earnings']:
        if n.abbr == 'RM':
            info['haber_mensual'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'VC':
            info['vacaciones'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'AF':
            info['asignacion_familiar'] = '{:.2f}'.format(n.amount)
        if n.salary_component == 'HORAS EXTRAS 25':
            info['horas_25'] = '{:.2f}'.format(n.amount)
        if n.salary_component == 'HORAS EXTRAS 35':
            info['horas_35'] = '{:.2f}'.format(n.amount)
        if n.salary_component == 'HORAS EXTRAS 100':
            info['horas_100'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'HN':
            info['horas_nocturnas'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'MV':
            info['movilidad'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'OI':
            info['otros_ingresos'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'GRATI':
            info['gratificacion'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'BE9':
            info['bonif_ext'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'VIT':
            info['viaticos_earn'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'VI':
            info['viaticos_ingreso'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'APY':
            info['apoyos'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'MVU':
            info['movilidad_variable'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'DM':
            info['descando_medico'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'LIC':
            info['licencia'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'LCG':
            info['LICENCIA_GOCE'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'LPF':
            info['LICENCIA_FALLECIMIENTO'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'LPP':
            info['LICENCIA_PATERNIDAD'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'COMP':
            info['COMPENSATORIO'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'SPA':
            info['SUBSIDIO_ACCIDENTE'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'SPE':
            info['SUBSIDIO_ENFERMEDAD'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'SPM':
            info['SUBSIDIO_MATERNIDAD'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'VI':
            info['ingreso_viaticos'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'CDT':
            info['condiciones_trabajo'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'CDN':
            info['canasta_navidad_in'] = '{:.2f}'.format(n.amount)

    # Conditions Deductions
    for n in info['deductions']:
        if n.abbr == 'SNP':
            info['snp'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'AFPF':
            info['afp_fondo'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'AFPS':
            info['afp_seguro'] = '{:.2f}'.format(n.amount)
        if n.salary_component == 'AFP COMISION ERP':
            info['afp_comision'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'FP':
            info['faltas_y_permisos'] = '{:.2f}'.format(n.amount)
        if n.abbr == '5CA':
            info['ta_categoria'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'VIA D':
            info['viaticos'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'GB':
            info['gratificacion_bonificacion'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'RIMAC':
            info['seguros_rimac'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'ADEL':
            info['adelantos'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'DESA':
            info['desc_alimentos'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'EPP':
            info['epp'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'OD':
            info['otros_descuentos'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'APY_1':
            info['apoyos_deductions'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'SS':
            info['seguro_salud_erp'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'VDL':
            info['vida_ley_componente'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'SCTRP':
            info['sctr_componente_pension'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'SCTRS':
            info['sctr_componente_salud'] = '{:.2f}'.format(n.amount)
        if n.abbr == 'CDN_2':
            info['canasta_navidad_eg'] = '{:.2f}'.format(n.amount)

    info['viaticos_earn'] = 0 if info['viaticos_earn'] == 0 else info['viaticos_earn']
    info['viaticos_ingreso'] = 0 if info['viaticos_ingreso'] == 0 else info['viaticos_ingreso']
    info['suma_viaticos'] = float(info['viaticos_earn']) + float(info['viaticos_ingreso'])

    info['total_aportes_componente'] = '{:.2f}'.format(float(info['seguro_salud_erp']) + float(info['vida_ley_componente']) + float(info['sctr_componente_pension']) + float(info['sctr_componente_salud']))
    info['sumAllMobility'] = '{:.2f}'.format(float(info['movilidad_variable']) + float(info['movilidad']))

    # Datos del Trabajador
    # info['sueldo'] = '{:.2f}'.format(info['data_employee'].remuneracion_mensual)

    info['fecha_de_cese'] = info['data_employee'].fecha_de_relevo

    if info['fecha_de_cese'] == None :
        info['fecha_de_cese'] = '-'
    else:
        # Fecha de relevo

        fecha_relevo = str(info['fecha_de_cese']).split(sep='-')

        anio_relevo = str(info['fecha_de_cese']).split(sep='-')[0]
        mes_relevo = str(info['fecha_de_cese']).split(sep='-')[1]
        dia_relevo = str(info['fecha_de_cese']).split(sep='-')[2]

        fecha_relevo_final = dia_relevo + '-' + mes_relevo + '-' + anio_relevo

        info['fecha_de_cese'] = fecha_relevo_final

    if info['data_employee'].place_of_issue == None :
        info['data_employee'].place_of_issue = '-'

    if info['data_employee'].cussp == None :
        info['data_employee'].cussp = '-'

    if info['data_employee'].gender == None :
        info['data_employee'].gender = '-'

    if info['data_employee'].calificacion_trabajador == None :
        info['data_employee'].calificacion_trabajador = '-'


    if info['data_employee'].fondo_de_pensiones == None :
        info['data_employee'].fondo_de_pensiones = '-'

    if info['data_employee'].bank_ac_no == None :
        info['data_employee'].bank_ac_no = '-'
    else:
        info['numero_de_cuenta'] = info['data_employee'].bank_ac_no


    # return info
    html = template.render(info)
    frappe.local.response.filename = "Nomina "+doc_data["employee"]+".pdf"
    frappe.local.response.filecontent = get_pdf(html, {"orientation": "Portrait","page-size":"A4"})
    frappe.local.response.type = "pdf"

@frappe.whitelist()
def report_salary_slip_massive(branch=None,department=None,month=None,year=None):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'salary_slip_pdf_massive.html')

    route_template = filename
    name_template = route_template.split('/')[-1]
    route_template = route_template.replace(name_template, '')

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(route_template))
    template = env.get_template(name_template)
    filters = {}
    if branch is not None:
        filters["branch"] = branch
    if department is not None:
        filters["department"] = department
    start_date = year+'-'+month+'-01'
    filters["start_date"] = start_date
    data_salary_slip = frappe.db.get_list('Salary Slip', filters=filters, fields=['*'], as_list=False)
    sal_slip = []
    for gg in data_salary_slip:
        info = get_payroll_by_name_massive(gg)
        info['haber_mensual']  = 0
        info['vacaciones']  = 0
        info['asignacion_familiar']  = 0
        info['horas_25']  = 0
        info['horas_35']  = 0
        info['horas_100']  = 0
        info['horas_nocturnas']  = 0
        info['movilidad']  = 0
        info['otros_ingresos']  = 0
        info['gratificacion']  = 0
        info['bonif_ext']  = 0
        info['viaticos_earn']  = 0
        info['viaticos_ingreso']  = 0
        info['apoyos']  = 0
        info['descando_medico']  = 0
        info['licencia']  = 0
        info['LICENCIA_GOCE']  = 0
        info['LICENCIA_FALLECIMIENTO']  = 0
        info['LICENCIA_PATERNIDAD']  = 0
        info['COMPENSATORIO']  = 0
        info['SUBSIDIO_ACCIDENTE']  = 0
        info['SUBSIDIO_ENFERMEDAD']  = 0
        info['SUBSIDIO_MATERNIDAD']  = 0
        info['ingreso_viaticos']  = 0
        info['canasta_navidad_in']  = 0

        info['snp']  = 0
        info['afp_fondo']  = 0
        info['afp_seguro']  = 0
        info['afp_comision']  = 0
        info['faltas_y_permisos']  = 0
        info['ta_categoria']  = 0
        info['viaticos_ded']  = 0
        info['gratificacion_bonificacion']  = 0
        info['seguros_rimac']  = 0
        info['adelantos']  = 0
        info['desc_alimentos']  = 0
        info['epp']  = 0
        info['otros_descuentos']  = 0
        info['apoyos_deductions']  = 0
        info['seguro_salud_erp'] = 0
        info['vida_ley_componente'] = 0
        info['total_aportes_componente'] = 0
        info['sctr_componente_pension'] = 0
        info['sctr_componente_salud'] = 0
        info['canasta_navidad_eg']  = 0

        # Fecha de boleta
        Meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre']
        Mes_boleta = str(info['start_date']).split(sep='-')
        Mes = str(info['start_date']).split(sep='-')[1]
        Anio = str(info['start_date']).split(sep='-')[0]
        numero_mes = int(Mes)
        info['mes_boleta'] = Meses[numero_mes - 1].upper()
        info['ano_boleta'] = Anio.upper()

        # return info['mes_boleta']

        # Fecha de pago final Dia Mes Año
        fecha_pago = str(info['end_date']).split(sep='-')

        dia_pago  = str(info['end_date']).split(sep='-')[2]
        mes_pago  = str(info['end_date']).split(sep='-')[1]
        anio_pago = str(info['end_date']).split(sep='-')[0]

        fecha_pago_final = dia_pago + '-' + mes_pago + '-' + anio_pago

        info['fecha_final_pago'] = fecha_pago_final

        # fecha de ingreso
        fecha_ingreso = str(info['fecha_ingreso']).split(sep='-')

        anio_ingreso = str(info['fecha_ingreso']).split(sep='-')[0]
        mes_ingreso = str(info['fecha_ingreso']).split(sep='-')[1]
        dia_ingreso = str(info['fecha_ingreso']).split(sep='-')[2]

        fecha_ingreso_final = dia_ingreso + '-' + mes_ingreso + '-' + anio_ingreso

        info['fecha_final_ingreso'] = fecha_ingreso_final

        # Fecha de nacimiento
        fecha_nacimiento_nomina = str(info['fecha_nacimiento']).split(sep='-')

        anio_nacimiento = str(info['fecha_nacimiento']).split(sep='-')[0]
        mes_nacimiento = str(info['fecha_nacimiento']).split(sep='-')[1]
        dia_nacimiento = str(info['fecha_nacimiento']).split(sep='-')[2]

        fecha_nacimiento_final = dia_nacimiento + '-' + mes_nacimiento + '-' + anio_nacimiento

        info['fecha_final_nacimiento'] = fecha_nacimiento_final

        # return fecha_ingreso_final
        #data empleado by PIERO
        info['data_employee'] = frappe.db.get_list('Employee', fields=["*"],filters={'name': info['employee']}, as_list=False)[0]
        # info["VACACIONES"].holidays_validation = False
        # info["VACACIONES"].holidays_periodo = ""
        # info["VACACIONES"].holidays_from_date = ""
        # info["VACACIONES"].holidays_to_date = ""
        # info["VACACIONES"] = {
        #     "holidays_validation" : False
        # }
        # return info
        info["vacaciones_uno"] = {
            "holidays_validation" : False,
            "holidays_periodo" : '',
            "holidays_from_date" : '',
            "holidays_to_date" : ''
        }
        info["vacaciones_compradas_dos"] = {
            "holidays_validation" : False,
            "holidays_periodo" : '',
            "holidays_from_date" : '',
            "holidays_to_date" : ''
        }
        holidays = frappe.db.get_list('Leave Allocation', fields=["from_date","to_date","leave_type","periodo"],filters={'employee': info['employee'],'leave_type':['in',["VACACIONES","VACACIONES COMPRADAS"]]}, as_list=False)
        if len(holidays)>0:
            for n in holidays:
                from_date = str(n.from_date).split('-')
                to_date = str(n.to_date).split('-')
                start_date = str(info['start_date']).split('-')
                end_date = str(info['end_date']).split('-')
                from_date = datetime(int(from_date[0]), int(from_date[1]), int(from_date[2]))
                to_date = datetime(int(to_date[0]), int(to_date[1]), int(to_date[2]))
                start_date = datetime(int(start_date[0]), int(start_date[1]), int(start_date[2]))
                end_date = datetime(int(end_date[0]), int(end_date[1]), int(end_date[2]))
                if start_date<=from_date<=end_date or  start_date<=to_date<=end_date :
                    if n.leave_type == "VACACIONES":
                        info["vacaciones_uno"] = {
                            "holidays_validation" : True,
                            "holidays_periodo" : "2022-2023" if (n.periodo is None) else n.periodo,
                            "holidays_from_date" : n.from_date.strftime('%d-%m-%Y'),
                            "holidays_to_date" : n.to_date.strftime('%d-%m-%Y')
                        }
                    if n.leave_type == "VACACIONES COMPRADAS":
                        info["vacaciones_compradas_dos"] = {
                            "holidays_validation" : True,
                            "holidays_periodo" : "2022-2023" if (n.periodo is None) else n.periodo,
                            "holidays_from_date" : n.from_date.strftime('%d-%m-%Y'),
                            "holidays_to_date" : n.to_date.strftime('%d-%m-%Y')
                        }
        if info['data_employee'].bank_name == None :
            info['data_employee'].bank_name = '-'
        else:
            info['nombre_banco_erp'] = info['data_employee'].bank_name

        # Conviertiendo a entero
        info['total_dias_trabajo'] = int(info['payment_days'])
        info['ausencias'] = int(info['ausencias_reales'])
        info['dias_subsidio'] = int(info['dias_subsidiados'])
        info['dias_no_subsidio'] = int(info['dias_no_subsidiados'])

        # vacaciones + compras de vacaciones

        info['pago_neto'] = '{:.2f}'.format(info['net_pay'])
        info['vacaciones_cantidad'] = int(info['dias_vaciones'])
        info['vacaciones_compradas_cantidad'] = info['vacaciones_compradas']

        info['vacaciones_con_compradas'] = info['vacaciones_cantidad'] + info['vacaciones_compradas_cantidad']

        info['licencia_falle_pate'] = info['licencia_por_fallecimiento'] + info['licencia_paternidad']

        info['sueldo_empleado'] = '{:.2f}'.format(info['sueldo'])
        info['horas_25_cantidad'] = '{:.2f}'.format(info['n_horas_extras_25'])
        info['horas_35_cantidad'] = '{:.2f}'.format(info['n_horas_extras_35'])
        info['horas_100_cantidad'] = '{:.2f}'.format(info['n_horas_extras_100'])
        info['total_ingresos_nomina'] = '{:.2f}'.format(info['gross_pay'])
        info['total_deduciones_nomina'] = '{:.2f}'.format(info['total_deduction'])

        # info['sueldo'] = '{:.2f}'.format(info['haber_mensual'])

        # Dias Subsidiados
        info['sub_maternidad'] = info['subsidio_por_maternidad']
        info['sub_accidente'] = info['subsidio_accidente']
        info['sub_enfermedad'] = int(info['subsidio_enfermedad'])

        info['dias_subsidio_total'] = info['sub_maternidad'] + info['sub_accidente'] + info['sub_enfermedad']
        info['Dias_No_Laborados_ERP'] = int(info['total_working_days'] - info['payment_days'] - info['dias_subsidio_total'])

        # Dias No Subsidiados
        info['desca_medico'] = int(info['descanso_medico'])

        info['es_salud'] = info['essalud'] if info['essalud'] != None else 0.00

        # return info['es_salud']

        # Datos de la empresa
        info['ruc_compania'] = info['rucc']
        info['nombre_compania'] = info['razonn_social']
        info['telefono_compania'] = info['telefono']
        info['direccion_compania'] = info['direccion']

        # Nombre de compania
        info['compania_logo'] = info['company']

        if info['telefono_compania'] == None :
            info['telefono_compania'] = '-'

        for n in info['earnings']:
            if n.abbr == 'RM':
                info['haber_mensual'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'VC':
                info['vacaciones'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'AF':
                info['asignacion_familiar'] = '{:.2f}'.format(n.amount)
            if n.salary_component == 'HORAS EXTRAS 25':
                info['horas_25'] = '{:.2f}'.format(n.amount)
            if n.salary_component == 'HORAS EXTRAS 35':
                info['horas_35'] = '{:.2f}'.format(n.amount)
            if n.salary_component == 'HORAS EXTRAS 100':
                info['horas_100'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'HN':
                info['horas_nocturnas'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'MV':
                info['movilidad'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'OI':
                info['otros_ingresos'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'GRATI':
                info['gratificacion'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'BE9':
                info['bonif_ext'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'VIT':
                info['viaticos_earn'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'VI':
                info['viaticos_ingreso'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'APY':
                info['apoyos'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'DM':
                info['descando_medico'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'LIC':
                info['licencia'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'LCG':
                info['LICENCIA_GOCE'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'LPF':
                info['LICENCIA_FALLECIMIENTO'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'LPP':
                info['LICENCIA_PATERNIDAD'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'COMP':
                info['COMPENSATORIO'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'SPA':
                info['SUBSIDIO_ACCIDENTE'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'SPE':
                info['SUBSIDIO_ENFERMEDAD'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'SPM':
                info['SUBSIDIO_MATERNIDAD'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'VI':
                info['ingreso_viaticos'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'CDN':
                info['canasta_navidad_in'] = '{:.2f}'.format(n.amount)

        # Conditions Deductions
        for n in info['deductions']:
            if n.abbr == 'SNP':
                info['snp'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'AFPF':
                info['afp_fondo'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'AFPS':
                info['afp_seguro'] = '{:.2f}'.format(n.amount)
            if n.salary_component == 'AFP COMISION ERP':
                info['afp_comision'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'FP':
                info['faltas_y_permisos'] = '{:.2f}'.format(n.amount)
            if n.abbr == '5CA':
                info['ta_categoria'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'VIA D':
                info['viaticos_ded'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'GB':
                info['gratificacion_bonificacion'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'RIMAC':
                info['seguros_rimac'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'ADEL':
                info['adelantos'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'DESA':
                info['desc_alimentos'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'EPP':
                info['epp'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'OD':
                info['otros_descuentos'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'APY_1':
                info['apoyos_deductions'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'SS':
                info['seguro_salud_erp'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'VDL':
                info['vida_ley_componente'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'SCTRP':
                info['sctr_componente_pension'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'SCTRS':
                info['sctr_componente_salud'] = '{:.2f}'.format(n.amount)
            if n.abbr == 'CDN_2':
                info['canasta_navidad_eg'] = '{:.2f}'.format(n.amount)


        #earning ingr
        #deduction ded
        info['viaticos_earn'] = 0 if info['viaticos_earn'] == 0 else info['viaticos_earn']
        info['viaticos_ingreso'] = 0 if info['viaticos_ingreso'] == 0 else info['viaticos_ingreso']
        info['suma_viaticos'] = float(info['viaticos_earn']) + float(info['viaticos_ingreso'])


        info['total_aportes_componente'] = '{:.2f}'.format(float(info['seguro_salud_erp']) + float(info['vida_ley_componente']) + float(info['sctr_componente_pension']) + float(info['sctr_componente_salud']))

        # Datos del Trabajador
        # info['sueldo'] = '{:.2f}'.format(info['data_employee'].remuneracion_mensual)

        info['fecha_de_cese'] = info['data_employee'].fecha_de_relevo

        if info['fecha_de_cese'] == None :
            info['fecha_de_cese'] = '-'
        else:
            # Fecha de relevo

            fecha_relevo = str(info['fecha_de_cese']).split(sep='-')

            anio_relevo = str(info['fecha_de_cese']).split(sep='-')[0]
            mes_relevo = str(info['fecha_de_cese']).split(sep='-')[1]
            dia_relevo = str(info['fecha_de_cese']).split(sep='-')[2]

            fecha_relevo_final = dia_relevo + '-' + mes_relevo + '-' + anio_relevo

            info['fecha_de_cese'] = fecha_relevo_final

        if info['data_employee'].place_of_issue == None :
            info['data_employee'].place_of_issue = '-'

        if info['data_employee'].cussp == None :
            info['data_employee'].cussp = '-'

        if info['data_employee'].gender == None :
            info['data_employee'].gender = '-'

        if info['data_employee'].calificacion_trabajador == None :
            info['data_employee'].calificacion_trabajador = '-'

        if info['data_employee'].fondo_de_pensiones == None :
            info['data_employee'].fondo_de_pensiones = '-'

        if info['data_employee'].bank_ac_no == None :
            info['data_employee'].bank_ac_no = '-'
        else:
            info['numero_de_cuenta'] = info['data_employee'].bank_ac_no

        sal_slip.append(info)
    my_dict = {'sal_slip':sal_slip}
    html = template.render(my_dict)
    frappe.local.response.filename = "Nominas.pdf"
    frappe.local.response.filecontent = get_pdf(html, {"orientation": "Portrait","page-size":"A4"})
    frappe.local.response.type = "pdf"


