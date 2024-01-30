import frappe
from datetime import date
from datetime import datetime

@frappe.whitelist()
def check_cortes_permissions():
    user = frappe.session.user

    if "System Manager" in frappe.get_roles(user):
        return

    meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Setiembre","Octubre","Noviembre","Diciembre"]
    hoy = date.today()
    mes = hoy.month
    anio = hoy.year
    cortes = frappe.get_list("Corte Mensual",
                             fields=["fecha_de_corte","habilitado"],
                             filters=[
                                 ["mes","=",meses[int(mes)-1]],
                                 ["año","=",anio],
                             ],
                             order_by="creation desc")
    if len(cortes) <= 0:
        return
    fecha = cortes[0]["fecha_de_corte"]
    habilitado = cortes[0]["habilitado"]
    if hoy>fecha and habilitado == 1:
        frappe.throw("No se puede crear, editar, cancelar ni eliminar despues de la fecha de corte mensual")