# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe.utils import flt
from frappe import _
from datetime import datetime
from datetime import date


def execute(filters=None):
    if not filters: filters = {}
    currency = 'PEN'
    company_currency = erpnext.get_company_currency(filters.get("company"))
    salary_slips = get_salary_slips(filters, company_currency)

    if not salary_slips: return [], []

    columns = get_columns(salary_slips)
    ss_earning_map = get_ss_earning_map(salary_slips, currency, company_currency)
    ss_ded_map = get_ss_ded_map(salary_slips,currency, company_currency)
    data = []
    for ss in salary_slips:
        #EARNINGS
        absence = get_attendance(ss.start_date, ss.end_date, ss.employee)[0]["contador"]
        viati = get_viaticos(ss.start_date,ss.employee)
        employees = get_employee(ss.employee)
        viat_earn = 0
        viat_ded = 0
        if len(viati) > 0 :
            viati = viati[0]
            if viati.solo_entrada:
                viat_ded = 0
                viat_earn = viati.monto_total
            else:
                viat_earn = viati.monto_total
                viat_ded = viati.monto_total
        haber_mensual = 0 if ss_earning_map.get(ss.name, {}).get("HABER MENSUAL") is None else ss_earning_map.get(ss.name, {}).get("HABER MENSUAL")
        vacaciones = 0 if ss_earning_map.get(ss.name, {}).get("VACACIONES") is None else ss_earning_map.get(ss.name, {}).get("VACACIONES")
        asigna_f = 0 if ss_earning_map.get(ss.name, {}).get("ASIGNACION FAMILIAR") is None else ss_earning_map.get(ss.name, {}).get("ASIGNACION FAMILIAR")
        apoyos = 0 if ss_earning_map.get(ss.name, {}).get("APOYOS") is None else ss_earning_map.get(ss.name, {}).get("APOYOS")
        h_25 =  0 if ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 25") is None else ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 25")
        h_35 =  0 if ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 35") is None else ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 35")
        h_100 =  0 if ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 100") is None else ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 100")
        hours = h_25 + h_35
        horas_extras_totales = h_25 + h_35 + h_100
        hours = round(hours,2)
        h_n =  0 if ss_earning_map.get(ss.name, {}).get("HORAS NOCTURNAS") is None else ss_earning_map.get(ss.name, {}).get("HORAS NOCTURNAS")
        movilidad = 0 if ss_earning_map.get(ss.name, {}).get("MOVILIDAD") is None else ss_earning_map.get(ss.name, {}).get("MOVILIDAD")
        gratificacion_earn = 0 if ss_earning_map.get(ss.name, {}).get("GRATIFICACION") is None else ss_earning_map.get(ss.name, {}).get("GRATIFICACION")
        bonif = 0 if ss_earning_map.get(ss.name, {}).get("BONIF EXT 9%") is None else ss_earning_map.get(ss.name, {}).get("BONIF EXT 9%")
        otrs_ing = 0 if ss_earning_map.get(ss.name, {}).get("OTROS INGRESOS") is None else ss_earning_map.get(ss.name, {}).get("OTROS INGRESOS")
        #DEDUCTIONS

        snp = 0 if ss_ded_map.get(ss.name, {}).get("SNP") is None else ss_ded_map.get(ss.name, {}).get("SNP")
        afp_fondo = 0 if ss_ded_map.get(ss.name, {}).get("AFP FONDO") is None else ss_ded_map.get(ss.name, {}).get("AFP FONDO")
        afp_seguro = 0 if ss_ded_map.get(ss.name, {}).get("AFP SEGURO") is None else ss_ded_map.get(ss.name, {}).get("AFP SEGURO")
        afp_comision = 0 if ss_ded_map.get(ss.name, {}).get("AFP COMISION ERP") is None else ss_ded_map.get(ss.name, {}).get("AFP COMISION ERP")
        totals_afp = afp_fondo + afp_seguro + afp_comision
        adelantos = 0 if ss_ded_map.get(ss.name, {}).get("ADELANTOS") is None else ss_ded_map.get(ss.name, {}).get("ADELANTOS")
        cat = 0 if ss_ded_map.get(ss.name, {}).get("5TA CAGEGORIA") is None else ss_ded_map.get(ss.name, {}).get("5TA CAGEGORIA")
        grat_ded = 0 if ss_ded_map.get(ss.name, {}).get("GRATIFICACION / BONIF 9%") is None else ss_ded_map.get(ss.name, {}).get("GRATIFICACION / BONIF 9%")
        sg_r = 0 if ss_ded_map.get(ss.name, {}).get("SEGUROS RIMAC") is None else ss_ded_map.get(ss.name, {}).get("SEGUROS RIMAC")
        ret_judicial = 0 if ss_ded_map.get(ss.name, {}).get("DESC ALIMENTOS") is None else ss_ded_map.get(ss.name, {}).get("DESC ALIMENTOS")
        otr_desc = 0 if ss_ded_map.get(ss.name, {}).get("OTROS DESCUENTOS") is None else ss_ded_map.get(ss.name, {}).get("OTROS DESCUENTOS")
        epp = 0 if ss_ded_map.get(ss.name, {}).get("EPP") is None else ss_ded_map.get(ss.name, {}).get("EPP")
        essalud = 0 if ss_ded_map.get(ss.name, {}).get("SEGURO SALUD") is None else ss_ded_map.get(ss.name, {}).get("SEGURO SALUD")
        inasistencias = (absence) * round(((employees[0].remuneracion_mensual + asigna_f ) / ss.total_working_days ),2)
        totals = epp + otr_desc + ret_judicial + sg_r + grat_ded + viat_ded + cat + adelantos + totals_afp + snp + inasistencias
        totals = round(totals,2)
        jornal_diary = round(((employees[0].remuneracion_mensual + asigna_f ) / ss.total_working_days ),2)
        subsidy = ss.subsidio_por_maternidad + ss.subsidio_accidente + ss.subsidio_enfermedad
        hours_working = ss.total_working_days * 8
        row = [ss.name, ss.employee, ss.employee_name,ss.branch,employees[0].zona_recursos,ss.documento_identidad,
               employees[0].date_of_birth, ss.fecha_ingreso, employees[0].designation, employees[0].fondo_de_pensiones,ss.fondo_comision,
               ss.payment_days,ss.total_working_days - ss.payment_days, ss.dias_vaciones, ss.descanso_medico,subsidy,ss.sueldo,asigna_f,ss.n_horas_extras_25,
               ss.n_horas_extras_35, ss.n_horas_extras_100, h_25, h_35, h_100, horas_extras_totales,employees[0].movilidad,
               h_n,ss.apoyo, " ", otrs_ing, employees[0].bank_name, employees[0].bank_ac_no, ret_judicial,
               cat, adelantos, otr_desc, viat_ded, " ", sg_r, epp, " ", " ",
               " ", " ", " ", " "

               ]
        # if ss.branch is not None: columns[4] = columns[4].replace('-1','120')
        data.append(row)

    return columns, data

