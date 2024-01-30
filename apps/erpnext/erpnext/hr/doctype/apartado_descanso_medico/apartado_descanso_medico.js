// Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Apartado Descanso Medico', {
	refresh: function(frm) {
        if ( frm.doc.seguimiento === "CON SEGUIMIENTO" && frm.doc.cantidad_de_llamadas !== 0 ) {
            let tamanoTabla = frm.doc.table_35

            if ( tamanoTabla.length && tamanoTabla.length >= frm.doc.cantidad_de_llamadas ) frm.toggle_enable('table_35', false)
        }
	},
});

frappe.ui.form.on('table_control', {
    table_35_add(frm, cdt, cdn) {
        if ( frm.doc.table_35.length > frm.doc.cantidad_de_llamadas ) {
            var tbl = frm.doc.table_35 || [];
            var i = tbl.length;
            while (i--) {
                if ( tbl[i].fecha == undefined ) {
                    cur_frm.get_field("table_35").grid.grid_rows[i].remove();
                }
            }
            frappe.throw('Excedio el maximo de llamadas')
        }
    }
});