def get_attendance(start_date, end_date, employee):
    values = {'start_date': start_date, 'end_date':end_date, 'employee':employee}
    attendance = frappe.db.sql("""select count(name) as contador from `tabAttendance` where attendance_date BETWEEN %(start_date)s AND %(end_date)s  AND status NOT IN ('Present','Work From Home') AND employee = %(employee)s  AND docstatus != 2 """ ,values=values, as_dict=True)
    return attendance

def get_employee(employee):
    values = {'name': employee}
    employees = frappe.db.sql("""select name,fondo_de_pensiones, movilidad, remuneracion_mensual, designation, date_of_birth, bank_name, bank_ac_no, zona_recursos from `tabEmployee` where name=%(name)s  """ ,values=values, as_dict=True)
    return employees

def get_viaticos(start_date, employee):
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre']
    start_date = str(start_date).split(sep='-')
    mes = meses[int(start_date[1]) - 1]
    anio = int(start_date[0])
    values = {'mes': mes, 'employee':employee,'anio': anio}
    viaticos = frappe.db.sql("""select name,monto_total, solo_entrada from `tabViaticos Nomina` where empleado=%(employee)s AND mes = %(mes)s AND ano = %(anio)s""" ,values=values, as_dict=True)
    return viaticos

def get_columns(salary_slips):
    columns = [
        _("ID DE NOMINA") + ":Link/Salary Slip:150",
        _("EMPLEADO") + ":Link/Employee:200",
        _("NOMBRE DE EMPLEADO") + "::200",
        _("SUCURSAL") + ":Link/Branch:-1" + "::200",
        {
            'label': _("ZONA"),
            'fieldname': 'zona',
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'label': _("DNI"),
            'fieldname': 'documento_identidad',
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'label': "FECHA DE NACIMIENTO",
            'fieldname': 'date_of_birth',
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'label': _("FECHA DE INGRESO"),
            'fieldname': 'fecha_ingreso',
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'label': _("CARGO"),
            'fieldname': 'designation',
            'fieldtype': 'Data',
            'width': 200
        },
        _("SPP") + ":Link/Fondo de Pensiones:-1" + "::200",
        {
            'label': _("%"),
            'fieldname': 'fondo_comision',
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'label': _("DIAS LABORADOS"),
            'fieldname': 'dias_laborados',
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'label': _("DIAS NO LABORADOS"),
            'fieldname': 'dias_no_laborados',
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'label': _("VACACIONES"),
            'fieldname': 'dias_vaciones',
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'label': _("DESCANSO MEDICO"),
            'fieldname': 'descanso_medico',
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'label': _("SUBSIDIO"),
            'fieldname': 'subsidio',
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'label': _("REM. MENSUAL"),
            'fieldname': 'haber_mensual',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("ASIG. FAM"),
            'fieldname': 'asigna_f',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("HORAS AL 25%"),
            'fieldname': 'n_horas_extras_25',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("HORAS AL 35%"),
            'fieldname': 'n_horas_extras_35',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("HORAS AL 100%"),
            'fieldname': 'n_horas_extras_100',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("S/ HH.EE AL 25%"),
            'fieldname': 'h_25',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("S/ HH.EE AL 35%"),
            'fieldname': 'h_35',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("S/ HH.EE AL 100%"),
            'fieldname': 'h_100',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("TOTAL S/ HH.EE"),
            'fieldname': 'horas_extras_totales',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("MOVILIDAD"),
            'fieldname': 'movilidad_employee',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("S/ HORA NOCTURNA"),
            'fieldname': 'h_n',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("APOYO"),
            'fieldname': 'apoyo',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("REINTEGRO"),
            'fieldname': 'reintegro',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("OTROS INGRESOS"),
            'fieldname': 'otrs_ing',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("BANCO"),
            'fieldname': 'banco',
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'label': _("CUENTA A SUELDO"),
            'fieldname': 'cuenta',
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'label': _("RETENCION ALIMENTOS"),
            'fieldname': 'ret_judicial',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("RENTA 5TA"),
            'fieldname': 'renta',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("ADELANTO"),
            'fieldname': 'adelanto',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("OTROS DESCUENTOS"),
            'fieldname': 'otros_descuentos',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("VIATICOS"),
            'fieldname': 'viaticos_ded',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("SCTR"),
            'fieldname': 'sctr',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("RIMAC"),
            'fieldname': 'rimac',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("E.P.P"),
            'fieldname': 'epp',
            'fieldtype': 'Float',
            'width': 200
        },
        {
            'label': _("FECHA INICIO CONTRATO"),
            'fieldname': 'inicio_contrato',
            'fieldtype': 'data',
            'width': 200
        },
        {
            'label': _("FECHA FIN CONTRATO"),
            'fieldname': 'fin_contrato',
            'fieldtype': 'data',
            'width': 200
        },
        {
            'label': _("SUSPENSION"),
            'fieldname': 'suspension',
            'fieldtype': 'data',
            'width': 200
        },
        {
            'label': _("INICIO DE SUSPENSION"),
            'fieldname': 'inicio_suspension',
            'fieldtype': 'data',
            'width': 200
        },
        {
            'label': _("FIN DE SUSPENSION"),
            'fieldname': 'fin_suspension',
            'fieldtype': 'data',
            'width': 200
        },
        {
            'label': _("OBS"),
            'fieldname': 'obs',
            'fieldtype': 'data',
            'width': 200
        },
        ]
    return columns

def get_salary_slips(filters, company_currency):
    filters.update({"from_date": filters.get("from_date"), "to_date":filters.get("to_date")})
    conditions, filters = get_conditions(filters, company_currency)
    salary_slips = frappe.db.sql("""select * from `tabSalary Slip` where %s
		order by employee""" % conditions, filters, as_dict=1)

    return salary_slips or []

def get_conditions(filters, company_currency):
    conditions = ""
    doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

    if filters.get("docstatus"):
        conditions += "docstatus = {0}".format(doc_status[filters.get("docstatus")])

    if filters.get("from_date"): conditions += " and start_date >= %(from_date)s"
    if filters.get("to_date"): conditions += " and end_date <= %(to_date)s"
    if filters.get("company"): conditions += " and company = %(company)s"
    if filters.get("employee"): conditions += " and employee = %(employee)s"
    if filters.get("branch"): conditions += " and branch = %(branch)s"

    return conditions, filters


def get_ss_earning_map(salary_slips, currency, company_currency):
    ss_earnings = frappe.db.sql("""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)""" %
                                (', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

    ss_earning_map = {}
    for d in ss_earnings:
        ss_earning_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, [])
        if currency == company_currency:
            ss_earning_map[d.parent][d.salary_component] = flt(d.amount) * flt(d.exchange_rate if d.exchange_rate else 1)
        else:
            ss_earning_map[d.parent][d.salary_component] = flt(d.amount)

    return ss_earning_map

def get_ss_ded_map(salary_slips, currency, company_currency):
    ss_deductions = frappe.db.sql("""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)""" %
                                  (', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

    ss_ded_map = {}
    for d in ss_deductions:
        ss_ded_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, [])
        if currency == company_currency:
            ss_ded_map[d.parent][d.salary_component] = flt(d.amount) * flt(d.exchange_rate if d.exchange_rate else 1)
        else:
            ss_ded_map[d.parent][d.salary_component] = flt(d.amount)

    return ss_ded_map
